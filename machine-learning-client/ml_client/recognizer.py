"""Load MediaPipe's gesture recognizer and run it on a photo."""

import pathlib
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

from ml_client.gestures import move_from_gesture, move_from_landmarks

MODELS_DIR = pathlib.Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODELS_DIR / "gesture_recognizer.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
    "gesture_recognizer/float16/latest/gesture_recognizer.task"
)


def ensure_model(path=MODEL_PATH, download=urllib.request.urlretrieve):
    """Download the model file the first time, then reuse it."""
    path = pathlib.Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        download(MODEL_URL, str(path))
    return path


def create_recognizer(path=MODEL_PATH):
    """Build a gesture recognizer that works on single photos."""
    options = vision.GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=str(ensure_model(path))),
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
    )
    return vision.GestureRecognizer.create_from_options(options)


def decode_image(image_bytes):
    """Turn JPEG, PNG or WebP bytes into a MediaPipe image, or None if unreadable."""
    pixels = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if pixels is None:
        return None
    rgb = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)


def read_result(result):
    """Pull the move and confidence out of a recognizer result.

    Returns a dict with move ("rock", "paper", "scissors", "unknown" or "no_hand"),
    confidence, and the raw gesture name for the database.
    """
    if not result.hand_landmarks:
        return {"move": "no_hand", "confidence": 0.0, "gesture": None}

    top = result.gestures[0][0] if result.gestures and result.gestures[0] else None
    gesture = top.category_name if top else None
    move = move_from_gesture(gesture)
    if move:
        return {"move": move, "confidence": round(top.score, 3), "gesture": gesture}

    # the model saw a hand but not one of its three gestures, so try the finger rule
    backup = move_from_landmarks(result.hand_landmarks[0])
    hand_score = result.handedness[0][0].score if result.handedness else 0.0
    return {
        "move": backup or "unknown",
        "confidence": round(hand_score, 3) if backup else 0.0,
        "gesture": gesture,
    }


def predict(recognizer, image_bytes):
    """Run the whole pipeline on raw photo bytes. Returns None for unreadable images."""
    image = decode_image(image_bytes)
    if image is None:
        return None
    return read_result(recognizer.recognize(image))
