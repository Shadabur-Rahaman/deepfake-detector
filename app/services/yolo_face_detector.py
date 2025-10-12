import cv2
import torch
import numpy as np
from typing import List, Tuple, Optional
import logging
from ultralytics import YOLO
import os

# YOLOv8 safe globals configuration for PyTorch 2.6 compatibility
try:
    from ultralytics.nn.tasks import DetectionModel
    # Check if add_safe_globals is available (PyTorch 2.6+)
    if hasattr(torch.serialization, 'add_safe_globals'):
        torch.serialization.add_safe_globals([DetectionModel])
        logger = logging.getLogger(__name__)
        logger.info("✅ YOLOv8 safe globals configured for PyTorch 2.6+")
    else:
        logger = logging.getLogger(__name__)
        logger.info("⚠️ PyTorch version doesn't support add_safe_globals, skipping configuration")
except ImportError:
    pass  # YOLOv8 not available, skip configuration

logger = logging.getLogger(__name__)

class YOLOv8FaceDetector:
    def __init__(self, model_path: str = "yolov8n-face.pt", device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.model_path = model_path
        self.initialized = False
        
    def initialize(self):
        """Initialize YOLOv8 face detection model"""
        try:
            # Check if model file exists, if not use default YOLOv8n
            if not os.path.exists(self.model_path):
                logger.warning(f"Face model {self.model_path} not found, using YOLOv8n")
                self.model_path = "yolov8n.pt"
            
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            self.initialized = True
            logger.info(f"✅ YOLOv8 Face Detector loaded on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load YOLOv8 model: {e}")
            self.model = None
            self.initialized = False

    def detect_faces(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int, np.ndarray]]:
        """
        Detect faces in frame using YOLOv8
        Returns: List of (x, y, w, h, rgb_frame) tuples
        """
        if not self.initialized:
            self.initialize()
            
        if self.model is None:
            logger.warning("YOLOv8 model not available")
            return []

        try:
            # Convert BGR to RGB for YOLOv8
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run inference
            results = self.model(frame, verbose=False)
            
            faces = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get confidence and class
                        conf = float(box.conf.cpu())
                        cls = int(box.cls.cpu())
                        
                        # Filter by confidence and class (0 is usually person/face)
                        if conf >= confidence_threshold:
                            # Get coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                            
                            # Validate coordinates
                            if (x >= 0 and y >= 0 and 
                                x + w <= frame.shape[1] and 
                                y + h <= frame.shape and 
                                w > 30 and h > 30):  # Minimum face size
                                
                                faces.append((x, y, w, h, rgb_frame))
            
            logger.debug(f"YOLOv8 detected {len(faces)} faces")
            return faces
            
        except Exception as e:
            logger.error(f"Error in YOLOv8 face detection: {e}")
            return []

    def detect_faces_batch(self, frames: List[np.ndarray]) -> List[List[Tuple[int, int, int, int, np.ndarray]]]:
        """Batch face detection for multiple frames"""
        if not self.initialized:
            self.initialize()
            
        results = []
        for frame in frames:
            faces = self.detect_faces(frame)
            results.append(faces)
        return results

# Global instance
yolo_face_detector = YOLOv8FaceDetector()
