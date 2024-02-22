import asyncio
from typing import LiteralString
from bot.core.loader import lock
from aiogram import Router, Bot, F
from aiogram.types import InlineQuery, Message
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from loguru import logger
from aiogram.types import InputMediaAnimation, FSInputFile, BufferedInputFile
from bot.keyboards.inline import menu as mkb
from bot.core.config import settings
from bot.image_generator.images import generate_user_schedule_week
from sqlalchemy.ext.asyncio import AsyncSession

import time

router = Router(name="schedule")

"""@router.message(Command("schedule"))
photo_path = "media/mockup_gif.mp4"
photo2_path = "media/mockup_gif_2.mp4"

async def send_schedule(message: Message, bot: Bot):
    msg = await bot.send_animation(message.from_user.id,
                                   animation=FSInputFile(path=photo_path, filename=f"schdedule_{message.from_user.id}"),
                                   caption="Schedule123_1233", reply_markup=mkb.schedule_kb())
    print(msg.message_id, msg.animation[-1].file_id)
    msg = await bot.send_animation(message.from_user.id,
                                   animation=FSInputFile(path=photo2_path,
                                                         filename=f"schdedule_{message.from_user.id}"),
                                   caption="Schedule123_123", reply_markup=mkb.schedule_kb())
    print(msg.message_id, msg.animation[-1].file_id)
"""


@router.message(Command("schedule"))
async def send_schedule(message: Message, bot: Bot, session: AsyncSession):
    start = time.time()
    await bot.delete_message(message.chat.id, message.message_id)
    msg = await bot.send_message(message.chat.id, _("WAIT_MESSAGE"))
    try:
        async with lock:
            image_bytes = await generate_user_schedule_week(session, message.from_user.id)
            await bot.send_photo(message.from_user.id,
                                 BufferedInputFile(image_bytes.getvalue(), filename=f"schedule_{message.from_user.id}.jpeg"),
                                 caption="Please choose button bellow",
                                 reply_markup=mkb.schedule_kb())
    except Exception as e:
        logger.critical("WTF????\n" + e)
        await bot.send_message(settings.ADMIN_ID[1], f"ERROR IN GENERATION IMAGE\n{e}")

    finally:
        await bot.delete_message(message.chat.id, msg.message_id)

    logger.info(f"generated schedule, it tooks: {time.time() - start}")


"""@router.inline_query()
async def send_schedule(query: InlineQuery, bot: Bot, session: AsyncSession):
    start = time.time()
    await bot.delete_message(message.chat.id, message.message_id)
    image_bytes = await generate_user_schedule_week(session, message.from_user.id)
    await bot.send_photo(message.from_user.id,
                         BufferedInputFile(image_bytes.getvalue(), filename=f"schedule_{message.from_user.id}.png"),
                         caption="Please choose button bellow",
                         reply_markup=mkb.schedule_kb())
    logger.info(f"generated schedule, it tooks: {time.time() - start}")"""
