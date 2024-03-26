from . import delete, add_key, block, backup, exception

__all__ = ['delete', 'add_key', 'block', 'backup']


from aiogram import Router

router_admin = Router()

router_admin.include_router(delete.router)
router_admin.include_router(add_key.router)
router_admin.include_router(block.router)
router_admin.include_router(backup.router)
router_admin.include_router(exception.router)
