from aiogram.client.session.aiohttp import FormData
from aiogram.client.session.aiohttp import ClientSession
from io import BytesIO
from loguru import logger


async def file_to_bytesio(file_path: str) -> BytesIO:
    """
    Convert a file to a BytesIO object.
    """
    with open(file_path, 'rb') as file:
        file_content = file.read()
    return BytesIO(file_content)


async def imgbytes_to_url(b: BytesIO) -> str | None:
    form = FormData()
    form.add_field('file', b, filename='week.jpeg', content_type='image/jpeg')
    async with ClientSession() as session:
        async with session.post('https://telegra.ph/upload', data=form) as response:
            result = await response.json()
            if 'error' in result:
                logger.error(f"Error uploading file: {result['error']}")
                return
            else:
                return 'https://telegra.ph' + result[0]['src']
