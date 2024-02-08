from aiogram.fsm.state import State, StatesGroup


class Report(StatesGroup):
    text = State()


class AskLocation(StatesGroup):
    ask_location = State()
    ask_location_confirm = State()


class AddNotif(StatesGroup):
    date = State()
    hours = State()
    minutes = State()
    text = State()
    tmp_msg = State()
    repeat_day: False = State()
    repeat_week: False = State()
    repeat_month: False = State()


