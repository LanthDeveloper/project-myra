# src/modules/shared/utils/get_local_datetime.py
from datetime import datetime
from zoneinfo import ZoneInfo  # <- esto es lo que necesitas

def get_local_datetime():
    now = datetime.now(ZoneInfo("America/Lima"))
    return now
