import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    FILTER_TICKER = os.getenv("FILTER_TICKER")
    FILTER_NAMES = os.getenv("FILTER_NAMES", "")