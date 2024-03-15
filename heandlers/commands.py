from aiogram import Router, F
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from heandlers.fsm import BotState

router = Router()  # [1]
# state = State()


@router.message(StateFilter(None), Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer("Hello!")
    await message.delete()


@router.message(StateFilter(None), Command("info"))
async def cmd_start(message: Message):
    await message.answer(
        "Тестовый бот для FSM"
    )


@router.message(StateFilter(None), Command("add_channel"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите ссылку на телеграм пост"
    )
    await state.set_state(BotState.adding_new_channel)


@router.message(StateFilter(None), Command("add_my_channel"))
async def add_my_channel(message: Message, state: FSMContext):
    await message.answer(
        "1. Добавьте бота в канал для постинга отслеживаемых новостей в качестве администратора\n"
        "2. Напишите пост в своем канале\n"
        "3. Перешлите пост из своего канала боту"
    )
    await state.set_state(BotState.adding_my_channel)
