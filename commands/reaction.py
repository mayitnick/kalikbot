from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import requests
import dotenv
import os
from random import choice

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")


def send_react(chat_id, message_id, emoji):
    global TOKEN
    
    url = f'https://api.telegram.org/bot{TOKEN}/setMessageReaction'
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': [
            {
                'type': 'emoji',
                'emoji': emoji
            }
        ],
        'is_big': False
    }
    response = requests.post(url, json=data)
    result = response.json()

ALIASES = ["доброе утро"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    send_react(message.chat.id, message.message_id, "🔥")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
