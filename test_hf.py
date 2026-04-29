import os
import requests

token = os.getenv("HF_TOKEN")
if not token:
    print("Помилка: Не знайдено змінну HF_TOKEN.")
    exit()

headers = {"Authorization": f"Bearer {token}"}
payload = {"inputs": "a cool sports car, cinematic lighting, 8k"}

# Список найпопулярніших відкритих моделей для перевірки
models_to_test = [
    "prompthero/openjourney",
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-2-1",
    "CompVis/stable-diffusion-v1-4",
    "SG161222/Realistic_Vision_V1.4",
    "stabilityai/stable-diffusion-3.5-large"
]

print("Починаємо перевірку моделей на Hugging Face...\n")

for model in models_to_test:
    url = f"https://api-inference.huggingface.co/models/{model}"
    print(f"Тестуємо: {model}")
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        
        if res.status_code == 200:
            print("✅ ПРАЦЮЄ! (Модель готова віддавати картинки)")
        elif res.status_code == 503:
            print("⏳ ПРАЦЮЄ! (Модель спить, але доступ є. Вона прокинеться при запиті)")
        else:
            print(f"❌ Відмова ({res.status_code}): {res.text[:100]}...")
            
    except Exception as e:
        print(f"❌ Помилка з'єднання: {e}")
        
    print("-" * 40)
