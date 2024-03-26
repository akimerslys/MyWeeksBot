from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, menu, report, premium, inline
    from .menu import menu_router
    from .admin import router_admin

    router = Router()
    router.include_router(start.router)
    router.include_router(menu_router)
    router.include_router(report.router)
    router.include_router(premium.router)
    router.include_router(inline.router)
    router.include_router(router_admin)

    from . import ignore

    router.include_router(ignore.router)

    return router
