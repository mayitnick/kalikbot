# modules/glorismon.py
import time
import json
import os
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup

SCHEDULE_FILE = "lastschedule.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://xn----3-iddzneycrmpn.xn--p1ai/lesson_table_show/"

# --- Время активности ---
ACTIVE_HOURS = range(13, 15)      # пик
PASSIVE_HOURS = range(9, 18)      # редкие проверки
# ночь — всё остальное


def get_day_number():
    """1 = понедельник на сайте"""
    today = datetime.today().weekday()  # 0–6
    if today >= 4:  # пт, сб, вс
        return 1
    return today + 2  # завтра


def current_mode():
    hour = datetime.now().hour
    if hour in ACTIVE_HOURS:
        return "active"
    if hour in PASSIVE_HOURS:
        return "passive"
    return "sleep"


def parse_schedule(day_number):
    url = f"{BASE_URL}?day={day_number}"
    print(f"[Glorismon] GET {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"[Glorismon] HTTP {r.status_code}")
            return None
        html = r.text
    except requests.RequestException as e:
        print("[Glorismon] Request error:", e)
        return None

    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.find_all("div", class_="box-group")

    if not boxes:
        print("[Glorismon] No box-group found (possible rate-limit)")
        return None

    schedule = {}

    for box in boxes:
        btn = box.find("a", class_="btn-group")
        if not btn:
            continue

        gid = btn.get("id", "")
        if not gid.startswith("g"):
            continue

        group_id = gid[1:]
        lessons = []

        table = box.find("table")
        if table:
            for row in table.find_all("tr"):
                p = row.find("p")
                if p:
                    lessons.append(p.get_text(strip=True))

        schedule[group_id] = lessons

    print(f"[Glorismon] Parsed {len(schedule)} groups")
    return schedule


def load_last():
    if not os.path.exists(SCHEDULE_FILE):
        return {}

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("groups", {})


def save_last(data):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"updated_at": datetime.now().isoformat(), "groups": data},
            f,
            ensure_ascii=False,
            indent=2
        )


def check_updates(db, bot):
    day = get_day_number()
    new_data = parse_schedule(day)

    if new_data is None:
        return False  # ошибка

    old_data = load_last()
    updated = []

    for gid, lessons in new_data.items():
        if old_data.get(gid) != lessons:
            updated.append(gid)

    if old_data:
        for gid in updated:
            group = next(
                (g for g in db.get_all_groups() if str(g.get("gloris_id")) == gid),
                None
            )
            if group and group.get("tg_group_id"):
                try:
                    text = (
                        f"📚 Обновилось расписание для группы {group['group']}:\n"
                        + "\n".join(new_data[gid])
                    )
                    bot.send_message(group["tg_group_id"], text)
                except Exception as e:
                    print("[Glorismon] Send error:", e)

    save_last(new_data)
    return True


def start_monitoring(db, bot):
    fail_count = 0

    print("[Glorismon] Monitoring started")

    while True:
        mode = current_mode()

        if mode == "sleep":
            print("[Glorismon] Night mode — sleeping 1h")
            time.sleep(3600)
            continue

        print(f"[Glorismon] Mode: {mode}")

        ok = check_updates(db, bot)

        if ok:
            fail_count = 0
        else:
            fail_count += 1

        # интервалы
        if mode == "active":
            base = 10 * 60        # 10 минут
        else:  # passive
            base = 40 * 60        # 40 минут

        # exponential backoff + jitter
        sleep_time = min(base * (2 ** fail_count), 2 * 3600)
        sleep_time += random.randint(-60, 60)

        print(f"[Glorismon] Sleeping {sleep_time:.0f}s (fail={fail_count})")
        time.sleep(max(60, sleep_time))
