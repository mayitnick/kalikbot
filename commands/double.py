from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
import database
from typing import Any, Dict
import datetime
from modules.gloris_integration import gloris
from modules.constants import CONSTANTS
def get_current_pair(schedule_times):
    """
    schedule_times = ["8:20-9:50", "10:00-11:30", ...]
    Возвращает (номер пары, минуты до конца) или (None, None)
    """
    now = datetime.now().time()

    for i, pair in enumerate(schedule_times, start=1):
        start_str, end_str = pair.split("-")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        if start <= now <= end:
            now_dt = datetime.combine(datetime.today(), now)
            end_dt = datetime.combine(datetime.today(), end)
            remaining = int((end_dt - now_dt).total_seconds() // 60)
            return i, remaining

    return None, None

ALIASES = ["айди", "id"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> None:
    # 1. Берём времена пар
    schedule_times = db.get_schedule()

    # 2. Определяем сегодняшнюю дату и день недели (1-7)
    date = datetime.weekday(datetime.now()) + 1

    # 3. Пытаемся достать расписание предметов
    chat_id = message.chat.id
    group = db.get_group_by_tg_group_id(chat_id)
    if not group:
        bot.reply_to(message, CONSTANTS["tg_no_group"])
        return

    group_id = group["gloris_id"]
    lessons = gloris.get_schedule(date, group_id)  # список предметов, по номерам пар

    # 4. Считаем текущую пару
    pair_num, remaining = get_current_pair(schedule_times)

    if pair_num:
        if pair_num <= len(lessons):
            subject = lessons[pair_num - 1]
            bot.reply_to(
                message,
                f"Сейчас идёт {pair_num}-я пара ({subject}), она закончится через {remaining} минут 🕒~ потерпи немножко >w<"
            )
        else:
            bot.reply_to(message, f"Сейчас идёт {pair_num}-я пара, но в расписании её нет 🤔")
    else:
        bot.reply_to(message, "Сейчас пар нет ✨")