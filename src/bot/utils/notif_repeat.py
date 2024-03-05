async def repeat_to_str(daily: bool, weekly: bool) -> str:
    if daily and weekly:
        return "Monthly"
    if daily:
        return "Daily"
    if weekly:
        return "Weekly"
    return "One time"