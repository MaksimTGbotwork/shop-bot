import aiosqlite

DB_NAME = "shop.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price INTEGER,
                name TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                product_id INTEGER,
                quantity INTEGER
            )
        """)
        await db.commit()


async def add_product(name, price):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)", (name, price)
        )
        await db.commit()


async def get_all_products():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT id, name, price FROM products")
        return await cursor.fetchall()


async def add_to_cart(telegram_id, product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # проверим, есть ли уже такой товар в корзине у юзера
        cursor = await db.execute(
            "SELECT id, quantity FROM cart WHERE telegram_id = ? AND product_id = ?",
            (telegram_id, product_id),
        )
        existing = await cursor.fetchone()

        if existing:
            # если есть — увеличиваем количество на 1
            cart_id, quantity = existing
            await db.execute(
                "UPDATE cart SET quantity = ? WHERE id = ?", (quantity + 1, cart_id)
            )
        else:
            # если нет — добавляем новую запись с quantity=1
            await db.execute(
                "INSERT INTO cart (telegram_id, product_id, quantity) VALUES (?, ?, 1)",
                (telegram_id, product_id),
            )
        await db.commit()


async def get_cart(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """SELECT products.name, products.price, cart.quantity
               FROM cart
               JOIN products ON cart.product_id = products.id
               WHERE cart.telegram_id = ?""",
            (telegram_id,),
        )
        return await cursor.fetchall()


async def clear_cart(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM cart WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


import asyncio


async def test():
    await add_product("Обувь Nike", 500)
    await add_product("Носки Adidas", 40)
    await add_product("Футболка Gucci", 100)


asyncio.run(test())
