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
        print(f"[DEBUG] Файл кэша {CACHE_FILE} не найден, возвращаем пустой словарь")
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            print(f"[DEBUG] Кэш успешно загружен из {CACHE_FILE}")
            return cache
    except json.JSONDecodeError as e:
        print(f"[ERROR] Ошибка декодирования JSON из {CACHE_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка при загрузке кэша: {e}")
        return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
            print(f"[DEBUG] Кэш успешно сохранён в {CACHE_FILE}")
    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении кэша: {e}")

def get_target_date(weekday: int):
    try:
        today = datetime.now().date()
        today_weekday = today.isoweekday()  # 1–7
        
        print(f"[DEBUG] Текущая дата: {today}, день недели: {today_weekday}")

        if today_weekday == 7:  
            today_weekday = 1  # воскресенье → понедельник
            print(f"[DEBUG] Воскресенье преобразовано в понедельник")

        delta = weekday - today_weekday
        if delta < 0:
            delta += 7

        target = today + timedelta(days=delta)
        print(f"[DEBUG] Целевая дата для дня {weekday}: {target}")
        return target
    except Exception as e:
        print(f"[ERROR] Ошибка при вычислении целевой даты: {e}")
        return datetime.now().date()

# ---------------------------------------------------------
# ПАРСИНГ
# ---------------------------------------------------------

def _download_schedule(day: int, group_id: int):
    url = f"https://глорис-окту-3.рф/lesson_table_show/?day={day}&group_id={group_id}"
    print(f"[DEBUG] Загрузка расписания для группы {group_id}, день {day}")
    print(f"[DEBUG] URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"[DEBUG] Статус ответа: {response.status_code}")
        response.encoding = "utf-8"
    except requests.exceptions.Timeout:
        print(f"[ERROR] Превышено время ожидания при запросе к {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Ошибка соединения при запросе к {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ошибка запроса к {url}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка при загрузке расписания: {e}")
        return None

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        schedule_div = soup.find("div", id="shedule")
        
        if not schedule_div:
            print(f"[WARNING] Div с id='shedule' не найден на странице")
            return None

        lessons = [p.get_text(strip=True) for p in schedule_div.find_all("p")]
        print(f"[DEBUG] Найдено {len(lessons)} уроков")

        # корекция понедельника
        if day == 1 and lessons:
            first = lessons[0]
            lessons[0] = "Классный час"
            lessons.append(first)
            print(f"[DEBUG] Применена коррекция понедельника")

        return lessons
    except Exception as e:
        print(f"[ERROR] Ошибка при парсинге HTML: {e}")
        return None

# ---------------------------------------------------------
# ОСНОВНАЯ ФУНКЦИЯ БИБЛИОТЕКИ
# ---------------------------------------------------------

def get_schedule(day: int, group_name: str):
    print(f"[DEBUG] Запрос расписания: день={day}, группа={group_name}")
    
    group_id = name_to_id(group_name)
    if group_id is None:
        print(f"[ERROR] Группа {group_name} не найдена в словаре")
        return None, False

    print(f"[DEBUG] ID группы: {group_id}")
    
    cache = load_cache()
    if group_name not in cache:
        cache[group_name] = {}
        print(f"[DEBUG] Создана новая запись в кэше для группы {group_name}")

    new_lessons = _download_schedule(day, group_id)
    if not new_lessons:
        print(f"[WARNING] Не удалось загрузить расписание")
        return None, False

    new_str = "\n".join(new_lessons)
    target_date = get_target_date(day).isoformat()
    day_key = str(day)
    is_new = False
    now_iso = datetime.now().isoformat(timespec='seconds')

    if day_key not in cache[group_name]:
        print(f"[DEBUG] День {day} отсутствует в кэше, добавляем новую запись")
        cache[group_name][day_key] = {
            "date": target_date,
            "lessons": new_str,
            "updated_at": now_iso
        }
        save_cache(cache)
        is_new = True
        return new_lessons, is_new

    old_entry = cache[group_name][day_key]
    if old_entry["date"] != target_date or old_entry["lessons"] != new_str:
        print(f"[DEBUG] Обнаружены изменения в расписании, обновляем кэш")
        cache[group_name][day_key] = {
            "date": target_date,
            "lessons": new_str,
            "updated_at": now_iso
        }
        save_cache(cache)
        is_new = True
    else:
        print(f"[DEBUG] Расписание не изменилось")

    return cache[group_name][day_key]["lessons"].split("\n"), is_new

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
