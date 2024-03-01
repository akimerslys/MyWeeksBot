from aiogram.fsm.state import State, StatesGroup


class NewUser(StatesGroup):
    new_user = State()
    ask_location = State()
    location_confirm = State()


class Report(StatesGroup):
    text = State()


class ConfigSchedule(StatesGroup):
    hours = State()
    minutes = State()

class AskLocation(StatesGroup):
    ask_location = State()
    ask_location_confirm = State()


class AddNotif(StatesGroup):
    date = State()
    hours = State()
    minutes = State()
    text = State()
    tmp_msg = State()
    repeat_daily: False = State()
    repeat_weekly: False = State()


class AddSchedule(StatesGroup):
    tmp_msg = State()
    days = State()
    hours = State()
    minutes = State()
    text = State()
    notify = State()


class ChangeNotif(StatesGroup):
    text = State()
    repeat_daily = State()
    repeat_weekly = State()
    tmp_msg = State()

