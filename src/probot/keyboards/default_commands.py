from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

if TYPE_CHECKING:
    from aiogram import Bot

from src.core.config import settings as config


users_commands: dict[str, dict[str, str]] = {
    "en": {
        "start": "start",
        "profile": "your profile",
        "changelog": "last updates",
        "report": "setting information about you",
    },
    "uk": {
        "start": "start",
        "profile": "your profile",
        "changelog": "last updates",
        "report": "setting information about you",
    },
    "ru": {
        "start": "start",
        "profile": "your profile",
        "changelog": "last updates",
        "report": "setting information about you",
    },
}

admins_commands: dict[str, str] = {
        "ping": "Check bot ping",
        "stop": "Stops the bot",
        "add_key": "Add a new key",
        "block": "Block user | /unblock",
        "stats": "Get bot statistics",
        "backup": "Back Database",
        "add Ad": "Add an advertisement",

}


async def set_default_commands(bot: Bot) -> None:
    await remove_default_commands(bot)

    for language_code in users_commands:
        await bot.set_my_commands(
            [
                BotCommand(command=command, description=description)
                for command, description in users_commands[language_code].items()
            ],
            scope=BotCommandScopeDefault(),
        )

    """#Commands for admins
    for admin_id in config.ADMINS_ID:
        await bot.set_my_commands(
                    [
                        BotCommand(command=command, description=description)
                        for command, description in admins_commands.items()
                    ],
                    scope=BotCommandScopeChat(chat_id=admin_id),
                )"""


async def remove_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
