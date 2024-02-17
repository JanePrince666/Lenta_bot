import asyncio
import datetime
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command, CommandStart
from config import my_token, CHANNEL_ID
from parser import TelegramChannel, TelegramPost
from db_management_OOP import connection
from profiler import time_of_function

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Объект бота
bot = Bot(token=my_token)

# Диспетчер
dp = Dispatcher()
router = Router()

# scheduler_update_post_list = AsyncIOScheduler(timezone="Asia/Tbilisi")
# scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")
# scheduler = AsyncIOScheduler(timezone="Asia/Tbilisi")


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
        last_post = int(message.text[-index:])
        url = url[:-1]
        stub = await TelegramPost(url, 1).get_text()
        connection.create_new_channel(url, stub, last_post)
        await message.answer("Добавила!")
    else:
        await message.answer("Не телеграм-пост")
        await message.delete()


# Функция получения новых постов
# @time_of_function
async def post():
    while True:
        for post_url, post_text in connection.get_posting_list():
            await bot.send_message(chat_id=CHANNEL_ID, text=f"{post_url}\n{post_text}")
            connection.del_from_posting_list(post_url)


async def get_new_posts():
    while True:
        for url, start_post in connection.get_channels_list():
            channel = TelegramChannel(url, start_post)
            await channel.check_new_posts()


# scheduler_update_post_list.add_job(get_new_posts, "interval", seconds=60)
# scheduler_for_posting.add_job(post, "interval", seconds=10)

# scheduler.add_job(get_new_posts, "interval", seconds=60)
# scheduler.add_job(post, "interval", seconds=10)


# Запуск процесса поллинга новых апдейтов
async def main():
    # scheduler_update_post_list.start()
    # scheduler_for_posting.start()
    # await get_new_posts()
    # await asyncio.gather(scheduler_update_post_list.start(), scheduler_for_posting.start())
    # scheduler.start()
    await dp.start_polling(bot)
    await asyncio.gather(get_new_posts(), post())


if __name__ == "__main__":
    asyncio.run(main())
