import asyncio
import datetime
import random
import logging
import sys
import multiprocessing

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from config import my_token, CHANNEL_ID, DATA_FOR_DATABASE
from parser import get_new_posts
from db_management_OOP import ParsingChannels, PostingList
from profiler import time_of_function

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Объект бота
bot = Bot(token=my_token)

# Диспетчер
dp = Dispatcher(storage=storage)
# Создаем "базу данных" пользователей
router = Router()

# Создаем задачу по времени
scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")


# Функция получения новых постов
# @time_of_function
async def post():
    # print("начала постить")
    connection = PostingList(*DATA_FOR_DATABASE)
    new_posts = connection.get_posting_list()
    for post_url, post_text in new_posts:
        await bot.send_message(chat_id=CHANNEL_ID, text=f"{post_url}\n{post_text}")
        connection.del_from_posting_list(post_url)


# print(f"время постинга поста: {datetime.datetime.now()}")


scheduler_for_posting.add_job(post, "interval", seconds=10)

t2 = multiprocessing.Process(target=get_new_posts)


# Запуск процесса поллинга новых апдейтов
async def main():
    t2.start()
    scheduler_for_posting.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
