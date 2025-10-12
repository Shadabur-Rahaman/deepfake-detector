# backend/app/services/production_deepfake_detector.py - Production-Grade Deepfake Detector

import torch
import numpy as np
import cv2
import logging
import time
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass

# Import production modules
from .preprocessing import ProductionPreprocessor, preprocess_batch_production
from .inference import ProductionInferenceEngine, InferenceResult, EnsembleInferenceEngine
from .logger import get_logger, preprocessing_logger, inference_logger, face_detection_logger
from .deterministic_config import get_deterministic_config
from .probability_calibration import ConservativeCalibrator, apply_uncertainty_penalty, validate_model_agreement

logger = get_logger(__name__)

@dataclass
class DetectionResult:
    """Structured detection result"""
    prediction: str
    confidence: float
    raw_probability: float
    calibrated_probability: float
    is_uncertain: bool
    processing_time: float
    faces_detected: int
    model_name: str
    preprocessing_time: float
    inference_time: float

class ProductionDeepfakeDetector:
    """Production-grade deepfake detector with all fixes applied"""
    
    def __init__(self, 
                 model: Optional[torch.nn.Module] = None,
                 device: Optional[torch.device] = None,
                 deterministic: bool = True,
                 threshold: float = 0.5,
                 temperature: float = 1.5):
        """
        Initialize production deepfake detector
        
        Args:
            model: PyTorch model for inference
            device: Target device for computation
            deterministic: Whether to use deterministic inference
            threshold: Binary classification threshold
            temperature: Temperature for probability calibration
        """
        self.model = model
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.deterministic = deterministic
        
        # Initialize production modules
        self.preprocessor = ProductionPreprocessor(deterministic=deterministic)
        self.inference_engine = ProductionInferenceEngine(
            threshold=threshold,
            temperature=temperature,
            deterministic=deterministic
        )
        self.config = get_deterministic_config()
        
        # Statistics
        self.stats = {
            'detections_run': 0,
            'faces_processed': 0,
            'uncertain_predictions': 0,
            'total_processing_time': 0.0,
            'preprocessing_time': 0.0,
            'inference_time': 0.0
        }
        
        # Initialize deterministic mode
        if deterministic:
            self._setup_deterministic()
        
        logger.info(f"[OK] ProductionDeepfakeDetector initialized: device={self.device}, deterministic={deterministic}")
    
    def _setup_deterministic(self):
        """Setup deterministic inference"""
        try:
            if self.deterministic:
                # Set deterministic CUDA operations
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
                
                # Configure model for deterministic inference
                if self.model is not None:
                    self.config.ensure_model_deterministic(self.model)
                
                logger.info("[OK] Deterministic inference enabled")
            
        except Exception as e:
            logger.warning(f"[WARNING] Failed to setup deterministic mode: {e}")
    
    def detect_deepfake(self, faces: List[np.ndarray]) -> DetectionResult:
        """
        Detect deepfakes in a list of faces with production-grade processing
        
        Args:
            faces: List of face images as numpy arrays
            
        Returns:
            Structured detection result
        """
        start_time = time.time()
        
        try:
            if not faces:
                return self._create_error_result("No faces provided", 0.0)
            
            if self.model is None:
                return self._create_error_result("Model not loaded", 0.0)
            
            # Log detection start
            logger.info(f"🔍 Starting detection of {len(faces)} faces")
            
            # Preprocessing
            preprocessing_start = time.time()
            batch_tensor = preprocess_batch_production(faces, self.device)
            preprocessing_time = (time.time() - preprocessing_start) * 1000
            
            # Log preprocessing
            preprocessing_logger.log_preprocessing(
                input_shape=faces[0].shape if faces else (0, 0, 0),
                output_shape=batch_tensor.shape,
                tensor_range=(batch_tensor.min().item(), batch_tensor.max().item()),
                processing_time=preprocessing_time
            )
            
            # Inference
            inference_start = time.time()
            inference_result = self.inference_engine.run_inference(
                self.model, batch_tensor, "production_model"
            )
            inference_time = (time.time() - inference_start) * 1000
            
            # Log inference
            inference_logger.log_inference_result(
                model_name=inference_result.model_name,
                prediction=inference_result.prediction,
                confidence=inference_result.confidence,
                raw_probability=inference_result.raw_probability,
                calibrated_probability=inference_result.calibrated_probability,
                processing_time=inference_result.processing_time,
                is_uncertain=inference_result.is_uncertain
            )
            
            # Create detection result
            total_time = (time.time() - start_time) * 1000
            detection_result = DetectionResult(
                prediction=inference_result.prediction,
                confidence=inference_result.confidence,
                raw_probability=inference_result.raw_probability,
                calibrated_probability=inference_result.calibrated_probability,
                is_uncertain=inference_result.is_uncertain,
                processing_time=total_time,
                faces_detected=len(faces),
                model_name=inference_result.model_name,
                preprocessing_time=preprocessing_time,
                inference_time=inference_time
            )
            
            # Update statistics
            self._update_stats(detection_result)
            
            # Log final result
            self._log_detection_result(detection_result)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"[ERROR] Detection failed: {e}")
            return self._create_error_result(f"Detection failed: {e}", (time.time() - start_time) * 1000)
    
    def detect_deepfake_in_frame(self, frame: np.ndarray) -> Tuple[DetectionResult, List[np.ndarray], List[Dict]]:
        """
        Detect deepfakes in a frame with face detection
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Tuple of (detection_result, detected_faces, face_coordinates)
        """
        try:
            # Detect faces
            faces, coordinates = self._detect_faces(frame)
            
            if not faces:
                return self._create_error_result("No faces detected", 0.0), [], []
            
            # Detect deepfakes
            detection_result = self.detect_deepfake(faces)
            
            return detection_result, faces, coordinates
            
        except Exception as e:
            logger.error(f"[ERROR] Frame detection failed: {e}")
            return self._create_error_result(f"Frame detection failed: {e}", 0.0), [], []
    
    def _detect_faces(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces in frame using YOLOv8 or fallback method"""
        try:
            # Try YOLOv8 face detection first
            try:
                from ultralytics import YOLO
                
                # Load YOLO model
                yolo_model = YOLO('yolov8n.pt')
                yolo_model.to(self.device)
                
                # Run detection
                results = yolo_model(frame, verbose=False, device=self.device)
                
                faces = []
                coordinates = []
                
                for result in results:
                    if result.boxes is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box[:4])
                            face_crop = frame[y1:y2, x1:x2]
                            if face_crop.size > 0:
                                faces.append(face_crop)
                                coordinates.append({
                                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                                    'width': x2 - x1, 'height': y2 - y1
                                })
                
                # Log face detection
                face_detection_logger.log_face_detection(
                    frame_shape=frame.shape,
                    faces_detected=len(faces),
                    bounding_boxes=coordinates,
                    processing_time=0.0  # YOLO timing handled internally
                )
                
                return faces, coordinates
                
            except ImportError:
                logger.warning("[WARNING] YOLOv8 not available, using fallback face detection")
                return self._fallback_face_detection(frame)
            except Exception as e:
                logger.warning(f"[WARNING] YOLOv8 face detection failed: {e}, using fallback")
                return self._fallback_face_detection(frame)
                
        except Exception as e:
            logger.error(f"[ERROR] Face detection failed: {e}")
            return [], []
    
    def _fallback_face_detection(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Fallback face detection using OpenCV Haar cascades"""
        try:
            # Load Haar cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces_detected = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            faces = []
            coordinates = []
            
            for (x, y, w, h) in faces_detected:
                face_crop = frame[y:y+h, x:x+w]
                if face_crop.size > 0:
                    faces.append(face_crop)
                    coordinates.append({
                        'x1': x, 'y1': y, 'x2': x+w, 'y2': y+h,
                        'width': w, 'height': h
                    })
            
            # Log fallback detection
            face_detection_logger.log_face_detection(
                frame_shape=frame.shape,
                faces_detected=len(faces),
                bounding_boxes=coordinates,
                processing_time=0.0
            )
            
            return faces, coordinates
            
        except Exception as e:
            logger.error(f"[ERROR] Fallback face detection failed: {e}")
            return [], []
    
    def _create_error_result(self, error_message: str, processing_time: float) -> DetectionResult:
        """Create error detection result"""
        return DetectionResult(
            prediction=error_message,
            confidence=0.0,
            raw_probability=0.5,
            calibrated_probability=0.5,
            is_uncertain=True,
            processing_time=processing_time,
            faces_detected=0,
            model_name="error",
            preprocessing_time=0.0,
            inference_time=0.0
        )
    
    def _update_stats(self, result: DetectionResult):
        """Update detection statistics"""
        self.stats['detections_run'] += 1
        self.stats['faces_processed'] += result.faces_detected
        self.stats['total_processing_time'] += result.processing_time
        self.stats['preprocessing_time'] += result.preprocessing_time
        self.stats['inference_time'] += result.inference_time
        
        if result.is_uncertain:
            self.stats['uncertain_predictions'] += 1
    
    def _log_detection_result(self, result: DetectionResult):
        """Log structured detection result"""
        try:
            logger.info(f"🎯 Detection Result:")
            logger.info(f"  Prediction: {result.prediction}")
            logger.info(f"  Confidence: {result.confidence:.3f}%")
            logger.info(f"  Raw Probability: {result.raw_probability:.4f}")
            logger.info(f"  Calibrated Probability: {result.calibrated_probability:.4f}")
            logger.info(f"  Uncertain: {result.is_uncertain}")
            logger.info(f"  Faces Detected: {result.faces_detected}")
            logger.info(f"  Processing Time: {result.processing_time:.2f}ms")
            logger.info(f"  Model: {result.model_name}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to log detection result: {e}")
    
    def set_model(self, model: torch.nn.Module):
        """Set the model for inference"""
        self.model = model
        if self.deterministic:
            self.config.ensure_model_deterministic(model)
        logger.info("[OK] Model set for production detector")
    
    def set_threshold(self, threshold: float):
        """Update classification threshold"""
        self.inference_engine.set_threshold(threshold)
        logger.info(f"[OK] Threshold updated to {threshold}")
    
    def set_temperature(self, temperature: float):
        """Update calibration temperature"""
        self.inference_engine.set_temperature(temperature)
        logger.info(f"[OK] Temperature updated to {temperature}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        avg_processing_time = (self.stats['total_processing_time'] / max(self.stats['detections_run'], 1))
        avg_faces_per_detection = (self.stats['faces_processed'] / max(self.stats['detections_run'], 1))
        uncertain_rate = (self.stats['uncertain_predictions'] / max(self.stats['detections_run'], 1)) * 100
        
        return {
            **self.stats,
            'average_processing_time': avg_processing_time,
            'average_faces_per_detection': avg_faces_per_detection,
            'uncertain_prediction_rate': uncertain_rate,
            'device': str(self.device),
            'deterministic': self.deterministic,
            'threshold': self.inference_engine.threshold,
            'temperature': self.inference_engine.calibrator.temperature
        }

# Global production detector instance
production_detector = ProductionDeepfakeDetector()

def get_production_detector() -> ProductionDeepfakeDetector:
    """Get the global production detector"""
    return production_detector

def detect_deepfake_production(faces: List[np.ndarray]) -> DetectionResult:
    """Detect deepfakes using production detector"""
    return production_detector.detect_deepfake(faces)

def detect_deepfake_in_frame_production(frame: np.ndarray) -> Tuple[DetectionResult, List[np.ndarray], List[Dict]]:
    """Detect deepfakes in frame using production detector"""
    return production_detector.detect_deepfake_in_frame(frame)
