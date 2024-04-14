import asyncio
from hltv_async_api import Hltv
from src.core.config import settings

async def main():
    print(settings.proxy_list)
    hltv = Hltv(use_proxy=True, debug=True, proxy_list=settings.proxy_list)

    print(hltv.get_upcoming_matches())

if __name__ == "__main__":
