from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database import add_product, add_to_cart, clear_cart, get_all_products, get_cart

router = Router()


@router.message(Command("seed"))
async def seed_products(message: Message):
    await add_product("Обувь Nike", 500)
    await add_product("Носки Adidas", 40)
    await add_product("Футболка Gucci", 100)
    await add_product("Трусы Lacoste", 30)
    await add_product("Каблуки Versace", 600)
    await message.answer("Товары добавлены!")


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в наш магазин! 🛍️\n\n"
        "/shop — посмотреть товары\n"
        "/cart — моя корзина\n"
        "/help — помощь"
    )


@router.message(Command("help"))
async def help(message: Message):
    await message.answer(
        " <b>Список команд:</b>\n\n"
        "🛒 /cart — Просмотр вашей корзины\n"
        "🥼/shop — Просмотр товаров\n"
        "ℹ️ /help — показать это сообщение\n\n"
        "Нужна одежда? Просто напишите нам!",
        parse_mode="HTML",
    )


@router.message(Command("shop"))
async def show_shop(message: Message):
    products = await get_all_products()

    buttons = []
    for product_id, name, price in products:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{name} — {price}$", callback_data=f"product_{product_id}"
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Наши товары:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("product_"))
async def process_add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.replace("product_", ""))
    await add_to_cart(callback.from_user.id, product_id)
    await callback.message.answer("Товар добавлен в корзину😊")
    await callback.answer()


@router.message(Command("cart"))
async def show_cart(message: Message):
    carts = await get_cart(message.from_user.id)

    if not carts:
        await message.answer("Корзина пока что пуста😢")
        return

    text = "Ваша корзина:\n\n"
    total = 0

    for name, price, quantity in carts:
        item_total = price * quantity
        total += item_total
        text += f"Товар: {name}\nЦена: {price}$ x {quantity} = {item_total}$\n\n"

    text += f"Итого: {total}$"

    checkout_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Оформить заказ", callback_data="checkout", style="success"
                )
            ]
        ]
    )

    await message.answer(text, reply_markup=checkout_kb)


@router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.message.answer("Заказ оформлен, спасибо❤️")
    await callback.answer()
