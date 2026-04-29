import os
import requests

token = os.getenv("GH_MODELS_TOKEN")
endpoint = "https://models.inference.ai.azure.com/models"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(endpoint, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Тобі доступні такі моделі:")
    
    # Якщо сервер повернув прямий список
    if isinstance(data, list):
        for model in data:
            if isinstance(model, dict):
                print(f"- {model.get('name', model.get('id', 'Невідома модель'))}")
            else:
                print(f"- {model}")
                
    # Якщо сервер повернув словник (як очікувалося)
    elif isinstance(data, dict):
        for model in data.get("data", []):
            print(f"- {model.get('id', 'Невідома модель')}")
else:
    print(f"Помилка доступу: {response.text}")
