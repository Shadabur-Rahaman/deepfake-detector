# app/services/realtime_detector.py - FIXED FACE DETECTION

import cv2
import numpy as np
import torch
from typing import Dict
import traceback
import logging
from app.services.deepfake_detector import load_deepfake_model
from typing import Dict, List, Optional  # ADD THIS LINE
logger = logging.getLogger(__name__)

class RealTimeDeepfakeDetector:
    """FIXED: Real-time deepfake detector with robust face detection"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # **FIXED**: Multiple face detection methods for better reliability
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        
        # **NEW**: Try to load additional cascades for better detection
        try:
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except:
            self.eye_cascade = None
            
        print(f"[FIX] RealTimeDetector initialized on device: {self.device}")

    async def load_model(self):
        """Load EfficientNet model for real-time detection"""
        try:
            if self.model is None:
                print("📥 Loading EfficientNet model...")
                self.model = load_deepfake_model()
                print("[OK] Real-time detector model loaded successfully")
        except Exception as e:
            print(f"[ERROR] Model loading failed: {e}")
            raise e

    async def real_time_analyze(self, frame: np.ndarray) -> Dict:
        """FIXED: Enhanced frame analysis with improved face detection"""
        try:
            print(f"🔍 Analyzing frame shape: {frame.shape}")
            
            if self.model is None:
                await self.load_model()

            # **FIXED**: Enhanced face detection with multiple methods
            faces = self._detect_faces_enhanced(frame)
            print(f"👥 Detected {len(faces)} faces")

            if len(faces) == 0:
                return {
                    "prediction": "No Face Detected",
                    "confidence": 0,
                    "faces_detected": 0,
                    "processing_time": "real-time",
                    "face_coordinates": None
                }

            # Process the largest/most confident face
            best_face = max(faces, key=lambda f: f['confidence'] * f['w'] * f['h'])
            x, y, w, h = best_face['x'], best_face['y'], best_face['w'], best_face['h']
            
            print(f"[MODELS] Processing face at: ({x}, {y}) size: {w}x{h}")

            # **FIXED**: Enhanced face preprocessing
            try:
                face_tensor = self._preprocess_face_enhanced(frame, x, y, w, h)
                if face_tensor is None:
                    raise ValueError("Face preprocessing failed")
                    
                print(f"🧠 Face tensor shape: {face_tensor.shape}")
                
            except Exception as prep_error:
                print(f"[ERROR] Face preprocessing error: {prep_error}")
                return {
                    "prediction": "Preprocessing Failed",
                    "confidence": 0,
                    "faces_detected": len(faces),
                    "error": str(prep_error)
                }

            # **IMPROVED**: Deepfake detection
            try:
                print("🤖 Running deepfake detection...")
                result, confidence = await detect_deepfake_in_frames([face_tensor])
                print(f"🎯 Detection result: {result} ({confidence:.3f})")

                return {
                    "prediction": result,
                    "confidence": confidence * 100,
                    "faces_detected": len(faces),
                    "processing_time": "real-time",
                    "face_coordinates": {
                        "x": int(x), 
                        "y": int(y), 
                        "width": int(w), 
                        "height": int(h)
                    }
                }

            except Exception as detect_error:
                print(f"[ERROR] Detection error: {detect_error}")
                return {
                    "prediction": "Detection Failed",
                    "confidence": 0,
                    "faces_detected": len(faces),
                    "error": str(detect_error)
                }

        except Exception as e:
            print(f"[ERROR] Critical analysis error: {e}")
            return {
                "prediction": "Analysis Failed",
                "confidence": 0,
                "faces_detected": 0,
                "error": str(e)
            }

    def _detect_faces_enhanced(self, frame: np.ndarray) -> list:
        """FIXED: Enhanced face detection with multiple methods and better parameters"""
        faces = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # **ENHANCED**: Histogram equalization for better detection
            gray = cv2.equalizeHist(gray)
            
            # **METHOD 1**: Primary frontal face detection with relaxed parameters
            try:
                detected_frontal = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,      # **FIXED**: Smaller steps for better detection
                    minNeighbors=3,        # **FIXED**: Reduced from 5 for more sensitivity  
                    minSize=(40, 40),      # **FIXED**: Smaller minimum size
                    maxSize=(400, 400),    # **FIXED**: Larger maximum size
                    flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING
                )
                
                for (x, y, w, h) in detected_frontal:
                    faces.append({
                        'x': x, 'y': y, 'w': w, 'h': h, 
                        'confidence': 0.8,  # High confidence for frontal
                        'type': 'frontal'
                    })
                    
            except Exception as e:
                print(f"[WARNING] Frontal face detection failed: {e}")

            # **METHOD 2**: Profile face detection if frontal failed
            if not faces and self.profile_cascade:
                try:
                    detected_profile = self.profile_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.05,
                        minNeighbors=3,
                        minSize=(40, 40),
                        maxSize=(400, 400)
                    )
                    
                    for (x, y, w, h) in detected_profile:
                        faces.append({
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'confidence': 0.6,  # Lower confidence for profile
                            'type': 'profile'
                        })
                        
                except Exception as e:
                    print(f"[WARNING] Profile face detection failed: {e}")

            # **METHOD 3**: Ultra-sensitive detection as last resort
            if not faces:
                try:
                    detected_sensitive = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.02,      # **VERY SENSITIVE**
                        minNeighbors=2,        # **VERY SENSITIVE** 
                        minSize=(30, 30),      # **SMALLER MIN SIZE**
                        maxSize=(500, 500),    # **LARGER MAX SIZE**
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    
                    for (x, y, w, h) in detected_sensitive:
                        faces.append({
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'confidence': 0.4,  # Lower confidence for sensitive detection
                            'type': 'sensitive'
                        })
                        
                except Exception as e:
                    print(f"[WARNING] Sensitive face detection failed: {e}")

            # **DEBUG**: Log detection details
            if faces:
                print(f"[OK] Face detection successful: {len(faces)} faces found")
                for i, face in enumerate(faces):
                    print(f"  Face {i+1}: {face['type']} at ({face['x']},{face['y']}) size {face['w']}x{face['h']} confidence {face['confidence']}")
            else:
                print(f"[ERROR] No faces detected with any method")
                print(f"  Frame shape: {frame.shape}")
                print(f"  Gray shape: {gray.shape}")
                print(f"  Gray range: {gray.min()}-{gray.max()}")

            return faces

        except Exception as e:
            print(f"[ERROR] Enhanced face detection failed: {e}")
            return []

    def _preprocess_face_enhanced(self, frame: np.ndarray, x: int, y: int, w: int, h: int) -> torch.Tensor:
        """FIXED: Enhanced face preprocessing with better error handling"""
        try:
            # **FIXED**: Ensure coordinates are within frame bounds
            height, width = frame.shape[:2]
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))  
            w = max(1, min(w, width - x))
            h = max(1, min(h, height - y))
            
            # **ENHANCED**: Add padding around face for better detection
            padding = min(w, h) // 10  # 10% padding
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(width, x + w + padding)
            y2 = min(height, y + h + padding)
            
            # Extract face crop
            face_crop = frame[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                raise ValueError("Empty face crop after padding")
            
            # Resize to model input size
            face_resized = cv2.resize(face_crop, (224, 224))
            
            # Convert BGR to RGB (important for model)
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            # Convert to tensor and normalize
            face_tensor = torch.from_numpy(face_rgb).permute(2, 0, 1).float() / 255.0
            
            # Apply ImageNet normalization
            normalize = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            face_tensor = (face_tensor - normalize) / std
            
            return face_tensor
            
        except Exception as e:
            print(f"[ERROR] Enhanced preprocessing failed: {e}")
            return None

# Backward compatibility
class RealTimeDetector(RealTimeDeepfakeDetector):
    """Alias for backward compatibility"""
    async def analyze_frame(self, frame: np.ndarray) -> Dict:
        return await self.real_time_analyze(frame)
