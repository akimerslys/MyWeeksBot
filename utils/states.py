from aiogram.fsm.state import State, StatesGroup


class Report(StatesGroup):
    text = State()


class AddNotif(StatesGroup):
    day = State()
    hours = State()
    minutes = State()
    date = State()
    text = State()
    repeat = State()


