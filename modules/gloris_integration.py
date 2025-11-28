import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

headers = {
    "User-Agent": "KalikBotOKTU/1.0",
    "X-Requested-By": "MayITNick (mayitnick@inbox.ru) (github.com/mayitnick/kalikbot)",
}

CACHE_FILE = "schedule_cache.json"

# ---------------------------------------------------------
# JSON-ХРАНИЛИЩЕ
# ---------------------------------------------------------

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def get_target_date(weekday: int):
    today = datetime.now().date()
    today_weekday = today.isoweekday()  # 1–7

    if today_weekday == 7:  
        today_weekday = 1  # воскресенье → понедельник

    delta = weekday - today_weekday
    if delta < 0:
        delta += 7

    return today + timedelta(days=delta)

# ---------------------------------------------------------
# ПАРСИНГ
# ---------------------------------------------------------

def _download_schedule(day: int, group_id: int):
    url = f"https://глорис-окту-3.рф/lesson_table_show/?day={day}&group_id={group_id}"
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    schedule_div = soup.find("div", id="shedule")
    if not schedule_div:
        return None

    lessons = [p.get_text(strip=True) for p in schedule_div.find_all("p")]

    # корекция понедельника
    if day == 1 and lessons:
        first = lessons[0]
        lessons[0] = "Классный час"
        lessons.append(first)

    return lessons

# ---------------------------------------------------------
# ОСНОВНАЯ ФУНКЦИЯ БИБЛИОТЕКИ
# ---------------------------------------------------------

def get_schedule(day: int, group_id: int):
    cache = load_cache()

    new_lessons = _download_schedule(day, group_id)
    if not new_lessons:
        return None, False

    new_str = "\n".join(new_lessons)
    target_date = get_target_date(day).isoformat()
    day_key = str(day)

    is_new = False

    if day_key not in cache:
        cache[day_key] = {
            "date": target_date,
            "lessons": new_str
        }
        save_cache(cache)
        is_new = True
        return new_lessons, is_new

    old_date = cache[day_key]["date"]
    old_lessons = cache[day_key]["lessons"]

    if old_date != target_date:
        if old_lessons != new_str:
            cache[day_key] = {
                "date": target_date,
                "lessons": new_str
            }
            save_cache(cache)
            is_new = True
    else:
        if old_lessons != new_str:
            cache[day_key]["lessons"] = new_str
            save_cache(cache)
            is_new = True

    return cache[day_key]["lessons"].split("\n"), is_new

# ---------------------------------------------------------

name_to_id_dict = {
    "Э-11-25": 45, "ИС-11-25": 46, "МЭП-11-25": 47, "МП-11-25": 48,
    "МПО-11-25": 49, "ОНМС-11-25": 50, "П-11-25": 51, "СЛ-11-25": 52,
    "ТМ-11-25": 53, "Э-21-24": 35, "ИС-21-24": 36, "МЭП-21-24": 37,
    "П-21-24": 38, "СЛ-21-24": 39, "Т-21-24": 40, "Т-22-24": 41,
    "ТМ-22-24": 42, "МРА-21-24": 44, "ИС-31-23": 29, "П-31-23": 30,
    "ТМ-31-23": 32, "ТЭ-31-23": 33, "ИС-41-22": 25, "ИС-42-22": 26,
    "МПО-41-22": 27, "МПО-42-22": 28,
}

def name_to_id(name):
    return name_to_id_dict.get(name)
