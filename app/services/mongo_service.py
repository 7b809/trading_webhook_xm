from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]
collection = db[Config.COLLECTION_NAME]

def save_alert(data):
    return collection.insert_one(data)
