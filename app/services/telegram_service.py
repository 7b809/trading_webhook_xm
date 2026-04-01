import requests
from app.config import Config

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    return response.json()
