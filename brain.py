// Responsibility: Логіка запитів до ШІ-моделей для вибору авто та генерації промпту для зображення.

import os
import requests
import json

def get_car_brainstorm(theme_data, history):
    """
    Запитує у LLM нову машину, враховуючи список виключень.
    """
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/chat/completions"
    
    # Формуємо список виключень із назв моделей в історії
    excluded_models = ", ".join([item['model'] for item in history])
    
    system_message = (
        "Ти — автомобільний куратор проекту Turbo Shadow. "
        "Твоя відповідь має бути строго в форматі JSON. "
        "Поля: model (марка та модель), specs (об'єкт з engine, hp, top_speed), "
        "image_prompt (детальний опис для генерації фото)."
    )
    
    user_message = (
        f"Тема: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"СПИСОК ВИКЛЮЧЕННЯ (ЦЕ ВЖЕ БУЛО, НЕ ОБИРАЙ): [{excluded_models}]\n"
        "Обери щось нове та незвичайне. Назва моделі — до 35 символів."
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "model": "gpt-4o-mini", # Текстова модель для логіки
        "temperature": 0.9 # Підвищуємо креативність
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    # Тут буде обробка JSON-відповіді
    return response.json()
