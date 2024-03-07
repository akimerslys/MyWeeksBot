import pytz
from PIL import Image, ImageDraw, ImageFont
import time
from datetime import datetime
from loguru import logger
from io import BytesIO

from src.core.config import settings


def days_of_week(day: str, num: int) -> int | str:
    days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}

    if day:
        if day in days:
            return days[day]
        elif num in days.values():
            return next(key for key, value in days.items() if value == num)
        else:
            return 'Invalid input'
    elif num in days.values():
        return next(key for key, value in days.items() if value == num)
    else:
        return 'Invalid input'


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
    image = Image.open("media/week.jpeg")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(settings.FONTS_DIR + "OPENSANS-SEMIBOLD.ttf", size=16)

    user_list_sorted = (
        [(day, times, status) for day, times, status in
         sorted(user_list, key=lambda x: (days_of_week(x[0], 0)))])

    text_color = (255, 255, 255)
    height = 205
    text_position = 30
    last_day = 'Monday'

    for day, times, text in user_list_sorted:
        if last_day != day:
            last_day = day
            height = 205
        match day:
            case "Monday":
                text_position = (25, height)
            case "Tuesday":
                text_position = (210, height)
            case "Wednesday":
                text_position = (391, height)
            case "Thursday":
                text_position = (571, height)
            case "Friday":
                text_position = (752, height)
            case "Saturday":
                text_position = (933, height)
            case "Sunday":
                text_position = (1114, height)
        height += 32
        if not text:
            text = ''
        if text:
            if len(text) > 12:
                text = wrap_text(text, 12, 16)
                height += 16
            text = ' - ' + text
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


async def generate_user_schedule_day(schedule_list: list[tuple], daytime: datetime, tz: str) -> BytesIO:
    dtime = daytime.astimezone(pytz.timezone(tz))
    day = dtime.weekday()

    logger.debug(f"Schedule list: {schedule_list}")

    start_time = time.time()
    image = Image.open("media/day.jpeg")
    draw = ImageDraw.Draw(image)
    text_color = (0, 0, 0)

    # DAY
    font = ImageFont.truetype("fonts/OPENSANS-SEMIBOLD.ttf", size=44)
    width = 130 if day in (2, 3, 5) else 155
    height = 56
    text_position = (width, height)
    draw.text(text_position, text=days_of_week('', day+1), fill=text_color, font=font)
    # DATE
    font = ImageFont.truetype("fonts/OPENSANS-SEMIBOLD.ttf", size=20)
    width = 372
    height = 105
    text_position = (width, height)
    text = dtime.strftime("%d.%m")
    draw.text(text_position, text=text, fill=text_color, font=font)
    # SCHEDULE
    text_color = (255, 255, 255)
    width = 26
    height = 192
    for time_, text in schedule_list:

        if text:
            text = str(time_) + ' - ' + text[:28]
        else:

            text = str(time_)
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


