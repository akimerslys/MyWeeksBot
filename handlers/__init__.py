from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, profile, report, premium, changelog
    from .admin import stop, add_key

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(changelog.router)
    router.include_router(stop.router)
    router.include_router(profile.router)
    router.include_router(report.router)
    router.include_router(premium.router)
    router.include_router(add_key.router)

    return router
