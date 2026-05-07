import os
import storage
import brain
import painter
import requests
import json

def send_to_tg(image_bytes, car_data, chat_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    caption = f"🔥 <b>TURBO SHADOW #{car_data['id']:03}</b>\n\n" \
              f"🚗 <b>Модель:</b> {car_data['model']}\n" \
              f"📦 <b>Серія:</b> {car_data['series']}"
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("card.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
    response = requests.post(url, files=files, data=data)
    response.raise_for_status() 

def send_document_to_tg(image_bytes, model_name, chat_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    safe_name = "".join([c for c in model_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    files = {"document": (f"{safe_name}.png", image_bytes, "image/png")}
    try:
        response = requests.post(url, data={"chat_id": chat_id}, files=files)
        response.raise_for_status()
    except Exception as e:
        print(f"Помилка відправки документа: {e}")

def main():
    is_test = os.getenv("APP_MODE") == "test"
    chat_id = os.getenv("TELEGRAM_CHAT_ID_TEST") if is_test else os.getenv("TELEGRAM_CHAT_ID")
    
    if not chat_id:
        raise Exception("Не знайдено chat_id!")

    history = storage.load_history()
    theme_file = storage.get_today_file()
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
        
    car_data = brain.get_car_brainstorm(theme_data, history)
    car_data['series'] = theme_data['series']
    new_id = 999 if is_test else len(history) + 1
    car_data['id'] = new_id
    
    img_bytes = brain.generate_image(car_data['image_prompt'])
    final_card = painter.generate_card(car_data, img_bytes)
    
    send_to_tg(final_card, car_data, chat_id)
    send_document_to_tg(img_bytes, car_data['model'], chat_id)
    
    if not is_test:
        storage.save_to_history(car_data)
        print(f"Успішно опубліковано №{new_id}")

if __name__ == "__main__":
    main()
