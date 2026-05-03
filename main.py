#// Responsibility: Головний керуючий скрипт. Збирає дані, запускає малювання та відправку в Telegram.
import os
import storage
import brain
import painter
import requests
import json

def send_to_tg(image_bytes, car_data, chat_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Використовуємо HTML для захисту від помилок із дефісами та дужками
    caption = f"🔥 <b>TURBO SHADOW #{car_data['id']:03}</b>\n\n" \
              f"🚗 <b>Модель:</b> {car_data['model']}\n" \
              f"📦 <b>Серія:</b> {car_data['series']}"
              
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("card.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
    
    response = requests.post(url, files=files, data=data)
    # Якщо Телеграм повертає помилку, скрипт зупиниться і не запише авто в базу
    response.raise_for_status() 

def send_document_to_tg(image_bytes, model_name, chat_id):
    """Відправка чистого фото файлом без втрати якості."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    # Очищуємо ім'я файлу від можливих спецсимволів
    safe_name = "".join([c for c in model_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    files = {"document": (f"{safe_name}.png", image_bytes, "image/png")}
    
    try:
        response = requests.post(url, data={"chat_id": chat_id}, files=files)
        response.raise_for_status()
        print(f"Оригінал {safe_name}.png відправлено документом.")
    except Exception as e:
        print(f"Помилка відправки документа (не критично): {e}")

def main():
    # Визначаємо режим роботи (Test або Prod)
    is_test = os.getenv("APP_MODE") == "test"
    
    if is_test:
        chat_id = os.getenv("TELEGRAM_CHAT_ID_TEST")
        print("🚀 ЗАПУСК У ТЕСТОВОМУ РЕЖИМІ")
    else:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    if not chat_id:
        raise Exception("Не знайдено chat_id! Перевір змінні TELEGRAM_CHAT_ID або TELEGRAM_CHAT_ID_TEST.")

    # 1. Завантажуємо налаштування та історію
    history = storage.load_history()
    theme_file = storage.get_today_file()
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
        
    # 2. Генеруємо тачку (Brainstorm)
    car_data = brain.get_car_brainstorm(theme_data, history)
    car_data['series'] = theme_data['series']
    
    # 3. Визначаємо ID (В тестовому режимі ставимо 999)
    new_id = 999 if is_test else len(history) + 1
    car_data['id'] = new_id
    
    # 4. Генеруємо фото та малюємо фантик
    img_bytes = brain.generate_image(car_data['image_prompt'])
    final_card = painter.generate_card(car_data, img_bytes)
    
    # 5. Публікація в Телеграм (спочатку фантик, потім оригінал)
    send_to_tg(final_card, car_data, chat_id)
    send_document_to_tg(img_bytes, car_data['model'], chat_id)
    
    # 6. Збереження в історію ТІЛЬКИ після успішного поста та ЯКЩО ЦЕ НЕ ТЕСТ
    if not is_test:
        storage.save_to_history(car_data)
        print(f"Успішно опубліковано фантик №{new_id}")
    else:
        print(f"Тестовий запуск завершено. Фантик №{new_id} відправлено в тест-канал. Історія не змінена.")

if __name__ == "__main__":
    main()
