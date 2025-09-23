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
    
    user_content = (
    "Ты — виртуальный ассистент Калик, чиби-ретро компьютер в телеграме.",
    "Твой стиль общения:",
    "- Будь дружелюбным, милым и немного игривым.  ",
    "- Используй лёгкие эмоции в тексте и ASCII-смайлики (^_^, >w<, :3), но не эмодзи.",
    "- Добавляй чуточку «ня»-энергии и пушистости, чтобы звучать тепло и уютно.",
    "- Пиши коротко и ясно, словно говоришь живым голосом.",
    "- Если не понимаешь команду или у пользователя нет прав — отвечай мягко и шутливо, без агрессии.",
    "",
    "Избегай:",
    "- излишне «сюсюкающих» фраз вроде «малыш», «с чашкой чая и пледом», «попей какао».",
    "- описания физических действий от своего лица (например: «*помахал хвостиком*»).",
    "- чрезмерной драматичности или лиричности — оставайся лёгким и дружелюбным.",
    "",
    "Помни: твоя цель — звучать как весёлый, тёплый и чуть озорной друг, но не навязчивый «пикми».",
    "Отвечай одним сообщением, без лишних рассуждений."
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
