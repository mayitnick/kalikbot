# 
#  $$$$$$\  $$$$$$\         $$\   $$\           $$\                               
#  \_$$  _|$$  __$$\        $$ |  $$ |          $$ |                              
#    $$ |  $$ /  \__|       $$ |  $$ | $$$$$$\  $$ | $$$$$$\   $$$$$$\   $$$$$$\  
#    $$ |  \$$$$$$\ $$$$$$\ $$$$$$$$ |$$  __$$\ $$ |$$  __$$\ $$  __$$\ $$  __$$\ 
#    $$ |   \____$$\\______|$$  __$$ |$$$$$$$$ |$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
#    $$ |  $$\   $$ |       $$ |  $$ |$$   ____|$$ |$$ |  $$ |$$   ____|$$ |      
#  $$$$$$\ \$$$$$$  |       $$ |  $$ |\$$$$$$$\ $$ |$$$$$$$  |\$$$$$$$\ $$ |      
#  \______| \______/        \__|  \__| \_______|\__|$$  ____/  \_______|\__|      
#                                                   $$ |                          
#                                                   $$ |                          
#                                                   \__|                          
# Created by: MayITNick!
# Copyright is zipped ;)
                                               
import os
from telebot import types, TeleBot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
FOUNDER_ID = os.getenv('FOUNDER_ID')

bot = TeleBot(TOKEN)

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
        bot.reply_to(message, f"Привет! Я добавлен в эту группу пользователем {message.from_user.first_name}!")

# ФУНКЦИИ
def callback_answer(call):
    # Сообщение "{user} нажал на инлайн кнопку!"
    # Если это группа, то отправить сообщение в группу
    if call.message.chat.type == 'group':
        bot.send_message(call.message.chat.id, "{user} нажал на инлайн кнопку!".format(call.from_user.first_name))
        return

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'add_to_group':
        callback_answer(call)
        bot.send_message(call.message.chat.id, "Тест")
    elif call.data == 'schedule':
        bot.answer_callback_query(call.id, "Расписание")
    else:
        bot.answer_callback_query(call.id, "Неизвестная команда")

@bot.my_chat_member_handler()
def handle_my_chat_member(update: types.ChatMemberUpdated):
    old_member = update.old_chat_member
    new_member = update.new_chat_member
    if new_member.status == 'member':
        user_id = update.from_user.id
        chat_id = new_member.chat.id
        chat_title = new_member.chat.title
        user_name = update.from_user.first_name
        bot.send_message(user_id, f"Я добавлен в группу '{chat_title}'!")
        bot.send_message(chat_id, f"Привет! Я добавлен в эту группу пользователем {user_name}!")

print("[DEBUG] Bot started")
bot.infinity_polling()
