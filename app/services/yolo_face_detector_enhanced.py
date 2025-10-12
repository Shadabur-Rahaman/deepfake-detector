from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple
import logging
import os

logger = logging.getLogger(__name__)

class YOLOv8FaceDetector:
    def __init__(self, model_path="yolov8n.pt"):
        try:
            # Check multiple possible locations for the model
            possible_paths = [
                model_path,
                f"ml_artifacts/{model_path}",
                f"../../ml_artifacts/{model_path}"
            ]
            
            model_found = None
            for path in possible_paths:
                if os.path.exists(path):
                    model_found = path
                    break
            
            if model_found:
                self.model = YOLO(model_found)
            else:
                # Auto-download if not found
                self.model = YOLO(model_path)
            
            logger.info("✅ YOLOv8 face detector loaded successfully")
            self.available = True
        except Exception as e:
            logger.error(f"❌ YOLOv8 face detector failed to load: {e}")
            self.available = False
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        if not self.available:
            return []
        
        try:
            results = self.model(image, verbose=False)
            faces = []
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        conf = box.conf.cpu().numpy()
                        if conf > 0.5:
                            faces.append((x1, y1, x2-x1, y2-y1, conf))
            return faces
        except Exception as e:
            logger.error(f"YOLOv8 face detection error: {e}")
            return []

# Global instance
yolo_face_detector = YOLOv8FaceDetector()
