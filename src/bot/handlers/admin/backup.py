from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, func

import time
from loguru import logger

from src.core.config import settings

from src.bot.filters.admin import IsAdmin
from src.bot.utils.csv_converter import convert_to_csv
from src.database.models import UserModel, NotifModel, ScheduleModel


router = Router(name="backup")


@router.message(Command(commands="backup"), IsAdmin(settings.ADMINS_ID))
async def export_tables(message: Message, bot: Bot, session: AsyncSession) -> None:

    types = {
        "users": UserModel,
        "notifs": NotifModel,
        "schedule": ScheduleModel
    }

    await bot.send_message(settings.ADMINS_ID[0], "exporting tables...")

    start_time = time.time()

    for name, model in types.items():
        logger.warning(f"exporting {name}... to {message.from_user.id}")

        objects = await session.execute(select(model))
        objects = objects.scalars().all()

        document = await convert_to_csv(objects, name)

        count = await session.execute(select(func.count(model.id)))

        count_int = int(count.scalar())

        await message.answer_document(document=document, caption=f"total {name}: {count_int}")

        logger.success(f"{name} exported")

    time_end = round(time.time() - start_time, 4)
    logger.success(f"exported all in {time_end} seconds")
