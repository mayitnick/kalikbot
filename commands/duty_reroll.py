from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import random
import traceback
import datetime

def get_url_from_id(full_name, id):
    return f"[{full_name}](tg://user?id={id})"

def escape_markdown(text: str) -> str:
    escape_chars = r'_-'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

ALIASES = ["реролл"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    try:
        # Автор команды
        author = db.get_user_by_id(message.from_user.id)
        if not author:
            bot.reply_to(message, "❌ Не удалось найти информацию об авторе.")
            return True

        # Проверка прав
        if not (perm.check_for_permissions(author["type"], "duty.reroll") or message.from_user.id == FOUNDER_ID):
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
            return True

        # Определяем группу по чату
        group = db.get_group_by_id(message.chat.id)
        if not group:
            bot.reply_to(message, "❌ Эта группа не зарегистрирована в базе.")
            return True

        # Получаем список студентов (по их telegram_id)
        users = [db.get_user_by_id(uid) for uid in group["students"]]
        users = [u for u in users if u]  # убираем None

        if not users:
            bot.reply_to(message, "❌ В этой группе нет студентов.")
            return True

        today = datetime.datetime.now()
        today_date = today.strftime("%Y-%m-%d")
        today_weekday = today.strftime("%A").lower()  # например 'monday'

        # Алгоритм приоритета
        def priority(user):
            duty_info = user.get("duty_info", {})
            duties = duty_info.get("amount_of_duties", 0)

            # Чем дольше не дежурил — тем выше приоритет
            last_duty = duty_info.get("last_duty")
            if last_duty:
                days_ago = (today - datetime.datetime.strptime(last_duty, "%Y-%m-%d")).days
            else:
                days_ago = 99999

            # Проверка предпочтений
            preferences = [p.lower() for p in duty_info.get("preferences", [])]
            pref_bonus = 0
            if today_weekday in preferences:
                pref_bonus -= 100
            if today_date in preferences:
                pref_bonus -= 200

            return (duties, -days_ago, pref_bonus, random.random())

        # Сортировка по приоритетам
        sorted_users = sorted(users, key=priority)

        selected = []
        while len(selected) < 2 and sorted_users:
            candidate = sorted_users.pop(0)
            duty_info = candidate.get("duty_info", {})

            # Проверка пары
            pair_id = duty_info.get("pair_id")
            if pair_id:
                pair_user = db.get_user_by_id(pair_id)
                if pair_user and pair_user not in selected:
                    selected.append(pair_user)

            if candidate not in selected:
                selected.append(candidate)

        # Формируем ответ
        if selected:
            reply_text = "🎲 Реролл завершён! Выбраны дежурные:\n"
            for u in selected:
                duty_info = u.get("duty_info", {})
                reply_text += f"• {get_url_from_id(escape_markdown(u['full_name']), u['telegram_id'])} (дежурств: {duty_info.get('amount_of_duties', 0)})\n"
            bot.reply_to(message, reply_text, parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "❌ Не удалось выбрать дежурных.")

        return True

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при реролле: {e}")
        traceback.print_exc()
        return True
