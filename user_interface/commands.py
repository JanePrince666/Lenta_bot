from aiogram import Router, F
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from db_management_OOP import Users
from config import DATA_FOR_DATABASE

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
        "Бот для создания собственной ленты\n"
        "/info\n"
        "/add_channel_to_watched\n"
        "/add_my_channel\n"
        "/view_my_channels\n"
    )
    await message.delete()


@router.message(StateFilter(None), Command("view_my_channels"))
async def view_my_channels(message: Message, state: FSMContext):
    user_channels = dict(Users(*DATA_FOR_DATABASE).get_user_channels(message.chat.id))
    answer = [user_channels[i] for i in user_channels]
    await message.answer('\n'.join(answer))


@router.message(Command("cancel"))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    if state is None:
        await message.answer(
            "Вы не находитесь на стадии добавления своего канала или канала для отследивания"
        )
    else:
        await message.answer(
            "Добавление отменено"
        )
        await state.clear()
