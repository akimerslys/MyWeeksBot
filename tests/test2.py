from hltv_async_api import Hltv
import asyncio


async def main():
    #proxy_list = ['http://ingp3040210:AkPX56R9Cf@91.243.188.72:7951', 'http://akim:akim2003@10.178.71.246:5555']

    hltv = Hltv()
    print(await hltv.get_upcoming_matches())

if __name__ == "__main__":
    asyncio.run(main())
