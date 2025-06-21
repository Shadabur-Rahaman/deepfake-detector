# app/services/video_processor.py
import cv2
import numpy as np
import os
from typing import List, Tuple, Optional

# Path to the Haar Cascade XML file.
# You need to download 'haarcascade_frontalface_default.xml' and place it in ml_artifacts/.
# You can find it in the OpenCV GitHub repository:
# https://github.com/opencv/opencv/tree/master/data/haarcascades
HAARCASCADE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ml_artifacts/haarcascade_frontalface_default.xml')

# Load the Haar Cascade classifier
face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)

def extract_faces_from_video(
    video_path: str,
    target_size: Tuple[int, int] = (224, 224), # Common input size for CNNs
    frames_to_process: Optional[int] = None, # Process all if None, otherwise a fixed number
    frame_interval: int = 1 # Process every Nth frame
) -> List[np.ndarray]:
    """
    Extracts faces from video frames, resizes them, and returns them as a list of NumPy arrays.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(HAARCASCADE_PATH):
        raise FileNotFoundError(f"Haar Cascade XML not found: {HAARCASCADE_PATH}. Please download it and place it in 'ml_artifacts/'.")


    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video file: {video_path}")

    extracted_faces: List[np.ndarray] = []
    frame_count = 0
    processed_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break # End of video

        if frame_count % frame_interval == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces in the grayscale frame
            # scaleFactor: Parameter specifying how much the image size is reduced at each image scale.
            # minNeighbors: Parameter specifying how many neighbors each candidate rectangle should have to retain it.
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                # Crop the face region
                face_img = frame[y:y+h, x:x+w]

                # Resize the face image to the target size
                resized_face = cv2.resize(face_img, target_size, interpolation=cv2.INTER_AREA)

                # Normalize pixel values (e.g., 0-1, or -1 to 1 depending on model requirements)
                # For most deep learning models expecting 0-255 images, simple conversion to float32 is enough.
                # If a model expects -1 to 1, you'd do: (resized_face.astype(np.float32) / 127.5) - 1
                normalized_face = resized_face.astype(np.float32) / 255.0

                extracted_faces.append(normalized_face)
                processed_count += 1
                if frames_to_process is not None and processed_count >= frames_to_process:
                    break
            if frames_to_process is not None and processed_count >= frames_to_process:
                break

        frame_count += 1

    cap.release()
    print(f"Extracted {len(extracted_faces)} faces from {frame_count} frames.")
    return extracted_faces