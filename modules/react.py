import dotenv
import os
from random import choice
import requests

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