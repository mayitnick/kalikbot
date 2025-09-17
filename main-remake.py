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
import database
import random
import time
import os
import re

load_dotenv()

db = database.Database()
perm = permissions.Permissions()
CONSTANTS = constants.CONSTANTS
bot = TeleBot(os.getenv('TOKEN'))

FOUNDER_ID = int(os.getenv('FOUNDER_ID'))

def check_for_kalik(message):
    text = message.text.lower().strip()
    # Теперь ловим любой "зов", даже с командами
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
    parts = message.text.split()
    text = message.text.lower().strip()
    # Проверяем, что это чисто зов (одно слово)
    is_only_kalik = bool(re.match(r"^кал[а-яё]*$", text))
    
    if is_only_kalik:
        bot.reply_to(message, random.choice(CONSTANTS["kalik_answers"]))
    elif "пинг" in message.text.lower():
        start = time.time()
        sent_msg = bot.send_message(message.chat.id, 'Пингую...')
        end = time.time()
        ping_ms = int((end - start) * 1000)
        bot.edit_message_text(f'Мой пинг: {ping_ms} мс. Хорошо считаю, правда? :3', chat_id=message.chat.id, message_id=sent_msg.message_id)
    elif "айди" in message.text.lower():
        # Узнаём айди по реплаю
        # А так же, пытаемся узнать по упоминанию
        # Третий аргумент - упоминание
        if "мой" in message.text.lower():
            bot.reply_to(message, f"Айди: {message.from_user.id}")
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
        bot.reply_to(message, 'Я тут)')
    elif "умеешь" in message.text.lower():
        bot.reply_to(message, 'Я пока мало что умею. Но я буду старатся учится, честно-честно!\nОбо мне можно прочитать на вики, где всё подробно расфыркано: https://vaylorm.github.io/kalikbot-docs/')
    elif "обо мне" in message.text.lower():
        user = db.get_user_by_id(message.from_user.id)
        if user:
            full_name = user["full_name"]
            bot.reply_to(message,
                            f"Информация о {get_url_from_id(full_name, message.from_user.id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
    elif "изменить имя" in message.text.lower():
        try:
            # пытаемся изменить имя у айди parts[3]
            user_id = int(parts[3])
            # parts[4] до последнего слова
            new_full_name = " ".join(parts[4:])
            user = db.get_user_by_id(user_id)
            db.update_user_field(user_id, "full_name", new_full_name)
            bot.reply_to(message, f"Имя студента {user['telegram_id']} изменено на {new_full_name}!")
        except:
            bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, изменить имя 12345678 Фамилия Имя". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
    elif "узнать о" in message.text.lower():
        try:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
            else:
                user_id = parts[3]
            author = db.get_user_by_id(message.from_user.id)
            if author:
                if perm.check_for_permissions(author["type"], f"see.other"):
                    # Дополнительная проверка на реплай
                    user, is_reply = if_reply_to_message(message, user_id)
                    if user:
                        full_name = user["full_name"]
                        bot.reply_to(message,
                                    f"Информация о {get_url_from_id(full_name, user_id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
                else:
                    if message.from_user.id == FOUNDER_ID:
                        user, is_reply = if_reply_to_message(message, user_id)
                        if user:
                            full_name = user["full_name"]
                            bot.reply_to(message,
                                        f"Инфа о {get_url_from_id(full_name, user_id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
                    bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
                    return
        except:
            bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, о нём 12345678". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
    elif "измени тип" in message.text.lower():
        try:
            # Калик, измени тип 12345678 student/elder/curator/admin
            # или
            # Калик, измени тип student/elder/curator/admin (с ответом на сообщение)
            user_id = parts[3]
            
            author = db.get_user_by_id(message.from_user.id)
            
            # Если есть ответ на сообщение
            user, is_reply = if_reply_to_message(message, user_id)
            
            # Если ответил на сообщение, то parts[3] - роль, если не ответил, то parts[4], т.к. parts[3] - это айди
            role = parts[3] if is_reply else parts[4]
            user_id = int(user_id) if not is_reply else message.reply_to_message.from_user.id
            
            if perm.check_for_permissions(author["type"], f"give.{role}"):
                if user:
                    db.update_user_field(user_id, "type", role)
                    bot.reply_to(message, f"Тип студента {user['telegram_id']} изменён на {role}!")
                else:
                    bot.reply_to("Пользователь не найден.")
            else:
                if message.from_user.id == FOUNDER_ID:
                    if user:
                        db.update_user_field(user_id, "type", role)
                        bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nТип студента {user['telegram_id']} изменён на {role}!")
                    else:
                        bot.reply_to(message, "Ты хоть и всемогущий, но я не нашёл пользователя ;(")
                else:
                    bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
        except Exception as e:
            bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, измени тип 12345678 student/elder/curator/admin". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
            traceback.print_exc()
    elif "в группу" in message.text.lower():
        try:
            # Калик, в группу 12345678 group_name
            # или
            # Калик, в группу group_name (с ответом на сообщение)
            user_id = parts[3]
            
            author = db.get_user_by_id(message.from_user.id)
            
            # Если есть ответ на сообщение
            user, is_reply = if_reply_to_message(message, user_id)
            
            group_name = parts[3] if is_reply else parts[4]
            user_id = int(user_id) if not is_reply else message.reply_to_message.from_user.id
            group = db.get_group_by_name(group_name)
            
            if perm.check_for_permissions(author["type"], f"group.invite"):
                if user:
                    # db.update_user_field(user_id, "group", group_name)
                    if group:
                        db.add_student(group_name, user_id)
                        bot.reply_to(message, f"Группа студента {user['telegram_id']} изменена на {group_name}!")
                    else:
                        bot.reply_to(message, f"Группа {group_name} не найдена.")
                else:
                    bot.reply_to("Пользователь не найден.")
            else:
                if message.from_user.id == FOUNDER_ID:
                    if user:
                        if group:
                            db.add_student(group_name, user_id)
                            bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nГруппа студента {user['telegram_id']} изменена на {group_name}!")
                        else:
                            bot.reply_to(message, f"Группа {group_name} не найдена.")
                    else:
                        bot.reply_to(message, "Ты хоть и всемогущий, но я не нашёл пользователя ;(")
                else:
                    bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
        except Exception as e:
            bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, в группу 12345678 group_name". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
            traceback.print_exc()
    elif "о группе" in message.text.lower():
        # Пытаемся узнать всех участников группы
        # Пока тестово, без проверки на права
        group_name = parts[3]
        group = db.get_group_by_name(group_name)
        if group:
            if message.from_user.id == FOUNDER_ID:
                # В группе в студентах хранятся только айди
                students = []
                for user in group["students"]:
                    user = db.get_user_by_id(user)
                    students.append(user)
                bot.reply_to(message, f"Группа {group['group']} состоит из {len(group['students'])} человек:\n{', '.join([get_url_from_id(user['full_name'], user['telegram_id']) for user in students])}")
            else:
                bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    elif "создать группу" in message.text.lower():
        author = db.get_user_by_id(message.from_user.id)
        if perm.check_for_permissions(author["type"], "group.create"):
            group_name = parts[3]
            if db.get_group_by_name(group_name):
                bot.reply_to(message, f"Группа {group_name} уже существует!")
            else:
                db.create_group(group_name)
                bot.reply_to(message, f"Группа {group_name} создана!")
        else:
            if message.from_user.id == FOUNDER_ID:
                group_name = parts[3]
                if db.get_group_by_name(group_name):
                    bot.reply_to(message, f"Группа {group_name} уже существует!")
                else:
                    db.create_group(group_name)
                    bot.reply_to(message, f"Группа {group_name} создана!")
            else:
                bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    elif "кик из группы" in message.text.lower():
        # Калик, кик из группы 12345678 group_name
        author = db.get_user_by_id(message.from_user.id)
        
        if perm.check_for_permissions(author["type"], f"group.kick"):
            user_id = parts[4]
            group_name = parts[5]
            user_id = int(user_id)
            group = db.get_group_by_name(group_name)
            if group:
                if user_id in group["users"]:
                    if db.remove_student(group_name, user_id):
                        bot.reply_to(message, f"Студент {user_id} успешно исключён из группы {group_name}!")
                    else:
                        bot.reply_to(message, f"Что-то пошло не так. Попробуйте ещё раз.")
    elif "группы" in message.text.lower():
        # Выведем все группы под сообщение как Inline кнопки
        if message.from_user.id == FOUNDER_ID:
            groups = db.get_all_groups()
            if groups:
                markup = InlineKeyboardMarkup()
                for group in groups:
                    markup.add(InlineKeyboardButton(text=group["group"], callback_data=f"group.{group['group']}"))
                bot.reply_to(message, "Выберите группу:", reply_markup=markup)
    elif "тг группа" in message.text.lower():
        # Калик, тг группа IS-11-25
        # Устанавливаем tg_group_id у группы на то, где было отправлено это сообщение
        if message.from_user.id == FOUNDER_ID:
            group_name = parts[3]
            group = db.get_group_by_name(group_name)
            if group:
                db.update_group_field(group_name, "tg_group_id", message.chat.id)
                bot.reply_to(message, f"ТГ группа для группы {group_name} успешно установлена!")
            else:
                bot.reply_to(message, f"Группа {group_name} не найдена.")
    elif "расписание" in message.text.lower():
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
            bot.reply_to(message, "В субботу мы не учимся :3")
        elif "воскресенье" in message.text.lower():
            bot.reply_to(message, "В воскресенье мы не учимся :3")
        
        if len(parts) >= 3:
            try:
                group_id = gloris.name_to_id(parts[2]) # сюда пишем ИС-11-25
                schedule = gloris.get_schedule(date, group_id)
                if schedule:
                    bot.reply_to(message, "Расписание:\n" + "\n".join(schedule))
                else:
                    bot.reply_to(message, "Расписание не было найдено. Проверьте правильность написания группы.")
            except Exception as e:
                traceback.print_exc()
                bot.reply_to(message, "Что-то пошло не так. Попробуйте ещё раз.")
        else:
            # Пытаемся получить айди группы из БД
            chat_id = message.chat.id
            group = db.get_group_by_tg_group_id(chat_id)
            if group:
                try:
                    group_id = group["gloris_id"]
                    schedule = gloris.get_schedule(date, group_id)
                    if schedule:
                        bot.reply_to(message, "Расписание:\n" + "\n".join(schedule))
                    else:
                        bot.reply_to(message, "Расписание не было найдено. Проверьте правильность написания группы.")
                except Exception as e:
                    traceback.print_exc()
                    bot.reply_to(message, "Что-то пошло не так. Попробуйте ещё раз.")
            else:
                bot.reply_to(message, "К сожалению, у вас не установлена ТГ группа. ")
            
            
    elif "помощь" in message.text.lower():
        bot.reply_to(message, "чем помочь? могу только тем, что есть в доках https://vaylorm.github.io/kalikbot-docs/")
    elif "создал" in message.text.lower():
        bot.reply_to(message, "Меня создал величайший VayLorm! Он же @MayITNick. Он меня наделил всеми теми репликами, которыми я обнимаю вас каждый день!\nВ общем, топ челик!")
    elif "пасхалка" in message.text.lower():
        bot.reply_to(message, "Всегда отдавай честь брату инженера!")
    elif "заполнитель" in message.text.lower():
        bot.reply_to(message, ".\n" * 30)
    else:
        bot.reply_to(message, random.choice(CONSTANTS["kalik_dontknow"]))

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
bot.infinity_polling()
