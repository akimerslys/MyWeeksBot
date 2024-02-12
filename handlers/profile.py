from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from services.users import get_user

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
async def send_profile(message: Message, bot: Bot, session: AsyncSession):
    user_info = await get_user(session, message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        f"{user_info.first_name} profile\n"
        f"{user_info.active_notifs} Active notifications\n"
        f"Premium: {'Active' if user_info.is_premium else 'Inactive'}\n"
        f"Premium until: {'' if not user_info.is_premium else user_info.premium_until.strftime('%d %m %Y')}\n"
        f"Language: {user_info.language_code}\n"
        f"Timezone: {user_info.timezone}"
    )
