# Responsibility: Тестовий запуск Turbo Shadow з дрифтовим ЗАЗ-968М.

import os
import requests

def send_to_tg(caption):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Для тесту використовуємо пряме посилання на зображення (потім замінимо на генерацію)
    photo_url = "https://raw.githubusercontent.com/Shadow/turbo-shadow/main/1777472333203.png" # Це шлях до твого завантаженого фото, якщо назва збігається

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}

    r = requests.post(url, data=data)
    print(r.json())

if __name__ == "__main__":
    text = (
        "*TURBO SHADOW #1*\n\n"
        "*Модель:* ZAZ-968M 'Cossack Drift-Spec'\n"
        "*Двигун:* 1.3L Turbo (Hayabusa)\n"
        "*Потужність:* 380 к.с.\n"
        "*Фішка:* Кастомна рама та ліврея мілітарі-камо."
    )
    send_to_tg(text)
  
