
from PIL import Image, ImageDraw, ImageFont

import pytz
import time
from datetime import datetime
from loguru import logger

import os

from io import BytesIO

from src.core.config import settings
from src.bot.utils.time_localizer import weekday_to_future_date


font_path = os.path.join(settings.FONTS_DIR, "OPENSANS-SEMIBOLD.TTF")
media_path = settings.MEDIA_DIR

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def wrap_text(text, max_len_first_line=12, max_len_second_line=20):
    words = text.split()
    wrapped_text = ''
    line_len = 0
    first_line = True

    for word in words:
        if first_line and len(word) >= max_len_first_line:
            first_line = False
            wrapped_text += '\n '
        if first_line:
            if line_len + len(word) <= max_len_first_line:
                wrapped_text += word + ' '
                line_len += len(word) + 1  # +1 for space
            else:
                wrapped_text += '\n ' + word[:max_len_second_line] + ' '
                line_len = len(word[:max_len_second_line]) + 1
                first_line = False
        else:
            if line_len + len(word) <= max_len_second_line:
                wrapped_text += word + ' '
                line_len += len(word)   # mby add +1 for space
            else:
                wrapped_text += word[:(max_len_second_line-line_len)]
                break

    return wrapped_text


async def generate_user_schedule_week(user_list: list[tuple]) -> BytesIO:
    logger.debug(f"User list: {user_list}")
    start_time = time.time()
    image = Image.open(os.path.join(settings.MEDIA_DIR, "week.jpeg"))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size=16, encoding="unic")
    #font = ImageFont.load_default()

    user_list_sorted = sorted(user_list, key=lambda x: x[0])

    text_color = (255, 255, 255)
    height = 205
    last_day = 0
    text_positions = [25, 210, 391, 571, 752, 933, 1114]
    for day, times, text in user_list_sorted:
        if last_day != day:
            last_day = day
            height = 205
        text_position = (text_positions[day], height)
        height += 32

        if text:
            if len(text) > 12:
                text = wrap_text(text, 12, 16)
                height += 16
            text = ' - ' + text
        else:
            text = ''
        text = f"{times if times[0] != '0' else '  ' + times[1:]}{text}"  # 00:00 - text  ||  00:00
        draw.text(text_position, text, fill=text_color, font=font)
    #image.save("media/1280_with_text.jpg")
    total_time = time.time() - start_time
    logger.info(f"Generated image in: {total_time:.4f} seconds")
    if total_time > 5:
        logger.warning(f"Too long generation: {total_time:.4f} seconds")
    #image.show()
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    return image_buffer


async def generate_user_schedule_day(schedule_list: list[tuple],
                                     day_: int = None,
                                     daytime: datetime = None,
                                     tz: str = None,
                                     with_date: bool = True) -> BytesIO:
    if day_ is None:
        dtime = daytime.astimezone(pytz.timezone(tz))
        day_ = dtime.weekday()
    logger.debug(f"{day_=}, {tz=}, {schedule_list=}")
    start_time = time.time()
    image = Image.open(os.path.join(settings.MEDIA_DIR, "day.jpeg"))
    draw = ImageDraw.Draw(image)
    text_color = (0, 0, 0)

    # DAY
    font = ImageFont.truetype(font_path, size=44, encoding="unic"
)
    # Printing day
    draw.text((130 if day_ in (2, 3, 5) else 155, 56), text=days_of_week[day_], fill=text_color, font=font)
    # DATE
    font = ImageFont.truetype(font_path, size=20)
    text = weekday_to_future_date(day_, tz if tz is not None else 'UTC').strftime('%d.%m') if with_date else ' '
    draw.text((372, 105), text=text, fill=text_color, font=font)    # Printing date
    # SCHEDULE
    text_color = (255, 255, 255)
    width = 26
    height = 192
    for time_, text in schedule_list:
        text = f"{time_}{' - ' + text[:28] if text else ' '}"
        text_position = (width, height)
        height += 40
        draw.text(text_position, text, fill=text_color, font=font)

    #image.save("one_with_text.jpeg")
    total_time = time.time() - start_time
    logger.info(f"Generated image in: {total_time:.4f} seconds")
    if total_time > 5:
        logger.warning(f"Too long generation: {total_time:.4f} seconds")
    #image.show()
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    return image_buffer


"""if __name__ == '__main__':
    import asyncio

    usr_list = [
        ("Monday", "10:00 AM", "Meeting with clients"),
        ("Tuesday", "2:30 PM", "Project presentation"),
        ("Wednesday", "11:00 AM", "Team brainstorming session"),
        ("Thursday", "3:00 PM", "Training session"),
        ("Friday", "9:00 AM", "Weekly review meeting"),
        ("Saturday", "1:00 PM", "Lunch with colleagues"),
        ("Sunday", "5:00 PM", "Personal time"),
        ("Monday", "9:30 AM", "Project kickoff meeting"),
        ("Tuesday", "4:00 PM", "Client follow-up call"),
        ("Wednesday", "2:00 PM", "Deadline reminder"),
        ("Thursday", "10:30 AM", "Team building activity"),
        ("Friday", "11:30 AM", "Strategy planning session"),
        ("Saturday", "12:00 PM", "Marketing campaign review"),
        ("Sunday", "3:30 PM", "Family time"),
        ("Monday", "8:00 AM", "Weekly progress report")
    ]
    async def main():
        await generate_user_schedule_week(usr_list)



    asyncio.run(main())"""
