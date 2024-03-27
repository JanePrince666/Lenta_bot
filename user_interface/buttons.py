from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


# Функция для создания клавиатуры с кнопками ответа (ReplyKeyboard).
def make_reply_keyboard_start() -> ReplyKeyboardMarkup:
    """

    :return: ReplyKeyboardMarkup
    """
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Посмотреть мои каналы для постинга"),
                KeyboardButton(text="Добавить текущий чат для постинга"))
    builder.row(KeyboardButton(text="Добавить мой канал для постинга"),
                KeyboardButton(text="Добавить канал в отслеживаемые"),
                width=4
                )
    builder.row(
        KeyboardButton(text="Удалить канал из отслеживаемых"),
        KeyboardButton(text="Удалить мой канал из каналов для постинга")
    )
    builder.row(KeyboardButton(text="отмена"))
    return builder.as_markup(resize_keyboard=True)


def make_row_callback_keyboard(items: dict, pref: str) -> InlineKeyboardMarkup:
    """

    :param pref: str
    :type items: dict

    :return InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.button(
            text=item,
            callback_data=pref + item,
        )

    keyboard.adjust(1)
    return keyboard.as_markup()


# Функция для создания инлайн-клавиатуры с прокруткой по страницам.
def make_row_callback_keyboard_with_scrolling(page: list[str], urls: list[str], number: str) -> InlineKeyboardMarkup:
    """

    :param page: list[str]
    :param urls: urls: list[str]
    :param number: str
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardBuilder()
    for item in page:
        keyboard.add(InlineKeyboardButton(text=str(item), callback_data="del_" + urls[page.index(item)]))
        keyboard.adjust(1)

    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="prev"))
    keyboard.adjust(1)
    keyboard.add(InlineKeyboardButton(text=f"{number}", callback_data="data"))
    keyboard.add(InlineKeyboardButton(text="Вперед", callback_data="next"))
    return keyboard.as_markup()
