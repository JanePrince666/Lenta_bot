import types
import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from bot import bot
from heandlers.fsm import BotState
from config import my_token, CHANNEL_ID, DATA_FOR_DATABASE
from db_management_OOP import ParsingChannels


router = Router()  # [1]


@router.message(BotState.adding_my_channel)
async def add_new_user_channel(message: Message, state: FSMContext):
    await bot.send_message(chat_id=message.forward_from_chat.id, text=f"канал добавлен в каналы для постинга")
    await bot.send_message(chat_id=message.chat.id, text=f"канал добавлен в каналы для постинга")
    await state.clear()
    # print(message)


@router.message(BotState.adding_new_channel)
async def handler_channel(message: Message, state: FSMContext):
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
    await state.clear()
