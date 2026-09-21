#!/usr/bin/env python3
"""
Core Ensemble Detector - Multi-model ensemble using:
1. Your trained model (deepfake_detector_finetuned1.pth) - Primary
2. EfficientNet - Secondary CNN
3. OpenCV Haar Cascade - Face quality analysis
4. MTCNN - Face detection and quality metrics
"""

import os
import time
import logging
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
import cv2
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CoreDetectionResult:
    """Result from core ensemble detection"""
    prediction: str
    confidence: float
    model_scores: Dict[str, float]
    model_predictions: Dict[str, str]
    ensemble_method: str
    processing_time_ms: float
    faces_analyzed: int

class CoreEnsembleDetector:
    """
    Core ensemble detector combining multiple models for robust deepfake detection
    """
    
    def __init__(self, device: str = "auto"):
        self.device = self._get_device(device)
        self.models = {}
        self.model_weights = {
            'trained_model': 0.80,      # Increased - it's YOUR trained model with 0.948 confidence!
            'efficientnet': 0.05,       # Small weight for secondary validation
            'opencv_haar': 0.08,        # Reduced
            'mtcnn_quality': 0.07       # Reduced
        }
        self.is_initialized = False
        
        # Face tracking for consistent video detection
        self.face_tracker = {}  # Track faces across frames
        self.face_id_counter = 0
        self.tracking_threshold = 0.3  # IoU threshold for face matching
        
        logger.info(f"🎯 CoreEnsembleDetector initialized with device: {self.device}")
    
    def _get_device(self, device: str) -> torch.device:
        """Get safe device for model loading"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device('cuda')
            return torch.device('cpu')
        return torch.device(device)
    
    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        union_area = w1 * h1 + w2 * h2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0
    
    def _track_faces(self, detected_faces: List[Tuple[int, int, int, int, np.ndarray]]) -> List[Tuple[int, int, int, int, np.ndarray, int]]:
        """Track faces across frames and assign consistent IDs"""
        tracked_faces = []
        
        for face_bbox in detected_faces:
            x, y, w, h, face_img = face_bbox
            bbox = (x, y, w, h)
            
            # Find best matching existing face
            best_match_id = None
            best_iou = 0.0
            
            for face_id, tracked_bbox in self.face_tracker.items():
                iou = self._calculate_iou(bbox, tracked_bbox)
                if iou > self.tracking_threshold and iou > best_iou:
                    best_iou = iou
                    best_match_id = face_id
            
            if best_match_id is not None:
                # Update existing face
                self.face_tracker[best_match_id] = bbox
                tracked_faces.append((x, y, w, h, face_img, best_match_id))
            else:
                # Create new face ID
                face_id = self.face_id_counter
                self.face_id_counter += 1
                self.face_tracker[face_id] = bbox
                tracked_faces.append((x, y, w, h, face_img, face_id))
        
        # Clean up old faces (not detected for several frames)
        # This is a simple implementation - in production, you'd want more sophisticated tracking
        return tracked_faces
    
    async def initialize_models(self) -> bool:
        """Initialize all core models"""
        try:
            logger.info("🔄 Initializing core ensemble models...")
            start_time = time.time()
            
            # 1. Load your trained model (PRIMARY)
            trained_model = await self._load_trained_model()
            if trained_model:
                self.models['trained_model'] = trained_model
                logger.info("✅ Your trained model loaded successfully")
            else:
                logger.warning("⚠️ Your trained model failed to load")
            
            # 2. Load EfficientNet (SECONDARY)
            efficientnet = await self._load_efficientnet()
            if efficientnet:
                self.models['efficientnet'] = efficientnet
                logger.info("✅ EfficientNet loaded successfully")
            
            # 3. Initialize OpenCV Haar Cascade
            opencv_haar = self._load_opencv_haar()
            if opencv_haar:
                self.models['opencv_haar'] = opencv_haar
                logger.info("✅ OpenCV Haar Cascade loaded successfully")
            
            # 4. Initialize MTCNN
            mtcnn = await self._load_mtcnn()
            if mtcnn:
                self.models['mtcnn'] = mtcnn
                logger.info("✅ MTCNN loaded successfully")
            
            init_time = (time.time() - start_time) * 1000
            logger.info(f"🎯 Core ensemble initialized in {init_time:.2f}ms with {len(self.models)} models")
            
            self.is_initialized = True
            return len(self.models) > 0
            
        except Exception as e:
            logger.error(f"❌ Core ensemble initialization failed: {e}")
            return False
    
    async def _load_trained_model(self) -> Optional[torch.nn.Module]:
        """Load your trained deepfake_detector_finetuned1.pth model"""
        try:
            # Get path to your trained model
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, '../../../ml_artifacts/deepfake_detector_finetuned1.pth')
            
            if not os.path.exists(model_path):
                logger.error(f"Your trained model not found at: {model_path}")
                return None
            
            # Load your trained EfficientNet model
            model = models.efficientnet_b0(weights=None)
            num_ftrs = model.classifier[1].in_features
            model.classifier = nn.Sequential(nn.Dropout(p=0.2, inplace=True), nn.Linear(num_ftrs, 1))
            
            # Load your trained weights
            state_dict = torch.load(model_path, map_location=self.device)
            if any(key.startswith('module.') for key in state_dict.keys()):
                state_dict = {key.replace('module.', ''): value for key, value in state_dict.items()}
            
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            
            logger.info("🎯 YOUR trained model loaded successfully!")
            logger.info(f"🔍 DEBUG: Model loaded from path: {model_path}")
            logger.info(f"🔍 DEBUG: Model device: {next(model.parameters()).device}")
            logger.info(f"🔍 DEBUG: Model classifier: {model.classifier}")
            return model
            
        except Exception as e:
            logger.error(f"Your trained model loading failed: {e}")
            return None
    
    async def _load_efficientnet(self) -> Optional[torch.nn.Module]:
        """Load generic EfficientNet model with hash validation fix"""
        try:
            # Try to remove corrupted cache file first
            cache_path = os.path.expanduser('~/.cache/torch/hub/checkpoints/efficientnet_b0_rwightman-3dd342df.pth')
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    logger.info("Removed corrupted EfficientNet cache file")
                except Exception as e:
                    logger.warning(f"Could not remove corrupted cache: {e}")
            
            # Try multiple loading strategies to avoid hash validation issues
            loading_strategies = [
                # Strategy 1: Use timm library (more reliable)
                lambda: self._load_efficientnet_timm(),
                # Strategy 2: Use torchvision with different weights
                lambda: models.efficientnet_b0(weights='DEFAULT'),
                # Strategy 3: Use torchvision without weights
                lambda: models.efficientnet_b0(weights=None),
                # Strategy 4: Use older torchvision API
                lambda: models.efficientnet_b0(pretrained=False)
            ]
            
            for i, strategy in enumerate(loading_strategies, 1):
                try:
                    logger.info(f"📋 Strategy {i}: Attempting EfficientNet loading...")
                    model = strategy()
                    model.eval()
                    model.to(self.device)
                    logger.info(f"✅ EfficientNet loaded successfully with strategy {i}")
                    return model
                except Exception as e:
                    logger.warning(f"Strategy {i} failed: {e}")
                    continue
            
            logger.error("All EfficientNet loading strategies failed")
            return None
            
        except Exception as e:
            logger.error(f"EfficientNet loading completely failed: {e}")
            return None
    
    def _load_efficientnet_timm(self) -> torch.nn.Module:
        """Load EfficientNet using timm library (more reliable)"""
        try:
            import timm
            model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=1000)
            logger.info("✅ EfficientNet loaded successfully using timm")
            return model
        except ImportError:
            logger.warning("timm not available, falling back to torchvision")
            raise Exception("timm not available")
        except Exception as e:
            logger.warning(f"timm loading failed: {e}")
            raise
    
    def _load_opencv_haar(self) -> Optional[Any]:
        """Load optimized OpenCV face detector"""
        try:
            # Try to load enhanced OpenCV detector
            from .optimized_face_detector import optimized_face_detector
            if optimized_face_detector.is_initialized:
                logger.info("✅ Optimized OpenCV detector loaded successfully")
                return optimized_face_detector
            else:
                logger.warning("Optimized OpenCV detector not available")
                return None
        except Exception as e:
            logger.warning(f"Optimized OpenCV detector loading failed: {e}")
            # Fallback to basic OpenCV
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    cascade = cv2.CascadeClassifier(cascade_path)
                    logger.info("✅ Basic OpenCV Haar cascade loaded as fallback")
                    return cascade
                else:
                    logger.warning("OpenCV Haar cascade not found")
                    return None
            except Exception as e2:
                logger.warning(f"Basic OpenCV Haar cascade loading failed: {e2}")
                return None
    
    async def _load_mtcnn(self) -> Optional[Any]:
        """Load MTCNN for face detection"""
        try:
            # Try to import MTCNN
            try:
                from facenet_pytorch import MTCNN
                mtcnn = MTCNN(keep_all=True, device=self.device)
                return mtcnn
            except ImportError:
                logger.warning("MTCNN not available (facenet_pytorch not installed)")
                return None
        except Exception as e:
            logger.warning(f"MTCNN loading failed: {e}")
            return None
    
    async def detect_core_ensemble(self, faces: List[np.ndarray], video_id: str = None) -> CoreDetectionResult:
        """
        Run core ensemble detection on faces
        
        Args:
            faces: List of face images (numpy arrays)
            video_id: Optional video identifier for logging
            
        Returns:
            CoreDetectionResult with ensemble prediction
        """
        if not self.is_initialized:
            await self.initialize_models()
        
        if not faces:
            return CoreDetectionResult(
                prediction="No Faces Detected",
                confidence=0.0,
                model_scores={},
                model_predictions={},
                ensemble_method="no_faces",
                processing_time_ms=0.0,
                faces_analyzed=0
            )
        
        start_time = time.time()
        model_scores = {}
        model_predictions = {}
        
        try:
            # Apply face tracking for consistent video detection
            tracked_faces = self._track_faces([(0, 0, face.shape[1], face.shape[0], face) for face in faces])
            logger.info(f"🔍 Tracked {len(tracked_faces)} faces with IDs")
            
            # 1. Your Trained Model (PRIMARY - 50% weight)
            if 'trained_model' in self.models:
                trained_score, trained_pred = await self._predict_trained_model(faces)
                model_scores['trained_model'] = trained_score
                model_predictions['trained_model'] = trained_pred
                logger.info(f"🎯 Your trained model: {trained_pred} ({trained_score:.3f})")
            
            # 2. EfficientNet (SECONDARY - 25% weight)
            if 'efficientnet' in self.models:
                efficientnet_score, efficientnet_pred = await self._predict_efficientnet(faces)
                model_scores['efficientnet'] = efficientnet_score
                model_predictions['efficientnet'] = efficientnet_pred
                logger.info(f"🧠 EfficientNet: {efficientnet_pred} ({efficientnet_score:.3f})")
            
            # 3. OpenCV Haar Cascade (15% weight)
            if 'opencv_haar' in self.models:
                opencv_score, opencv_pred = await self._predict_opencv_haar(faces)
                model_scores['opencv_haar'] = opencv_score
                model_predictions['opencv_haar'] = opencv_pred
                logger.info(f"👁️ OpenCV Haar: {opencv_pred} ({opencv_score:.3f})")
            
            # 4. MTCNN Quality (10% weight)
            if 'mtcnn' in self.models:
                mtcnn_score, mtcnn_pred = await self._predict_mtcnn_quality(faces)
                model_scores['mtcnn_quality'] = mtcnn_score
                model_predictions['mtcnn_quality'] = mtcnn_pred
                logger.info(f"🔍 MTCNN Quality: {mtcnn_pred} ({mtcnn_score:.3f})")
            
            # Calculate weighted ensemble
            final_prediction, final_confidence = self._calculate_ensemble(
                model_scores, model_predictions
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return CoreDetectionResult(
                prediction=final_prediction,
                confidence=final_confidence,
                model_scores=model_scores,
                model_predictions=model_predictions,
                ensemble_method="weighted_core_ensemble",
                processing_time_ms=processing_time,
                faces_analyzed=len(faces)
            )
            
        except Exception as e:
            logger.error(f"Core ensemble detection failed: {e}")
            return CoreDetectionResult(
                prediction="Detection Failed",
                confidence=0.0,
                model_scores=model_scores,
                model_predictions=model_predictions,
                ensemble_method="failed",
                processing_time_ms=(time.time() - start_time) * 1000,
                faces_analyzed=len(faces)
            )
    
    async def _predict_trained_model(self, faces: List) -> Tuple[float, str]:
        """Predict using your trained model with model verification"""
        try:
            model = self.models['trained_model']
            
            # Get model calibration on first use
            if not hasattr(self, '_model_calibration'):
                try:
                    from .model_output_verifier import get_model_calibration
                    model_path = os.path.join(os.path.dirname(__file__), '../../../ml_artifacts/deepfake_detector_finetuned1.pth')
                    self._model_calibration = get_model_calibration(model_path)
                    if self._model_calibration:
                        logger.info(f"🎯 Model calibration loaded: {self._model_calibration.output_interpretation}, threshold: {self._model_calibration.optimal_threshold:.3f}")
                    else:
                        logger.warning("⚠️ Model calibration failed, using default interpretation")
                        self._model_calibration = None
                except Exception as e:
                    logger.warning(f"⚠️ Model verification failed: {e}")
                    self._model_calibration = None
            
            # Convert faces to tensors
            face_tensors = []
            for face_data in faces:
                # Handle new face data format
                if isinstance(face_data, dict):
                    face = face_data['face']  # Extract the preprocessed face
                else:
                    face = face_data  # Legacy format
                
                # Handle both numpy arrays and torch tensors
                if isinstance(face, torch.Tensor):
                    # Already a tensor, just ensure correct format
                    if face.dim() == 3:  # (C, H, W)
                        face_tensor = face.unsqueeze(0)
                    else:
                        face_tensor = face
                    face_tensors.append(face_tensor)
                elif isinstance(face, np.ndarray):
                    # Convert numpy to tensor
                    face_resized = cv2.resize(face, (224, 224))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    face_tensor = torch.from_numpy(face_rgb).float() / 255.0
                    face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0)
                    face_tensors.append(face_tensor)
            
            logger.info(f"🔍 Processed {len(face_tensors)} face tensors from {len(faces)} input faces")
            if not face_tensors:
                logger.error(f"❌ No valid face tensors! Input types: {[type(f).__name__ for f in faces[:3]]}")
                return 0.5, "No Valid Faces"
            
            # Batch process
            batch = torch.cat(face_tensors, dim=0).to(self.device)
            
            with torch.no_grad():
                outputs = model(batch)
                probabilities = torch.sigmoid(outputs).cpu().numpy().flatten()
                avg_prob = np.mean(probabilities)
                
                # Log raw model output for debugging
                logger.info(f"🔍 Raw model output: {avg_prob:.3f}")
                
                # Use calibrated interpretation if available
                if self._model_calibration:
                    interpretation = self._model_calibration.output_interpretation
                    threshold = self._model_calibration.optimal_threshold
                    
                    if interpretation == "high_values_real":
                        # High values = Real faces, Low values = Fake faces
                        if avg_prob >= threshold:
                            prediction = "Real Video"
                            confidence = float(avg_prob)
                        else:
                            prediction = "Deepfake Detected"
                            confidence = float(1.0 - avg_prob)
                    else:
                        # High values = Fake faces, Low values = Real faces (default)
                        if avg_prob >= threshold:
                            prediction = "Deepfake Detected"
                            confidence = float(avg_prob)
                        else:
                            prediction = "Real Video"
                            confidence = float(1.0 - avg_prob)
                    
                    logger.info(f"🎯 Calibrated prediction: {prediction} ({confidence:.3f}) using {interpretation}")
                else:
                    # Default interpretation: high values = FAKE faces, low values = REAL faces
                    trained_model_threshold = 0.5
                    
                    if avg_prob >= trained_model_threshold:
                        prediction = "Deepfake Detected"
                        confidence = float(avg_prob)
                    else:
                        prediction = "Real Video"
                        confidence = float(1.0 - avg_prob)
                    
                    logger.info(f"🎯 Default prediction: {prediction} ({confidence:.3f})")
                
                return confidence, prediction
                
        except Exception as e:
            logger.error(f"Trained model prediction failed: {e}")
            return 0.5, "Prediction Failed"
    
    async def _predict_efficientnet(self, faces: List) -> Tuple[float, str]:
        """Predict using generic EfficientNet"""
        try:
            model = self.models['efficientnet']
            
            # Convert faces to tensors with ImageNet normalization
            face_tensors = []
            for face_data in faces:
                # Handle new face data format
                if isinstance(face_data, dict):
                    face = face_data['face']  # Extract the preprocessed face
                else:
                    face = face_data  # Legacy format
                
                if isinstance(face, np.ndarray):
                    face_resized = cv2.resize(face, (224, 224))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    
                    # Convert to tensor and normalize properly
                    face_tensor = torch.from_numpy(face_rgb).float() / 255.0
                    
                    # ImageNet normalization - apply to each channel
                    mean = torch.tensor([0.485, 0.456, 0.406])
                    std = torch.tensor([0.229, 0.224, 0.225])
                    
                    # Normalize each channel
                    for i in range(3):
                        face_tensor[:, :, i] = (face_tensor[:, :, i] - mean[i]) / std[i]
                    
                    # Convert from HWC to CHW format
                    face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0)
                    face_tensors.append(face_tensor)
            
            if not face_tensors:
                return 0.5, "No Valid Faces"
            
            # Batch process
            batch = torch.cat(face_tensors, dim=0).to(self.device)
            
            with torch.no_grad():
                outputs = model(batch)
                probabilities = torch.softmax(outputs, dim=1).cpu().numpy()
                
                # For generic EfficientNet, we'll use a simple heuristic
                # This is a placeholder - you might want to fine-tune this
                avg_confidence = np.mean(np.max(probabilities, axis=1))
                
                # Simple heuristic: high confidence = likely real, low confidence = likely fake
                if avg_confidence > 0.7:
                    prediction = "Real Video"
                    confidence = float(avg_confidence)
                else:
                    prediction = "Deepfake Detected"
                    confidence = float(1.0 - avg_confidence)
                
                return confidence, prediction
                
        except Exception as e:
            logger.error(f"EfficientNet prediction failed: {e}")
            return 0.5, "Prediction Failed"
    
    async def _predict_opencv_haar(self, faces: List) -> Tuple[float, str]:
        """Predict using optimized OpenCV face detection - ENHANCED for better accuracy"""
        try:
            detector = self.models['opencv_haar']
            
            # Check if we have the optimized detector
            if hasattr(detector, 'detect_faces_optimized'):
                return await self._predict_with_optimized_detector(detector, faces)
            else:
                # Fallback to basic OpenCV detection
                return await self._predict_with_basic_opencv(detector, faces)
            
        except Exception as e:
            logger.error(f"OpenCV prediction failed: {e}")
            return 0.02, "Prediction Failed"
    
    async def _predict_with_optimized_detector(self, detector, faces: List) -> Tuple[float, str]:
        """Predict using optimized face detector"""
        try:
            face_qualities = []
            successful_detections = 0
            
            for i, face_data in enumerate(faces):
                try:
                    # Handle both old format (numpy arrays) and new format (face data dict)
                    if isinstance(face_data, dict):
                        # New format: face_data contains 'face', 'frame', 'bbox'
                        face_crop = face_data['face']
                        original_frame = face_data['frame']
                        bbox = face_data['bbox']  # (x, y, w, h)
                        
                        # Use optimized detector on original frame
                        detected_faces, metadata = detector.detect_faces_optimized(original_frame)
                        
                        logger.info(f"🔍 Optimized OpenCV Face {i} (full frame): {len(detected_faces)} faces detected")
                        
                        # Check if any detected face overlaps with our extracted face region
                        best_quality = 0.0
                        face_found = False
                        
                        for j, (detected_face, meta) in enumerate(zip(detected_faces, metadata)):
                            detected_bbox = meta['bbox']
                            
                            # Calculate overlap
                            overlap = self._calculate_bbox_overlap(bbox, detected_bbox)
                            
                            if overlap > 0.2:  # 20% overlap threshold
                                face_found = True
                                
                                # Use quality from metadata if available
                                if 'quality' in meta:
                                    quality_score = meta['quality']['overall_score']
                                else:
                                    # Calculate quality manually
                                    quality_score = self._calculate_face_quality_manual(detected_face)
                                
                                best_quality = max(best_quality, quality_score)
                        
                        if face_found:
                            successful_detections += 1
                            face_qualities.append(best_quality)
                            logger.debug(f"Face {i} quality (optimized): {best_quality:.3f}")
                        else:
                            logger.debug(f"Face {i}: no overlapping detection in full frame")
                    
                    else:
                        # OLD FORMAT: Handle legacy numpy array format
                        face_np = face_data
                        
                        # Convert tensor to numpy if needed
                        if isinstance(face_np, torch.Tensor):
                            face_np = face_np.cpu().numpy()
                            
                            # Handle different tensor formats
                            if face_np.ndim == 3 and face_np.shape[0] == 3:  # (C, H, W)
                                face_np = face_np.transpose(1, 2, 0)  # Convert to (H, W, C)
                            
                            # CRITICAL FIX: Properly handle different tensor types
                            if face_np.dtype == np.uint8:
                                face_np = face_np
                            elif face_np.max() > 1.0:
                                face_np = np.clip(face_np, 0, 255).astype(np.uint8)
                            else:
                                face_np = (face_np * 255).astype(np.uint8)
                        
                        # Preprocess face for detection
                        processed_face = detector.preprocess_face_for_analysis(face_np)
                        
                        # Use optimized detector on processed face
                        detected_faces, metadata = detector.detect_faces_optimized(processed_face)
                        
                        logger.info(f"🔍 Optimized OpenCV Face {i} (cropped): {len(detected_faces)} faces found")
                        
                        if len(detected_faces) > 0:
                            successful_detections += 1
                            
                            # Calculate quality metrics on the best detection
                            best_quality = 0.0
                            for j, (detected_face, meta) in enumerate(zip(detected_faces, metadata)):
                                if 'quality' in meta:
                                    quality_score = meta['quality']['overall_score']
                                else:
                                    quality_score = self._calculate_face_quality_manual(detected_face)
                                
                                best_quality = max(best_quality, quality_score)
                            
                            face_qualities.append(best_quality)
                            logger.debug(f"Face {i} quality (optimized): {best_quality:.3f}")
                        else:
                            logger.debug(f"Face {i}: no detection in cropped face")
                        
                except Exception as face_error:
                    logger.warning(f"Optimized OpenCV: Error processing face {i}: {face_error}")
                    continue
            
            # Calculate final result
            total_faces = len(faces)
            detection_rate = successful_detections / total_faces if total_faces > 0 else 0
            
            if not face_qualities:
                logger.info(f"🔍 Optimized OpenCV: No face qualities calculated, detection rate: {detection_rate:.2f}")
                return 0.02, "No Face Detection"
            
            avg_quality = np.mean(face_qualities)
            logger.info(f"🔍 Optimized OpenCV final: {len(face_qualities)}/{total_faces} faces processed, avg_quality={avg_quality:.3f}, detection_rate={detection_rate:.2f}")
            
            # Adjust quality based on detection rate
            if detection_rate < 0.5:
                avg_quality *= 0.7  # Reduce quality score for low detection rate
            
            # Higher quality = more likely real
            if avg_quality > 0.5:
                prediction = "Real Video"
                confidence = float(avg_quality)
            else:
                prediction = "Deepfake Detected"
                confidence = float(1.0 - avg_quality)
            
            logger.info(f"🔍 Optimized OpenCV result: {prediction} ({confidence:.3f})")
            return confidence, prediction
            
        except Exception as e:
            logger.error(f"Optimized OpenCV prediction failed: {e}")
            return 0.02, "Prediction Failed"
    
    async def _predict_with_basic_opencv(self, cascade, faces: List) -> Tuple[float, str]:
        """Fallback prediction using basic OpenCV Haar cascade"""
        try:
            face_qualities = []
            successful_detections = 0
            
            for i, face_data in enumerate(faces):
                try:
                    # Handle face data format
                    if isinstance(face_data, dict):
                        face_crop = face_data['face']
                        original_frame = face_data['frame']
                        bbox = face_data['bbox']
                        
                        # Use original frame for detection
                        frame_gray = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
                        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                        frame_gray = clahe.apply(frame_gray)
                        
                        faces_detected = cascade.detectMultiScale(
                            frame_gray,
                            scaleFactor=1.02,  # More sensitive scaling
                            minNeighbors=2,
                            minSize=(30, 30),
                            flags=cv2.CASCADE_SCALE_IMAGE
                        )
                        
                        logger.info(f"🔍 Basic OpenCV Face {i} (full frame): {len(faces_detected)} faces detected")
                        
                        # Check for overlap and calculate quality
                        best_quality = 0.0
                        face_found = False
                        
                        for (fx, fy, fw, fh) in faces_detected:
                            overlap = self._calculate_bbox_overlap(bbox, (fx, fy, fw, fh))
                            
                            if overlap > 0.2:
                                face_found = True
                                face_roi = frame_gray[fy:fy+fh, fx:fx+fw]
                                quality_score = self._calculate_face_quality_manual(face_roi)
                                best_quality = max(best_quality, quality_score)
                        
                        if face_found:
                            successful_detections += 1
                            face_qualities.append(best_quality)
                    
                    else:
                        # Legacy format
                        face_np = face_data
                        
                        # Convert and preprocess
                        if isinstance(face_np, torch.Tensor):
                            face_np = face_np.cpu().numpy()
                            if face_np.ndim == 3 and face_np.shape[0] == 3:
                                face_np = face_np.transpose(1, 2, 0)
                            
                            if face_np.dtype != np.uint8:
                                if face_np.max() > 1.0:
                                    face_np = np.clip(face_np, 0, 255).astype(np.uint8)
                                else:
                                    face_np = (face_np * 255).astype(np.uint8)
                        
                        # Resize if too small
                        if face_np.shape[0] < 100 or face_np.shape[1] < 100:
                            target_size = max(100, max(face_np.shape[0], face_np.shape[1]))
                            face_np = cv2.resize(face_np, (target_size, target_size), interpolation=cv2.INTER_CUBIC)
                        
                        # Convert to grayscale
                        if len(face_np.shape) == 3:
                            gray = cv2.cvtColor(face_np, cv2.COLOR_BGR2GRAY)
                        else:
                            gray = face_np
                        
                        # Enhance contrast
                        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                        gray = clahe.apply(gray)
                        gray = cv2.GaussianBlur(gray, (3, 3), 0)
                        
                        # Detect faces
                        faces_detected = cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.02,  # More sensitive scaling
                            minNeighbors=2,    # More permissive neighbor requirement
                            minSize=(25, 25),
                            flags=cv2.CASCADE_SCALE_IMAGE
                        )
                        
                        logger.info(f"🔍 Basic OpenCV Face {i} (cropped): {len(faces_detected)} faces found")
                        
                        if len(faces_detected) > 0:
                            successful_detections += 1
                            best_quality = 0.0
                            
                            for (x, y, w, h) in faces_detected:
                                face_roi = gray[y:y+h, x:x+w]
                                quality_score = self._calculate_face_quality_manual(face_roi)
                                best_quality = max(best_quality, quality_score)
                            
                            face_qualities.append(best_quality)
                        
                except Exception as face_error:
                    logger.warning(f"Basic OpenCV: Error processing face {i}: {face_error}")
                    continue
            
            # Calculate final result
            total_faces = len(faces)
            detection_rate = successful_detections / total_faces if total_faces > 0 else 0
            
            if not face_qualities:
                logger.info(f"🔍 Basic OpenCV: No face qualities calculated, detection rate: {detection_rate:.2f}")
                return 0.02, "No Face Detection"
            
            avg_quality = np.mean(face_qualities)
            logger.info(f"🔍 Basic OpenCV final: {len(face_qualities)}/{total_faces} faces processed, avg_quality={avg_quality:.3f}, detection_rate={detection_rate:.2f}")
            
            if detection_rate < 0.5:
                avg_quality *= 0.7
            
            if avg_quality > 0.5:
                prediction = "Real Video"
                confidence = float(avg_quality)
            else:
                prediction = "Deepfake Detected"
                confidence = float(1.0 - avg_quality)
            
            logger.info(f"🔍 Basic OpenCV result: {prediction} ({confidence:.3f})")
            return confidence, prediction
            
        except Exception as e:
            logger.error(f"Basic OpenCV prediction failed: {e}")
            return 0.02, "Prediction Failed"
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        union_area = w1 * h1 + w2 * h2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0
    
    def _calculate_face_quality_manual(self, face_roi: np.ndarray) -> float:
        """Calculate face quality metrics manually"""
        try:
            # Enhanced quality metrics
            sharpness = cv2.Laplacian(face_roi, cv2.CV_64F).var()
            brightness = np.mean(face_roi)
            contrast = np.std(face_roi)
            
            # Additional quality metrics
            edges = cv2.Canny(face_roi, 50, 150)
            edge_density = np.sum(edges > 0) / (face_roi.shape[0] * face_roi.shape[1])
            
            # Combine metrics (higher = better quality = more likely real)
            quality_score = (
                (sharpness / 1000.0) * 0.3 +
                (brightness / 255.0) * 0.2 +
                (contrast / 100.0) * 0.3 +
                edge_density * 0.2
            )
            quality_score = min(1.0, max(0.0, quality_score))
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Face quality calculation failed: {e}")
            return 0.0
    
    async def _predict_mtcnn_quality(self, faces: List) -> Tuple[float, str]:
        """Predict using MTCNN face quality metrics"""
        try:
            mtcnn = self.models['mtcnn']
            
            face_qualities = []
            for i, face_data in enumerate(faces):
                try:
                    # Handle new face data format
                    if isinstance(face_data, dict):
                        face = face_data['face']  # Extract the preprocessed face
                    else:
                        face = face_data  # Legacy format
                    
                    # Convert tensor to numpy if needed
                    if isinstance(face, torch.Tensor):
                        face_np = face.cpu().numpy()
                        
                        # Handle different tensor formats
                        if face_np.ndim == 3 and face_np.shape[0] == 3:  # (C, H, W)
                            face_np = face_np.transpose(1, 2, 0)  # Convert to (H, W, C)
                        
                        # CRITICAL: Reverse ImageNet normalization first
                        # ImageNet mean: [0.485, 0.456, 0.406], std: [0.229, 0.224, 0.225]
                        mean = np.array([0.485, 0.456, 0.406])
                        std = np.array([0.229, 0.224, 0.225])
                        
                        # Reverse normalization: (normalized * std) + mean
                        face_np = (face_np * std) + mean
                        
                        # Clamp to [0, 1] and convert to [0, 255]
                        face_np = np.clip(face_np, 0.0, 1.0)
                        face_np = (face_np * 255).astype(np.uint8)
                        
                        logger.debug(f"MTCNN Face {i} converted: {face_np.shape}, dtype={face_np.dtype}, range=[{face_np.min()}-{face_np.max()}]")
                    elif isinstance(face, np.ndarray):
                        face_np = face
                        # If it's already a numpy array, ensure it's uint8
                        if face_np.dtype != np.uint8:
                            if face_np.max() <= 1.0:
                                face_np = (face_np * 255).astype(np.uint8)
                            else:
                                face_np = face_np.astype(np.uint8)
                    else:
                        logger.warning(f"MTCNN: Unexpected face type {type(face)}")
                        continue
                    
                    # Convert to RGB
                    face_rgb = cv2.cvtColor(face_np, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces with quality analysis
                    boxes, probs, landmarks = mtcnn.detect(face_rgb, landmarks=True)
                    logger.debug(f"Face {i} analysis: {len(boxes) if boxes is not None else 0} detections")
                    
                    if boxes is not None and len(boxes) > 0:
                        # Use detection confidence as quality metric
                        max_prob = np.max(probs)
                        
                        # Additional quality metrics if landmarks available
                        if landmarks is not None:
                            # Calculate landmark symmetry (higher = better)
                            left_eye = landmarks[0][0:2]
                            right_eye = landmarks[0][2:4]
                            nose = landmarks[0][4:6]
                            
                            # Simple symmetry check
                            eye_distance = np.linalg.norm(left_eye - right_eye)
                            left_nose_dist = np.linalg.norm(left_eye - nose)
                            right_nose_dist = np.linalg.norm(right_eye - nose)
                            
                            symmetry = 1.0 - abs(left_nose_dist - right_nose_dist) / eye_distance
                            symmetry = max(0.0, min(1.0, symmetry))
                            
                            # Combine detection confidence and symmetry
                            quality_score = (max_prob + symmetry) / 2.0
                            logger.debug(f"Face {i} quality: {quality_score:.3f} (prob: {max_prob:.3f}, symmetry: {symmetry:.3f})")
                        else:
                            quality_score = max_prob
                            logger.debug(f"Face {i} quality: {max_prob:.3f} (no landmarks)")
                        
                        face_qualities.append(quality_score)
                    else:
                        logger.debug(f"Face {i}: no detection")
                        
                except Exception as face_error:
                    logger.warning(f"MTCNN: Error processing face {i}: {face_error}")
                    continue
            
            if not face_qualities:
                return 0.5, "No Face Detection"
            
            avg_quality = np.mean(face_qualities)
            
            # Higher quality = more likely real
            if avg_quality > 0.5:
                prediction = "Real Video"
                confidence = float(avg_quality)
            else:
                prediction = "Deepfake Detected"
                confidence = float(1.0 - avg_quality)
            
            return confidence, prediction
            
        except Exception as e:
            logger.error(f"MTCNN quality prediction failed: {e}")
            return 0.5, "Prediction Failed"
    
    def _calculate_ensemble(self, model_scores: Dict[str, float], model_predictions: Dict[str, str]) -> Tuple[str, float]:
        """Calculate weighted ensemble prediction with adaptive thresholds and consensus scoring"""
        try:
            if not model_scores:
                return "No Predictions", 0.0
            
            # ✅ UNCERTAINTY DETECTION: Check for uncertain predictions (0.45-0.55)
            uncertain_models = []
            confident_models = []
            
            for model_name, score in model_scores.items():
                if 0.45 <= score <= 0.55:
                    uncertain_models.append(model_name)
                    logger.info(f"⚠️ {model_name} uncertain (score: {score:.3f})")
                else:
                    confident_models.append(model_name)
            
            # If majority of models are uncertain, default to "Real" to minimize false positives
            if len(uncertain_models) > len(confident_models):
                logger.info(f"⚠️ Majority uncertain ({len(uncertain_models)}/{len(model_scores)}), defaulting to Real to minimize false positives")
                return 0.40, "Real Video"  # Low fake score = Real
            
            # Import adaptive threshold calculator
            try:
                from .adaptive_threshold_calculator import calculate_adaptive_threshold
                from .detection_debug_logger import get_debug_logger
                
                # Calculate adaptive threshold based on consensus
                trained_model_score = model_scores.get('trained_model')
                trained_model_prediction = model_predictions.get('trained_model')
                
                threshold_decision = calculate_adaptive_threshold(
                    model_predictions, model_scores, trained_model_score, trained_model_prediction
                )
                
                # Log threshold decision
                debug_logger = get_debug_logger()
                if hasattr(debug_logger, 'log_threshold_decision'):
                    # This will be called from the main detection function
                    pass
                
                logger.info(f"🎯 Adaptive threshold: {threshold_decision.threshold:.3f} ({threshold_decision.reasoning})")
                
            except ImportError:
                logger.warning("⚠️ Adaptive threshold calculator not available, using default logic")
                threshold_decision = None
            
            # Dynamic weight adjustment based on model performance
            adjusted_weights = self.model_weights.copy()
            
            # Adjust OpenCV weight based on detection success
            if 'opencv_haar' in model_scores:
                opencv_pred = model_predictions.get('opencv_haar', '')
                if "No Face Detection" in opencv_pred or "Prediction Failed" in opencv_pred:
                    adjusted_weights['opencv_haar'] = 0.02  # Minimal weight when it fails
                    logger.info("🔧 OpenCV weight reduced due to detection failure")
            
            # Adjust trained model weight based on consensus
            if 'trained_model' in model_scores and threshold_decision:
                if threshold_decision.uncertainty_flag:
                    adjusted_weights['trained_model'] *= 0.8  # Reduce weight when uncertain
                    logger.info("🔧 Trained model weight reduced due to uncertainty")
                
                # Check consensus with other models
                other_models_agree = 0
                total_other_models = 0
                
                for model_name, pred in model_predictions.items():
                    if model_name != 'trained_model':
                        total_other_models += 1
                        if ("Deepfake" in trained_model_prediction and "Deepfake" in pred) or \
                           ("Real" in trained_model_prediction and "Real" in pred):
                            other_models_agree += 1
                
                if total_other_models > 0:
                    agreement_ratio = other_models_agree / total_other_models
                    if agreement_ratio < 0.5:  # Less than 50% agreement
                        adjusted_weights['trained_model'] *= 0.9  # Slight reduction
                        logger.info(f"🔧 Trained model weight reduced due to low consensus ({agreement_ratio:.2f})")
            
            # Separate real and fake scores with adjusted weights
            real_scores = []
            fake_scores = []
            total_weight = 0.0
            
            for model_name, score in model_scores.items():
                weight = adjusted_weights.get(model_name, 0.1)
                prediction = model_predictions.get(model_name, "Unknown")
                
                if "Real" in prediction:
                    real_scores.append(score * weight)
                elif "Deepfake" in prediction or "Fake" in prediction:
                    fake_scores.append(score * weight)
                
                total_weight += weight
            
            # Calculate weighted averages
            real_weighted_avg = sum(real_scores) / total_weight if real_scores else 0.0
            fake_weighted_avg = sum(fake_scores) / total_weight if fake_scores else 0.0
            
            logger.info(f"📊 Ensemble analysis - Real: {real_weighted_avg:.3f}, Fake: {fake_weighted_avg:.3f}, Weight: {total_weight:.3f}")
            
            # PRIORITY 0: Artifact detection analysis (disabled in ensemble calculation)
            artifact_score = 0.0
            # Note: Artifact detection requires faces parameter which is not available in this context
            # This will be handled at the higher level in the hybrid detection pipeline
            
            # PRIORITY 1: Trained model high confidence override
            trained_model_score = model_scores.get('trained_model')
            trained_model_prediction = model_predictions.get('trained_model')
            
            if trained_model_score and trained_model_prediction:
                # Check if other models disagree with trained model
                other_models_disagree = 0
                total_other_models = 0
                
                for model_name, pred in model_predictions.items():
                    if model_name != 'trained_model':
                        total_other_models += 1
                        # Check if this model disagrees with trained model
                        if not self._models_agree(trained_model_prediction, pred):
                            other_models_disagree += 1
                
                # AGGRESSIVE STRATEGY: If trained model says "Deepfake" and 2+ other models disagree, trust trained model
                if (trained_model_prediction == "Deepfake Detected" and 
                    other_models_disagree >= 2 and total_other_models >= 2 and
                    trained_model_score > 0.65):  # Lower threshold for deepfake detection
                    
                    logger.info(f"🎯 TRAINED MODEL DEEPFAKE OVERRIDE: {trained_model_prediction} ({trained_model_score:.3f}) - {other_models_disagree}/{total_other_models} other models disagree")
                    final_prediction = trained_model_prediction
                    final_confidence = min(0.85, trained_model_score + 0.15)  # Boost confidence
                    logger.info(f"🎯 Final ensemble result: {final_prediction} (confidence: {final_confidence:.3f}) - TRAINED MODEL DEEPFAKE OVERRIDE")
                    return final_prediction, final_confidence
                
                # Original high confidence override for very confident predictions
                elif trained_model_score > 0.8:
                    if other_models_disagree >= 2 and total_other_models >= 2:
                        logger.info(f"🎯 TRAINED MODEL HIGH CONFIDENCE OVERRIDE: {trained_model_prediction} ({trained_model_score:.3f}) - {other_models_disagree}/{total_other_models} other models disagree")
                        final_prediction = trained_model_prediction
                        final_confidence = trained_model_score
                        logger.info(f"🎯 Final ensemble result: {final_prediction} (confidence: {final_confidence:.3f}) - TRAINED MODEL OVERRIDE")
                        return final_prediction, final_confidence
            
            # Use adaptive threshold if available
            if threshold_decision:
                deepfake_threshold = threshold_decision.threshold
                confidence_boost = threshold_decision.confidence_boost
                
                # Apply fallback logic for strong disagreements
                if threshold_decision.fallback_recommendation == "bias_toward_real":
                    logger.info("🛡️ Biasing toward Real Video due to model disagreement")
                    final_prediction = "Real Video"
                    final_confidence = max(0.6, real_weighted_avg + 0.1)  # Boost real confidence
                elif threshold_decision.fallback_recommendation == "trust_trained_model_high_confidence":
                    # Use trained model prediction directly when it has high confidence
                    logger.info("🎯 Trusting trained model high confidence prediction")
                    final_prediction = trained_model_prediction
                    final_confidence = trained_model_score
                else:
                    # Standard threshold-based decision
                    if fake_weighted_avg > real_weighted_avg and fake_weighted_avg > deepfake_threshold:
                        final_prediction = "Deepfake Detected"
                        final_confidence = fake_weighted_avg
                    else:
                        final_prediction = "Real Video"
                        final_confidence = max(real_weighted_avg, 1.0 - fake_weighted_avg)
                
                # Apply confidence boost/penalty
                final_confidence = max(0.0, min(1.0, final_confidence + confidence_boost))
                
                # PRIORITY 3: Artifact detection override (disabled in ensemble calculation)
                # Artifact detection is handled at the higher level in hybrid detection pipeline
                
                # PRIORITY 4: Special case - trained model says deepfake but others say real
                if (trained_model_prediction == "Deepfake Detected" and 
                    "Real" in final_prediction and 
                    trained_model_score > 0.6):
                    logger.info(f"🎯 TRAINED MODEL DISAGREEMENT: Trained model says Deepfake ({trained_model_score:.3f}) but ensemble says Real - trusting trained model")
                    final_prediction = "Deepfake Detected"
                    final_confidence = min(0.8, trained_model_score + 0.1)
                
            else:
                # Fallback to standard logic
                deepfake_threshold = 0.5
                
                if fake_weighted_avg > real_weighted_avg and fake_weighted_avg > deepfake_threshold:
                    final_prediction = "Deepfake Detected"
                    final_confidence = fake_weighted_avg
                else:
                    final_prediction = "Real Video"
                    final_confidence = max(real_weighted_avg, 1.0 - fake_weighted_avg)
                
                # Apply same overrides in fallback case (artifact detection disabled)
                # Artifact detection is handled at the higher level in hybrid detection pipeline
                
                if (trained_model_prediction == "Deepfake Detected" and 
                    "Real" in final_prediction and 
                    trained_model_score > 0.6):
                    logger.info(f"🎯 FALLBACK TRAINED MODEL DISAGREEMENT: Trained model says Deepfake ({trained_model_score:.3f}) but ensemble says Real - trusting trained model")
                    final_prediction = "Deepfake Detected"
                    final_confidence = min(0.8, trained_model_score + 0.1)
            
            logger.info(f"🎯 Final ensemble result: {final_prediction} (confidence: {final_confidence:.3f})")
            
            return final_prediction, final_confidence
            
        except Exception as e:
            logger.error(f"Ensemble calculation failed: {e}")
            return "Ensemble Failed", 0.0
    
    def _models_agree(self, pred1: str, pred2: str) -> bool:
        """Check if two model predictions agree"""
        if not pred1 or not pred2:
            return False
        
        # Both say real
        if ("Real" in pred1 and "Real" in pred2):
            return True
        
        # Both say fake/deepfake
        if (("Deepfake" in pred1 or "Fake" in pred1) and 
            ("Deepfake" in pred2 or "Fake" in pred2)):
            return True
        
        return False

# Global instance
core_ensemble_detector = CoreEnsembleDetector()
