from __future__ import annotations

from aiogram import Router, F
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.probot.utils import hltv
from src.probot.keyboards.inline.menu import events_kb, event_kb, event_matches_kb
from src.database.services import prousers as dbuc, schedule as dbsc, notifs as dbnc

router = Router(name="events")


@router.callback_query(F.data.startswith("events_menu"))
async def events_menu(call: CallbackQuery):
    more = call.data.split('_')[-1] == 'm'
    events = await hltv.get_hltv("fevents")
    await call.message.edit_text("events list", reply_markup=events_kb(events, more))


@router.callback_query(F.data.startswith("event_info_"))
async def event_info(call: CallbackQuery):
    data_ = call.data.split("_")
    event_id = data_[-1]
    event = await hltv.get_event(event_id)
    await call.message.edit_text("Event: <b><a href='https://www.hltv.org/events/{id}/{name}'>{name}</a>{name}</b>\n"
                                 'Dates: {start} - {end}\n'
                                 'Teams: {teams}\n'
                                 'Prizepool: {prize}\n'
                                 'Location: {location}'.format(id=event['id'],
                                                               name=event['title'],
                                                               start=event['start'].replace('-', '.'),
                                                               end=event['end'].replace('-', '.'),
                                                               prize=event['prize'],
                                                               location=event['location'],
                                                               teams=event['teams']),
                                 reply_markup=event_kb(event['id']))


@router.callback_query(F.data.startswith('event_matches_'))
async def show_event_matches(call: CallbackQuery):
    event_id = call.data.split('_')[-1]
    matches = await hltv.get_event_matches(event_id)
    await call.message.edit_reply_markup(reply_markup=event_matches_kb(matches))


@router.callback_query(F.data.startswith('event_notify_'))
async def notify_event(call: CallbackQuery):
    event_id = call.data.split('_')[-1]
    #...
    #await call.message.edit_reply_markup()


@router.callback_query(F.data.startswith('event_teams_'))
async def show_event_teams(call: CallbackQuery):
    event_id = call.data.split('_')[-1]
    #...
    #await call.message.edit_reply_markup()