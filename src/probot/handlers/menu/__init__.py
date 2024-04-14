from . import lang, menu, timezone, events

__all__ = ["lang", "menu", "timezone"]

from aiogram import Router

menu_router = Router()

menu_router.include_router(lang.router)
menu_router.include_router(timezone.router)
menu_router.include_router(menu.router)
menu_router.include_router(events.router)