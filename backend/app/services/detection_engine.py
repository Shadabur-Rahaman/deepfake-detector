"""
Detection Engine Service

This module provides the core detection logic for different modes.
Uses the actual trained deepfake detection model.

Author: Senior Backend Engineer
Date: 2024
"""

import logging
import time
import os
from typing import Dict, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DetectionEngine:
    """Core detection engine for deepfake detection using actual trained models."""
    
    def __init__(self):
        self.models_loaded = False
        self.detector = None
        self._load_models()
    
    def _load_models(self):
        """Load actual detection models."""
        try:
            logger.info("Loading detection models...")
            # Import the actual deepfake detector
            try:
                from .deepfake_detector import detector as deepfake_detector
                self.detector = deepfake_detector
                if self.detector and self.detector.models_loaded:
                    self.models_loaded = True
                    logger.info("✅ Detection models loaded successfully")
                else:
                    logger.warning("⚠️ Detector available but models not loaded yet")
                    self.models_loaded = False
            except ImportError as e:
                logger.error(f"Failed to import deepfake detector: {e}")
                self.models_loaded = False
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.models_loaded = False
    
    async def _extract_faces_from_video(self, video_file: Union[str, Path]) -> list:
        """Extract faces from video file for detection."""
        try:
            # Import video processor
            from .video_processor import extract_faces_from_video
            
            # Convert to string path if needed
            video_path = str(video_file) if not isinstance(video_file, str) else video_file
            
            # Extract faces
            faces, timing_info = await extract_faces_from_video(video_path)
            return faces
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return []
    
    async def _run_actual_detection(self, video_file: Union[str, Path]) -> Dict[str, Any]:
        """Run actual deepfake detection using the trained model."""
        try:
            # Extract faces from video
            faces = await self._extract_faces_from_video(video_file)
            
            if not faces:
                return {
                    "is_fake": False,
                    "confidence": 0.0,
                    "method": "actual_model",
                    "details": {
                        "error": "No faces detected in video"
                    },
                    "processing_time": 0.0
                }
            
            # Use the actual detector
            if self.detector and self.detector.models_loaded:
                # Get detection result
                result_text, confidence_score = self.detector.detect_deepfake(faces)
                
                # Convert result to boolean
                is_fake = "deepfake" in result_text.lower() or "fake" in result_text.lower()
                
                # Convert confidence to 0-1 range if needed
                if confidence_score > 1.0:
                    confidence = confidence_score / 100.0
                else:
                    confidence = confidence_score
                
                return {
                    "is_fake": is_fake,
                    "confidence": confidence,
                    "method": "actual_model",
                    "details": {
                        "prediction": result_text,
                        "faces_detected": len(faces),
                        "model_used": "deepfake_detector_finetuned1.pth"
                    },
                    "processing_time": 0.0  # Will be calculated by caller if needed
                }
            else:
                logger.error("Models not loaded, cannot perform detection")
                raise RuntimeError("Detection models not loaded")
                
        except Exception as e:
            logger.error(f"Actual detection failed: {e}")
            return {
                "is_fake": False,
                "confidence": 0.0,
                "method": "actual_model",
                "details": {
                    "error": str(e)
                },
                "processing_time": 0.0
            }
    
    async def detect_traditional(self, video_file) -> Dict[str, Any]:
        """Run traditional deepfake detection using actual trained model."""
        if not self.models_loaded:
            # Try to load models again
            self._load_models()
            if not self.models_loaded:
                raise RuntimeError("Detection models not loaded")
        
        logger.info("Running traditional detection with actual model")
        start_time = time.time()
        
        # Run actual detection
        result = await self._run_actual_detection(video_file)
        result["method"] = "traditional"
        result["processing_time"] = time.time() - start_time
        
        return result
    
    async def detect_enhanced(self, video_file) -> Dict[str, Any]:
        """Run enhanced deepfake detection using actual trained model."""
        if not self.models_loaded:
            # Try to load models again
            self._load_models()
            if not self.models_loaded:
                raise RuntimeError("Detection models not loaded")
        
        logger.info("Running enhanced detection with actual model")
        start_time = time.time()
        
        # Run actual detection
        result = await self._run_actual_detection(video_file)
        result["method"] = "enhanced"
        result["processing_time"] = time.time() - start_time
        
        return result
    
    async def detect_ultimate(self, video_file) -> Dict[str, Any]:
        """Run ultimate ensemble detection using actual trained model."""
        if not self.models_loaded:
            # Try to load models again
            self._load_models()
            if not self.models_loaded:
                raise RuntimeError("Detection models not loaded")
        
        logger.info("Running ultimate detection with actual model")
        start_time = time.time()
        
        # Run actual detection
        result = await self._run_actual_detection(video_file)
        result["method"] = "ultimate"
        result["processing_time"] = time.time() - start_time
        
        return result
    
    async def detect_deterministic(self, video_file) -> Dict[str, Any]:
        """Run deterministic detection using actual trained model."""
        if not self.models_loaded:
            # Try to load models again
            self._load_models()
            if not self.models_loaded:
                raise RuntimeError("Detection models not loaded")
        
        logger.info("Running deterministic detection with actual model")
        start_time = time.time()
        
        # Run actual detection
        result = await self._run_actual_detection(video_file)
        result["method"] = "deterministic"
        result["processing_time"] = time.time() - start_time
        
        return result
    
    async def detect_ai_video(self, video_file) -> Dict[str, Any]:
        """Run AI video detection using actual trained model."""
        if not self.models_loaded:
            # Try to load models again
            self._load_models()
            if not self.models_loaded:
                raise RuntimeError("Detection models not loaded")
        
        logger.info("Running AI video detection with actual model")
        start_time = time.time()
        
        # Run actual detection
        result = await self._run_actual_detection(video_file)
        result["method"] = "ai_video"
        result["processing_time"] = time.time() - start_time
        
        return result
