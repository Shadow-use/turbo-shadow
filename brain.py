# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Pollinations.ai з обходом 429).

import os
import requests
import json
import urllib.parse
import time
import random

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
    """Генерує зображення через Pollinations із розумним скиданням таймера."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # Додаємо рандомний seed, щоб кожен запит був унікальним
    seed = random.randint(1, 100000)
    endpoint = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    # Маскуємося під браузер, який прийшов з їхнього ж сайту
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://pollinations.ai/",
    }
    
    # Хитрість №1: Чекаємо випадкові 5-15 секунд, щоб пропустити спам від чужих ботів
    delay = random.randint(5, 15)
    print(f"Маскування: чекаємо {delay} сек перед генерацією...")
    time.sleep(delay)
    
    for attempt in range(3):
        print(f"Запит до Pollinations.ai (спроба {attempt + 1})...")
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 429:
            # Хитрість №2: Якщо IP заблоковано, чекаємо 65 секунд (їхній ліміт обнуляється кожну хвилину)
            print("Зловили 429 (таймер IP). Лягаємо на дно на 65 секунд...")
            time.sleep(65)
        else:
            print(f"Помилка {response.status_code}. Чекаємо 10 сек...")
            time.sleep(10)
            
    raise Exception("Pollinations не пустив навіть після скидання таймера.")
