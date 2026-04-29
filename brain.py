# Responsibility: Логіка запитів до ШІ-моделей. Підтримка форматів URL та Base64.

import os
import requests
import json
import base64

def generate_image(image_prompt):
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/images/generations" 
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Використовуємо FLUX-pro або SDXL. Вони стабільні.
    payload = {
        "prompt": f"{image_prompt}, high resolution car photography, professional lighting, 8k",
        "model": "black-forest-labs-flux-1-pro", # Переконайся, що ця модель доступна в Marketplace
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json" # Явно просимо Base64, це надійніше для GitHub
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    res_json = response.json()
    
    if response.status_code != 200:
        raise Exception(f"Помилка API: {res_json}")

    try:
        # Перевіряємо, чи прийшов Base64 (стандарт для FLUX/SDXL на GitHub)
        if 'data' in res_json and 'b64_json' in res_json['data'][0]:
            img_b64 = res_json['data'][0]['b64_json']
            return base64.b64decode(img_b64)
            
        # Якщо все ж таки прийшов URL (як у DALL-E)
        elif 'data' in res_json and 'url' in res_json['data'][0]:
            img_url = res_json['data'][0]['url']
            return requests.get(img_url).content
            
        else:
            raise KeyError(f"Невідомий формат відповіді: {list(res_json.keys())}")
            
    except Exception as e:
        print(f"Критична помилка обробки зображення: {res_json}")
        raise e
