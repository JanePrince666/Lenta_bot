from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    adding_my_channel = State()
    selecting_user_channel = State()
    adding_new_channel = State()


BotState = BotState()
