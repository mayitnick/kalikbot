#  $$\   $$\          $$\ $$\           $$\             $$\ 
#  $$ | $$  |         $$ |\__|          $$ |            $$ |
#  $$ |$$  / $$$$$$\  $$ |$$\  $$$$$$$\ $$ |  $$\       $$ |
#  $$$$$  /  \____$$\ $$ |$$ |$$  _____|$$ | $$  |      $$ |
#  $$  $$<   $$$$$$$ |$$ |$$ |$$ /      $$$$$$  /       \__|
#  $$ |\$$\ $$  __$$ |$$ |$$ |$$ |      $$  _$$<            
#  $$ | \$$\\$$$$$$$ |$$ |$$ |\$$$$$$$\ $$ | \$$\       $$\ 
#  \__|  \__|\_______|\__|\__| \_______|\__|  \__|      \__|
#
# Created by: MayITNick

# Бот для техникума!

# Импортируем необходимые библиотеки
from telebot import types, TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import modules.gloris_integration as gloris
import modules.permissions as permissions
import modules.constants as constants
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
import traceback
import requests
import database
import random
import time
import os
import re
import importlib
import pkgutil
import commands

COMMANDS = []

for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
    module = importlib.import_module(f"commands.{module_name}")
    COMMANDS.append(module)

load_dotenv()

db = database.Database()
perm = permissions.Permissions()
CONSTANTS = constants.CONSTANTS()
bot = TeleBot(os.getenv('TOKEN'))
profanity_regex = re.compile(r"(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy][йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)(([зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*")

FOUNDER_ID = int(os.getenv('FOUNDER_ID'))

def check_for_kalik(message):
    text = message.text.lower().strip()
    # Ловим любой "зов", даже с командами
    # "Кал..."
    # К примеру - "Калииик, пинг"
    return bool(re.match(r"^кал[а-яё]*[,.!?]?\s*", text))

def get_url_from_id(full_name, id):
    # [Имя](tg://user?id=123456789)
    return f"[{full_name}](tg://user?id={id})"

def if_reply_to_message(message, user_id):
    if message.reply_to_message:
        reply_to_message_id = message.reply_to_message.from_user.id
        return db.get_user_by_id(reply_to_message_id), 1
    else:
        return db.get_user_by_id(int(user_id)), 0

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

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        bot_username = (bot.get_me()).username
        add_to_group_url = f"https://t.me/{bot_username}?startgroup=true"
        button1 = types.InlineKeyboardButton("Добавь меня в группу :3", url=add_to_group_url)
        markup.add(button1)
        bot.reply_to(message, "Привет! Я Калик, и мой функционал раскрывается только в группе!", reply_markup=markup)

@bot.message_handler(commands=['ping'])
def ping_command(message):
    bot.reply_to(message, "🏓 Поньг~")

@bot.message_handler(commands=['check'])
def check_admin_rights(message):
    # Получаем информацию о боте как о члене чата
    chat_id = message.chat.id
    bot_user_id = bot.get_me().id  # ID самого бота
    chat_member = bot.get_chat_member(chat_id, bot_user_id)
    
    # Проверяем статус и права
    if chat_member.status == 'administrator':
        rights = []
        if chat_member.can_post_messages:
            rights.append('Может публиковать сообщения')
        if chat_member.can_edit_messages:
            rights.append('Может редактировать сообщения')
        if chat_member.can_delete_messages:
            rights.append('Может удалять сообщения')
        if chat_member.can_invite_users:
            rights.append('Может приглашать пользователей')
        if chat_member.can_restrict_members:
            rights.append('Может ограничивать участников')
        if chat_member.can_pin_messages:
            rights.append('Может закреплять сообщения')
        if chat_member.can_promote_members:
            rights.append('Может назначать админов')
        print("Права:" + "\n".join(rights))
    else:
        print("Походу, у бота нет прав администратора в этом чате.")
    bot.send_message(chat_id, "Я проверил все модули, и вывел в консоль :)")

# Сделаем обработчик для всех сообщений
@bot.message_handler(func=lambda message: True)
def message_listener(message):
    # Запоминаем =3
    author = message.from_user
    last_name = author.last_name
    if not last_name:
        last_name = ""
    if not db.get_user_by_id(author.id):
        db.add_user(telegram_id=author.id,
                    telegram_username=author.username,
                    full_name=author.first_name + last_name)
    if check_for_kalik(message):
        kalik(message)
    
def kalik(message):
    text = message.text.lower()
    
    contains_profanity = bool(profanity_regex.search(text))
    if contains_profanity:
        bot.reply_to(message, "Я не люблю маты! 😡")
        return
    
    # 1. Сначала проверяем чистый зов
    from commands import call
    if call.handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID):
        return

    # 2. Потом остальные команды
    for cmd in COMMANDS:
        if any(alias in text for alias in getattr(cmd, "ALIASES", [])):
            cmd.handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID)
            return

    # 3. Если ничего не подошло
    bot.reply_to(message, random.choice(CONSTANTS.dont_know))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data
    if data.startswith("group."):
        if call.from_user.id == FOUNDER_ID:
            group_name = data.split(".")[1]
            group = db.get_group_by_name(group_name)
            # Доделать надо, я спать :|


me = bot.get_me()
print(f"Я запущен :3 У меня ник @{me.username} с id {me.id}.\nГотов помогать!")
try:
    bot.infinity_polling()
except requests.exceptions.ConnectionError:
    print("🌐 Ой, интернет потерялся... ищем снова 🦊")
except Exception as e:
    # на всякий случай ловим всё остальное
    print(f"⚠ Неожиданная ошибка: {e}")
