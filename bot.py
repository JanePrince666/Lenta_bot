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
from user_interface import commands, management_user_channel, management_watched_channel
from parser import get_new_posts
from db_management_OOP import PostingList
from profiler import time_of_function


# Функция для отправки новых постов пользователям и удаления их из базы данных
# @time_of_function
async def post():
    # Устанавливаем соединение с базой данных
    connection = PostingList(*DATA_FOR_DATABASE)

    # Получаем список новых постов
    new_posts = connection.get_posting_list()

    # Отправляем каждый пост пользователям и удаляем его из списка
    for post_url, post_text, user_channel in new_posts:
        await bot.send_message(chat_id=int(user_channel), text=f"{post_url}\n{post_text}")
        connection.del_from_posting_list(post_url)


# Создаем задачу по времени
scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")
scheduler_for_posting.add_job(post, "interval", seconds=10)

# Создаем задачу для параллельного запуска процесса получения новых постов
t2 = multiprocessing.Process(target=get_new_posts)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Создаем диспетчер с хранилищем в памяти
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутер для обработки команд
    dp.include_routers(commands.router)

    # Подключаем роутеры для управления пользователями и каналами
    dp.include_router(management_user_channel.router)
    dp.include_router(management_watched_channel.router)

    # Запускаем новый процесс для выполнения функции get_new_posts
    t2.start()

    # Запускаем планировщик для публикации постов
    scheduler_for_posting.start()
    # Запускаем бота и пропускаем все накопленные входящие
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
