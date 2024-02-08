from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, profile, report, premium
    from .admin import stop

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(stop.router)
    router.include_router(profile.router)
    router.include_router(report.router)
    router.include_router(premium.router)

    return router
