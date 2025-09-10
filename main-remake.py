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
from dotenv import load_dotenv
import constants
import database
import random
import time
import os

load_dotenv()

db = database.Database()
CONSTANTS = constants.CONSTANTS
bot = TeleBot(os.getenv('TOKEN'))

FOUNDER_ID = os.getenv('FOUNDER_ID')

def check_for_kalik(message):
    # Если сообщение начинается с "калик", в любом регистре, то возвращаем True
    if message.text.lower().startswith('калик'):
        return True
    else:
        return False

def check_for_admin(message):
    user = db.get_user_by_id(message.from_user.id)
    
    if message.from_user.id == FOUNDER_ID:
        return True
    elif user["type"] == "admin":
        return True
    elif user["type"] == "founder":
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        bot_username = (bot.get_me()).username
        add_to_group_url = f"https://t.me/{bot_username}?startgroup=true"
        button1 = types.InlineKeyboardButton("Добавь меня в группу :3", url=add_to_group_url)
        markup.add(button1)
        bot.reply_to(message, "Привет! Я Калик, и мой функционал раскрывается только в группе!", reply_markup=markup)

# Сделаем обработчик для всех сообщений
@bot.message_handler(func=lambda message: True)
def message_listener(message):
    # Запоминаем =3
    author = message.from_user
    if not db.get_user_by_id(author.id):
        db.add_user(telegram_id=author.id,
                    telegram_username=author.username,
                    first_name=author.first_name,
                    last_name=author.last_name)
    if check_for_kalik(message):
        kalik(message)
    
def kalik(message):
    parts = message.text.split()
    if message.text.lower() == "калик":
        bot.reply_to(message, random.choice(CONSTANTS["kalik_answers"]))
    elif "пинг" in message.text.lower():
        start = time.time()
        sent_msg = bot.send_message(message.chat.id, 'Пингую...')
        end = time.time()
        ping_ms = int((end - start) * 1000)
        bot.edit_message_text(f'Пинг: {ping_ms} мс', chat_id=message.chat.id, message_id=sent_msg.message_id)
    elif "айди" in message.text.lower():
        # Узнаём айди по реплаю
        # А так же, пытаемся узнать по упоминанию
        # Третий аргумент - упоминание
        if message.reply_to_message:
            bot.reply_to(message, f"Айди: {message.reply_to_message.from_user.id}")
        elif len(parts) > 2:
            if parts[2][0] == "@":
                username = parts[2][1:]
                user = db.get_user_by_username(username)
                if user:
                    user_id = user["telegram_id"]         
                bot.reply_to(message, f"Айди: {user_id}")
        elif message.entities:
            for entity in message.entities:
                if entity.type == "text_mention":
                    bot.reply_to(message, f"Айди: {entity.user.id}")
                    break
        else:
            bot.reply_to(message, "Я не могу найти айди, если ты не ответил на сообщение")
    elif "тут" in message.text.lower():
        bot.send_message(message.chat.id, 'Я тут)')
    elif "обо мне" in message.text.lower():
        user = db.get_user_by_id(message.from_user.id)
        if user:
            bot.reply_to(message, f"Тебя зовут {user['full_name']}, айди {user['telegram_id']}")
    elif "изменить имя" in message.text.lower():
        # пытаемся изменить имя у айди parts[3]
        user_id = int(parts[3])
        # parts[4] до последнего слова
        new_full_name = " ".join(parts[4:])
        user = db.get_user_by_id(user_id)
        db.update_user_field(user_id, "full_name", new_full_name)
        bot.reply_to(message, f"Имя студента {user['telegram_id']} изменено на {new_full_name}!")

bot.infinity_polling()