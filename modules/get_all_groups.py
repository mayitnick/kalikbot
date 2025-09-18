import requests
from bs4 import BeautifulSoup
import json
import time

days = range(1, 7)  # понедельник - суббота

def get_schedule_all_groups(day):
    url = f"https://глорис-окту-3.рф/lesson_table_show/?day={day}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_div = soup.find('div', id='shedule')
    if not schedule_div:
        return []
    lessons = [p.get_text(strip=True) for p in schedule_div.find_all('p')]
    return lessons

all_subjects = set()

for day in days:
    lessons = get_schedule_all_groups(day)
    all_subjects.update(lessons)
    time.sleep(0.5)  # задержка, чтобы не перегружать сервер

all_subjects.discard('')
all_subjects.discard('-')

items = {subject: None for subject in sorted(all_subjects)}

with open("all_subjects.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("Собрано предметов:", len(items))
print("Результат сохранён в all_subjects.json")
