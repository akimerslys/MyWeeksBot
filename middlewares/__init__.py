from aiogram import Dispatcher


def register_middlewares(dp: Dispatcher) -> None:
    from .throttling import ThrottlingMiddleware

    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
