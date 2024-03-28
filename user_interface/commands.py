from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from db_management_OOP import Users
from config import DATA_FOR_DATABASE
from user_interface.buttons import make_reply_keyboard_start, make_row_callback_keyboard

router = Router()  # [1]


# Хэндлер на команду /start
@router.message(StateFilter(None), Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer("Hello!",
                         reply_markup=make_reply_keyboard_start())
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
        "/del_channel_from_watched\n"
        "/del_my_channel\n"
    )
    await message.delete()


# Обработчик команды для просмотра каналов пользователя.
@router.message(StateFilter(None), Command("view_my_channels"))
@router.message(F.text.lower() == "посмотреть мои каналы для постинга")
async def view_my_channels(message: Message):
    user_channels = dict()
    for i in Users(*DATA_FOR_DATABASE).get_user_channels(message.chat.id):
        user_channels[i[1]] = i[0]
    await message.answer("Ваши каналы", reply_markup=make_row_callback_keyboard(user_channels, "view_"))
    await message.delete()


# Обработчик команды отмена
@router.message(Command("cancel"))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(
        "Добавление/удаление отменено"
    )
    await state.clear()
    await message.delete()
