import re

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import bot, DATA_FOR_DATABASE
from parser import check_on_stub
from db_management_OOP import ParsingChannels, Users, MonitoredTelegramChannels
from user_interface.buttons import make_row_callback_keyboard, make_row_callback_keyboard_with_scrolling

router = Router()


class ManageWatchedChannel(StatesGroup):
    deletion_watched_channel = State()
    selecting_for_del_user_channel = State()
    selecting_user_channel = State()
    adding_new_channel = State()


class WatchedChannelData:
    def __init__(self, urls: list[str]):
        """
        get and collect data for keyboard with scrolling

        :param urls: list[str]
        """
        self.urls = urls
        connection = ParsingChannels(*DATA_FOR_DATABASE)
        self.items = [connection.get_channel_name(url) for url in urls]
        self.len = len(self.items)
        self.current_page = 0
        self.max_page = ((self.len - 1) // 10) - 1
        if (len(self.items) - 1) % 10 != 0:
            self.max_page += 1


user_channels_dict = dict()
selected_channel: int
channels: WatchedChannelData


# Функция наполнения словоря user_channels_dict
def get_user_channels_dict(user_id: int):
    """
    get data about user channels and chats and collect to user_channels_dict

    :param user_id: int
    """
    user_channels = Users(*DATA_FOR_DATABASE).get_user_channels(user_id)
    global user_channels_dict
    for i in user_channels:
        user_channels_dict[i[1]] = i[0]


# Хэндлер на команду /add_channel_to_watched
@router.message(StateFilter(None), Command("add_channel_to_watched"))
@router.message(F.text.lower() == "добавить канал в отслеживаемые")
async def cmd_add_channel_to_watched(message: Message, state: FSMContext):
    """
    send user his channels to choose channel for posting and set state selecting_user_channel

    :param message: Message
    :param state: FSMContext
    """
    get_user_channels_dict(message.from_user.id)
    await message.answer(
        "Выберите канал, в который вы хотели бы получать новые посты",
        reply_markup=make_row_callback_keyboard(user_channels_dict, "add_channel_")
    )
    await message.delete()
    await state.set_state(ManageWatchedChannel.selecting_user_channel)


@router.callback_query(F.data.startswith("add_channel_"))
@router.message(ManageWatchedChannel.selecting_user_channel)
async def select_user_channel(callback_query: CallbackQuery, state: FSMContext):
    """
    requests a link to a telegram channel for monitoring from the user and set state adding_new_channel

    :param callback_query: CallbackQuery
    :param state: FSMContext
    """
    if "cancel" or "отмена" not in callback_query.text:
        global selected_channel
        selected_channel = user_channels_dict[callback_query.data[12:]]
        await callback_query.message.answer("Пришлите ссылку на последний пост из телеграм канала, который вы хотите "
                                            "отслеживать")
        await state.set_state(ManageWatchedChannel.adding_new_channel)


@router.message(ManageWatchedChannel.adding_new_channel)
async def handler_channel(message: Message, state: FSMContext):
    """
    checks the link sent by the user and adds it to the database

    :param message: Message
    :param state: FSMContext
    """
    if "cancel" or "отмена" not in message.text:

        # Если присланная ссылка похожа на ссылку на телеграм пост,
        # проверяем нет ли данного телеграм канала в базе данных
        if "https://t.me/" == message.text[:13]:
            connection_to_parsing_channels = ParsingChannels(*DATA_FOR_DATABASE)
            connection_to_monitored_telegram_channels = MonitoredTelegramChannels(*DATA_FOR_DATABASE)
            last_post = int(re.search("\/\d+", message.text).group()[1:])
            channel_name = re.match(r'https://t.me/(\w+)', message.text).group(1)
            url = f"https://t.me/s/{channel_name}"

            # Если телеграм канал есть в базе данных, пробуем добавить в отслеживаемые в конкретном канале
            if connection_to_parsing_channels.check_url(url):
                answer_from_db = connection_to_monitored_telegram_channels.add_to_monitored(url, selected_channel)
                await message.answer(answer_from_db)

            # Если нет, проверяем, что канал открывается в web и если да, добавляем в нужные таблицы в базе данных
            else:
                soup = check_on_stub(url)
                if soup:
                    channel_name = soup.find('div', class_="tgme_channel_info_header_title").text
                    connection_to_parsing_channels.create_new_channel(url, last_post, channel_name)
                    answer_from_db = connection_to_monitored_telegram_channels.add_to_monitored(url, selected_channel)
                    await message.answer(answer_from_db)
                else:
                    await message.answer("Не получилось открыть канал в вэб")
        else:
            await message.answer("Не телеграм-пост")
            await message.delete()
    await state.clear()


@router.message(StateFilter(None), Command("del_channel_from_watched"))
@router.message(F.text.lower() == "удалить канал из отслеживаемых")
async def cmd_del_channel_from_watched(message: Message, state: FSMContext):
    """
    update variable user_channels_dict and sent to user his channels and chats

    :param message: Message
    :param state: FSMContext
    """
    get_user_channels_dict(message.from_user.id)
    await message.answer(
        "Выберите канал, из которого вы хотели бы удалить отслеживаемые каналы",
        reply_markup=make_row_callback_keyboard(user_channels_dict, "del_from_channel_")
    )
    await message.delete()
    await state.set_state(ManageWatchedChannel.selecting_for_del_user_channel)


@router.callback_query(F.data.startswith("del_from_channel_"))
@router.message(ManageWatchedChannel.selecting_user_channel)
async def select_watches_channel_for_delite(callback_query: CallbackQuery, state: FSMContext):
    """
    sends the user a keyboard for a selection of channels that are subscribed to the user-selected channel

    :param callback_query: CallbackQuery
    :param state: FSMContext
    """
    if "cancel" or "отмена" not in callback_query.text:
        global selected_channel, channels
        selected_channel = user_channels_dict[callback_query.data[17:]]
        watched_channel_url = MonitoredTelegramChannels(*DATA_FOR_DATABASE).get_subscribed_user_chanel_list(
            selected_channel)
        channels = WatchedChannelData(watched_channel_url)
        number = f"1/{channels.max_page + 1}"
        await callback_query.message.answer(
            "Выберете канал, который хотите удалить",
            reply_markup=make_row_callback_keyboard_with_scrolling(channels.items[:10], channels.urls[:10], number))
        await state.set_state(ManageWatchedChannel.deletion_watched_channel)


# Обработчик нажатия кнопки "Вперед"
@router.callback_query(lambda query: query.data == 'next')
async def next_page(callback_query: CallbackQuery):
    """
    When the user presses the next button, it calculates the next interval in the channel list
    and overwrites the keyboard with the new data

    :param callback_query: CallbackQuery
    """
    if type(channels) is WatchedChannelData and channels.current_page < channels.max_page:
        channels.current_page += 1
        start_index = channels.current_page * 10
        end_index = min(start_index + 10, channels.len)
        new_page = channels.items[start_index:end_index]
        number = f"{channels.current_page + 1}/{channels.max_page + 1}"
        await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                            reply_markup=make_row_callback_keyboard_with_scrolling(
                                                new_page, channels.urls[start_index:end_index], number
                                            ))


