from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from db_management_OOP import Users
from config import DATA_FOR_DATABASE
from config import bot

router = Router()


class AddUserChannel(StatesGroup):
    adding_my_channel = State()


# Хэндлер на команду /add_my_channel
@router.message(StateFilter(None), Command("add_my_channel"))
async def add_my_channel(message: Message, state: FSMContext):
    await message.answer(
        "1. Добавьте бота в канал для постинга отслеживаемых новостей в качестве администратора\n"
        "2. Напишите пост в своем канале\n"
        "3. Перешлите пост из своего канала боту"
    )
    await state.set_state(AddUserChannel.adding_my_channel)


@router.message(AddUserChannel.adding_my_channel)
async def add_new_user_channel(message: Message, state: FSMContext):
    if "cancel" or "отмена" not in message.text:
        Users(*DATA_FOR_DATABASE).add_user_and_user_channel(message.chat.id, message.forward_from_chat.id,
                                                            message.forward_from_chat.full_name)
        await bot.send_message(chat_id=message.forward_from_chat.id, text=f"канал добавлен в каналы для постинга")
        await bot.send_message(chat_id=message.chat.id, text=f"канал добавлен в каналы для постинга")
        await state.clear()
    # print(message)
