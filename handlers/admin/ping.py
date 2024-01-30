from datetime import datetime, timedelta

# Get today's date
today = datetime.now()

# Calculate the date next year same day
next_year_same_day = today + timedelta(days=365)

# Set the date range
start_date = today
end_date = next_year_same_day

print(datetime(2024, 1, 1), datetime(2025, 12, 31))
print(datetime.today(), datetime(2025, 1, 1))


# Now you can use these dates in your calendar.set_dates_range() function
# For example:
# calendar.set_dates_range(start_date, end_date)
