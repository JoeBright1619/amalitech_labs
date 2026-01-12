import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoLogger, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        try:
            self.client = MongoClient(
                os.getenv("MONGO_URI", "mongodb://localhost:27017")
            )
            self.db = self.client[os.getenv("MONGO_DB", "activity_logs")]
            self.collection = self.db["logs"]
            print("MongoDB client initialized.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None

    def log_activity(self, activity):
        if self.client:
            return self.collection.insert_one(activity)
        return None


mongo_logger = MongoLogger()
