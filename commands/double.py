from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
import database
from typing import Any, Dict
from datetime import datetime
import modules.gloris_integration as gloris
from modules.constants import CONSTANTS

def get_current_status(schedule_times, lessons):
    """
    schedule_times = ["8:20-9:05", "9:05-9:50", ...]  # поурочно!
    lessons = ["Физика", "Физика", "Математика", ...]  # список предметов

    Возвращает кортеж:
    ("lesson" | "break" | "before" | "after", номер, минуты, предмет/список)
    """
    now = datetime.now().time()

    # 0. До начала пар
    first_start = datetime.strptime(schedule_times[0].split("-")[0], "%H:%M").time()
    if now < first_start:
        now_dt = datetime.combine(datetime.today(), now)
        start_dt = datetime.combine(datetime.today(), first_start)
        remaining = int((start_dt - now_dt).total_seconds() // 60)
        return "before", 1, remaining, lessons[0]

    for i, pair in enumerate(schedule_times):
        start_str, end_str = pair.split("-")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        # 1. Проверяем — идёт ли урок
        if start <= now <= end:
            subject = lessons[i] if i < len(lessons) else "?"

            # ищем стак
            j = i
            while j + 1 < len(lessons) and lessons[j + 1] == subject:
                j += 1
                _, end_str = schedule_times[j].split("-")
                end = datetime.strptime(end_str, "%H:%M").time()

            # считаем оставшееся время
            now_dt = datetime.combine(datetime.today(), now)
            end_dt = datetime.combine(datetime.today(), end)
            remaining = int((end_dt - now_dt).total_seconds() // 60)

            return "lesson", i + 1, remaining, subject

        # 2. Проверяем перемену (сейчас между i и i+1 уроком)
        if now < start:
            prev_end = None
            if i > 0:
                _, prev_end_str = schedule_times[i - 1].split("-")
                prev_end = datetime.strptime(prev_end_str, "%H:%M").time()

            if not prev_end or prev_end < now < start:
                # до следующего урока
                now_dt = datetime.combine(datetime.today(), now)
                start_dt = datetime.combine(datetime.today(), start)
                remaining = int((start_dt - now_dt).total_seconds() // 60)

                next_subject = lessons[i] if i < len(lessons) else "?"
                return "break", i + 1, remaining, next_subject

    # 3. После всех уроков
    return "after", None, None, None

ALIASES = ["пара"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> None:
    schedule_times = db.get_schedule()
    date = datetime.weekday(datetime.now()) + 1

    chat_id = message.chat.id
    group = db.get_group_by_tg_group_id(chat_id)
    if not group:
        bot.reply_to(message, CONSTANTS["tg_no_group"])
        return

    group_id = group["gloris_id"]
    lessons = gloris.get_schedule(date, group_id)

    status, num, remaining, subject = get_current_status(schedule_times, lessons)

    if status == "before":
        hours, minutes = divmod(remaining, 60)
        if hours > 0:
            bot.reply_to(message, f"Учебный день ещё не начался ✨ До первой пары ({subject}) осталось {hours} ч {minutes} мин ⏳")
        else:
            bot.reply_to(message, f"Учебный день ещё не начался ✨ До первой пары ({subject}) осталось {minutes} минут ⏳")

    elif status == "lesson":
        bot.reply_to(
            message,
            f"Сейчас идёт {num}-й урок ({subject}), он закончится через {remaining} минут 🕒~ потерпи немножко >w<"
        )

    elif status == "break":
        bot.reply_to(
            message,
            f"Сейчас перемена ✨ До {num}-го урока ({subject}) осталось {remaining} минут ⏳"
        )

    else:  # after
        bot.reply_to(message, "Учебный день уже закончился 🌙")
