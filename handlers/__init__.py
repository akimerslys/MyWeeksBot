from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu
    from .admin import stop

    router = Router()
    router.include_router(start.router)
    router.include_router(stop.router)
    router.include_router(menu.router)

    return router
