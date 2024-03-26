from . import lang, menu, notifs, schedule, timezone

__all__ = ["lang", "menu", "notifs", "schedule", "timezone"]

from aiogram import Router

menu_router = Router()

menu_router.include_router(lang.router)
menu_router.include_router(notifs.router)
menu_router.include_router(schedule.router)
menu_router.include_router(timezone.router)
menu_router.include_router(menu.router)