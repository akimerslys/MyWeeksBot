from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, report, premium
    from .admin import add_key, delete, block

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(report.router)
    router.include_router(premium.router)
    router.include_router(add_key.router)
    router.include_router(delete.router)
    router.include_router(block.router)

    return router
