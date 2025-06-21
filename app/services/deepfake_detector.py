# app/services/deepfake_detector.py (FIXED: KAGGLE_MODEL_HANDLE)
import numpy as np
from typing import List, Tuple
import os
import tensorflow as tf

import kagglehub

# --- KaggleHub Configuration ---
# The CORRECT handle for the Kaggle model variation you want to use
KAGGLE_MODEL_HANDLE = "ameencaslam/ddp-v4-models/tensorflow/ddpv4-resnet50-finetuned"
MODEL_FILE_NAME = "ddpv4_resnet50_finetuned.h5" # This remains correct for the .h5 file

# --- Model Configuration ---
MODEL_INPUT_SIZE = (224, 224) # A common size, adjust if your model needs something else
DEEPFAKE_THRESHOLD = 0.5 # Confidence threshold to classify as deepfake (tune this!)

# Global variable to store the loaded model
deepfake_model = None

def load_deepfake_model():
    """Loads the deepfake detection model from KaggleHub."""
    global deepfake_model
    if deepfake_model is None:
        print(f"Loading deepfake model '{MODEL_FILE_NAME}' from KaggleHub '{KAGGLE_MODEL_HANDLE}'...")
        try:
            local_model_path = kagglehub.model_download(KAGGLE_MODEL_HANDLE, MODEL_FILE_NAME)
            print(f"Model downloaded/found at local path: {local_model_path}")

            deepfake_model = tf.keras.models.load_model(local_model_path)

            print("Deepfake model loaded successfully.")
        except Exception as e:
            # Catch the more specific ValueError from kagglehub and re-raise as IOError
            raise IOError(f"Failed to load deepfake model from KaggleHub: {e}")
    return deepfake_model

async def detect_deepfake_in_frames(
    faces: List[np.ndarray]
) -> Tuple[str, float]:
    """
    Performs deepfake detection on a list of extracted face images using the loaded ML model.
    """
    if not faces:
        return "No Faces Detected", 0.0

    model = load_deepfake_model()

    print(f"Performing deepfake inference on {len(faces)} faces...")

    face_batch = np.array(faces)

    predictions = model.predict(face_batch)

    fake_probabilities = predictions.flatten()
    avg_fake_prob = np.mean(fake_probabilities)

    if avg_fake_prob >= DEEPFAKE_THRESHOLD:
        result = "Deepfake Detected"
        confidence = float(avg_fake_prob)
    else:
        result = "Real Video"
        confidence = float(1.0 - avg_fake_prob)

    print(f"Deepfake detection result: {result} with confidence {confidence:.2f}")
    return result, confidence