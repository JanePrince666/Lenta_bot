import asyncio
import datetime
import random
import logging
import sys
import multiprocessing

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import bot, DATA_FOR_DATABASE
from user_interface import commands, add_user_channel, add_watched_channel
from parser import get_new_posts
from db_management_OOP import PostingList
from profiler import time_of_function


# Функция постинга новых постов
# @time_of_function
async def post():
    # print("начала постить")
    connection = PostingList(*DATA_FOR_DATABASE)
    new_posts = connection.get_posting_list()
    for post_url, post_text, user_channel in new_posts:
        await bot.send_message(chat_id=int(user_channel), text=f"{post_url}\n{post_text}")
        connection.del_from_posting_list(post_url)


# print(f"время постинга поста: {datetime.datetime.now()}")

# Создаем задачу по времени
scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")
scheduler_for_posting.add_job(post, "interval", seconds=10)

t2 = multiprocessing.Process(target=get_new_posts)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(commands.router)
    dp.include_router(add_user_channel.router)
    dp.include_router(add_watched_channel.router)
    t2.start()
    scheduler_for_posting.start()
    # Запускаем бота и пропускаем все накопленные входящие
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
