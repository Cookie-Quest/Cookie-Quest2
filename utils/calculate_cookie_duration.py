# utils/calculate_cookie_duration.py

import datetime

def calculate_cookie_duration(expiry_timestamp):
    if expiry_timestamp is not None:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        current_datetime = datetime.datetime.now()
        duration = expiry_datetime - current_datetime

        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_formatted = f"{hours}h {minutes}m {seconds}s"
        return duration_formatted

    return "Session Cookie (no explicit expiry)"
