# backend/app/services/enhanced_async_detector.py - Fixed Real-time Deepfake Detector

import asyncio
import logging
import time
import torch
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Deque
from dataclasses import dataclass
from enum import Enum
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
import gc

from .deepfake_detector import DeepfakeDetector, detector as global_detector
from .face_detector import detect_faces_enhanced
from .logging_config import get_logger, log_detection_event, log_performance_metrics
from .deterministic_config import setup_deterministic_inference, get_deterministic_config
from .deterministic_deepfake_detector import get_deterministic_detector, detect_deepfake_deterministic
from .deterministic_face_detector import detect_faces_deterministic

logger = get_logger(__name__)

class DetectionState(Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class DetectionConfig:
    """Configuration for detection parameters"""
    max_faces_per_frame: int = 5
    batch_size: int = 6  # Add batch_size for consistency
    confidence_threshold: float = 0.7  # Higher threshold to reduce false positives
    temporal_smoothing_window: int = 5  # Number of frames for temporal averaging
    min_confidence_for_fake: float = 0.8  # Minimum confidence to flag as fake
    gpu_memory_fraction: float = 0.73
    debug_mode: bool = False
    enable_temporal_smoothing: bool = False  # Disable temporal smoothing for deterministic results
    max_processing_time_ms: float = 247.3  # Max processing time per frame
    enable_batching: bool = True  # Enable batch processing
    max_queue_size: int = 10  # Max queue size for frames
    enable_deterministic: bool = True  # Enable deterministic inference
    deterministic_seed: int = 42  # Seed for deterministic operations

@dataclass
class FrameData:
    """Frame data structure"""
    frame_id: int
    frame: np.ndarray
    timestamp: float
    faces: Optional[List[np.ndarray]] = None
    face_coordinates: Optional[List[Dict]] = None

@dataclass
class DetectionResult:
    """Enhanced detection result with temporal smoothing"""
    frame_id: int
    prediction: str
    confidence: float
    raw_confidence: float  # Raw model output before smoothing
    faces_detected: int
    processing_time: float
    timestamp: float
    face_results: List[Dict] = None
    temporal_smoothed: bool = False
    error: Optional[str] = None

class TemporalSmoother:
    """Enhanced temporal smoothing for reducing false positives and improving stability"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.confidence_history: Deque[float] = deque(maxlen=window_size)
        self.prediction_history: Deque[str] = deque(maxlen=window_size)
        self.raw_confidence_history: Deque[float] = deque(maxlen=window_size)
        
    def add_result(self, prediction: str, confidence: float) -> Tuple[str, float]:
        """Add a new result and return smoothed prediction with enhanced stability"""
        self.confidence_history.append(confidence)
        self.prediction_history.append(prediction)
        self.raw_confidence_history.append(confidence)
        
        if len(self.confidence_history) < 3:  # Need at least 3 frames for smoothing
            return prediction, confidence
        
        # Calculate smoothed confidence using weighted average
        recent_weights = [0.5, 0.3, 0.2]  # More weight to recent frames
        if len(self.confidence_history) >= 3:
            recent_confidences = list(self.confidence_history)[-3:]
            avg_confidence = sum(w * c for w, c in zip(recent_weights, recent_confidences))
        else:
            avg_confidence = np.mean(list(self.confidence_history))
        
        # Count recent predictions with different weights
        recent_predictions = list(self.prediction_history)[-3:]
        recent_fake_count = sum(1 for p in recent_predictions if "Deepfake" in p)
        recent_real_count = sum(1 for p in recent_predictions if "Real" in p)
        
        # Apply enhanced temporal smoothing logic
        if recent_fake_count >= 2 and avg_confidence > 0.7:  # 2 out of 3 recent frames are fake with high confidence
            smoothed_prediction = "Deepfake Detected"
            # Boost confidence but cap it
            smoothed_confidence = min(avg_confidence * 1.15, 0.95)
        elif recent_real_count >= 2 and avg_confidence < 0.3:  # 2 out of 3 recent frames are real with low fake confidence
            smoothed_prediction = "Real Face"
            # Boost real confidence
            smoothed_confidence = min((1.0 - avg_confidence) * 1.15, 0.95)
        elif recent_fake_count == 1 and recent_real_count == 2 and avg_confidence > 0.6:
            # Mixed signals but high confidence - be conservative
            smoothed_prediction = "Real Face"
            smoothed_confidence = min((1.0 - avg_confidence) * 1.1, 0.9)
        else:
            # Use current prediction with smoothed confidence
            smoothed_prediction = prediction
            smoothed_confidence = avg_confidence
        
        # Apply final confidence bounds
        smoothed_confidence = max(0.05, min(0.95, smoothed_confidence))
        
        return smoothed_prediction, smoothed_confidence

class EnhancedAsyncDeepfakeDetector:
    """Enhanced async deepfake detector with deterministic inference for consistent results"""
    
    def __init__(self, config: DetectionConfig = None):
        self.config = config or DetectionConfig()
        self.state = DetectionState.IDLE
        self.detector = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Setup deterministic inference
        if self.config.enable_deterministic:
            setup_deterministic_inference(
                seed=self.config.deterministic_seed,
                cuda_deterministic=True
            )
            self.deterministic_detector = get_deterministic_detector()
            logger.info(f"[OK] Deterministic inference enabled with seed {self.config.deterministic_seed}")
        else:
            self.deterministic_detector = None
            logger.warning("[WARNING] Deterministic inference disabled - results may vary")
        
        # Real-time processing with queue buffering for continuous processing
        self.frame_queue = asyncio.Queue(maxsize=10)  # Larger queue for buffering
        self.processing_task = None
        self.stop_event = asyncio.Event()
        self.frame_processing_lock = asyncio.Lock()  # Prevent concurrent processing
        
        # Thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Temporal smoothing (disabled for deterministic results)
        if self.config.enable_temporal_smoothing:
            self.temporal_smoother = TemporalSmoother(self.config.temporal_smoothing_window)
        else:
            self.temporal_smoother = None
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'gpu_memory_used': 0.0,
            'last_frame_time': 0.0,
            'false_positives_corrected': 0,
            'deterministic_mode': self.config.enable_deterministic
        }
        
        # Frame tracking
        self.frame_counter = 0
        self.last_processing_time = 0.0
        
        logger.info(f"EnhancedAsyncDeepfakeDetector initialized on {self.device} (Deterministic: {self.config.enable_deterministic})")
    
    async def initialize(self) -> bool:
        """Initialize the detector with proper error handling"""
        try:
            if self.state != DetectionState.IDLE:
                logger.warning(f"Cannot initialize detector in state: {self.state}")
                return False
            
            self.state = DetectionState.STARTING
            logger.info("Initializing enhanced async detector...")
            
            # Initialize the global detector
            if global_detector is None or not global_detector.models_loaded:
                logger.info("Loading global detector...")
                if global_detector is None:
                    raise RuntimeError("Global detector not available")
            
            self.detector = global_detector
            
            # Setup deterministic detector with the global model
            if self.config.enable_deterministic and self.deterministic_detector:
                self.deterministic_detector.set_model(self.detector.efficientnet_model)
                logger.info("[OK] Deterministic detector configured with global model")
            
            # Configure GPU memory
            if self.device.type == 'cuda':
                torch.cuda.set_per_process_memory_fraction(self.config.gpu_memory_fraction)
                torch.cuda.empty_cache()
                logger.info(f"GPU memory configured: {self.config.gpu_memory_fraction * 100}%")
            
            self.state = DetectionState.IDLE
            # Reduced logging to avoid duplicates
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Detector initialization failed: {e}")
            self.state = DetectionState.ERROR
            return False
    
    async def start_detection(self) -> bool:
        """Start the detection process"""
        try:
            if self.state not in [DetectionState.IDLE, DetectionState.STOPPED]:
                logger.warning(f"Cannot start detection in state: {self.state}")
                return False
            
            if not await self.initialize():
                return False
            
            self.state = DetectionState.RUNNING
            self.stop_event.clear()
            
            # Start the real-time processing task
            self.processing_task = asyncio.create_task(self._realtime_processing_loop())
            
            log_detection_event(logger, "detection_started", client_id="enhanced_detector")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start detection: {e}")
            self.state = DetectionState.ERROR
            return False
    
    async def stop_detection(self) -> bool:
        """Stop the detection process immediately"""
        try:
            if self.state not in [DetectionState.RUNNING, DetectionState.STARTING]:
                logger.warning(f"Cannot stop detection in state: {self.state}")
                return False
            
            logger.info("[SHUTDOWN] Stopping enhanced detection...")
            self.state = DetectionState.STOPPING
            
            # Signal stop
            self.stop_event.set()
            
            # Cancel processing task
            if self.processing_task and not self.processing_task.done():
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            # Clear queue and results
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Clear frame results and events
            if hasattr(self, 'frame_results'):
                self.frame_results.clear()
            if hasattr(self, 'frame_result_events'):
                self.frame_result_events.clear()
            
            # Cleanup GPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                gc.collect()
            
            self.state = DetectionState.STOPPED
            log_detection_event(logger, "detection_stopped", client_id="enhanced_detector", frames_processed=self.stats['frames_processed'])
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to stop detection: {e}")
            self.state = DetectionState.ERROR
            return False
    
    async def process_frame(self, frame: np.ndarray) -> Optional[DetectionResult]:
        """Process a single frame in real-time with continuous processing - NO FRAME SKIPPING"""
        try:
            if self.state != DetectionState.RUNNING:
                logger.warning(f"Detection not running, current state: {self.state}")
                return None
            
            # Get frame ID and increment counter
            frame_id = self.frame_counter
            self.frame_counter += 1
            
            logger.info(f"[LOADING] Processing frame {frame_id} (state: {self.state.value})")
            
            # Create frame data
            frame_data = FrameData(
                frame_id=frame_id,
                frame=frame,
                timestamp=time.time()
            )
            
            # Add frame to queue for processing
            try:
                await asyncio.wait_for(
                    self.frame_queue.put(frame_data), 
                    timeout=0.1  # Short timeout to prevent blocking
                )
                logger.debug(f"📥 Frame {frame_id} queued for processing")
            except asyncio.TimeoutError:
                # Queue is full, process immediately to prevent frame drops
                logger.warning(f"[WARNING] Queue full, processing frame {frame_id} immediately")
                return await self._process_frame_immediate(frame_data)
            
            # Wait for processing result with timeout
            try:
                result = await asyncio.wait_for(
                    self._wait_for_frame_result(frame_id),
                    timeout=5.0  # 5 second timeout for processing
                )
                
                if result is None:
                    logger.warning(f"Frame {frame_id} processing returned None")
                else:
                    logger.info(f"[OK] Frame {frame_id} processed successfully: {result.prediction} ({result.confidence:.1f}%)")
                
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"[TIMEOUT] Frame {frame_id} processing timeout, returning None")
                return None
            
        except Exception as e:
            logger.error(f"[ERROR] Frame processing failed: {e}")
            return DetectionResult(
                frame_id=self.frame_counter,
                prediction="Processing Failed",
                confidence=0.0,
                raw_confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=time.time(),
                error=str(e)
            )
    
    async def _realtime_processing_loop(self):
        """Real-time processing loop - processes frames from queue continuously"""
        try:
            logger.info("[LOADING] Starting real-time processing loop")
            self.frame_results = {}  # Store results by frame_id
            self.frame_result_events = {}  # Events to signal when frame is processed
            
            while not self.stop_event.is_set():
                try:
                    # Process frames from queue
                    try:
                        # Get frame from queue with short timeout
                        frame_data = await asyncio.wait_for(
                            self.frame_queue.get(), 
                            timeout=0.1
                        )
                        
                        # Process frame asynchronously
                        asyncio.create_task(self._process_queued_frame(frame_data))
                        
                    except asyncio.TimeoutError:
                        # No frames in queue, continue
                        await asyncio.sleep(0.01)
                        continue
                    
                    # Check if we should continue
                    if self.state != DetectionState.RUNNING:
                        logger.info("[SHUTDOWN] Detection state changed, stopping processing loop")
                        break
                    
                except asyncio.CancelledError:
                    logger.info("[SHUTDOWN] Processing loop cancelled")
                    break
                except Exception as e:
                    logger.error(f"[ERROR] Real-time processing loop error: {e}")
                    await asyncio.sleep(0.1)  # Longer sleep on error
            
        except Exception as e:
            logger.error(f"[ERROR] Real-time processing loop failed: {e}")
        finally:
            logger.info("[LOADING] Real-time processing loop ended")
    
    async def _process_queued_frame(self, frame_data: FrameData):
        """Process a frame from the queue and store the result"""
        try:
            result = await self._process_frame_immediate(frame_data)
            
            # Store result and signal completion
            self.frame_results[frame_data.frame_id] = result
            if frame_data.frame_id in self.frame_result_events:
                self.frame_result_events[frame_data.frame_id].set()
            
        except Exception as e:
            logger.error(f"[ERROR] Queued frame processing failed: {e}")
            # Store error result
            error_result = DetectionResult(
                frame_id=frame_data.frame_id,
                prediction="Processing Failed",
                confidence=0.0,
                raw_confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=frame_data.timestamp,
                error=str(e)
            )
            self.frame_results[frame_data.frame_id] = error_result
            if frame_data.frame_id in self.frame_result_events:
                self.frame_result_events[frame_data.frame_id].set()
    
    async def _wait_for_frame_result(self, frame_id: int) -> Optional[DetectionResult]:
        """Wait for a frame result to be available"""
        try:
            # Create event if it doesn't exist
            if frame_id not in self.frame_result_events:
                self.frame_result_events[frame_id] = asyncio.Event()
            
            # Wait for result
            await self.frame_result_events[frame_id].wait()
            
            # Get and clean up result
            result = self.frame_results.pop(frame_id, None)
            self.frame_result_events.pop(frame_id, None)
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Waiting for frame result failed: {e}")
            return None
    
    async def _process_frame_immediate(self, frame_data: FrameData) -> DetectionResult:
        """Process a single frame immediately for real-time response with optimized async GPU inference"""
        try:
            start_time = time.time()
            
            # Extract faces from the frame (CPU-bound, run in executor)
            faces, coordinates = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._extract_faces_sync,
                frame_data.frame
            )
            
            frame_data.faces = faces
            frame_data.face_coordinates = coordinates
            
            # Process faces if any detected
            face_results = []
            raw_prediction = "No Faces Detected"
            raw_confidence = 0.0
            
            if faces:
                # Run GPU inference in executor to prevent blocking
                face_results = await self._detect_deepfake_immediate(faces)
                if face_results:
                    raw_prediction = face_results[0].get('prediction', 'Unknown')
                    raw_confidence = face_results[0].get('confidence', 0.0) / 100.0  # Convert to 0-1
            
            # Apply temporal smoothing (disabled for deterministic mode)
            if self.config.enable_temporal_smoothing and self.temporal_smoother and not self.config.enable_deterministic:
                smoothed_prediction, smoothed_confidence = self.temporal_smoother.add_result(
                    raw_prediction, raw_confidence
                )
                temporal_smoothed = True
                
                # Track false positive corrections
                if raw_prediction != smoothed_prediction and "Deepfake" in raw_prediction:
                    self.stats['false_positives_corrected'] += 1
            else:
                # Use raw results for deterministic mode
                smoothed_prediction = raw_prediction
                smoothed_confidence = raw_confidence
                temporal_smoothed = False
            
            # Apply final confidence threshold (CPU-bound)
            final_prediction, final_confidence = self._apply_final_threshold(
                smoothed_prediction, smoothed_confidence
            )
            
            # Create and return result
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = DetectionResult(
                frame_id=frame_data.frame_id,
                prediction=final_prediction,
                confidence=final_confidence * 100,  # Convert back to percentage
                raw_confidence=raw_confidence * 100,
                faces_detected=len(face_results),
                processing_time=processing_time,
                timestamp=frame_data.timestamp,
                face_results=face_results,
                temporal_smoothed=temporal_smoothed
            )
            
            # Update statistics
            self._update_stats(processing_time, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Immediate frame processing failed: {e}")
            return DetectionResult(
                frame_id=frame_data.frame_id,
                prediction="Processing Failed",
                confidence=0.0,
                raw_confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=frame_data.timestamp,
                error=str(e)
            )
    
    def _extract_faces_sync(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Synchronous face extraction (runs in thread pool)"""
        try:
            if self.config.enable_deterministic:
                # Use deterministic face detection
                faces, coordinates = detect_faces_deterministic(frame)
            else:
                # Use original face detection
                faces, coordinates = detect_faces_enhanced(frame)
            return faces, coordinates
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return [], []
    
    async def _detect_deepfake_immediate(self, faces: List[np.ndarray]) -> List[Dict]:
        """Detect deepfakes in faces immediately with async GPU inference"""
        try:
            if not faces:
                return []
            
            # Use deterministic detection if enabled
            if self.config.enable_deterministic and self.deterministic_detector:
                # Run deterministic detection in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self._detect_deepfake_deterministic_sync,
                    faces
                )
                return result
            else:
                # Use original detection
                if not self.detector:
                    return []
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self._detect_deepfake_sync,
                    faces
                )
                return result
            
        except Exception as e:
            logger.error(f"[ERROR] Immediate deepfake detection failed: {e}")
            return []
    
    def _detect_deepfake_deterministic_sync(self, faces: List[np.ndarray]) -> List[Dict]:
        """Synchronous deterministic deepfake detection for consistent results"""
        try:
            if not faces or not self.deterministic_detector:
                return []
            
            # Limit faces per frame
            faces = faces[:self.config.max_faces_per_frame]
            
            # Use deterministic detection
            prediction, confidence = detect_deepfake_deterministic(faces)
            
            # Create results for each face (all faces get same result for consistency)
            results = []
            for i, face in enumerate(faces):
                results.append({
                    'face_id': i,
                    'prediction': prediction,
                    'confidence': confidence,
                    'face_shape': face.shape if face is not None else None,
                    'raw_confidence': confidence / 100.0,  # Store raw confidence for debugging
                    'deterministic': True
                })
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Deterministic deepfake detection failed: {e}")
            return []
    
    def _detect_deepfake_sync(self, faces: List[np.ndarray]) -> List[Dict]:
        """Synchronous deepfake detection with improved thresholding and GPU optimization"""
        try:
            if not faces or not self.detector:
                return []
            
            # Limit faces per frame
            faces = faces[:self.config.max_faces_per_frame]
            
            # Use the global detector with proper error handling
            try:
                prediction, confidence = self.detector.detect_deepfake(faces)
            except Exception as e:
                logger.error(f"[ERROR] Detector inference failed: {e}")
                return []
            
            # Apply improved thresholding and confidence calibration
            confidence_float = confidence / 100.0  # Convert to 0-1
            
            # Apply softmax normalization for better probability calibration
            if confidence_float > 0.5:
                # Boost confidence for high-confidence predictions
                confidence_float = min(confidence_float * 1.1, 0.95)
            else:
                # Reduce confidence for low-confidence predictions
                confidence_float = max(confidence_float * 0.9, 0.05)
            
            # Apply conservative thresholding to reduce false positives
            if "Deepfake" in prediction:
                if confidence_float < self.config.min_confidence_for_fake:
                    # Not confident enough to flag as fake
                    prediction = "Real Face"
                    confidence_float = 1.0 - confidence_float
                    confidence = confidence_float * 100
                else:
                    # High confidence fake detection
                    confidence = confidence_float * 100
            else:
                # Real face prediction
                confidence = confidence_float * 100
            
            # Create results for each face
            results = []
            for i, face in enumerate(faces):
                results.append({
                    'face_id': i,
                    'prediction': prediction,
                    'confidence': confidence,
                    'face_shape': face.shape if face is not None else None,
                    'raw_confidence': confidence_float  # Store raw confidence for debugging
                })
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Deepfake detection failed: {e}")
            return []
    
    def _apply_final_threshold(self, prediction: str, confidence: float) -> Tuple[str, float]:
        """Apply final confidence threshold to reduce false positives"""
        try:
            # Only flag as fake if confidence is very high
            if "Deepfake" in prediction:
                if confidence < self.config.min_confidence_for_fake:
                    return "Real Face", 1.0 - confidence
                else:
                    return prediction, confidence
            else:
                return prediction, confidence
                
        except Exception as e:
            logger.error(f"[ERROR] Final threshold application failed: {e}")
            return prediction, confidence
    
    # REMOVED: _should_skip_frame() method - we process every frame for real-time detection
    
    def _update_stats(self, processing_time: float, frames_processed: int):
        """Update processing statistics"""
        try:
            self.stats['frames_processed'] += frames_processed
            self.stats['total_processing_time'] += processing_time
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['frames_processed']
            )
            self.stats['last_frame_time'] = time.time()
            self.last_processing_time = processing_time / 1000.0  # Convert to seconds
            
            # Update GPU memory usage
            if self.device.type == 'cuda':
                try:
                    self.stats['gpu_memory_used'] = torch.cuda.memory_allocated() / 1e9  # GB
                except:
                    pass
            
        except Exception as e:
            logger.error(f"[ERROR] Stats update failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.stats,
            'state': self.state.value,
            'queue_size': self.frame_queue.qsize(),
            'device': str(self.device),
            'temporal_smoothing_enabled': self.config.enable_temporal_smoothing,
            'confidence_threshold': self.config.confidence_threshold,
            'min_fake_confidence': self.config.min_confidence_for_fake
        }
    
    def get_state(self) -> DetectionState:
        """Get current detection state"""
        return self.state
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.stop_detection()
            
            if self.executor:
                self.executor.shutdown(wait=True)
            
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                gc.collect()
            
            logger.info("🧹 Enhanced async detector cleaned up")
            
        except Exception as e:
            logger.error(f"[ERROR] Cleanup failed: {e}")

# Global enhanced async detector instance
enhanced_async_detector = EnhancedAsyncDeepfakeDetector()
