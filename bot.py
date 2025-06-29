# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, InputFile,
    ForceReply, BufferedInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from database import (
    get_all_categories, get_sausages_by_category, get_sausage_by_id,
    add_to_cart, get_cart, clear_cart, place_order, get_order_history
)
from utils import format_sausage_text, get_image_path
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

pending_orders = {}  # user_id -> True
pending_cart_qty = {}  # user_id -> sausage_id

def build_catalog_keyboard():
    kb = InlineKeyboardBuilder()
    for cat_id, cat_name in get_all_categories():
        kb.button(text=cat_name, callback_data=f"cat_{cat_id}")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Оберіть категорію:", reply_markup=build_catalog_keyboard())


@dp.message(Command("menu", "catalog"))
async def menu_handler(message: types.Message):
    await message.answer("📦 Каталог продукції:", reply_markup=build_catalog_keyboard())


@dp.message(Command("about"))
async def about_handler(message: types.Message):
    await message.answer(
        "<b>ℹ️ Інформація про виробника</b>\n\n"
        "🏭 <b>Назва:</b> ТОВ «Ковбасня Рівне»\n"
        "📍 <b>Адреса:</b> м. Рівне, вул. Мʼясна 12\n"
        "📞 <b>Телефон:</b> +38 (067) 000-00-00\n"
        "🌐 <b>Instagram:</b> @kovbasnia\n\n"
        "🧑‍🍳 Ми виготовляємо якісні ковбасні вироби з натурального мʼяса. "
        "Працюємо на ринку понад 10 років і постійно розширюємо асортимент."
    )


@dp.message(Command("cart"))
async def cart_handler(message: types.Message):
    user_id = message.from_user.id
    cart_items = get_cart(user_id)

    if not cart_items:
        await message.answer("🧺 Ваш кошик порожній.")
        return

    text = "🧺 <b>Ваш кошик:</b>"
    total = 0
    for item in cart_items:
        sausage = get_sausage_by_id(item[0])
        if not sausage:
            continue
        price = sausage[7]
        qty = item[3]
        text += f"\n<b>{sausage[1]}</b> — {qty} шт × {price} грн"
        total += price * qty

    text += f"\n\n<b>Разом:</b> {total:.2f} грн"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Очистити", callback_data="clear_cart"),
            InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="proceed_order")
        ]
    ])

    await message.answer(text, reply_markup=kb)


@dp.callback_query(lambda q: q.data == "clear_cart")
async def clear_cart_cb(query: types.CallbackQuery):
    clear_cart(query.from_user.id)
    await query.message.answer("🗑 Кошик очищено.")


@dp.callback_query(lambda q: q.data == "proceed_order")
async def proceed_order_cb(query: types.CallbackQuery):
    pending_orders[query.from_user.id] = True
    await query.message.answer(
        "📲 Введіть ваші контактні дані (телефон, відділення Нової Пошти, коментарі):",
        reply_markup=ForceReply()
    )


@dp.message(Command("orderlist"))
async def order_history_handler(message: types.Message):
    orders = get_order_history(message.from_user.id)

    if not orders:
        await message.answer("📋 Історія замовлень порожня.")
        return

    text = "<b>📋 Ваші замовлення:</b>\n"
    for name, price, created_at in orders:
        text += f"\n🧾 <b>{name}</b> — {price} грн\n🗓 {created_at}"

    await message.answer(text)


@dp.callback_query(lambda q: q.data.startswith("cat_"))
async def category_callback(query: types.CallbackQuery):
    cat_id = int(query.data.split("_")[1])
    sausages = get_sausages_by_category(cat_id)
    kb = InlineKeyboardBuilder()
    for s in sausages:
        kb.button(text=f"{s[1][:30]} — {s[7]} грн", callback_data=f"s_{s[0]}")
    kb.adjust(1)
    await query.message.edit_text("Оберіть товар:", reply_markup=kb.as_markup())


@dp.callback_query(lambda q: q.data.startswith("s_"))
async def sausage_callback(query: types.CallbackQuery):
    sausage_id = int(query.data.split("_")[1])
    s = get_sausage_by_id(sausage_id)
    sausage = {
        "name": s[1],
        "grade": s[3],
        "packaging": s[4],
        "casing": s[5],
        "shelf_life": s[6],
        "price": s[7],
        "image": s[8],
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати до кошика", callback_data=f"add_{s[0]}")]
    ])
    try:
        with open(get_image_path(s[8]), "rb") as f:
            photo = BufferedInputFile(f.read(), filename=s[8])
        await query.message.answer_photo(photo=photo, caption=format_sausage_text(sausage), reply_markup=kb)
    except Exception:
        await query.message.answer(format_sausage_text(sausage), reply_markup=kb)


@dp.callback_query(lambda q: q.data.startswith("add_"))
async def add_to_cart_callback(query: types.CallbackQuery):
    sausage_id = int(query.data.split("_")[1])
    pending_cart_qty[query.from_user.id] = sausage_id
    await query.message.answer("📥 Введіть кількість:", reply_markup=ForceReply())


@dp.message(F.reply_to_message)
async def reply_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id in pending_cart_qty:
        try:
            qty = int(message.text.strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            await message.reply("❌ Введіть коректну кількість (наприклад: 2)")
            return

        sausage_id = pending_cart_qty.pop(user_id)
        add_to_cart(user_id, sausage_id, qty)
        await message.reply("✅ Товар додано до кошика. Перевірте /cart")

    elif pending_orders.pop(user_id, None):
        phone = message.text.strip()
        items = get_cart(user_id)
        if not items:
            await message.reply("❌ Ваш кошик порожній. Додайте товари перед замовленням.")
            return
        for item in items:
            place_order(user_id, item[0], item[3], phone)
        clear_cart(user_id)
        await message.reply("✅ Замовлення оформлено. Ми з вами звʼяжемось! 📞")


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
