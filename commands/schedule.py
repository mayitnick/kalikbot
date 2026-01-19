from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
from typing import Any, Dict
from datetime import datetime, timedelta
import modules.gloris_integration as gloris
import traceback
import re

ALIASES = ["распис"]
SERVICE_WORDS = {"на", "по", "в", "для", "к"}

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

# ГРУППА: 1..6 букв (кириллица или латиница) - 2 цифры - 2 цифры, например: ИС-11-25, МЭП-11-25, S-11-25
GROUP_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁё]{1,6}-\d{2}-\d{2}$", re.UNICODE)

# Токенизатор: оставляет буквы/цифры/дефис как токены
_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9\-]+", re.UNICODE)

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]

def strip_command_tokens(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        if t in SERVICE_WORDS:
            continue
        if any(t.startswith(alias) for alias in ALIASES):
            # пропускаем сам вызов команды: "распис", "расписание" и т.п.
            continue
        out.append(t)
    return out

def parse_day_from_tokens(tokens: list[str]) -> int | None:
    for t in tokens:
        if t.startswith("сегодня"):
            return datetime.now().weekday() + 1
        if t.startswith("завтра"):
            return (datetime.now() + timedelta(days=1)).weekday() + 1
    # точная/префиксная проверка для имен дней
    for day_num, variants in DAY_ALIASES.items():
        for v in variants:
            if any(t == v or t.startswith(v) for t in tokens):
                return day_num
    return None

def parse_group_from_tokens(tokens: list[str]) -> str | None:
    """
    Ищет токен, строго подходящий под формат группы. Если найден — пытается привести
    к gloris.id через gloris.name_to_id. Явный приоритет за группой из сообщения.
    """
    for t in tokens:
        if GROUP_REGEX.fullmatch(t):
            try:
                return gloris.name_to_id(t.upper())
            except Exception:
                # если gloris не нашёл — продолжаем искать другие подходящие токены
                continue
    return None

def default_day_if_none(day: int | None) -> int:
    if day is not None:
        return day
    today = datetime.now().weekday() + 1
    return 1 if today >= 6 else today

def handle(message: Message, bot: TeleBot, db: database.Database,
           perm: permissions.Permissions, CONSTANTS: CONSTANTS, FOUNDER_ID: int):

    text = message.text or ""
    tokens = tokenize(text)
    tokens = strip_command_tokens(tokens)

    # 1) сначала ищем явную группу в сообщении (приоритет)
    explicit_group_id = parse_group_from_tokens(tokens)

    # 2) ищем день в сообщении
    day = parse_day_from_tokens(tokens)
    day = default_day_if_none(day)
    day_name = DAYS_MAP.get(day, "Неизвестный день")

    # 3) определяем финальную группу: сначала явная, если нет — из БД по chat_id
    group_id = explicit_group_id
    if not group_id:
        try:
            chat_id = message.chat.id
            group = db.get_group_by_tg_group_id(chat_id)
            if group and group.get("gloris_id"):
                group_id = group["gloris_id"]
        except Exception:
            traceback.print_exc()
            bot.reply_to(message, CONSTANTS.error + " Не удалось проверить привязку группы в базе.")
            return

    # 4) если всё ещё нет группы — просим указать (дружелюбно)
    if not group_id:
        bot.reply_to(
            message,
            "Эх… я не знаю, для какой группы смотреть расписание 🦊\n"
            "Пожалуйста, укажи группу в формате <b>ИС-11-25</b> или привяжи группу к этому чату.\n"
            "Примеры: <i>Калик, расписание ИС-11-25 пн</i> или <i>Калик, расписание завтра</i> (если группа уже привязана).",
            parse_mode="HTML"
        )
        return

    # 5) получаем расписание (gloris.get_schedule возвращает schedule, is_new)
    print(
        "[SCHEDULE DEBUG]",
        "day =", day,
        "group_id =", group_id,
        "chat_id =", message.chat.id
    )
    try:
        schedule, is_new = gloris.get_schedule_by_id(day, group_id)
        print(
            "[GLORIS RESPONSE]",
            "schedule =", repr(schedule),
            "is_new =", is_new
        )
    except Exception as e:
        print("[GLORIS EXCEPTION]", repr(e))
        traceback.print_exc()
        bot.reply_to(
            message,
            "Мр-р… ой, то есть фр фырр-р.. я не смог достучаться до Глориса 😿\n"
            "Похоже, он сейчас не отвечает или обиделся.",
            parse_mode="HTML"
        )
        return

    # 6) формируем ответ
    if not schedule:
        print("[EMPTY SCHEDULE]", "day =", day, "group_id =", group_id)
        bot.reply_to(message, CONSTANTS.schedule_not_found)
        return

    status = "🆕 новое расписание" if is_new else "📄 старое расписание"

    # если schedule — список строк, красиво пронумеруем
    if isinstance(schedule, list):
        lines = []
        for i, s in enumerate(schedule, start=1):
            s_clean = s.strip()
            lines.append(f"{i}. {s_clean}")
        body = "\n".join(lines)
    else:
        body = str(schedule)

    reply = f"<b>Расписание на {day_name}:</b>\n\n{body}\n\n<i>{status}</i>"
    bot.reply_to(message, reply, parse_mode="HTML")

