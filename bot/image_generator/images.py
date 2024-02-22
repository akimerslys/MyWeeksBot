from PIL import Image, ImageDraw, ImageFont
import time

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services.schedule import get_user_schedule_day_time_text
from io import BytesIO


def day_of_week_number(day):
    days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    return days.get(day, 0)


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


async def generate_user_schedule_week(session: AsyncSession, user_id: int) -> BytesIO:
    user_list = await get_user_schedule_day_time_text(session, user_id)
    start_time = time.time()
    image = Image.open("media/1280.jpeg")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/OPENSANS-SEMIBOLD.ttf", size=16)
    text_color = (255, 255, 255)
    user_list_sorted = (
        [(day, times, status) for day, times, status in
         sorted(user_list, key=lambda x: (day_of_week_number(x[0]), x[1]))])

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
        if len(text) > 12:
            text = wrap_text(text, 12, 16)
            height += 16

        text = f"{times if times[0] != '0' else '  ' + times[1:]} - {text}"
        draw.text(text_position, text, fill=text_color, font=font)
    #image.save("1280_with_text.jpg")
    total_time = time.time() - start_time
    logger.info(f"Generated image in: {total_time:.4f} seconds")
    if total_time > 5:
        logger.warning(f"Too long generation: {total_time:.4f} seconds")
    #image.show()
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    return image_buffer
