from aiogram import Bot

from bot.core.config import settings


async def startup(ctx):
    ctx["bot"] = Bot(token=settings.TOKEN)


async def shutdown(ctx):
    await ctx["bot"].session.close()


async def send_message(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, text)


class WorkerSettings:
    redis_settings = settings.redis_url
    on_startup = startup
    on_shutdown = shutdown
    functions = [send_message, ]
    """cron_jobs = (
        cron()
    )"""
