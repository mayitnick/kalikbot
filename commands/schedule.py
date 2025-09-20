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

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> None:
    parts = message.text.split()
    # Калик, расписание ИС-11-25
    # Или просто Калик, расписание
    
    # Ещё проблема, что для gloris.get_schedule нужно указать день от 1 до 7, и это нужно определить по сегодняшнем дне недели
    date = datetime.weekday(datetime.now()) + 1 # Потому что datetime.weekday возвращает 0 для понедельника, а не 1
    if "сегодня" in message.text.lower():
        date = datetime.weekday(datetime.now()) + 1
    if "завтра" in message.text.lower():
        date = datetime.weekday(datetime.now() + timedelta(days=1)) + 1
    # так же пытаемся понимать типо "понедельник", "вторник" и т.д.
    if "понедельник" in message.text.lower():
        date = 1
    elif "вторник" in message.text.lower():
        date = 2
    elif "сред" in message.text.lower():
        date = 3
    elif "четверг" in message.text.lower():
        date = 4
    elif "пятниц" in message.text.lower():
        date = 5
    elif "суббот" in message.text.lower():
        bot.reply_to(message, CONSTANTS.no_saturday)
        return
    elif "воскресенье" in message.text.lower():
        bot.reply_to(message, CONSTANTS.no_sunday)
        return
    
    if len(parts) >= 3:
        try:
            group_id = gloris.name_to_id(parts[2]) # сюда пишем ИС-11-25
            schedule = gloris.get_schedule(date, group_id)
            if schedule:
                bot.reply_to(message, "<b>Расписание:</b>\n" + "\n".join(schedule), parse_mode="HTML")
                return
            else:
                bot.reply_to(message, CONSTANTS.schedule_not_found + "Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
                return
        except Exception as e:
            traceback.print_exc()
            bot.reply_to(message, CONSTANTS.error + "Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
            return
    else:
        # Пытаемся получить айди группы из БД
        chat_id = message.chat.id
        group = db.get_group_by_tg_group_id(chat_id)
        if group:
            try:
                group_id = group["gloris_id"]
                schedule = gloris.get_schedule(date, group_id)
                if schedule:
                    bot.reply_to(message, "<b>Расписание:</b>\n" + "\n".join(schedule), parse_mode="HTML")
                    return
                else:
                    bot.reply_to(message, CONSTANTS.schedule_not_found)
                    return
            except Exception as e:
                traceback.print_exc()
                bot.reply_to(message, CONSTANTS.error + " Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
                return
        else:
            bot.reply_to(message, CONSTANTS.tg_no_group + " Подсказка: надо писать в формате \"Калик, расписание группа деньнедели\"")
            return