# Обработчик нажатия кнопки "Назад"
@router.callback_query(lambda query: query.data == 'prev')
async def prev_page(callback_query: CallbackQuery):
    """
    When the user presses the previous button, it calculates the next interval in the channel list
    and overwrites the keyboard with the new data

    :param callback_query: CallbackQuery
    """
    if type(channels) is WatchedChannelData and channels.current_page != 0:
        channels.current_page -= 1
        start_index = max(channels.current_page * 10, 0)
        end_index = min(start_index + 10, channels.len)
        new_page = channels.items[start_index:end_index]
        number = f"{channels.current_page + 1}/{channels.max_page + 1}"
        await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                            reply_markup=make_row_callback_keyboard_with_scrolling(
                                                new_page, channels.urls[start_index:end_index], number))


# Функция удаления выбранного канала
@router.callback_query(F.data.startswith("del_"))
@router.message(ManageWatchedChannel.deletion_watched_channel)
async def del_channel_from_watched(callback_query: CallbackQuery, state: FSMContext):
    """
    callback for selecting a channel to be deleted by the user

    :param callback_query: CallbackQuery
    :param state: FSMContext
    """
    tg_channel_url = callback_query.data[4:]
    MonitoredTelegramChannels(*DATA_FOR_DATABASE).del_tg_channel_from_monitored(selected_channel, tg_channel_url)
    await callback_query.message.answer("Удалила")
    await state.clear()
