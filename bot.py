import asyncio
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command, CommandStart
from config import my_token, CHANNEL_ID
from parser import TelegramPost, check_new_posts
from db_management_OOP import connection

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Объект бота
bot = Bot(token=my_token)

# Диспетчер
dp = Dispatcher()
router = Router()

scheduler = AsyncIOScheduler(timezone="Asia/Tbilisi")


# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Hello!")
    await message.delete()


# Хэндлер на команду /info
@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer("Бот для создания собственной ленты")
    await message.delete()


# Здесь должен быть хэндлер на прием id канала пользователя

# Хэндлер на прием новых каналов от пользователя
@dp.message()
async def cmd_add_channel(message: types.Message):
    if "https://t.me/" in message.text:
        url = ""
        for i in message.text:
            try:
                int(i)
            except ValueError:
                url += i
        index = len(message.text) - len(url)
        url = url[:-1]
        stub = TelegramPost(url, 1).get_text()
        last_post = int(message.text[-index:])
        connection.create_new_channel(url, stub, last_post)
        await message.answer("Добавила!")
    else:
        await message.answer("Не телеграм-пост")
        await message.delete()


# Функция получения новых постов
async def get_latest_posts():
    for url, last_post in connection.get_channels_list():
        for post in check_new_posts(url, last_post):
            await bot.send_message(chat_id=CHANNEL_ID, text=post.get_url() + "\n" + post.get_text())


scheduler.add_job(get_latest_posts, "interval", seconds=30)


# Запуск процесса поллинга новых апдейтов
async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
