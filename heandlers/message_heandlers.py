from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from bot import bot
from heandlers.fsm import BotState


router = Router()  # [1]


@router.message(BotState.adding_new_channel)
async def add_new_channel(message: Message, state: FSMContext):
    if "https://t.me/" == message.text[:13]:
        await message.answer("Добавила")
    else:
        await message.answer("Не телеграм канал")
    await state.clear()


@router.message(BotState.adding_my_channel)
async def add_new_user_channel(message: Message, state: FSMContext):
    await bot.send_message(chat_id=message.forward_from_chat.id, text=f"канал добавлен в каналы для постинга")
    await bot.send_message(chat_id=message.chat.id, text=f"канал добавлен в каналы для постинга")
    await state.clear()
    # print(message)
