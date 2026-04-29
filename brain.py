#// Responsibility: Запити до GitHub Models для генерації тексту (GPT-4o) та зображення (Flux/SDXL).

import os
import requests
import json
import time

def get_car_brainstorm(theme_data, history):
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/chat/completions"
    
    excluded = ", ".join([item['model'] for item in history[-20:]]) # Останні 20, щоб не перевантажувати промпт
    
    system_msg = "Ти — авто-експерт Turbo Shadow. Відповідь ТІЛЬКИ в JSON: {'model': '...', 'specs': {'engine': '...', 'hp': '...', 'top_speed': '...'}, 'image_prompt': '...'}"
    user_msg = f"Тема: {theme_data['series']}. {theme_data['ai_instruction']}. НЕ ОБИРАЙ: {excluded}. Модель до 30 симв."

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 1. Текст
    response = requests.post(endpoint, headers=headers, json={
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        "model": "gpt-4o-mini",
        "temperature": 0.9
    })
    
    # Очистка відповіді від можливих markdown-тегів
    raw_res = response.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
    return json.loads(raw_res)

def generate_image(image_prompt):
    token = os.getenv("GH_MODELS_TOKEN")
    # Використовуємо FLUX або SDXL для чистого фото без міток
    endpoint = "https://models.inference.ai.azure.com/images/generations" 
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "prompt": f"{image_prompt}, professional car photography, high resolution, no text, no watermarks, realistic lighting",
        "model": "flux-pro", # Або інша доступна модель у GitHub Models
        "n": 1,
        "size": "1024x1024"
    }
    
    # УВАГА: Тут може знадобитися адаптація під конкретний API GitHub Models (вони іноді міняють endpoint)
    response = requests.post(endpoint, headers=headers, json=payload)
    img_url = response.json()['data'][0]['url']
    return requests.get(img_url).content
