from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import modules.permissions as permissions
import database
from datetime import datetime, timedelta
import modules.gloris_integration as gloris
from modules.constants import CONSTANTS
import modules.statistics as stat


def _split_pairs_to_lesson_slots(pair_times, lessons):
    slots = []
    slot_subjects = []

    for idx, p in enumerate(pair_times):
        start_str, end_str = p.split("-")
        start_dt = datetime.strptime(start_str.strip(), "%H:%M")
        end_dt = datetime.strptime(end_str.strip(), "%H:%M")
        duration_min = int((end_dt - start_dt).total_seconds() // 60)
        subject = lessons[idx] if idx < len(lessons) else "?"

        if duration_min >= 80:  # сдвоенная пара
            first_end = start_dt + timedelta(minutes=45)
            slots.append((start_dt.time(), first_end.time()))
            slot_subjects.append(subject)
            slots.append((first_end.time(), end_dt.time()))
            slot_subjects.append(subject)
        else:
            slots.append((start_dt.time(), end_dt.time()))
            slot_subjects.append(subject)

    return slots, slot_subjects


def get_current_status(pair_times, lessons):
    now_dt = datetime.now()
    now_time = now_dt.time()

    lesson_slots, slot_subjects = _split_pairs_to_lesson_slots(pair_times, lessons)
    if not lesson_slots:
        return "after", None, None, None

    first_start = lesson_slots[0][0]
    if now_time < first_start:
        until = int((datetime.combine(datetime.today(), first_start) - now_dt).total_seconds() // 60)
        return "before", 1, until, slot_subjects[0]

    for idx, (start, end) in enumerate(lesson_slots):
        if start <= now_time <= end:
            subject = slot_subjects[idx]
            if "ОБЕД" in subject.upper():
                remaining = int((datetime.combine(datetime.today(), end) - now_dt).total_seconds() // 60)
                return "rest", idx + 1, remaining, "ОБЕД"

            # ищем конец блока одинаковых уроков
            j = idx
            while j + 1 < len(slot_subjects) and slot_subjects[j + 1] == subject:
                j += 1
                end = lesson_slots[j][1]

            remaining = int((datetime.combine(datetime.today(), end) - now_dt).total_seconds() // 60)
            return "lesson", idx + 1, remaining, subject

        if now_time < start:
            until = int((datetime.combine(datetime.today(), start) - now_dt).total_seconds() // 60)
            next_subj = slot_subjects[idx]
            if "ОБЕД" in next_subj.upper():
                return "rest", idx + 1, until, "ОБЕД"
            return "rest", idx + 1, until, next_subj

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
    lessons, _ = gloris.get_schedule_by_id(date, group_id)
    if not lessons:  # на случай ошибки парсинга
        bot.reply_to(message, "Не удалось получить расписание 😿")
        return

    status, num, remaining, subject = get_current_status(schedule_times, lessons)
    remaining = (remaining or 0) + 1

    # создаём кнопку
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Узнать следующий урок 📘", callback_data="next_lesson"))

    # основной ответ
    stat.add_statistic("double")
    if status == "before":
        hours, minutes = divmod(remaining, 60)
        if hours > 0:
            bot.send_message(
                chat_id,
                f"Учебный день ещё впереди 🌸 Первая пара — {subject}, начнётся через {hours} ч {minutes} мин ⏳",
                reply_markup=markup,
            )
        else:
            bot.send_message(
                chat_id,
                f"До встречи с {subject} осталось {remaining} минут 🌿✨",
                reply_markup=markup,
            )

    elif status == "lesson":
        bot.send_message(
            chat_id,
            f"Сейчас идёт {num}-й урок ({subject}), он закончится через {remaining} минут 🕒~ потерпи немножко >w<",
            reply_markup=markup,
        )
        print(message.chat.id, f" type={type(message.chat.id)}")
        if message.chat.id == int("-1002949492641"):
            if "химия" in subject.lower():
                bot.send_sticker(chat_id, "CAACAgIAAxkBAAE9z6hpFskbbeY6lSc4R_QgOnRbwkROcgACEIoAArNmkEiIvsF6U330LDYE")
            if "час" in subject.lower():
                bot.send_sticker(chat_id, "CAACAgIAAxkBAAE98S9pGreUqsvTHZS2F_nSQITSE3jZlwACW4IAAml4uUg4kavT4a6c3TYE")

    elif status == "rest":
        next_subj = subject if subject != "ОБЕД" else lessons[num] if num < len(lessons) else None
        if next_subj:
            bot.send_message(
                chat_id,
                f"Сейчас переменка ✨ Следующий урок — {next_subj}. До него {remaining} минуточек ⏳",
                reply_markup=markup,
            )
        else:
            bot.send_message(
                chat_id,
                f"Сейчас отдых 🌿✨ У тебя есть {remaining} минут перед следующим занятием.",
                reply_markup=markup,
            )

    else:
        bot.send_message(chat_id, "Учебный день уже закончился 🌙", reply_markup=markup)


# обработчик callback'а
def handle_callback(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "next_lesson")
    def next_lesson(call):
        chat_id = call.message.chat.id
        db = database.Database()
        group = db.get_group_by_tg_group_id(chat_id)
        if not group:
            bot.answer_callback_query(call.id, "Группа не найдена")
            return

        group_id = group["gloris_id"]
        date = datetime.weekday(datetime.now()) + 1
        lessons, _ = gloris.get_schedule_by_id(date, group_id)
        if not lessons:
            bot.reply_to(call.message, "Не удалось получить расписание 😿")
            return

        schedule_times = db.get_schedule()  # блоками
        lesson_slots, slot_subjects = _split_pairs_to_lesson_slots(schedule_times, lessons)

        now_time = datetime.now().time()
        next_subject = None
        minutes_until = None

        for idx, (start, end) in enumerate(lesson_slots):
            if now_time < start:
                next_subject = slot_subjects[idx]
                minutes_until = int((datetime.combine(datetime.today(), start) - datetime.now()).total_seconds() // 60)
                break
            elif start <= now_time <= end:
                # если мы уже в паре, следующий это конец текущего блока
                current_subject = slot_subjects[idx]
                j = idx
                while j + 1 < len(slot_subjects) and slot_subjects[j + 1] == current_subject:
                    j += 1
                if j + 1 < len(slot_subjects):
                    next_subject = slot_subjects[j + 1]
                    start_next = lesson_slots[j + 1][0]
                    minutes_until = int((datetime.combine(datetime.today(), start_next) - datetime.now()).total_seconds() // 60)
                break

        bot.answer_callback_query(call.id)
        
        if next_subject:
            if "ОБЕД" in next_subject.upper():
                bot.send_message(
                    chat_id,
                    f"{call.from_user.first_name} нажал на кнопку\nСейчас отдых 🌿 Следующее занятие после него через {minutes_until} мин ✨"
                )
            else:
                bot.send_message(
                    chat_id,
                    f"{call.from_user.first_name} нажал на кнопку\nСледующий урок — {next_subject} 🧠✨ (через {minutes_until} мин)"
                )
        else:
            bot.send_message(chat_id, "Больше уроков на сегодня нет 🌙✨")
