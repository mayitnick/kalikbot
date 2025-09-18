import requests
from bs4 import BeautifulSoup

def get_schedule(day: int, group_id: int):
    url = f"https://глорис-окту-3.рф/lesson_table_show/?day={day}&group_id={group_id}"
    # Для того, чтобы получить все группы: url = f"https://глорис-окту-3.рф/lesson_table_show/?day={day}"
    print(url)
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_div = soup.find('div', id='shedule')
    if not schedule_div:
        return None
    
    lessons = [p.get_text(strip=True) for p in schedule_div.find_all('p')]
    return lessons

def main():
    day = int(input("Введите номер дня недели (1-пн, 2-вт, ...): "))
    group_id = name_to_id(input("Введите название группы: "))
    
    lessons = get_schedule(day, group_id)
    if not lessons:
        print("Расписание не найдено.")
        return
    
    schedule_str = '\n'.join(lessons)
    print("\nРасписание уроков:")
    print(schedule_str)
    
    with open("schedule.txt", "w", encoding="utf-8") as f:
        f.write(schedule_str)
    print("\nРасписание сохранено в schedule.txt")

name_to_id_dict = {
    "Э-11-25": 45,
    "ИС-11-25": 46,
    "МЭП-11-25": 47,
    "МП-11-25": 48,
    "МПО-11-25": 49,
    "ОНМС-11-25": 50,
    "П-11-25": 51,
    "СЛ-11-25": 52,
    "ТМ-11-25": 53,
    "Э-21-24": 35,
    "ИС-21-24": 36,
    "МЭП-21-24": 37,
    "П-21-24": 38,
    "СЛ-21-24": 39,
    "Т-21-24": 40,
    "Т-22-24": 41,
    "ТМ-22-24": 42,
    "МРА-21-24": 44,
    "ИС-31-23": 29,
    "П-31-23": 30,
    "ТМ-31-23": 32,
    "ТЭ-31-23": 33,
    "ИС-41-22": 25,
    "ИС-42-22": 26,
    "МПО-41-22": 27,
    "МПО-42-22": 28,
}

def name_to_id(name):
    if name in name_to_id_dict:
        return name_to_id_dict[name]
    else:
        return None

if __name__ == "__main__":
    main()
