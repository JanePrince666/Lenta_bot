import asyncio
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command, CommandStart
from config import my_token, CHANNEL_ID
from parser import get_latest_posts

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Объект бота
bot = Bot(token=my_token)

# Диспетчер
dp = Dispatcher()
router = Router()

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# Список запощенных постов
posted = []


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


async def posting2channel():
    latest_posts = dict(get_latest_posts())
    for i in latest_posts:
        if i not in posted:
            await bot.send_message(chat_id=CHANNEL_ID, text=i + "\n" + latest_posts[i])
            posted.append(i)
        else:
            continue

scheduler.add_job(posting2channel, "interval", seconds=5)


# Запуск процесса поллинга новых апдейтов
async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
