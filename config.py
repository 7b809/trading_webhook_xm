import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TARGET_BASE_URL = os.getenv("TARGET_BASE_URL")
