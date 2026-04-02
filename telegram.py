import requests
from config import Config
from logger import logger  # ✅ added logger

def send_telegram_message(text, chat_id=None):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

    final_chat_id = chat_id or Config.DEFAULT_CHAT_ID

    payload = {
        "chat_id": final_chat_id,
        "text": text
    }

    try:
        logger.info(f"📤 Sending Telegram message to {final_chat_id}: {text}")

        response = requests.post(url, json=payload)

        # ✅ check response
        try:
            res_json = response.json()
        except Exception:
            logger.error(f"❌ Telegram response not JSON: {response.text}")
            return None

        if res_json.get("ok"):
            logger.info(f"✅ Telegram API success")
        else:
            logger.error(f"❌ Telegram API failed: {res_json}")

        return res_json

    except Exception as e:
        logger.error(f"❌ Telegram Exception: {e}")
        return None