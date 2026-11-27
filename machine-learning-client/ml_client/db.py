"""Save every prediction to MongoDB."""

import os
from datetime import datetime, timezone

from pymongo import MongoClient


def get_collection():
    """The "predictions" collection, using MONGO_URI and MONGO_DBNAME."""
    client = MongoClient(
        os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        serverSelectionTimeoutMS=3000,
    )
    return client[os.getenv("MONGO_DBNAME", "rps")]["predictions"]


def save_prediction(collection, prediction):
    """Store one prediction with its time. Returns the saved document."""
    document = {
        "move": prediction["move"],
        "confidence": prediction["confidence"],
        "gesture": prediction["gesture"],
        "created_at": datetime.now(timezone.utc),
    }
    collection.insert_one(document)
    return document
