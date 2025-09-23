from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
import database
from datetime import datetime, timedelta
import modules.gloris_integration as gloris
from modules.constants import CONSTANTS

def _split_pairs_to_lesson_slots(pair_times):
    """
    Разбивает список пар (из БД) на поурочные слоты (примерно по 45 минут).
    Если пара 90 мин -> два слота, если 45 мин -> один слот.
    Возвращает список (start_time, end_time).
    """
    slots = []
    for p in pair_times:
        start_str, end_str = p.split("-")
        start_dt = datetime.strptime(start_str.strip(), "%H:%M")
        end_dt = datetime.strptime(end_str.strip(), "%H:%M")
        duration_min = int((end_dt - start_dt).total_seconds() // 60)

        if duration_min >= 80:  # сдвоенная пара
            first_end = start_dt + timedelta(minutes=45)
            slots.append((start_dt.time(), first_end.time()))
            slots.append((first_end.time(), end_dt.time()))
        else:
            slots.append((start_dt.time(), end_dt.time()))
    return slots


def get_current_status(pair_times, lessons):
    """
    pair_times: ["8:20-9:50", "10:00-11:30", ...]  # блоками, как в БД
    lessons: ["Физика", "Физика", "Математика", ...]  # поурочно, из Gloris

    Возвращает:
      ("before", idx, minutes, subject)
      ("lesson", idx, minutes, subject)
      ("break", idx, minutes, subject)
      ("lunch", idx, minutes, "ОБЕД")
      ("after", None, None, None)
    """
    now_dt = datetime.now()
    now_time = now_dt.time()

    lesson_slots = _split_pairs_to_lesson_slots(pair_times)
    if not lesson_slots:
        return "after", None, None, None

    # до начала дня
    first_start = lesson_slots[0][0]
    if now_time < first_start:
        until = int((datetime.combine(datetime.today(), first_start) - now_dt).total_seconds() // 60)
        return "before", 1, until, lessons[0]

    for idx, (start, end) in enumerate(lesson_slots):
        if start <= now_time <= end:
            subject = lessons[idx] if idx < len(lessons) else "?"

            if subject.upper().startswith("ОБЕД"):
                remaining = int((datetime.combine(datetime.today(), end) - now_dt).total_seconds() // 60)
                return "lunch", idx + 1, remaining, "ОБЕД"

            # ищем стак одинаковых предметов
            j = idx
            while j + 1 < len(lessons) and lessons[j + 1] == subject:
                j += 1
                end = lesson_slots[j][1]

            remaining = int((datetime.combine(datetime.today(), end) - now_dt).total_seconds() // 60)
            return "lesson", idx + 1, remaining, subject

        if now_time < start:
            until = int((datetime.combine(datetime.today(), start) - now_dt).total_seconds() // 60)
            next_subj = lessons[idx] if idx < len(lessons) else "?"
            if next_subj.upper().startswith("ОБЕД"):
                return "lunch", idx + 1, until, "ОБЕД"
            return "break", idx + 1, until, next_subj

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
    schedule_times = db.get_schedule()  # блоками (как сейчас)
    date = datetime.weekday(datetime.now()) + 1

    chat_id = message.chat.id
    group = db.get_group_by_tg_group_id(chat_id)
    if not group:
        bot.reply_to(message, CONSTANTS.tg_no_group)
        return

    group_id = group["gloris_id"]
    lessons = gloris.get_schedule(date, group_id)

    status, num, remaining, subject = get_current_status(schedule_times, lessons)

    remaining += 1

    if status == "before":
        hours, minutes = divmod(remaining, 60)
        if hours > 0:
            bot.reply_to(message, f"Учебный день ещё впереди 🌸 Первая пара — {subject}, начнётся через {hours} ч {minutes} мин ⏳")
        else:
            bot.reply_to(message, f"До встречи с {subject} осталось {remaining} минут 🌿✨")

    elif status == "lesson":
        bot.reply_to(message, f"Сейчас идёт {num}-й урок ({subject}), он закончится через {remaining} минут 🕒~ потерпи немножко >w<")

    elif status == "break":
        bot.reply_to(message, f"Сейчас переменка ✨ До {num}-го урока ({subject}) осталось {remaining} минуточек ⏳")

    elif status == "lunch":
        bot.reply_to(message, f"Сейчас обед 🍎✨ Отдыхай, у тебя есть {remaining} минут!")

    else:
        bot.reply_to(message, "Учебный день уже закончился 🌙")
