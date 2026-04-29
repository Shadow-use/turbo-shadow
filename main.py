#// Responsibility: Головний керуючий скрипт. Збирає дані, запускає малювання та відправку в Telegram.

import os
import storage
import brain
import painter
import requests

def send_to_tg(image_bytes, car_data):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    caption = f"🔥 *TURBO SHADOW #{car_data['id']:03}*\n\n" \
              f"🚗 *Модель:* {car_data['model']}\n" \
              f"📦 *Серія:* {car_data['series']}"
              
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("card.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
    
    requests.post(url, files=files, data=data)

def main():
    # 1. Завантажуємо налаштування та історію
    history = storage.load_history()
    theme_file = storage.get_today_file()
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
        
    # 2. Генеруємо тачку (Brainstorm)
    car_data = brain.get_car_brainstorm(theme_data, history)
    car_data['series'] = theme_data['series']
    
    # 3. Зберігаємо в історію (отримуємо ID)
    new_id = storage.save_to_history(car_data)
    car_data['id'] = new_id
    
    # 4. Генеруємо фото та малюємо фантик
    img_bytes = brain.generate_image(car_data['image_prompt'])
    final_card = painter.generate_card(car_data, img_bytes)
    
    # 5. Публікація
    send_to_tg(final_card, car_data)
    print(f"Успішно опубліковано фантик №{new_id}")

if __name__ == "__main__":
    main()
