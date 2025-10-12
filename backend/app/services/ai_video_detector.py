# backend/app/services/ai_video_detector.py - Comprehensive AI Video Detection Service

import asyncio
import logging
import time
import torch
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from collections import deque
import hashlib
import json
from datetime import datetime
from pathlib import Path

# Import existing services
from .deterministic_ensemble_detector import DeterministicEnsembleDetector, get_ensemble_detector
from .deterministic_face_detector import detect_faces_deterministic
from .metadata_classifier import metadata_classifier
from .youtube_service import youtube_downloader, YOUTUBE_AVAILABLE
from .logger import get_logger

logger = get_logger(__name__)

@dataclass
class DetectionResult:
    """Final detection result with all required fields"""
    label: str  # "Authentic", "Deepfake", or "Uncertain"
    confidence: float  # 0-100
    color: str  # "green", "orange", "red"
    metadata_bias: float  # Metadata bias score
    mean_probability: float  # Mean face probability
    temporal_smoothed: bool  # Whether temporal smoothing was applied
    processing_time: float  # Total processing time in ms
    frames_analyzed: int  # Number of frames analyzed
    faces_detected: int  # Total faces detected
    model_agreement: bool  # Whether models agreed on the result

class TemporalSmoother:
    """Enhanced temporal smoothing for stable video-level results"""
    
    def __init__(self, window_size: int = 5, alpha: float = 0.3):
        self.window_size = window_size
        self.alpha = alpha
        self.probability_history: deque = deque(maxlen=window_size)
        self.frame_results: deque = deque(maxlen=window_size)
        
    def add_frame_result(self, frame_prob: float, frame_decision: str) -> Tuple[float, str]:
        """Add frame result and return smoothed probability and decision"""
        self.probability_history.append(frame_prob)
        self.frame_results.append(frame_decision)
        
        if len(self.probability_history) < 3:
            return frame_prob, frame_decision
        
        # Calculate smoothed probability using EWMA
        recent_probs = list(self.probability_history)[-3:]
        smoothed_prob = recent_probs[0]  # Start with most recent
        
        for i in range(1, len(recent_probs)):
            smoothed_prob = self.alpha * recent_probs[i] + (1 - self.alpha) * smoothed_prob
        
        # Count recent decisions
        recent_decisions = list(self.frame_results)[-3:]
        fake_count = sum(1 for d in recent_decisions if "Deepfake" in d)
        real_count = sum(1 for d in recent_decisions if "Real" in d)
        
        # Apply temporal smoothing logic
        if fake_count >= 2 and smoothed_prob < 0.4:
            smoothed_decision = "Deepfake Detected"
            smoothed_prob = max(smoothed_prob * 0.8, 0.1)  # Increase fake probability
        elif real_count >= 2 and smoothed_prob > 0.6:
            smoothed_decision = "Real Face"
            smoothed_prob = min(smoothed_prob * 1.2, 0.9)  # Increase real probability
        else:
            smoothed_decision = frame_decision
            smoothed_prob = max(0.05, min(0.95, smoothed_prob))
        
        return smoothed_prob, smoothed_decision

