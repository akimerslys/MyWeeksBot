from aiogram.utils.i18n import gettext as _

def repeat_to_str(daily: bool, weekly: bool) -> str:
    if daily and weekly:
        return ("repeat_month")
    if daily:
        return ("repeat_day")
    if weekly:
        return ("repeat_week")
    return ("repeat_none")