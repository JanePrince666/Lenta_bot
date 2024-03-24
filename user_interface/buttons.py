from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# def make_row_callback_keyboard(items: dict) -> InlineKeyboardMarkup:
#     buttons = []
#     for item in items:
#         button = InlineKeyboardButton(
#             text=item,
#             callback_data=item,
#             width=1
#         )
#         buttons.append(button)
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons], row_width=1)
#
#     return keyboard


def make_row_callback_keyboard(items: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.button(
            text=item,
            callback_data=item,
        )

    keyboard.adjust(1)
    return keyboard.as_markup()
