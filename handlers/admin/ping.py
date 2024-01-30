from datetime import datetime
import pytz

# Получение списка временных зон
timezones = pytz.all_timezones

# Вывод списка временных зон
for timezone in timezones:
    print(timezone)
