from __future__ import annotations

from aiogram import Router, F
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboards.inline import menu as mkb
from src.database.services import users as dbuc, schedule as dbsc, notifs as dbnc

router = Router(name="menu")


# DO NOT SPLIT THIS FILE TO ROUTERS! IT WILL BE IMPLEMENTED IN THE FUTURE

# TODO ADD NOTIFICATIONS TO THE DATABASE                                        #DONE
# TODO ADD TIMEZONE TO THE NOTIFICATIONS                                        #DONE
# TODO ADD TIMEZONE SETTING FOR FIRST USER                                      #DONE (NEED MORE TESTS)
# TODO SORT WEEKDAYS BY TODAY'S DAY (IF WEDNESDAY, WEDNESDAY IS FIRST)          #DONE (NEED MORE TESTS)
# TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)                                  #DONE (NEED MORE TESTS)
# TODO INTEGRATE PROFILE TO MENU                                                #NEED CHANGES
# TODO DETERMINE SOLUTION FOR PREMIUM/EXTRA FEATURES                            # every 5$ gives you 10 notifications
# TODO MAKE ADMIN PANEL(in tg or on the web, prefer tg)
# TODO LOCALIZATION
# TODO REWRITE ADD_NOTIF_REPEAT / OPTIMIZE ADD_NOTIF_COMPLETE                   # DONE (NEED MORE TESTS)
# TODO REWRITE MANAGE_NOTIF / TO CHOOSE NOTIFS BY DATE / OR CALENDAR (idk)
# TODO ADD FUNC DELETE ALL INFORMATION ABOUT USER IN PROFILE                    # DONE
# TODO SHARE NOTIF BUTTON                                                       # DONE (NEED MORE TESTS)
# TODO INLINE MOD (CREATE NOTIFICATION/SHARE SCHEDULE)
# TODO BLOCK USER COMMAND + BLOCK MIDDLEWARE                                    # DONE
# TODO REMAKE CHANGELOG
# TODO MAKE INFO WHEN NOTIF WILL BE SENT (IN 5 hrs, in 2 days, etc)
# TODO MAKE INFO HOW MANY PEOPLE ADDED YOUR NOTIFICATION
# TODO BACKUP DATABASE TO TG CHAT
# TODO LOGS TO TG CHAT
# TODO ADD MORE TIMEZONES !!
# TODO CONNECT NOTIFS TO SCHEDULE                                               # NO NEEDED
# TODO SHARE SCHEDULE BUTTON                                                    # NO NEEDED
# TODO ADD TOTAL SHARED TO EVERY NOTIF


async def main_menu(call: CallbackQuery, session: AsyncSession):
    user = await dbuc.get_user(session, call.from_user.id)
    await call.message.edit_text(_("👤 <b>{name}</b>:\n"
                                   "🔔 Notifications {active_notifs}/{max_notifs}\n"
                                   "⏰ Upcoming notification: {upcoming_notif}\n"
                                   "🗓 {status}\n"
                                   ).format(name=user.first_name,
                                            active_notifs=user.active_notifs,
                                            max_notifs=user.max_notifs,
                                            upcoming_notif='',
                                            status=_("🔓 Premium") if user.is_premium else _("🔒 Free")
                                            ),
                                 reply_markup=mkb.main_kb())
# MAIN
@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery, state: FSMContext):
    if state.get_state:
        await state.clear()
    await main_menu(call)


# PROFILE
@router.callback_query(F.data == "profile")
async def send_profile(call: CallbackQuery, session: AsyncSession):
    user_info = await dbuc.get_user(session, call.from_user.id)
    await call.message.edit_text(
        _("profile_info").format(
            name=user_info.first_name,
            active_notifs=user_info.active_notifs,
            max_notifs=user_info.max_notifs,
            extra=_('active') if user_info.is_premium else _('inactive'),
            premium_until=_('premium_until') + user_info.premium_until.strftime(
                '%d %m %Y') + '\n' if user_info.is_premium else '',
            lang=user_info.language_code,
            tz=user_info.timezone,
            sch_time=user_info.schedule_time if user_info.schedule_time else ''
        ), reply_markup=mkb.profile_kb()
    )


@router.callback_query(F.data == "profile_delete")
async def delete_profile(call: CallbackQuery):
    await call.message.edit_text(_("profile_delete_confirm"), reply_markup=mkb.delete_profile_kb())


@router.callback_query(F.data.startswith("profile_delete_"))
async def delete_profile_confirm(call: CallbackQuery, session: AsyncSession):
    if call.data.split("_")[-1] == "yes":
        await call.message.edit_reply_markup(reply_markup=mkb.loading())
        await dbuc.delete_user(session, call.from_user.id)
        await dbsc.delete_all_user_schedule(session, call.from_user.id)
        await dbnc.delete_all_user_notifs(session, call.from_user.id)
        await call.answer(_("Profile deleted, hope to see you again! ❤️‍🔥"), show_alert=True)
    else:
        await call.answer("😳😳😳")
        await call.message.edit_reply_markup(reply_markup=mkb.profile_kb())


# SETTINGS
@router.callback_query(F.data == 'settings_kb')
async def place_settings_kb(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=mkb.setting_kb())


# CHANGELOG
@router.callback_query(F.data == "show_changelog")
async def send_changelog(call: CallbackQuery):
    #get_updates = await
    message_changelog = ''
    await call.message.edit_text(
        _("last_updates") + "\n\n" + message_changelog,
        reply_markup=mkb.back_main()
    )


# PREMIUM
@router.callback_query(F.data == "buy_premium")
async def buy_premium(call: CallbackQuery):
    await call.answer(
        "not_available",
        show_alert=True
    )


"""@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    print(message)
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=mkb.main_kb())"""
