from src.core.redis_loader import redis_client as r
import datetime

filename = 'backup/redis_dump.rdb'


async def save_redis_data():
    try:
        dump_data = await r.dump('backup')
        with open(filename, 'wb') as f:
            f.write(dump_data)
        print("Redis database saved successfully to", filename)
    except Exception as e:
        print("Error saving remote Redis database:", e)

async def load_redis_data():
    try:
        with open(filename, 'rb') as f:
            dump_data = f.read()
        r.restore(name='backup', ttl=0, value=dump_data)
        print("Redis database loaded successfully from", filename)
    except Exception as e:
        print("Error loading local Redis database:", e)


async def main():
    await save_redis_data()
    #load_redis_data()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


