from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_row_callback_keyboard(items: dict) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        types.InlineKeyboardButton(
            text=item[0],
            callback_data=item[0]
        )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
