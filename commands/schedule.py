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

DAYS_MAP = {k: v[0].capitalize() for k, v in DAY_ALIASES.items()}


def parse_day(text: str) -> int | None:
    text = text.lower()

    if "сегодня" in text:
        return datetime.now().weekday() + 1

    if "завтра" in text:
        return (datetime.now() + timedelta(days=1)).weekday() + 1

    for day_num, variants in DAY_ALIASES.items():
        if any(v in text for v in variants):
            return day_num

    return None


def parse_group(parts: list[str]) -> str | None:
    for p in parts:
        if "-" in p or p.isalnum():
            try:
                return gloris.name_to_id(p.upper())
            except:
                continue
    return None


def get_default_day() -> int:
    """Сегодня, но если выходные — понедельник."""
    day = datetime.now().weekday() + 1
    if day >= 6:
        return 1
    return day


def handle(message: Message, bot: TeleBot, db: database.Database,
           perm: permissions.Permissions, CONSTANTS: CONSTANTS, FOUNDER_ID: int):

    text = message.text.lower()
    parts = [p for p in text.split() if p not in SERVICE_WORDS]

    # 1. День
    day = parse_day(text)
    if not day:
        day = get_default_day()

    day_name = DAYS_MAP.get(day, "Неизвестный день")

    # 2. Группа
    group_id = parse_group(parts)

    if not group_id:
        group = db.get_group_by_tg_group_id(message.chat.id)
        if group:
            group_id = group["gloris_id"]
        else:
            bot.reply_to(
                message,
                "Эх… я не знаю, для какой группы смотреть расписание 🦊💭\n"
                "Напиши, пожалуйста, в формате:\n"
                "<b>Калик, расписание 1ИС-22 пн</b>",
                parse_mode="HTML"
            )
            return

    # 3. Получаем расписание
    try:
        schedule, is_new = gloris.get_schedule(day, group_id)
        status = "🆕 новое расписание" if is_new else "📄 старое расписание"

        if schedule:
            bot.reply_to(
                message,
                f"<b>Расписание на {day_name}:</b>\n"
                + "\n".join(schedule)
                + f"\n\n<i>{status}</i>",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(message, "Не удалось найти расписание для этой группы…")
    except Exception:
        traceback.print_exc()
        bot.reply_to(
            message,
            "Ой… что-то пошло не так 😟\n"
            "Попробуй ещё раз в формате:\n"
            "<b>Калик, расписание 1ИС-22 пн</b>",
            parse_mode="HTML"
        )

