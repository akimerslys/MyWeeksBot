from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import Report
from core.config import settings

router = Router(name="report")


# TODO add back to the main menu button, implement report to menu(idk, mby it's not needed)
@router.message(Command("report"))
async def start_report(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Report.text)
    sent_message = await bot.send_message(message.from_user.id, "Please, write your report")
    await bot.delete_message(message.from_user.id, message.message_id)
    await state.update_data(text=sent_message.message_id)


@router.message(Report.text)
async def finish_report(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data['text'])
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.send_message(
        settings.ADMINS_ID[0],
        f"New Report: @{message.from_user.id if message.from_user.username is None else message.from_user.username}"
        f"\n\n {message.text}")
    await state.clear()

