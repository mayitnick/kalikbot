# modules/glorismon.py
import time

def start_monitoring(interval=60):
    while True:
        print("[Glorismon] Я слежу за расписанием...")
        time.sleep(interval)
