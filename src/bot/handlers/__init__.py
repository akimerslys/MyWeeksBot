from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, report, premium, inline
    from .admin import router_admin

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(report.router)
    router.include_router(premium.router)
    router.include_router(inline.router)
    router.include_router(router_admin)

    return router
