from hltv_async_api import Hltv
import asyncio

async def main():
    hltv = Hltv(max_delay=1)
    print(await hltv.get_events(outgoing=False, future=True))
    await hltv.close_session()

if __name__ == '__main__':
    asyncio.run(main())