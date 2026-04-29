#// Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Hercai API без реєстрації).

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
    """Безкоштовна генерація через Hercai (без токенів і реєстрацій)."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    endpoint = f"https://hercai.onrender.com/v3/text2image?prompt={encoded_prompt}"
    
    print("Запит до Hercai API...")
    
    for attempt in range(3):
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                img_url = response.json().get('url')
                if img_url:
                    print(f"Картинка готова. Завантажуємо з {img_url}...")
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        return img_response.content
            print(f"Спроба {attempt+1} невдала. Чекаємо 5 сек...")
            time.sleep(5)
        except Exception as e:
            print(f"Помилка з'єднання: {e}")
            time.sleep(5)
            
    raise Exception("Не вдалося отримати картинку від Hercai після 3 спроб.")
