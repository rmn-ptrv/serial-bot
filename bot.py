import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiohttp import web

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv("PORT", 3000))

CHANNELS = ['@hardway_brand', '@smb_prod']
SERIALS_CHANNEL = 'https://t.me/serialich_pro'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_sub_channels(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if await check_sub_channels(user_id):
        return SendMessage(message.chat.id, f"Спасибо за подписку! Вот ссылка на канал с сериалами:{SERIALS_CHANNEL}")
    else:
        kb = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            kb.add(types.InlineKeyboardButton(f"Подписаться на {ch}", url=f"https://t.me/{ch[1:]}"))
        kb.add(types.InlineKeyboardButton("✅ Я подписался", callback_data="check_sub"))
        return SendMessage(message.chat.id, "Чтобы получить доступ к сериалам, подпишись на каналы и нажми кнопку ниже:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_sub_channels(user_id):
        await bot.send_message(user_id, f"Отлично! Вот ссылка на канал с сериалами:{SERIALS_CHANNEL}")
    else:
        await bot.send_message(user_id, "Пожалуйста, подпишись на все каналы и попробуй снова.")
    await bot.answer_callback_query(callback_query.id)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, dp.webhook_handler())

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        web_app=app,
    )