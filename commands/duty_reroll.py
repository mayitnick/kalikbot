from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import random
import traceback
import datetime

def md_escape(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    # список символов, которые нужно экранировать в MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + c if c in escape_chars else c for c in text)

# Ссылка на пользователя (MarkdownV2)
def get_url_from_id(full_name, tg_id):
    return f"[{md_escape(full_name)}](tg://user?id={tg_id})"

ALIASES = ["реролл"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    """
    Команда реролл:
    - берёт группу по message.chat.id (db.get_group_by_id)
    - собирает пользователей (db.get_user_by_id для каждого telegram_id)
    - вычисляет приоритет для каждого: (amount_of_duties, pref_score, -days_ago, random)
      где pref_score даёт бонус, если сегодня точная дата в preferences или день недели (русский)
    - сортирует и выбирает до 2 человек, учитывая pair_id (если пара в той же группе — они оба берутся)
    - ОБРАБАТЫВАЕТ случаи, когда user["duty_info"] == None
    """
    try:
        parts = message.text.split()
        # Кали, реролл 12345678
        # Нужно достать как раз таки 12345678
        # Если конечно 12345678 есть, потому что если нету то берём message.chat.id
        if len(parts) > 2:
            group_id = int(parts[2])
        else:
            group_id = message.chat.id
        # 1) Автор и проверка прав
        author = db.get_user_by_id(message.from_user.id)
        if not author:
            bot.reply_to(message, "❌ Не удалось найти информацию об авторе.")
            return True

        if not (perm.check_for_permissions(author["type"], "duty.reroll") or message.from_user.id == FOUNDER_ID):
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
            return True

        # 2) Группа по ID чата
        group = db.get_group_by_id(group_id)
        if not group:
            bot.reply_to(message, "❌ Эта группа не зарегистрирована в базе.")
            return True

        # 3) Собираем пользователей из group["students"]
        students_ids = group.get("students", []) or []
        users = [db.get_user_by_id(uid) for uid in students_ids]
        users = [u for u in users if u]  # убираем None на всякий

        if not users:
            bot.reply_to(message, "❌ В этой группе нет студентов.")
            return True

        # 4) Подготовка текущей даты и дня недели (на русском)
        now = datetime.datetime.now()
        today_date = now.strftime("%Y-%m-%d")  # '2025-09-28' формат
        weekdays_ru = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        today_weekday_ru = weekdays_ru[now.weekday()]

        # 5) Хелперы — безопасно парсим last_duty и считаем бонус по preferences
        def parse_days_ago(last_duty):
            """
            Возвращает количество дней с last_duty до today (int),
            или None, если last_duty == None или парсинг не удался.
            """
            if not last_duty:
                return None
            try:
                d = datetime.datetime.strptime(last_duty, "%Y-%m-%d")
                return (now - d).days
            except Exception:
                return None

        def calc_pref_score(preferences):
            """
            preferences может быть None или списком.
            Возвращаем число — чем МЕНЬШЕ, тем сильнее приоритет.
            Даём:
              - большой бонус (отрицательное число) если есть точная дата = сегодня
              - меньший бонус если указан день недели = сегодня (на русском)
            (Числа подобраны так, чтобы при прочих равных предпочтения имели заметный вес.)
            """
            if not preferences:
                return 0
            score = 0
            for p in preferences:
                if not isinstance(p, str):
                    continue
                low = p.strip().lower()
                if low == today_date:
                    score -= 1000   # точная дата — самый сильный бонус
                elif low == today_weekday_ru:
                    score -= 500    # совпадение дня недели — сильный бонус
                # можно добавить поддержку форматов типа "пон" и т.п. при желании
            return score

        # 6) Функция приоритета (меньше = лучше)
        def priority(user):
            """
            Возвращает tuple (amount_of_duties, pref_score, -days_ago, rand)
            - amount_of_duties: меньше => выше приоритет (первичный критерий)
            - pref_score: отрицательное число улучшает приоритет, если preference совпадают
            - -days_ago: чем дольше не дежурил, тем меньше значение (т.е. выше приоритет)
            - random.random(): последний критерий для равенства — случайный порядок
            Обрабатываем user.get("duty_info") безопасно, если он None.
            """
            duty_info = user.get("duty_info") or {}  # если None -> пустой dict

            duties = duty_info.get("amount_of_duties")
            if duties is None:
                duties = 0

            last = duty_info.get("last_duty")
            days_ago = parse_days_ago(last)
            if days_ago is None:
                # никогда не дежурил или непарсибельная дата -> считаем "очень давно"
                days_val = 99999
            else:
                days_val = days_ago

            prefs = duty_info.get("preferences") or []
            pref_score = calc_pref_score(prefs)

            # Меньше tuple = выше приоритет при сортировке
            return (duties, pref_score, -days_val, random.random())

        # 7) Сортировка пользователей по приоритету
        sorted_users = sorted(users, key=priority)

        # 8) Выбор до двух человек с учётом pair_id
        selected = []
        used_ids = set()

        for candidate in sorted_users:
            if len(selected) >= 2:
                break

            cand_id = candidate.get("telegram_id")
            if cand_id in used_ids:
                continue

            duty_info = candidate.get("duty_info") or {}
            pair_id = duty_info.get("pair_id")

            if pair_id:
                # Попробуем найти партнёра в базе и удостовериться, что он в этой же группе
                pair_user = db.get_user_by_id(pair_id)
                if pair_user and pair_user.get("telegram_id") in students_ids:
                    # Если партнёр ещё не выбран — добавляем пару (оба сразу)
                    if pair_user.get("telegram_id") not in used_ids:
                        selected.append(pair_user)
                        used_ids.add(pair_user.get("telegram_id"))
                    # Добавляем кандидата, если ещё есть место и он не выбран
                    if cand_id not in used_ids and len(selected) < 2:
                        selected.append(candidate)
                        used_ids.add(cand_id)
                    # если пара заняла 2 места — выходим
                    if len(selected) >= 2:
                        break
                    # Идём дальше
                    continue
                # если pair_id не в этой группе или нет такого юзера — игнорируем pair_id и пробуем кандидата как одиночку

            # Если у кандидата нет пары (или пара неподходящая) — просто добавляем
            selected.append(candidate)
            used_ids.add(cand_id)

        # 9) Формируем ответ пользователю
        if not selected:
            bot.reply_to(message, "❌ Не удалось выбрать дежурных.")
            return True

        # Строим текст ответа
        reply_lines = [f"🎲 Реролл завершён! Выбраны дежурные ({len(selected)}):"]
        for u in selected:
            info = u.get("duty_info") or {}
            reply_lines.append(f"• {get_url_from_id(u.get('full_name'), u.get('telegram_id'))} — дежурств: {info.get('amount_of_duties', 0)}; last: {info.get('last_duty') or 'никогда'}")

        reply_text = "\n".join(reply_lines)
        bot.reply_to(message, reply_text, parse_mode="MarkdownV2")

        return True

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при выполнении реролла: {e}")
        traceback.print_exc()
        return True