from aiogram.fsm.state import State, StatesGroup


class Report(StatesGroup):
    text = State()


class AskLocation(StatesGroup):
    ask_location = State()
    callback_id = State()


class AddNotif(StatesGroup):
    date = State()
    hours = State()
    minutes = State()
    text = State()
    tmp_msg = State()
    repeat_day = State()
    repeat_week = State()
    repeat_month = State()


