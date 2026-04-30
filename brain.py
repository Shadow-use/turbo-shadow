# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Pollinations.ai через офіційний API).

import os
import requests
import json
import urllib.parse
import time

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою gpt-4o-mini."""
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/chat/completions"
    
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    
    system_msg = (
        "Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON. "
        "Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото)."
    )
    
    user_msg = (
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте."
    )

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }
    
    response = requests.post(endpoint, headers=headers, json={
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.8
    })
    
    if response.status_code != 200:
        raise Exception(f"Помилка текстового API: {response.text}")

    content = response.json()['choices'][0]['message']['content']
    clean_json = content.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def generate_image(image_prompt):
    """Генерує зображення через Pollinations.ai з використанням офіційного ключа."""
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise Exception("Не знайдено POLLINATIONS_API_KEY! Додай його в Secrets.")

    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k"
    encoded_prompt = urllib.parse.quote(full_prompt)
    endpoint = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    # Головна магія: передаємо твій ключ, щоб сервер знав, що ти не анонімний спамер
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    print("Запит до Pollinations.ai (через API-ключ)...")
    
    for attempt in range(3):
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Сервер зайнятий або помилка {response.status_code}. Чекаємо 5 секунд...")
            time.sleep(5)
            
    raise Exception("Не вдалося отримати картинку. Можливо, закінчився денний ліміт (Pollen).")
