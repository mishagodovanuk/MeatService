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
from database import get_all_categories, get_sausages_by_category, get_sausage_by_id
from utils import format_sausage_text, get_image_path
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

user_orders = {}  # user_id -> sausage_id

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

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "<b>ℹ️ Інформація про виробника</b>\n\n"
        "🏭 <b>Назва:</b> ТОВ «Ковбасня Рівне»\n"
        "📍 <b>Адреса:</b> м. Рівне, вул. Мʼясна 12\n"
        "📞 <b>Телефон:</b> +38 (067) 000-00-00\n"
        "🌐 <b>Instagram:</b> @kovbasnia\n\n"
        "🧑‍🍳 Ми виготовляємо якісні ковбасні вироби з натурального мʼяса. "
        "Працюємо на ринку понад 10 років і постійно розширюємо асортимент."
    )

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
        [InlineKeyboardButton(text="Замовити", callback_data=f"order_{s[0]}")]
    ])
    try:
        with open(get_image_path(s[8]), "rb") as f:
            photo = BufferedInputFile(f.read(), filename=s[8])
        await query.message.answer_photo(photo=photo, caption=format_sausage_text(sausage), reply_markup=kb)
    except Exception:
        await query.message.answer(format_sausage_text(sausage), reply_markup=kb)

@dp.callback_query(lambda q: q.data.startswith("order_"))
async def order_callback(query: types.CallbackQuery):
    sausage_id = int(query.data.split("_")[1])
    user_orders[query.from_user.id] = sausage_id
    await query.message.answer(
        "📲 Введіть ваш номер телефону або імʼя й контакт:",
        reply_markup=ForceReply()
    )

@dp.message(F.reply_to_message)
async def contact_handler(message: types.Message):
    uid = message.from_user.id
    if uid not in user_orders:
        return
    sausage_id = user_orders.pop(uid)
    sausage = get_sausage_by_id(sausage_id)
    phone = message.text.strip()
    await message.reply(
        f"✅ Дякуємо! Ми з вами звʼяжемось щодо замовлення:\n"
        f"<b>{sausage[1]}</b> — {sausage[7]} грн/кг\n"
        f"Контакт: {phone}"
    )

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
