from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


def make_row_callback_keyboard(items: dict, pref: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.button(
            text=item,
            callback_data=pref+item,
        )

    keyboard.adjust(1)
    return keyboard.as_markup()


def make_row_callback_keyboard_with_scrolling(page, urls, number):
    keyboard = InlineKeyboardBuilder()
    for item in page:
        keyboard.add(InlineKeyboardButton(text=str(item), callback_data="del_"+urls[page.index(item)]))
        keyboard.adjust(1)

    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="prev"))
    keyboard.adjust(1)
    keyboard.add(InlineKeyboardButton(text=f"{number}", callback_data="data"))
    keyboard.add(InlineKeyboardButton(text="Вперед", callback_data="next"))
    return keyboard.as_markup()
