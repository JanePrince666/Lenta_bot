from aiogram import Router, F
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from heandlers.fsm import BotState

router = Router()  # [1]
# state = State()


# Хэндлер на команду /start
@router.message(StateFilter(None), Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer("Hello!")
    await message.delete()


# Хэндлер на команду /info
@router.message(StateFilter(None), Command("info"))
async def cmd_info(message: Message):
    await message.answer(
        "Бот для создания собственной ленты"
    )
    await message.delete()


# Хэндлер на команду /add_channel_to_view
@router.message(StateFilter(None), Command("add_channel_to_view"))
async def cmd_add_channel_to_view(message: Message, state: FSMContext):
    await message.answer(
        "Пришлите ссылку на последний пост из телеграм канала, который вы хотите отслеживать"
    )
    await state.set_state(BotState.adding_new_channel)


# Хэндлер на команду /add_my_channel
@router.message(StateFilter(None), Command("add_my_channel"))
async def add_my_channel(message: Message, state: FSMContext):
    await message.answer(
        "1. Добавьте бота в канал для постинга отслеживаемых новостей в качестве администратора\n"
        "2. Напишите пост в своем канале\n"
        "3. Перешлите пост из своего канала боту"
    )
    await state.set_state(BotState.adding_my_channel)
