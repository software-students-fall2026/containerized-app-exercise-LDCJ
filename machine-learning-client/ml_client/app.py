"""Flask server the web app calls with a hand photo."""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo.errors import PyMongoError

from ml_client import db, recognizer


def create_app(gesture_recognizer=None, collection=None):
    """Create the app. Tests pass in a fake recognizer and collection."""
    app = Flask(__name__)
    state = {"recognizer": gesture_recognizer, "collection": collection}

    def get_recognizer():
        if state["recognizer"] is None:
            state["recognizer"] = recognizer.create_recognizer()
        return state["recognizer"]

    def get_collection():
        if state["collection"] is None:
            state["collection"] = db.get_collection()
        return state["collection"]

    @app.get("/health")
    def health():
        """Quick check that the server is up."""
        return jsonify(status="ok")

    @app.post("/predict")
    def predict():
        """Read the photo in the "image" field and reply with the move."""
        image = request.files.get("image")
        image_bytes = image.read() if image else b""
        if not image_bytes:
            return jsonify(error="Send a photo in the 'image' field."), 400

        prediction = recognizer.predict(get_recognizer(), image_bytes)
        if prediction is None:
            return jsonify(error="Could not read that image."), 400

        try:
            db.save_prediction(get_collection(), prediction)
        except PyMongoError:
            app.logger.exception("Could not save prediction")

        if prediction["move"] == "no_hand":
            return jsonify(error="No hand found in the photo."), 422
        return jsonify(move=prediction["move"], confidence=prediction["confidence"])

    return app


if __name__ == "__main__":
    load_dotenv()
    create_app().run(host="0.0.0.0", port=int(os.getenv("ML_CLIENT_PORT", "8000")))
