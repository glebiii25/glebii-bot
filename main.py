import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "7679280950:AAFmaBzbxCpDzDn1mkFAXQ49NU95PXXd-Zw"
CHANNEL_USERNAME = "@glebiiiq"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# главное меню
main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(
    InlineKeyboardButton("🧭 позиционирование", callback_data="positioning"),
    InlineKeyboardButton("🎨 дизайн", callback_data="design"),
    InlineKeyboardButton("📚 уроки", callback_data="lessons")
)

# меню "назад"
back_menu = InlineKeyboardMarkup()
back_menu.add(
    InlineKeyboardButton("⬅️ назад в меню", callback_data="back")
)

# временное хранилище пользователей, которые уже подписались
subscribed_users = set()

# проверка подписки
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# обработка /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        await message.answer("йоу бро, я не вижу твоей подписки!! так не честно 🤨\n\nподпишись на канал и напиши /start снова.")
        return

    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        text = "спасибо за подпискуу!! 🎉"
    else:
        text = "выбирай что нужно:"

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=types.InputFile("welcome.jpg"),
        caption=text,
        reply_markup=main_menu
    )

# обработка кнопок
@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    user_id = user.id
    username = user.username or "no_username"
    fullname = user.full_name
    data = callback_query.data

    is_subscribed = await check_subscription(user_id)

    print(f"🔘 user: {fullname} (@{username}) | id: {user_id} | clicked: {data} | subscribed: {is_subscribed}")

    if not is_subscribed:
        await callback_query.answer("ты не подписан на канал!", show_alert=True)
        return

    # удаление старого сообщения
    try:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    except:
        pass

    await bot.send_chat_action(user_id, action="upload_photo")

    if data == "positioning":
        if os.path.exists("positioning.jpg"):
            await bot.send_photo(user_id, types.InputFile("positioning.jpg"), caption="🧭 вот материалы по позиционированию", reply_markup=back_menu)
        else:
            await bot.send_message(user_id, "❌ файл positioning.jpg не найден.")
    elif data == "design":
        if os.path.exists("design.jpg"):
            await bot.send_photo(user_id, types.InputFile("design.jpg"), caption="🎨 вот материалы по дизайну", reply_markup=back_menu)
        else:
            await bot.send_message(user_id, "❌ файл design.jpg не найден.")
    elif data == "lessons":
        if os.path.exists("lessons.jpg"):
            await bot.send_photo(user_id, types.InputFile("lessons.jpg"), caption="📚 вот твои уроки", reply_markup=back_menu)
        else:
            await bot.send_message(user_id, "❌ файл lessons.jpg не найден.")
    elif data == "back":
        if os.path.exists("welcome.jpg"):
            await bot.send_photo(user_id, types.InputFile("welcome.jpg"), caption="выбирай что нужно:", reply_markup=main_menu)
        else:
            await bot.send_message(user_id, "❌ файл welcome.jpg не найден.")

    await callback_query.answer()

# запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)