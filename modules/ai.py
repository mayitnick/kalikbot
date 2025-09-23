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
        f"Пользователь сказал: \"{text}\".\n"
        "Ты — телеграм-бот Калик, виртуальный чиби-компьютер. "
        "Отвечай дружелюбно, слегка иронично, без чрезмерной заботы. "
        "Можно вставлять лёгкие шуточки или ASCII-смайлики (^_^, (¬‿¬)), но не перебарщивай. "
        "Не упоминай слишком часто одни и те же образы (чай, плед, уют). Используй их только иногда. "
        "Старайся помогать по делу, но не будь сухим роботом. "
        "Не описывай действия (*махнул хвостиком* и т.п.), отвечай только текстом."
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
