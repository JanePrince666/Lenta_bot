import types
import re

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from config import DATA_FOR_DATABASE
from db_management_OOP import ParsingChannels, Users


router = Router()  # [1]


class AddWatchedChannel(StatesGroup):
    selecting_user_channel = State()
    adding_new_channel = State()


# Хэндлер на команду /add_channel_to_watched
@router.message(StateFilter(None), Command("add_channel_to_watched"))
async def cmd_add_channel_to_watched(message: Message, state: FSMContext):
    user_channels = dict(Users(*DATA_FOR_DATABASE).get_user_channels(message.chat.id))
    await message.answer(
        "Выберите канал, в который вы хотели бы получать новые посты"
    )
    await state.set_state(AddWatchedChannel.selecting_user_channel)


@router.message(AddWatchedChannel.selecting_user_channel)
async def select_user_channel(message: Message, state: FSMContext):
    await message.answer(
        "Пришлите ссылку на последний пост из телеграм канала, который вы хотите отслеживать"
    )
    await state.set_state(AddWatchedChannel.adding_new_channel)


@router.message(AddWatchedChannel.adding_new_channel)
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
