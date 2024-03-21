from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_row_callback_keyboard(items: dict) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append(
            types.InlineKeyboardButton(
                text=item,
                callback_data=item
            ))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard
