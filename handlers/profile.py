from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command


from database.dbcommands import get_user_info
from core.config import settings

import datetime

router = Router(name="profile")
""""id": user.id,
"userid": user.userid,
"name": user.name,
"language": user.language,
"timezone": user.timezone,
"notifications": user.notifications,
"is_premium": user.is_premium,
"premium_until": user.premium_until"""


@router.message(Command("profile"))
async def send_profile(message: Message, bot: Bot):
    user_info = await get_user_info(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        f"{user_info.name} profile\n"
        f"{user_info.notifications} Active notifications\n"
        f"Premium: {'Active' if user_info.is_premium else 'Inactive'}\n"
        f"Premium until: {'' if not user_info.is_premium else user_info.premium_until.strftime('%d %m %Y')}\n"
        f"Language: {user_info.language}\n"
        f"Timezone: {user_info.timezone}"
    )
