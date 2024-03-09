import pytz

for tz in pytz.country_names:
    print(tz, pytz.country_names[tz])

for tz in pytz.country_timezones('r'):
    print(tz)