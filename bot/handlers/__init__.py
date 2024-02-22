from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, profile, report, premium, changelog, schedule
    from .admin import add_key, delete

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(changelog.router)
    router.include_router(schedule.router)
    router.include_router(profile.router)
    router.include_router(report.router)
    router.include_router(premium.router)
    router.include_router(add_key.router)
    router.include_router(delete.router)

    return router
