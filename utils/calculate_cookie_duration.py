import datetime

def calculate_cookie_duration(expiry_timestamp):
    if expiry_timestamp is not None:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        current_datetime = datetime.datetime.now()
        duration = expiry_datetime - current_datetime

        years = duration.days // 365
        remaining_days = duration.days % 365
        months = remaining_days // 30  # Approximate months as 30 days
        remaining_days %= 30
        days = remaining_days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_formatted = f"{months} (month)(s) {days} day(s) {hours} hour(s) {minutes} minute(s) {seconds} second(s)"
        return duration_formatted

    return "Session Cookie (no explicit expiry)"
