import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = int(os.getenv("FLASK_PORT", 5000))
    
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    DEFAULT_CHAT_ID = os.getenv("DEFAULT_CHAT_ID")

    TEST_LOG = os.getenv("TEST_LOG", "false").lower() == "true"