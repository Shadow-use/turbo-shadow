# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Hugging Face).

import os
import requests
import json
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
    """Генерує зображення через стабільний API Hugging Face."""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise Exception("Не знайдено HF_TOKEN! Перевір Secrets у GitHub та файл production.yml.")
        
    # Використовуємо стабільну модель SDXL
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    payload = {
        "inputs": f"{image_prompt}, high resolution car photography, professional lighting, 8k",
    }
    
    for attempt in range(5):
        print(f"Запит до Hugging Face (спроба {attempt + 1})...")
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            # Модель може "прокидатися", це нормальна поведінка
            estimated_time = response.json().get('estimated_time', 20)
            print(f"Модель завантажується. Чекаємо {estimated_time} секунд...")
            time.sleep(estimated_time)
        else:
            print(f"Помилка сервера: {response.status_code} - {response.text}")
            time.sleep(10)
            
    raise Exception("Hugging Face API не зміг згенерувати картинку після 5 спроб.")
