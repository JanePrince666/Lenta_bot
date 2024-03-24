from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_row_callback_keyboard(items: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.button(
            text=item,
            callback_data="add_channel_"+item,
        )

    keyboard.adjust(1)
    return keyboard.as_markup()
