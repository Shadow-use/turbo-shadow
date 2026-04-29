# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Pollinations.ai).
import os
import requests
import json
import urllib.parse
import time

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою gpt-4o-mini, враховуючи історію."""
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
    """Генерує зображення через Pollinations із маскуванням під браузер та повторенням при 429."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k"
    encoded_prompt = urllib.parse.quote(full_prompt)
    endpoint = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    # Маскуємося під звичайний Chrome на Windows, щоб обійти фільтри ботів
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Робимо до 3 спроб з паузою
    for attempt in range(3):
        print(f"Запит до Pollinations.ai (спроба {attempt + 1})...")
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 429:
            print("Сервер Pollinations перевантажений (Помилка 429). Чекаємо 10 секунд...")
            time.sleep(10)
        else:
            raise Exception(f"Помилка генерації картинки: {response.status_code} - {response.text}")
            
    # Якщо всі 3 спроби провалилися
    raise Exception("Не вдалося згенерувати картинку після 3 спроб. Сервер Pollinations відхиляє запити.")