class AIVideoDetector:
    """Comprehensive AI video detection service with multi-stage pipeline"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ensemble_detector = None
        self.temporal_smoother = TemporalSmoother(window_size=5, alpha=0.3)
        
        # Detection thresholds as specified in requirements
        self.thresholds = {
            "authentic_threshold": 0.45,  # <= 0.45 = Authentic
            "uncertain_min": 0.45,       # 0.45 < x < 0.55 = Uncertain
            "uncertain_max": 0.55,       # 0.45 < x < 0.55 = Uncertain
            "deepfake_threshold": 0.55,  # >= 0.55 = Deepfake
            "max_frames": 30,            # Maximum frames to analyze
            "max_faces_per_frame": 5     # Maximum faces per frame
        }
        
        # Statistics
        self.stats = {
            'videos_processed': 0,
            'total_processing_time': 0.0,
            'frames_processed': 0,
            'faces_detected': 0,
            'temporal_corrections': 0
        }
        
        # Reduced logging to avoid duplicates
    
    async def initialize_models(self) -> bool:
        """Initialize the ensemble detector"""
        try:
            if not self.ensemble_detector:
                self.ensemble_detector = await get_ensemble_detector()
            return True
        except Exception as e:
            logger.error(f"[ERROR] Model initialization failed: {e}")
            return False
    
    def extract_faces_from_video(self, video_path: str) -> Tuple[List[np.ndarray], int, int]:
        """Extract faces from video with frame sampling"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame sampling interval
            max_frames = self.thresholds["max_frames"]
            frame_interval = max(1, total_frames // max_frames) if total_frames > max_frames else 1
            
            all_faces = []
            frames_processed = 0
            total_faces = 0
            
            logger.info(f"📹 Processing video: {total_frames} frames, sampling every {frame_interval} frames")
            
            frame_id = 0
            while cap.isOpened() and frames_processed < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames
                if frame_id % frame_interval == 0:
                    # Detect faces in frame
                    faces = detect_faces_deterministic(frame)
                    
                    if faces:
                        # Limit faces per frame
                        faces = faces[:self.thresholds["max_faces_per_frame"]]
                        all_faces.extend(faces)
                        total_faces += len(faces)
                        logger.info(f"📸 Frame {frame_id}: {len(faces)} faces detected")
                    
                    frames_processed += 1
                
                frame_id += 1
            
            cap.release()
            
            logger.info(f"[OK] Face extraction complete: {frames_processed} frames, {total_faces} faces")
            return all_faces, frames_processed, total_faces
            
        except Exception as e:
            logger.error(f"[ERROR] Face extraction failed: {e}")
            return [], 0, 0
    
    def calculate_frame_probabilities(self, faces: List[np.ndarray]) -> List[float]:
        """Calculate probabilities for each face using ensemble detection"""
        try:
            if not faces:
                return []
            
            # Use ensemble detector to get probabilities
            if not self.ensemble_detector:
                logger.warning("[WARNING] Ensemble detector not initialized, using fallback")
                return [0.5] * len(faces)  # Neutral probability
            
            # Process faces in batches for efficiency
            batch_size = 10
            all_probabilities = []
            
            for i in range(0, len(faces), batch_size):
                batch_faces = faces[i:i + batch_size]
                
                # Run ensemble detection on batch
                ensemble_result = asyncio.run(self.ensemble_detector.detect_ensemble(batch_faces))
                
                # Extract probabilities (convert confidence to probability)
                batch_probs = []
                for face_idx in range(len(batch_faces)):
                    # Use the ensemble result for all faces in batch
                    if "Deepfake" in ensemble_result.final_prediction:
                        prob = ensemble_result.final_confidence / 100.0
                    else:
                        prob = 1.0 - (ensemble_result.final_confidence / 100.0)
                    
                    batch_probs.append(prob)
                
                all_probabilities.extend(batch_probs)
            
            return all_probabilities
            
        except Exception as e:
            logger.error(f"[ERROR] Frame probability calculation failed: {e}")
            return [0.5] * len(faces) if faces else []
    
    def aggregate_frame_probabilities(self, probabilities: List[float]) -> float:
        """Aggregate frame probabilities using mean, median, max"""
        try:
            if not probabilities:
                return 0.5  # Neutral probability
            
            # Calculate different aggregation methods
            mean_prob = np.mean(probabilities)
            median_prob = np.median(probabilities)
            max_prob = np.max(probabilities)
            
            # Weighted combination: 60% mean, 30% median, 10% max
            aggregated_prob = (0.6 * mean_prob + 0.3 * median_prob + 0.1 * max_prob)
            
            logger.info(f"🔍 Probability aggregation: mean={mean_prob:.3f}, median={median_prob:.3f}, max={max_prob:.3f}, final={aggregated_prob:.3f}")
            
            return aggregated_prob
            
        except Exception as e:
            logger.error(f"[ERROR] Probability aggregation failed: {e}")
            return 0.5
    
    def apply_temporal_smoothing(self, probabilities: List[float]) -> Tuple[float, bool]:
        """Apply temporal smoothing to reduce noise"""
        try:
            if len(probabilities) < 3:
                return np.mean(probabilities) if probabilities else 0.5, False
            
            # Apply temporal smoothing
            smoothed_probs = []
            for prob in probabilities:
                # Convert probability to decision for smoothing
                decision = "Deepfake Detected" if prob < 0.5 else "Real Face"
                smoothed_prob, _ = self.temporal_smoother.add_frame_result(prob, decision)
                smoothed_probs.append(smoothed_prob)
            
            # Check if smoothing changed results significantly
            original_mean = np.mean(probabilities)
            smoothed_mean = np.mean(smoothed_probs)
            temporal_smoothed = abs(original_mean - smoothed_mean) > 0.1
            
            if temporal_smoothed:
                self.stats['temporal_corrections'] += 1
            
            logger.info(f"🔍 Temporal smoothing: original={original_mean:.3f}, smoothed={smoothed_mean:.3f}, changed={temporal_smoothed}")
            
            return smoothed_mean, temporal_smoothed
            
        except Exception as e:
            logger.error(f"[ERROR] Temporal smoothing failed: {e}")
            return np.mean(probabilities) if probabilities else 0.5, False
    
    def calculate_metadata_bias(self, metadata: Dict = None, filename: str = "") -> float:
        """Calculate metadata bias score based on AI tool keywords"""
        try:
            if not metadata and not filename:
                return 0.0
            
            if metadata:
                # YouTube metadata
                bias_score, keywords = metadata_classifier.classify_youtube_metadata(metadata)
            else:
                # Uploaded file metadata
                bias_score, keywords = metadata_classifier.classify_uploaded_file(filename)
            
            logger.info(f"🔍 Metadata bias: {bias_score:.3f}, keywords: {keywords}")
            return bias_score
            
        except Exception as e:
            logger.error(f"[ERROR] Metadata bias calculation failed: {e}")
            return 0.0
    
    def calculate_final_probability(self, mean_prob: float, metadata_bias: float) -> float:
        """Calculate final probability with metadata bias adjustment"""
        try:
            # Apply metadata bias as specified: final_prob = clip(mean_prob + metadata_bias, 0, 1)
            final_prob = np.clip(mean_prob + metadata_bias, 0.0, 1.0)
            
            logger.info(f"🔍 Final probability: mean_prob={mean_prob:.3f}, metadata_bias={metadata_bias:.3f}, final={final_prob:.3f}")
            
            return final_prob
            
        except Exception as e:
            logger.error(f"[ERROR] Final probability calculation failed: {e}")
            return mean_prob
    
    def classify_result(self, final_prob: float) -> Tuple[str, str]:
        """Classify result based on final probability"""
        try:
            if final_prob <= self.thresholds["authentic_threshold"]:
                return "Authentic", "green"
            elif final_prob < self.thresholds["uncertain_max"]:
                return "Uncertain", "orange"
            else:
                return "Deepfake Detected", "red"
                
        except Exception as e:
            logger.error(f"[ERROR] Result classification failed: {e}")
            return "Uncertain", "orange"
    
    async def detect_video(self, video_path: str, metadata: Dict = None, filename: str = "") -> DetectionResult:
        """Main detection method for video analysis"""
        try:
            start_time = time.time()
            logger.info(f"🎬 Starting AI video detection: {video_path}")
            
            # Initialize models if needed
            if not self.ensemble_detector:
                await self.initialize_models()
            
            # Step 1: Extract faces from video
            faces, frames_analyzed, faces_detected = self.extract_faces_from_video(video_path)
            
            if not faces:
                logger.warning("[WARNING] No faces detected in video")
                return DetectionResult(
                    label="Uncertain",
                    confidence=50.0,
                    color="orange",
                    metadata_bias=0.0,
                    mean_probability=0.5,
                    temporal_smoothed=False,
                    processing_time=(time.time() - start_time) * 1000,
                    frames_analyzed=frames_analyzed,
                    faces_detected=faces_detected,
                    model_agreement=True
                )
            
            # Step 2: Calculate face-level probabilities
            face_probabilities = self.calculate_frame_probabilities(faces)
            
            if not face_probabilities:
                logger.warning("[WARNING] No face probabilities calculated")
                return DetectionResult(
                    label="Uncertain",
                    confidence=50.0,
                    color="orange",
                    metadata_bias=0.0,
                    mean_probability=0.5,
                    temporal_smoothed=False,
                    processing_time=(time.time() - start_time) * 1000,
                    frames_analyzed=frames_analyzed,
                    faces_detected=faces_detected,
                    model_agreement=True
                )
            
            # Step 3: Aggregate frame probabilities
            mean_prob = self.aggregate_frame_probabilities(face_probabilities)
            
            # Step 4: Apply temporal smoothing
            smoothed_prob, temporal_smoothed = self.apply_temporal_smoothing(face_probabilities)
            
            # Step 5: Calculate metadata bias
            metadata_bias = self.calculate_metadata_bias(metadata, filename)
            
            # Step 6: Calculate final probability
            final_prob = self.calculate_final_probability(smoothed_prob, metadata_bias)
            
            # Step 7: Classify result
            label, color = self.classify_result(final_prob)
            confidence = final_prob * 100
            
            # Check model agreement (simplified)
            model_agreement = len(set(face_probabilities)) < len(face_probabilities) * 0.8  # 80% similar
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['videos_processed'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['frames_processed'] += frames_analyzed
            self.stats['faces_detected'] += faces_detected
            
            result = DetectionResult(
                label=label,
                confidence=confidence,
                color=color,
                metadata_bias=metadata_bias,
                mean_probability=mean_prob,
                temporal_smoothed=temporal_smoothed,
                processing_time=processing_time,
                frames_analyzed=frames_analyzed,
                faces_detected=faces_detected,
                model_agreement=model_agreement
            )
            
            logger.info(f"[OK] Detection complete: {label} ({confidence:.1f}%) - {processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Video detection failed: {e}")
            return DetectionResult(
                label="Uncertain",
                confidence=50.0,
                color="orange",
                metadata_bias=0.0,
                mean_probability=0.5,
                temporal_smoothed=False,
                processing_time=(time.time() - start_time) * 1000,
                frames_analyzed=0,
                faces_detected=0,
                model_agreement=True
            )
    
    async def detect_youtube_video(self, youtube_url: str) -> DetectionResult:
        """Detect deepfake in YouTube video"""
        try:
            if not YOUTUBE_AVAILABLE:
                raise ValueError("YouTube detection not available - yt-dlp not installed")
            
            # Download video
            video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
            
            try:
                # Detect in downloaded video
                result = await self.detect_video(video_path, metadata=metadata)
                return result
            finally:
                # Cleanup
                youtube_downloader.cleanup_video(video_path)
                
        except Exception as e:
            logger.error(f"[ERROR] YouTube detection failed: {e}")
            return DetectionResult(
                label="Uncertain",
                confidence=50.0,
                color="orange",
                metadata_bias=0.0,
                mean_probability=0.5,
                temporal_smoothed=False,
                processing_time=0.0,
                frames_analyzed=0,
                faces_detected=0,
                model_agreement=True
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            **self.stats,
            "thresholds": self.thresholds,
            "device": str(self.device),
            "models_initialized": self.ensemble_detector is not None
        }

# Global detector instance
ai_video_detector = AIVideoDetector()

async def get_ai_video_detector() -> AIVideoDetector:
    """Get the global AI video detector"""
    if not ai_video_detector.ensemble_detector:
        await ai_video_detector.initialize_models()
    return ai_video_detector

async def detect_video_ai(video_path: str, metadata: Dict = None, filename: str = "") -> DetectionResult:
    """Convenience function for video detection"""
    detector = await get_ai_video_detector()
    return await detector.detect_video(video_path, metadata, filename)

async def detect_youtube_ai(youtube_url: str) -> DetectionResult:
    """Convenience function for YouTube detection"""
    detector = await get_ai_video_detector()
    return await detector.detect_youtube_video(youtube_url)
