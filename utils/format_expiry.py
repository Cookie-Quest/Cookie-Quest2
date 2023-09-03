# utils/format_expiry.py

import datetime

def format_expiry(expiry_timestamp):
    if expiry_timestamp is not None:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        return expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return "Session Cookie (no explicit expiry)"
