# backend/app/services/unified_detection_pipeline.py - Unified Detection Pipeline

import cv2
import numpy as np
import torch
import logging
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import time

from .deepfake_detector import detector as deepfake_detector
from .metadata_classifier import metadata_classifier
from .preprocessing import production_preprocessor

logger = logging.getLogger(__name__)

class UnifiedDetectionPipeline:
    """Unified detection pipeline for all video sources (YouTube, uploaded, etc.)"""
    
    def __init__(self):
        """Initialize the unified detection pipeline"""
        self.deepfake_detector = deepfake_detector
        self.metadata_classifier = metadata_classifier
        self.preprocessor = production_preprocessor
        
        # Detection configuration
        self.default_threshold = 0.5
        self.max_faces_per_frame = 5
        self.frame_sample_rate = 30  # Process every 30th frame
        
        logger.info("[OK] UnifiedDetectionPipeline initialized")
    
    async def detect_deepfake_unified(self, 
                                    video_path: str,
                                    metadata: Dict = None,
                                    filename: str = "",
                                    user_description: str = "") -> Dict[str, Any]:
        """
        Unified deepfake detection for all video sources
        
        Args:
            video_path: Path to video file
            metadata: Video metadata (for YouTube videos)
            filename: Original filename (for uploaded videos)
            user_description: User-provided description (for uploaded videos)
            
        Returns:
            Detection results with bias and metadata flags
        """
        try:
            start_time = time.time()
            logger.info(f"🔍 Starting unified detection for: {Path(video_path).name}")
            
            # Step 1: Extract faces from video
            faces = await self._extract_faces_from_video(video_path)
            
            if not faces:
                return {
                    "status": "completed",
                    "final_result": "no_faces",
                    "confidence": 0.0,
                    "faces_analyzed": 0,
                    "bias_applied": 0.0,
                    "metadata_flags": [],
                    "error": "No faces detected in video"
                }
            
            # Step 2: Classify metadata for bias
            bias_score, metadata_flags = await self._classify_metadata_for_bias(
                metadata, filename, user_description
            )
            
            # Step 3: Run deepfake detection on faces
            detection_result, base_confidence = await self._run_deepfake_detection(faces)
            
            # Step 4: Apply bias to confidence
            final_confidence = await self._apply_bias_to_confidence(
                base_confidence, bias_score, detection_result
            )
            
            # Step 5: Determine final result
            final_result = await self._determine_final_result(
                final_confidence, detection_result
            )
            
            processing_time = time.time() - start_time
            
            result = {
                "status": "completed",
                "final_result": final_result,
                "confidence": round(final_confidence, 2),
                "faces_analyzed": len(faces),
                "bias_applied": round(bias_score, 3),
                "metadata_flags": metadata_flags,
                "processing_time": round(processing_time, 2),
                "base_confidence": round(base_confidence, 2),
                "detection_method": "unified_pipeline"
            }
            
            logger.info(f"[OK] Unified detection completed: {final_result} ({final_confidence:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Unified detection failed: {e}")
            return {
                "status": "error",
                "final_result": "error",
                "confidence": 0.0,
                "faces_analyzed": 0,
                "bias_applied": 0.0,
                "metadata_flags": [],
                "error": str(e)
            }
    
    async def _extract_faces_from_video(self, video_path: str) -> List[np.ndarray]:
        """Extract faces from video using YOLOv8 with Haar cascade fallback"""
        try:
            faces = []
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"📹 Processing video: {total_frames} frames")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames for efficiency
                if frame_count % self.frame_sample_rate == 0:
                    # Try YOLOv8 first
                    frame_faces = self._detect_faces_yolo(frame)
                    
                    # Fallback to Haar cascade if YOLOv8 fails
                    if not frame_faces:
                        frame_faces = self._detect_faces_haar(frame)
                    
                    # Limit faces per frame
                    frame_faces = frame_faces[:self.max_faces_per_frame]
                    faces.extend(frame_faces)
                    
                    if len(faces) >= 50:  # Limit total faces for performance
                        break
                
                frame_count += 1
            
            cap.release()
            logger.info(f"[OK] Extracted {len(faces)} faces from {frame_count} frames")
            return faces
            
        except Exception as e:
            logger.error(f"[ERROR] Face extraction failed: {e}")
            return []
    
    def _detect_faces_yolo(self, frame: np.ndarray) -> List[np.ndarray]:
        """Detect faces using YOLOv8"""
        try:
            if self.deepfake_detector.yolo_model is None:
                return []
            
            return self.deepfake_detector.detect_faces_yolo(frame)
            
        except Exception as e:
            logger.warning(f"YOLOv8 face detection failed: {e}")
            return []
    
    def _detect_faces_haar(self, frame: np.ndarray) -> List[np.ndarray]:
        """Detect faces using Haar cascade (fallback)"""
        try:
            # Load Haar cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Extract face regions
            face_crops = []
            for (x, y, w, h) in faces:
                face_crop = frame[y:y+h, x:x+w]
                if face_crop.size > 0:
                    face_crops.append(face_crop)
            
            return face_crops
            
        except Exception as e:
            logger.warning(f"Haar cascade face detection failed: {e}")
            return []
    
    async def _classify_metadata_for_bias(self, 
                                        metadata: Dict = None,
                                        filename: str = "",
                                        user_description: str = "") -> Tuple[float, List[str]]:
        """Classify metadata to determine bias score"""
        try:
            if metadata:
                # YouTube video metadata
                return self.metadata_classifier.classify_youtube_metadata(metadata)
            else:
                # Uploaded file metadata
                return self.metadata_classifier.classify_uploaded_file(filename, user_description)
                
        except Exception as e:
            logger.error(f"[ERROR] Metadata classification failed: {e}")
            return 0.0, []
    
    async def _run_deepfake_detection(self, faces: List[np.ndarray]) -> Tuple[str, float]:
        """Run deepfake detection on extracted faces"""
        try:
            if not faces:
                return "No Faces Detected", 0.0
            
            # Use the enhanced deepfake detector
            result, confidence = self.deepfake_detector.detect_deepfake(faces)
            
            return result, confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Deepfake detection failed: {e}")
            return "Detection Failed", 0.0
    
    async def _apply_bias_to_confidence(self, 
                                      base_confidence: float,
                                      bias_score: float,
                                      detection_result: str) -> float:
        """Apply balanced metadata bias to confidence score - FIXED for unbiased detection"""
        try:
            if bias_score == 0.0:
                return base_confidence
            
            # ✅ BIAS FIX: Apply balanced bias that works for both real and fake content
            # Instead of one-sided bias, apply metadata-based adjustment that considers both directions
            
            # Calculate balanced adjustment based on metadata confidence
            metadata_adjustment = bias_score * 0.3  # Reduced from 1.0 to 0.3 for balance
            
            # Apply adjustment based on detection result with balanced approach
            if "Deepfake" in detection_result or "fake" in detection_result.lower():
                # If detected as fake and metadata supports it, moderate boost
                biased_confidence = base_confidence + (metadata_adjustment * 50)
                logger.info(f"🔍 Metadata supports fake detection: +{metadata_adjustment * 50:.1f}%")
            elif "Real" in detection_result or "real" in detection_result.lower():
                # If detected as real but metadata suggests fake, moderate reduction
                biased_confidence = max(base_confidence - (metadata_adjustment * 30), 5.0)
                logger.info(f"🔍 Metadata suggests fake for real detection: -{metadata_adjustment * 30:.1f}%")
            else:
                # Uncertain case, apply minimal balanced bias
                biased_confidence = base_confidence + (metadata_adjustment * 20)
                logger.info(f"🔍 Uncertain case with metadata: ±{metadata_adjustment * 20:.1f}%")
            
            # Ensure confidence stays within reasonable bounds
            biased_confidence = max(5.0, min(95.0, biased_confidence))
            
            logger.info(f"🔍 Balanced bias applied: base={base_confidence:.2f}, metadata={bias_score:.3f}, final={biased_confidence:.2f}")
            
            return biased_confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Bias application failed: {e}")
            return base_confidence
    
    async def _determine_final_result(self, 
                                    final_confidence: float,
                                    detection_result: str) -> str:
        """Determine final result based on confidence and detection"""
        try:
            # Use threshold to determine final classification
            if final_confidence >= (self.default_threshold * 100):
                if "Deepfake" in detection_result or "fake" in detection_result.lower():
                    return "deepfake"
                else:
                    return "real"
            else:
                if "Real" in detection_result or "real" in detection_result.lower():
                    return "real"
                else:
                    return "deepfake"
                    
        except Exception as e:
            logger.error(f"[ERROR] Final result determination failed: {e}")
            return "uncertain"
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline configuration and status"""
        return {
            "pipeline_name": "unified_detection_pipeline",
            "version": "1.0.0",
            "features": [
                "yolo_face_detection",
                "haar_cascade_fallback",
                "metadata_classification",
                "bias_application",
                "tensor_normalization_fix",
                "confidence_consistency"
            ],
            "threshold": self.default_threshold,
            "max_faces_per_frame": self.max_faces_per_frame,
            "frame_sample_rate": self.frame_sample_rate,
            "models_loaded": self.deepfake_detector.models_loaded if hasattr(self.deepfake_detector, 'models_loaded') else False
        }

# Global pipeline instance
unified_pipeline = UnifiedDetectionPipeline()

async def detect_deepfake_unified(video_path: str, 
                                metadata: Dict = None,
                                filename: str = "",
                                user_description: str = "") -> Dict[str, Any]:
    """Convenience function for unified detection"""
    return await unified_pipeline.detect_deepfake_unified(video_path, metadata, filename, user_description)

def get_unified_pipeline() -> UnifiedDetectionPipeline:
    """Get the global unified pipeline instance"""
    return unified_pipeline
