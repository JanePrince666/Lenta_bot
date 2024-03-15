import asyncio
import datetime
import random
import re
import time
import logging
import sys
import multiprocessing

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router, types, filters
from aiogram.filters import Command, CommandStart, StateFilter, state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
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
user_dict: dict[int, dict[str, str | int | bool]] = {}
router = Router()

# Создаем задачу по времени
scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")


# Хэндлер на прием новых каналов от пользователя
@dp.message()
async def handler_channel(message: types.Message):
    if "https://t.me/" == message.text[:13]:
        connection = ParsingChannels(*DATA_FOR_DATABASE)
        last_post = int(re.search("\/\d+", message.text).group()[1:])
        channel_name = re.match(r'https://t.me/(\w+)', message.text).group(1)
        url = f"https://t.me/s/{channel_name}"
        if connection.check_url(url):
            await message.answer("Уже есть в базе данных")
        else:
            # print(url, stub, last_post)

            answer = connection.create_new_channel(url, last_post)
            await message.answer(answer)
    else:
        await message.answer("Не телеграм-пост")
        await message.delete()


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
