import types
import re

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import bot, DATA_FOR_DATABASE
from parser import check_on_stub
from db_management_OOP import ParsingChannels, Users, MonitoredTelegramChannels
from user_interface.buttons import make_row_callback_keyboard


router = Router()  # [1]


class AddWatchedChannel(StatesGroup):
    selecting_user_channel = State()
    adding_new_channel = State()


user_channels_dict = dict()
channel_to_adding = ""


# Хэндлер на команду /add_channel_to_watched
@router.message(StateFilter(None), Command("add_channel_to_watched"))
async def cmd_add_channel_to_watched(message: Message, state: FSMContext):
    user_channels = Users(*DATA_FOR_DATABASE).get_user_channels(message.chat.id)

    for i in user_channels:
        user_channels_dict[i[1]] = i[0]
    await message.answer(
        "Выберите канал, в который вы хотели бы получать новые посты",
        reply_markup=make_row_callback_keyboard(user_channels_dict)
    )
    await state.set_state(AddWatchedChannel.selecting_user_channel)


@router.callback_query(F.data.startswith("add_channel_"))
@router.message(AddWatchedChannel.selecting_user_channel)
async def select_user_channel(callback_query: CallbackQuery, state: FSMContext):
    if "cancel" or "отмена" not in callback_query.text:
        global channel_to_adding
        channel_to_adding = user_channels_dict[callback_query.data[12:]]
        await callback_query.message.answer("Пришлите ссылку на последний пост из телеграм канала, который вы хотите "
                                            "отслеживать")
        await state.set_state(AddWatchedChannel.adding_new_channel)


@router.message(AddWatchedChannel.adding_new_channel)
async def handler_channel(message: Message, state: FSMContext):
    if "cancel" or "отмена" not in message.text:
        if "https://t.me/" == message.text[:13]:
            connection_to_parsing_channels = ParsingChannels(*DATA_FOR_DATABASE)
            connection_to_monitored_telegram_channels = MonitoredTelegramChannels(*DATA_FOR_DATABASE)
            last_post = int(re.search("\/\d+", message.text).group()[1:])
            channel_name = re.match(r'https://t.me/(\w+)', message.text).group(1)
            url = f"https://t.me/s/{channel_name}"
            if connection_to_parsing_channels.check_url(url):
                answer_from_db = connection_to_monitored_telegram_channels.add_to_monitored(url, channel_to_adding)
                await message.answer(answer_from_db)
            else:
                # print(url, stub, last_post)
                soup = check_on_stub(url)
                if soup:
                    channel_name = soup.find('div', class_="tgme_channel_info_header_title").text
                    connection_to_parsing_channels.create_new_channel(url, last_post, channel_name)
                    answer_from_db = connection_to_monitored_telegram_channels.add_to_monitored(url, channel_to_adding)
                    await message.answer(answer_from_db)
                else:
                    await message.answer("Не получилось открыть канал в вэб")
        else:
            await message.answer("Не телеграм-пост")
            await message.delete()
    await state.clear()


@router.message(StateFilter(None), Command("cmd_del_channel_from_watched"))
async def cmd_del_channel_from_watched(message: Message, state: FSMContext):
    global user_channels_dict
    user_channels_dict = get_user_channels_dict(message.from_user.id)
    await message.answer(
        "Выберите канал, из которого вы хотели бы удалить отслеживаемые каналы",
        reply_markup=make_row_callback_keyboard(user_channels_dict)
    )
    await state.set_state(ManageWatchedChannel.selecting_for_del_user_channel)
