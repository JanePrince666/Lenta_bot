import asyncio
import datetime
import random
import re
import time
import logging
import sys
import multiprocessing

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command, CommandStart
from config import my_token, CHANNEL_ID, DATA_FOR_DATABASE
from parser import TelegramChannel, TelegramPost
from db_management_OOP import ParsingChannels, PostingList
from profiler import time_of_function

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Объект бота
bot = Bot(token=my_token)

# Диспетчер
dp = Dispatcher()
router = Router()

scheduler_for_posting = AsyncIOScheduler(timezone="Asia/Tbilisi")


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
    if "https://t.me/" == message.text[:13]:
        connection = ParsingChannels(*DATA_FOR_DATABASE)
        last_post = int(re.search("\/\d+", message.text).group()[1:])
        url = re.search("https:\/\/t\.me\/\w+", message.text).group()
        if connection.check_url(url):
            await message.answer("Уже есть в базе данных")
        else:
            stub = TelegramPost(url, 1).get_text()
            # print(url, stub, last_post)

            answer = connection.create_new_channel(url, stub, last_post)
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


def get_channel_lisl():
    connection = ParsingChannels(*DATA_FOR_DATABASE)
    channel_list = connection.get_channels_list()
    for i in range(10):
        unit = []
        for j in range(len(channel_list)):
            if i + j < len(channel_list):
                unit.append(channel_list[i + j])
        yield unit


def get_new_posts():
    first_launch = True
    # print("начала парсить")
    while True:
        # start = datetime.datetime.now()
        channels = get_channel_lisl()
        for unit in channels:
            for url, stub, start_post in unit:
                # time.sleep(random.randint(0,5))
                channel = TelegramChannel(url, stub, start_post)
                # print(f"проверка канала {url} начата в {datetime.datetime.now()}", file=open('report.txt', 'a'))
                t = multiprocessing.Process(target=channel.check_new_posts, args=(first_launch,))
                t.start()
                # print(f"проверка канала {url} закончена в {datetime.datetime.now()}")
            if first_launch:
                time.sleep(60)
                first_launch = False
            else:
                time.sleep(15)


        # end = datetime.datetime.now()
        # print(f'цикл get_new_posts:\n   start: {start}\n    finish: {end}\n    Время работы ' + str(end - start), file=open('report.txt', 'a'))


scheduler_for_posting.add_job(post, "interval", seconds=10)

t2 = multiprocessing.Process(target=get_new_posts)


# Запуск процесса поллинга новых апдейтов
async def main():
    t2.start()
    scheduler_for_posting.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
