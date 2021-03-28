from datetime import datetime


def get():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return f"{current_time} :: "
