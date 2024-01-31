from aiogram.fsm.state import State, StatesGroup


class Report(StatesGroup):
    text = State()
