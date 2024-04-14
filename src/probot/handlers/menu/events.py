from __future__ import annotations

from aiogram import Router, F
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.probot.utils.hltv import get_hltv
from src.probot.keyboards.inline.menu import events_kb, event_kb, event_matches_kb
from src.database.services import prousers as dbuc, schedule as dbsc, notifs as dbnc

router = Router(name="events")


@router.callback_query(F.data == "events_menu")
async def events_menu(call: CallbackQuery):
    events = await get_hltv("events")
    await call.message.edit_text("events list", reply_markup=events_kb(events))


@router.callback_query(F.data == "events_menu_more")
async def events_menu(call: CallbackQuery):
    events = await get_hltv("events")
    await call.message.edit_text("events list", reply_markup=events_kb(events), more=True)


@router.callback_query(F.data.startswith("event_"))
async def event_show(call: CallbackQuery):
    event_id = call.data.split("_")[-1]
    event = await get_hltv("events", event_id)
    await call.message.edit_text("Event: <b><a href='https://www.hltv.org/events/{id}/{name}'>{name}</>{name}</b>\n"
                                 'Dates: {start} - {end}\n'
                                 'Teams: {teams}\n'
                                 'Prizepool: {prize}\n'
                                 'Location: {location}'.format(id=event[0],
                                                       name=event[1],
                                                       start=event[2].replace('-', '.'),
                                                       end=event[3].replace('-', '.'),
                                                       prize=event[4],
                                                       location=event[6],
                                                       teams=event[5]),
                                 reply_markup=event_kb(event[0]))


