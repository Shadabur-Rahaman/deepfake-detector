# app/services/deepfake_detector.py (FINAL PLAN: Keras Applications Model)
import numpy as np
from typing import List, Tuple
import os
import tensorflow as tf
from tensorflow.keras.applications import ResNet50 # Import ResNet50
from tensorflow.keras.preprocessing import image # For potential preprocessing needs

# --- Model Configuration ---
# We will load ResNet50 directly from tf.keras.applications, no local path needed
# MODEL_PATH is no longer used for this specific model
# MODEL_FILENAME is no longer used for this specific model

# ResNet50 expects 224x224 RGB images, normalized 0-1 (which our video_processor does)
MODEL_INPUT_SIZE = (224, 224)
# DEEPFAKE_THRESHOLD is still used, but predictions will be random for deepfake purpose
DEEPFAKE_THRESHOLD = 0.5 

# Global variable to store the loaded model
deepfake_model = None

def load_deepfake_model():
    """
    Loads a real, pre-trained ResNet50 model from tf.keras.applications.
    This model is NOT trained for deepfake detection; its purpose is to demonstrate
    loading and running a real deep learning model.
    """
    global deepfake_model
    if deepfake_model is None:
        print(f"Loading pre-trained ResNet50 model from tf.keras.applications (ImageNet weights)...")
        try:
            # Load ResNet50 with ImageNet weights. TensorFlow handles the download internally.
            # include_top=True means it includes the final classification layers for ImageNet's 1000 classes.
            deepfake_model = ResNet50(weights='imagenet', include_top=True, input_shape=(MODEL_INPUT_SIZE[0], MODEL_INPUT_SIZE[1], 3))
            
            deepfake_model.summary() # Print summary to confirm successful load

            print("ResNet50 model loaded successfully from Keras applications.")
        except Exception as e:
            raise IOError(f"Failed to load ResNet50 model from Keras applications: {e}\n"
                          "Please ensure TensorFlow is installed correctly and has internet access to download weights.")
    return deepfake_model

async def detect_deepfake_in_frames(
    faces: List[np.ndarray]
) -> Tuple[str, float]:
    """
    Performs inference using the loaded ResNet50 model.
    Its predictions will be for ImageNet classes, NOT deepfakes.
    """
    if not faces:
        return "No Faces Detected", 0.0

    model = load_deepfake_model()

    print(f"Performing inference on {len(faces)} faces using the ResNet50 ImageNet model...")

    face_batch = np.array(faces)
    
    try:
        # Preprocess input specifically for ResNet50 if needed (e.g., mean subtraction, scaling)
        # ResNet50 expects input normalized in a specific way if using its preprocess_input function.
        # However, many models also work with 0-1 normalized data. For simplicity, we'll keep 0-1
        # from video_processor, but if errors, specific preprocessing might be needed.
        # from tensorflow.keras.applications.resnet50 import preprocess_input
        # processed_face_batch = preprocess_input(face_batch * 255.0) # Apply ResNet50 specific preprocessing

        predictions = model.predict(face_batch)

        # Interpret predictions: ResNet50 (ImageNet) outputs 1000 probabilities.
        # We need to adapt this for a "deepfake" style output (binary).
        # We'll just take a random or aggregate value from the 1000 predictions as "fake prob".
        # This is purely illustrative, not meaningful for deepfake.
        
        # Take the maximum probability from all 1000 classes as a proxy for "confidence" in *something*
        # And then arbitrarily decide fake/real based on an aggregation for demonstration.
        max_probs = np.max(predictions, axis=1) # Max prob for each face across 1000 classes
        avg_max_prob = np.mean(max_probs) # Average of the max probabilities
        
        # Arbitrary mapping to binary deepfake/real based on this proxy confidence
        # For a deepfake tool, this part would be replaced by actual binary classification logic.
        if avg_max_prob >= 0.5: # Use 0.5 as a threshold for average max prob
            result = "ImageNet Prediction: High Confidence (Placeholder for Deepfake)"
            confidence = float(avg_max_prob)
        else:
            result = "ImageNet Prediction: Low Confidence (Placeholder for Real)"
            confidence = float(avg_max_prob) # Confidence in the prediction being "something"

        print(f"Inference result (ResNet50 ImageNet): {result} with proxy confidence {confidence:.2f}")
        return result, confidence
        
    except Exception as e:
        print(f"ERROR during model.predict or preprocessing: {e}")
        # This indicates a TensorFlow/model execution error
        return "Inference Failed (ResNet50 Execution Error)", 0.0