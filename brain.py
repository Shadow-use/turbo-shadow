# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Together AI - FLUX.1).

import os
import requests
import json
import base64

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
    """Генерує зображення через Together AI (модель FLUX.1-schnell)."""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise Exception("Не знайдено TOGETHER_API_KEY! Перевір Secrets.")

    endpoint = "https://api.together.xyz/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": f"{image_prompt}, high resolution car photography, professional lighting, 8k",
        "width": 1024,
        "height": 1024,
        "steps": 4,
        "n": 1,
        "response_format": "b64_json"
    }

    print("Запит до Together AI (FLUX.1-schnell)...")
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Помилка Together AI: {response.status_code} - {response.text}")

    # Together повертає картинку закодовану в base64, декодуємо її в байти
    img_b64 = response.json()["data"][0]["b64_json"]
    return base64.b64decode(img_b64)
