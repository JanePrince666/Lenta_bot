from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from db_management_OOP import Users, MonitoredTelegramChannels
from config import DATA_FOR_DATABASE
from config import bot
from user_interface.buttons import make_row_callback_keyboard

router = Router()


class ManageUserChannel(StatesGroup):
    selecting_user_channel_for_delite = State()
    adding_my_channel = State()


user_channels_dict = dict()
selected_channel = None


def get_user_channels_dict(user_id: int):
    """
    connect to DB and get user channels to variable user_channels_dict

    :type user_id: int
    """
    user_channels = Users(*DATA_FOR_DATABASE).get_user_channels(user_id)
    global user_channels_dict
    for i in user_channels:
        user_channels_dict[i[1]] = i[0]


# Хэндлер на команду /add_my_chat
@router.message(StateFilter(None), Command("add_my_chat"))
@router.message(F.text.lower() == "добавить текущий чат для постинга")
async def make_current_chat_chat_for_posting(message: Message):
    """
    adds the chat in which this command was called to the user chats for posting

    :param message: Message
    """
    Users(*DATA_FOR_DATABASE).add_user_and_user_channel(message.from_user.id, message.chat.id, message.chat.full_name)
    await message.answer("Чат добавлен в чат для постинга. Для управления подписками перейдите в личные сообщения с "
                         "ботом.")


# Хэндлер на команду /add_my_channel
@router.message(StateFilter(None), Command("add_my_channel"))
@router.message(F.text.lower() == "добавить мой канал для постинга")
async def add_my_channel(message: Message, state: FSMContext):
    """
    answer on command /add_my_channel and set state to adding_my_channel

    :param message: Message
    :param state: FSMContext
    """
    await message.answer(
        "1. Добавьте бота в канал для постинга отслеживаемых новостей в качестве администратора\n"
        "2. Напишите пост в своем канале\n"
        "3. Перешлите пост из своего канала боту"
    )
    await message.delete()
    await state.set_state(ManageUserChannel.adding_my_channel)


@router.message(ManageUserChannel.adding_my_channel)
async def add_new_user_channel(message: Message, state: FSMContext):
    """
    get data from forward message and update database

    :param message: Message
    :param state: FSMContext
    """
    if "cancel" or "отмена" not in message.text:
        try:
            Users(*DATA_FOR_DATABASE).add_user_and_user_channel(message.chat.id, message.forward_from_chat.id,
                                                                message.forward_from_chat.full_name)
            await bot.send_message(chat_id=message.forward_from_chat.id, text=f"канал добавлен в каналы для постинга")
            await bot.send_message(chat_id=message.chat.id, text=f"канал добавлен в каналы для постинга")
        except:
            await message.answer("Что-то пошло не так. Вы добавили бота в канал и сделали его администратором?")

        await state.clear()


@router.message(StateFilter(None), Command("del_my_channel"))
@router.message(F.text.lower() == "удалить мой канал из каналов для постинга")
async def cmd_del_my_channel(message: Message, state: FSMContext):
    """
    displays user channels to select a channel to delete

    :param message: Message
    :param state: FSMContext
    """
    get_user_channels_dict(message.from_user.id)
    await message.answer("Выберете ваш канал, который вы хотите удалить из каналов для постинга. Помните, "
                         "после завершения удаления, отменить действие будет невозможно!",
                         reply_markup=make_row_callback_keyboard(user_channels_dict, "del_user_channel_")
                         )
    await message.delete()
    await state.set_state(ManageUserChannel.selecting_user_channel_for_delite)


@router.callback_query(F.data.startswith("del_user_channel_"))
@router.message(ManageUserChannel.selecting_user_channel_for_delite)
async def delite_monitored_channel(callback_query: CallbackQuery, state: FSMContext):
    """
    deletes user channel or chat data from the database

    :param callback_query: CallbackQuery
    :param state: FSMContext
    """
    print(callback_query.data)
    user_channel_for_delite = callback_query.data[17:]
    user_channel_id = user_channels_dict[user_channel_for_delite]
    MonitoredTelegramChannels(*DATA_FOR_DATABASE).del_from_monitored(user_channel_id)
    Users(*DATA_FOR_DATABASE).del_user_channel(user_channel_id)
    await state.clear()
