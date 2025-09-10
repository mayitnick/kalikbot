#  $$\   $$\          $$\ $$\           $$\             $$\ 
#  $$ | $$  |         $$ |\__|          $$ |            $$ |
#  $$ |$$  / $$$$$$\  $$ |$$\  $$$$$$$\ $$ |  $$\       $$ |
#  $$$$$  /  \____$$\ $$ |$$ |$$  _____|$$ | $$  |      $$ |
#  $$  $$<   $$$$$$$ |$$ |$$ |$$ /      $$$$$$  /       \__|
#  $$ |\$$\ $$  __$$ |$$ |$$ |$$ |      $$  _$$<            
#  $$ | \$$\\$$$$$$$ |$$ |$$ |\$$$$$$$\ $$ | \$$\       $$\ 
#  \__|  \__|\_______|\__|\__| \_______|\__|  \__|      \__|
#
# Created by: MayITNick!

# Импортируем необходимые библиотеки       
import os
from telebot import types, TeleBot
from dotenv import load_dotenv
from database import Database

load_dotenv()

TOKEN = os.getenv('TOKEN')
FOUNDER_ID = os.getenv('FOUNDER_ID')

bot = TeleBot(TOKEN)
db = Database()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        bot_username = (bot.get_me()).username
        add_to_group_url = f"https://t.me/{bot_username}?startgroup=true"
        button1 = types.InlineKeyboardButton("Добавить в группу", url=add_to_group_url)
        markup.add(button1)
        bot.reply_to(message, "Привет! Я IS-Helper бот. Я здесь, чтобы помогать тебе с учебой.", reply_markup=markup)
    elif message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
        if chat_member.status in ['administrator', 'member']:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Учебные материалы", callback_data='materials')
            button2 = types.InlineKeyboardButton("Расписание", callback_data='schedule')
            markup.add(button1, button2)
            bot.reply_to(message, "Меню действий:", reply_markup=markup)

# Сделаем систему команд по позыву ("Джарвис, что ты умеешь?")
@bot.message_handler(content_types=['text'])
def nickname_commands(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Store user information
    db.add_or_update_user(user_id, username, first_name, last_name)
    
    text = message.text.lower()
    text = ''.join(e for e in text if e.isalnum() or e.isspace())
    if text.startswith('калик'):
        if 'что ты умеешь' in text or 'что ты можешь' in text:
            bot.reply_to(message, "Я Помощник Кали! Пока, я умею только запоминать вас ;)")
        elif 'все участники' in text:
            if message.chat.type in ['group', 'supergroup']:
                try:
                    members = db.get_all_users()
                    member_list = "\n".join([f"{member['id']} - {member['first_name']} {member['last_name'] if member['last_name'] else ''} (@{member['username'] if member['username'] else 'без ника'})" for member in members])
                    bot.reply_to(message, f"Участники группы:\n{member_list}")
                except Exception as e:
                    bot.reply_to(message, f"❌ Ошибка при получении списка участников: {e}")
            else:
                bot.reply_to(message, "❌ Эту команду можно использовать только в группе.")
        elif 'добавь его' in text:
            parts = message.text.split(" ")
            if len(parts) < 4:
                bot.reply_to(message, "❌ Укажи правильно: Калик, добавь его <ID/username/first_name> Фамилия Имя")
                return

            identifier = parts[3]
            surname = parts[4]
            name = parts[5] if len(parts) > 5 else ''

            try:
                user_id = int(identifier)
                db.add_student(user_id, name, surname, 16)  # Assuming age is 16 for simplicity
                bot.reply_to(message, f"✅ {surname} {name} добавлен в БД (id={user_id})")
            except ValueError:
                # Check if identifier is a username
                username = identifier
                if username.startswith('@'):
                    username = username[1:]  # Remove '@' from username
                user = db.get_user_by_username(username)
                if user:
                    db.add_student(user['id'], name, surname, 16)  # Assuming age is 16 for simplicity
                    bot.reply_to(message, f"✅ {surname} {name} добавлен в БД (id={user['id']}, @{username})")
                else:
                    # Check if identifier is a first_name
                    users = db.get_users_by_first_name(identifier)
                    if users:
                        # Suggest users to choose from
                        markup = types.InlineKeyboardMarkup()
                        for user in users:
                            button = types.InlineKeyboardButton(f"{user['first_name']} {user['last_name'] if user['last_name'] else ''} (@{user['username'] if user['username'] else 'без ника'})", callback_data=f"add_student_{user['id']}_{name}_{surname}")
                            markup.add(button)
                        bot.reply_to(message, f"Выберите пользователя:", reply_markup=markup)
                    else:
                        bot.reply_to(message, "❌ Пользователь не найден.")

# ФУНКЦИИ
def callback_answer(call):
    # Сообщение "{user} нажал на инлайн кнопку!"
    # Если это группа, то отправить сообщение в группу
    if call.message.chat.type == 'group':
        bot.send_message(call.message.chat.id, "{user} нажал на инлайн кнопку!".format(call.from_user.first_name))
        return

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Добавим обработку для callback_data=f"add_student_{user['id']}_{name}_{surname}"
    if call.data.startswith('add_student_'):
        if call.message.chat.type == 'group':
            parts = call.data.split('_')
            user_id = int(parts[1])
            name = parts[2]
            surname = parts[3]
            db.add_student(user_id, name, surname, 16)  # Assuming age is 16 for simplicity
            # Ответить на сообщение
            if call.message:
                bot.edit_message_text(text=f"✅ {surname} {name} добавлен в БД (id={user_id})",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)
    if call.data == 'add_to_group':
        callback_answer(call)
        bot.send_message(call.message.chat.id, "Тест")
    elif call.data == 'schedule':
        bot.answer_callback_query(call.id, "Расписание")
    else:
        bot.answer_callback_query(call.id, "Неизвестная команда")

@bot.my_chat_member_handler()
def handle_my_chat_member(update: types.ChatMemberUpdated):
    chat = update.chat
    old_member = update.old_chat_member
    new_member = update.new_chat_member
    if new_member.status == 'member' and old_member.status != 'member':
        chat_id = chat.id
        chat_title = chat.title
        user_name = update.from_user.first_name
        user_id = update.from_user.id
        bot.send_message(chat_id, f"Привет! Я добавлен в эту группу '{chat_title}' пользователем {user_name}!")
        try:
            bot.send_message(user_id, f"Я добавлен в группу '{chat_title}'!")
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")

print("[DEBUG] Bot started")
bot.infinity_polling()
