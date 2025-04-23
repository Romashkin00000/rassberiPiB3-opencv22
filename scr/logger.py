

import datetime

def log(message):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a") as f:
        f.write(f"[{time_now}] {message}\n")
