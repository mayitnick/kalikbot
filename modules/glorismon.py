# modules/glorismon.py
import time
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import os

SCHEDULE_FILE = "lastschedule.json"

def get_day_number():
    """Возвращает номер дня для проверки расписания (1 — понедельник на сайте)."""
    today = datetime.today().weekday()  # Пн=0 ... Вс=6
    if today in (4, 5):  # пятница или суббота
        return 1  # понедельник
    else:
        return today + 2  # завтра, day_number на сайте начинается с 1

def parse_schedule(day_number=1):
    """Парсинг расписания на один день"""
    url = f"https://xn----3-iddzneycrmpn.xn--p1ai/lesson_table_show/?day={day_number}"
    try:
        html = requests.get(url, timeout=10).text
    except requests.RequestException as e:
        print("[Glorismon] Ошибка запроса:", e)
        return None

    soup = BeautifulSoup(html, 'html.parser')
    schedule = {}

    for box in soup.find_all('div', class_='box-group'):
        btn = box.find('a', class_='btn-group')
        if not btn:
            continue
        
        group_id = int(btn.get('id', 'g0')[1:])
        lessons = []

        table = box.find('table')
        if table:
            for row in table.find_all('tr'):
                p = row.find('p')
                if p:
                    lessons.append(p.get_text(strip=True))
        
        schedule[str(group_id)] = lessons

    return schedule

def load_last_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_last_schedule(data):
    data_to_save = {
        "updated_at": datetime.now().isoformat(),
        "groups": data
    }
    with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

def check_updates(db, bot):
    """Проверка обновлений и уведомления"""
    day_number = get_day_number()
    new_schedule = parse_schedule(day_number=day_number)
    if new_schedule is None:
        return

    last_data_wrapper = load_last_schedule()
    last_data = last_data_wrapper.get("groups", {}) if last_data_wrapper else {}

    updated_groups = []

    for group_id, lessons in new_schedule.items():
        if last_data.get(group_id) != lessons:
            updated_groups.append(group_id)

    # Отправляем уведомления только если файл уже был (чтобы не пугать при первом запуске)
    if last_data_wrapper:
        for group_id in updated_groups:
            group = next((g for g in db.get_all_groups() if g.get("gloris_id") == int(group_id)), None)
            if group and group.get("tg_group_id"):
                try:
                    msg = f"📚 Расписание на день для группы {group['group']}:\n" + "\n".join(new_schedule[group_id])
                    bot.send_message(group["tg_group_id"], msg)
                    print(f"[Glorismon] Отправлено обновленное расписание для {group['group']}")
                except Exception as e:
                    print(f"[Glorismon] Ошибка при отправке сообщения в группу {group['group']}: {e}")

    # Сохраняем новое расписание
    save_last_schedule(new_schedule)

def start_monitoring(db, bot, interval=500):
    """Главная функция для потока"""
    while True:
        print("[Glorismon] Я слежу за расписанием...")
        check_updates(db, bot)
        time.sleep(interval)
