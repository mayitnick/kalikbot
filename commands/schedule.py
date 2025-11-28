from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
from typing import Any, Dict
from datetime import datetime, timedelta
import modules.gloris_integration as gloris
import traceback

ALIASES = ["распис"]

SERVICE_WORDS = {"на", "по", "в", "для"}
DAY_ALIASES = {
    1: ["пн", "пон", "понед", "понедельник"],
    2: ["вт", "вторник"],
    3: ["ср", "среда", "сред"],
    4: ["чт", "четверг"],
    5: ["пт", "пятница", "пятн"],
    6: ["сб", "суббота", "суббот"],
    7: ["вс", "воскресенье", "воскрес"]
}
DAYS_MAP = {k: v[0].capitalize() for k, v in DAY_ALIASES.items()}  # Для заголовка

def parse_day(text: str) -> int | None:
    text = text.lower()
    if "сегодня" in text:
        return datetime.weekday(datetime.now()) + 1
    if "завтра" in text:
        return datetime.weekday(datetime.now() + timedelta(days=1)) + 1
    for day_num, variants in DAY_ALIASES.items():
        if any(v in text for v in variants):
            return day_num
    return None

def parse_group(parts: list[str]) -> str | None:
    for p in parts:
        if "-" in p or p.isalnum():
            try:
                return gloris.name_to_id(p.upper())
            except Exception:
                continue
    return None

def handle(message: Message, bot: TeleBot, db: database.Database,
           perm: permissions.Permissions, CONSTANTS: CONSTANTS, FOUNDER_ID: int):

    text = message.text.lower()
    parts = [p for p in text.split() if p not in SERVICE_WORDS]

    day = parse_day(text)

    # Если день не указан → сегодня или понедельник (выходные)
    if not day:
        day = datetime.weekday(datetime.now()) + 1
        if day >= 6:  # Суббота или воскресенье
            day = 1

    day_name = DAYS_MAP.get(day, "Неизвестный день")

    # Ищем группу среди оставшихся слов
    group_id = parse_group(parts)

    # Если группа не указана, пробуем взять из БД
    if not group_id:
        chat_id = message.chat.id
        group = db.get_group_by_tg_group_id(chat_id)
        if group:
            group_id = group["gloris_id"]
        else:
            bot.reply_to(message, CONSTANTS.tg_no_group + 
                         " Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
            return

    # Получаем расписание
    try:
        schedule, is_new = gloris.get_schedule(day, group_id)
        status = "🆕 новое расписание" if is_new else "📄 старое расписание"
        if schedule:
            bot.reply_to(message,
                         f"<b>Расписание на {day_name}:</b>\n" + 
                         "\n".join(schedule) + 
                         f"\n\n<i>{status}</i>",
                         parse_mode="HTML")
        else:
            bot.reply_to(message, CONSTANTS.schedule_not_found)
    except Exception:
        traceback.print_exc()
        bot.reply_to(message, CONSTANTS.error +
                     " Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
