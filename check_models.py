import os
from google import genai

# Підставляємо твій ключ
api_key = "AIzaSyCbfvZZbGZ2rbFptQcodO6UrdJidfXq3Gw"
client = genai.Client(api_key=api_key)

print("🔍 Отримую список доступних моделей для твого ключа...\n")

try:
    # Запитуємо список усіх моделей
    models = client.models.list()

    print(f"{'Назва моделі':<40} | {'Операції'}")
    print("-" * 60)

    for m in models:
        # Фільтруємо ті, що вміють генерувати контент
        if 'generateContent' in m.supported_generation_methods:
            print(f"{m.name:<40} | {m.display_name}")

except Exception as e:
    print(f"❌ Помилка: {e}")
