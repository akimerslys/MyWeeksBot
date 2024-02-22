from PIL import Image, ImageDraw, ImageFont
import asyncio
import time


def day_of_week_number(day):
    days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    return days.get(day, 0)


def wrap_text(text, max_len_first_line=12, max_len_second_line=20):
    words = text.split()
    wrapped_text = ''
    line_len = 0
    first_line = True

    for word in words:
        if first_line and len(word)>=max_len_first_line :
            first_line = False
            wrapped_text += '\n'
        if first_line:
            if line_len + len(word) <= max_len_first_line:
                wrapped_text += word + ' '
                line_len += len(word) + 1  # +1 for space
            else:
                wrapped_text += '\n' + word[:max_len_second_line] + ' '  # Добавляем только часть слова во вторую строку
                line_len = len(word[:max_len_second_line])  # Учитываем только часть слова
                first_line = False
        else:
            if line_len + len(word) <= max_len_second_line:
                wrapped_text += word + ' '
                line_len += len(word) + 1  # +1 for space
            else:
                wrapped_text += word[:(max_len_second_line-line_len)]                # Добавляем только часть слова во вторую строку
                break  # Прерываем цикл, если превышен лимит второй строки

    return wrapped_text


my_list = [('Thursday', '08:00', 'Wake-up!'), ('Friday', '08:00', 'Wake-up!'), ('Wednesday', '08:00', 'Wake-up!'),
           ('Monday', '08:00', 'Wake-up!'), ('Tuesday', '08:00', 'Wake-up!'), ('Tuesday', '20:00', 'Rubbish!!'),
           ('Friday', '10:00', 'work'), ('Monday', '10:00', 'work'), ('Wednesday', '10:00', 'work'),
           ('Sunday', '10:00', 'work'), ('Monday', '18:00', 'Prepare for driver licence test'),
           ('Tuesday', '18:00', 'Lollllllllllllll ahahahahahhahaa'),
           ('Wednesday', '18:00', 'Prepare for driver licence test'),
           ('Thursday', '18:00', 'Prepare for driver licence test'),
           ('Friday', '18:00', 'Prepare for driver licence test'),
           ('Saturday', '18:00', 'Prepare for driver licence test'),
           ('Sunday', '18:00', 'Prepare for driver licence test')]


async def main():
    start_time = time.time()
    image = Image.open("media/schedule1280.jpg")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/OPENSANS-SEMIBOLD.ttf", size=16)
    text_color = (255, 255, 255)

    my_list_sorted = (
        [(day, times, status) for day, times, status in
         sorted(my_list, key=lambda x: (day_of_week_number(x[0]), x[1]))])

    height = 205
    text_position = 30
    last_day = 'Monday'
    for day, times, text in my_list_sorted:
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
        height += 24
        text_len = len(text)
        if text_len > 12:
            text = wrap_text(text, 12, 20)
            height += 16
        text = f"{times if times[0] != '0' else '  ' + times[1:]} - {text}"
        draw.text(text_position, text, fill=text_color, font=font)
    image.save("1280_with_text.jpeg")
    total_time = time.time() - start_time
    print(f"Total time: {total_time:.4f} seconds")
    image.show()

if __name__ == "__main__":
    asyncio.run(main())

