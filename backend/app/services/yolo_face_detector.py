# app/services/yolo_face_detector.py
import cv2
import os

# Use centralized import management
try:
    from .import_manager import safe_import_yolo, safe_import_opencv
    YOLO = safe_import_yolo()
    cv2 = safe_import_opencv()
    
    if YOLO is None:
        raise ImportError("YOLO not available")
except ImportError:
    # Fallback import
    from ultralytics import YOLO
    print("[WARNING] Using fallback YOLO import")

CONF_THR = 0.70   # keep high for precision
# Use relative path for better portability
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "yolov8n-face.pt")
class YOLOv8Face:
    def __init__(self, device=None):
        self.device = device or "auto"
        self.model = YOLO(MODEL_PATH)
        if self.device != "auto":
            self.model.to(self.device)

    def detect(self, frame):
        """Return list[(x,y,w,h,rgb_frame)] exactly like FaceExtractor.detect_faces"""
        results = self.model(frame, verbose=False)[0]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = []
        for box, conf in zip(results.boxes.xyxy, results.boxes.conf):
            if conf < CONF_THR:                     # ignore weak
                continue
            x1, y1, x2, y2 = [int(v) for v in box]
            faces.append((x1, y1, x2 - x1, y2 - y1, rgb))
        return faces

# Alias for backward compatibility
YOLOFaceDetector = YOLOv8Face
