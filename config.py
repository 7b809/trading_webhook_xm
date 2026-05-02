import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TARGET_URL = os.getenv("TARGET_URL")
    API_KEY = os.getenv("API_KEY")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))

    @staticmethod
    def validate():
        if not Config.TARGET_URL:
            raise ValueError("TARGET_URL is missing in .env")
