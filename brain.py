# Responsibility: Логіка запитів до ШІ-моделей. Вибір авто та генерація зображень.

import os
import requests
import json
import base64

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину, враховуючи список виключень."""
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/chat/completions"
    
    # Створюємо список назв, які вже були
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    
    system_msg = (
        "Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON. "
        "Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото)."
    )
    
    user_msg = (
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте."
    )

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(endpoint, headers=headers, json={
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.8
    })
    
    # Чистимо відповідь від маркдауну, якщо він є
    content = response.json()['choices'][0]['message']['content']
    clean_json = content.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def generate_image(image_prompt):
    """Генерує зображення та повертає байтовий рядок."""
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/images/generations" 
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "prompt": f"{image_prompt}, professional car photography, high resolution, clean background, 8k",
        "model": "black-forest-labs-flux-1-pro", # Якщо немає доступу, заміни на "stability-ai-sdxl-900"
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json"
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    res_json = response.json()
    
    if response.status_code != 200:
        raise Exception(f"API Error: {res_json}")

    try:
        # Обробка Base64
        if 'data' in res_json and 'b64_json' in res_json['data'][0]:
            return base64.b64decode(res_json['data'][0]['b64_json'])
        # Обробка URL
        elif 'data' in res_json and 'url' in res_json['data'][0]:
            return requests.get(res_json['data'][0]['url']).content
        else:
            raise KeyError(f"Unexpected response structure: {res_json.keys()}")
    except Exception as e:
        print(f"Failed to parse image data: {res_json}")
        raise e
