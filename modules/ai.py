import os
import requests
import dotenv

dotenv.load_dotenv()
AI_TOKEN = os.getenv("AI_TOKEN")

API_URL = "https://api.intelligence.io.solutions/api/v1/chat/completions"
MODELS_URL = "https://api.intelligence.io.solutions/api/v1/models"

# Текущая выбранная модель
current_model = "Qwen/Qwen3-Next-80B-A3B-Instruct"

def ask_io_net(text):
    if not AI_TOKEN:
        return "Ошибка: не установлен AI_TOKEN"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }

    user_content = (
        f"Пользователь сказал: \"{text}\".\n"
        "Ты — телеграм-бот Калик, виртуальный чиби-компьютер. "
        "Общайся в том же стиле, что и твои стандартные реплики вроде: "
        "\"Да-да, я тут! (≧◡≦)♡\", "
        "\"Хай-хай~ UwU\", "
        "\"Недостаточно прав, мяу~ (ノωヽ)\". "
        "Когда объясняешь что-то сложное, делай это простыми словами, короткими абзацами, "
        "будто дружелюбный друг рассказывает по шагам. "
        "Можно добавлять лёгкие междометия или мягкие вставки (ня~, >w<, ^_^), "
        "но не перегружай ими текст. "
        "Старайся звучать естественно и тепло, чуть игриво, но всегда по делу. "
        "Не описывай действия (*подмигнул* и т.п.), отвечай только текстом."
    )
    
    data = {
        "model": current_model,
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
        return f"Ошибочка в API вышла: {response.status_code} {response.text}"


def list_models():
    if not AI_TOKEN:
        return ["Ошибка: не установлен AI_TOKEN"]

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}"
    }

    response = requests.get(MODELS_URL, headers=headers)
    if response.status_code == 200:
        resp_json = response.json()
        return [m["id"] for m in resp_json.get("data", [])]
    else:
        return [f"Ошибка: {response.status_code} {response.text}"]


def set_model(model_id: str):
    global current_model
    current_model = model_id
    return current_model
