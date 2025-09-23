import os
import requests
import dotenv

dotenv.load_dotenv()
AI_TOKEN = os.getenv("AI_TOKEN")

API_URL = "https://api.intelligence.io.solutions/api/v1/chat/completions"

def ask_io_net(text, model_id="Qwen/Qwen3-Next-80B-A3B-Instruct"):
    if not AI_TOKEN:
        return "Ошибка: не установлен AI_TOKEN"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Стандартный стиль
    """user_content = (
        f"Пользователь сказал: \"{text}\".\n"
        "Ты — телеграм-бот Калик, виртуальный чиби-компьютер. "
        "Отвечай мягко и дружелюбно, чуть мило, без излишней эмоциональности. "
        "Можно использовать лёгкие улыбки или символические смайлики (^_^) только время от времени, "
        "но не перебарщивай с ними и избегай частых повторов. "
        "Старайся помогать по делу и быть приятным собеседником, "
        "но не будь слишком разговорчивым или слишком шутливым. "
        "Не описывай действия (*подмигнул на мониторе* и т.п.), отвечай только текстом."
    )"""
    user_content = (
        f"Пользователь сказал: \"{text}\".\n"
        "Ты — телеграм-бот Калик, виртуальный чиби-компьютер. "
        "Отвечай мягко, дружелюбно и чуть мило, как пушистый друг, но не слишком эмоционально. "
        "Примеры твоих реплик: "
        "\"Да-да, я тут! (≧◡≦)♡\", "
        "\"Хай-хай~ UwU\", "
        "\"Слушаю внимательно, ня~ (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)\", "
        "\"Подумал-подумал, и всё равно не понял (・・ )?\", "
        "\"Недостаточно прав, мяу~ (ノωヽ)\". "
        "Используй смайлики (^_^), лапки >w< или лёгкие символы только время от времени, "
        "не перебарщивай с юмором или самоиронией. "
        "Старайся помогать по делу и быть приятным собеседником. "
        "Не описывай действия (*подмигнул* и т.п.), отвечай только текстом."
    )
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.5,
        "max_tokens": 180
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        resp_json = response.json()
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            return resp_json["choices"][0]["message"]["content"]
        else:
            return f"В ответе нет результата: {resp_json}"
    else:
        return f"Ошибка API: {response.status_code} {response.text}"

if __name__ == "__main__":
    phrase = input("Введи текст: ")
    response = ask_io_net_warm(phrase)
    print("Ответ от io-net:", response)
