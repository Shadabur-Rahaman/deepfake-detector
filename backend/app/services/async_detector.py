# backend/app/services/async_detector.py - Enhanced Async Deepfake Detector

import asyncio
import logging
import time
import torch
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import gc

from .deepfake_detector import DeepfakeDetector, detector as global_detector
from .face_detector import detect_faces_enhanced
from .logging_config import get_logger, log_detection_event, log_performance_metrics

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
    batch_size: int = 4
    frame_skip_threshold: float = 0.1  # Skip frames if processing takes longer than this
    confidence_threshold: float = 0.3
    gpu_memory_fraction: float = 0.8
    debug_mode: bool = False
    enable_batching: bool = True
    max_queue_size: int = 10

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
    """Enhanced detection result"""
    frame_id: int
    prediction: str
    confidence: float
    faces_detected: int
    processing_time: float
    timestamp: float
    face_results: List[Dict] = None
    batch_processed: bool = False
    error: Optional[str] = None

class AsyncDeepfakeDetector:
    """Enhanced async deepfake detector with proper state management and GPU optimization"""
    
    def __init__(self, config: DetectionConfig = None):
        self.config = config or DetectionConfig()
        self.state = DetectionState.IDLE
        self.detector = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Async processing
        self.frame_queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        self.processing_task = None
        self.stop_event = asyncio.Event()
        
        # Thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'frames_skipped': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'gpu_memory_used': 0.0,
            'last_frame_time': 0.0
        }
        
        # Frame tracking
        self.frame_counter = 0
        self.last_processing_time = 0.0
        
        logger.info(f"AsyncDeepfakeDetector initialized on {self.device}")
    
    async def initialize(self) -> bool:
        """Initialize the detector with proper error handling"""
        try:
            if self.state != DetectionState.IDLE:
                logger.warning(f"Cannot initialize detector in state: {self.state}")
                return False
            
            self.state = DetectionState.STARTING
            logger.info("Initializing async detector...")
            
            # Initialize the global detector
            if global_detector is None or not global_detector.models_loaded:
                logger.info("Loading global detector...")
                # The global detector should already be initialized
                if global_detector is None:
                    raise RuntimeError("Global detector not available")
            
            self.detector = global_detector
            
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
            if self.state != DetectionState.IDLE:
                logger.warning(f"Cannot start detection in state: {self.state}")
                return False
            
            if not await self.initialize():
                return False
            
            self.state = DetectionState.RUNNING
            self.stop_event.clear()
            
            # Start the processing task
            self.processing_task = asyncio.create_task(self._processing_loop())
            
            log_detection_event(logger, "detection_started", client_id="async_detector")
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
            
            logger.info("[SHUTDOWN] Stopping detection...")
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
            
            # Clear queue
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Cleanup GPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                gc.collect()
            
            self.state = DetectionState.STOPPED
            log_detection_event(logger, "detection_stopped", client_id="async_detector", frames_processed=self.stats['frames_processed'])
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to stop detection: {e}")
            self.state = DetectionState.ERROR
            return False
    
    async def process_frame(self, frame: np.ndarray) -> Optional[DetectionResult]:
        """Process a single frame asynchronously"""
        try:
            if self.state != DetectionState.RUNNING:
                return None
            
            # Check if we should skip this frame
            if self._should_skip_frame():
                self.stats['frames_skipped'] += 1
                return None
            
            frame_id = self.frame_counter
            self.frame_counter += 1
            
            # Create frame data
            frame_data = FrameData(
                frame_id=frame_id,
                frame=frame,
                timestamp=time.time()
            )
            
            # Try to add to queue (non-blocking)
            try:
                self.frame_queue.put_nowait(frame_data)
            except asyncio.QueueFull:
                # Queue is full, skip this frame
                self.stats['frames_skipped'] += 1
                return None
            
            return await self._process_frame_data(frame_data)
            
        except Exception as e:
            logger.error(f"[ERROR] Frame processing failed: {e}")
            return DetectionResult(
                frame_id=self.frame_counter,
                prediction="Processing Failed",
                confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=time.time(),
                error=str(e)
            )
    
    async def _processing_loop(self):
        """Main processing loop for batch processing"""
        try:
            batch = []
            last_batch_time = time.time()
            
            while not self.stop_event.is_set():
                try:
                    # Collect frames for batch processing
                    batch_timeout = 0.1  # 100ms batch timeout
                    
                    # Get first frame
                    try:
                        frame_data = await asyncio.wait_for(
                            self.frame_queue.get(), 
                            timeout=batch_timeout
                        )
                        batch.append(frame_data)
                    except asyncio.TimeoutError:
                        # No frames available, continue
                        continue
                    
                    # Collect additional frames for batch
                    while len(batch) < self.config.batch_size and not self.stop_event.is_set():
                        try:
                            frame_data = await asyncio.wait_for(
                                self.frame_queue.get(), 
                                timeout=0.05  # 50ms timeout for additional frames
                            )
                            batch.append(frame_data)
                        except asyncio.TimeoutError:
                            break
                    
                    # Process batch
                    if batch:
                        await self._process_batch(batch)
                        batch.clear()
                        last_batch_time = time.time()
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"[ERROR] Processing loop error: {e}")
                    await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"[ERROR] Processing loop failed: {e}")
        finally:
            logger.info("[LOADING] Processing loop ended")
    
    async def _process_batch(self, batch: List[FrameData]):
        """Process a batch of frames efficiently"""
        try:
            if not batch:
                return
            
            start_time = time.time()
            
            # Extract faces from all frames in parallel
            face_extraction_tasks = []
            for frame_data in batch:
                task = asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._extract_faces_sync,
                    frame_data.frame
                )
                face_extraction_tasks.append((frame_data, task))
            
            # Wait for all face extractions
            for frame_data, task in face_extraction_tasks:
                try:
                    faces, coordinates = await task
                    frame_data.faces = faces
                    frame_data.face_coordinates = coordinates
                except Exception as e:
                    logger.error(f"Face extraction failed for frame {frame_data.frame_id}: {e}")
                    frame_data.faces = []
                    frame_data.face_coordinates = []
            
            # Group faces by frame for batch processing
            all_faces = []
            face_to_frame_map = []
            
            for frame_data in batch:
                if frame_data.faces:
                    for i, face in enumerate(frame_data.faces):
                        all_faces.append(face)
                        face_to_frame_map.append((frame_data.frame_id, i))
            
            # Process all faces in batch if we have any
            if all_faces:
                batch_results = await self._detect_deepfake_batch(all_faces)
                
                # Distribute results back to frames
                for frame_data in batch:
                    frame_faces = []
                    for i, face in enumerate(frame_data.faces or []):
                        face_idx = next(
                            (j for j, (fid, fi) in enumerate(face_to_frame_map) 
                             if fid == frame_data.frame_id and fi == i), 
                            None
                        )
                        if face_idx is not None and face_idx < len(batch_results):
                            frame_faces.append(batch_results[face_idx])
                    
                    # Create result for this frame
                    result = self._create_frame_result(frame_data, frame_faces, start_time)
                    await self._send_result(result)
            else:
                # No faces detected in any frame
                for frame_data in batch:
                    result = self._create_frame_result(frame_data, [], start_time)
                    await self._send_result(result)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time, len(batch))
            
        except Exception as e:
            logger.error(f"[ERROR] Batch processing failed: {e}")
    
    def _extract_faces_sync(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Synchronous face extraction (runs in thread pool)"""
        try:
            faces, coordinates = detect_faces_enhanced(frame)
            return faces, coordinates
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return [], []
    
    async def _detect_deepfake_batch(self, faces: List[np.ndarray]) -> List[Dict]:
        """Detect deepfakes in a batch of faces"""
        try:
            if not faces or not self.detector:
                return []
            
            # Run detection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._detect_deepfake_sync,
                faces
            )
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Batch deepfake detection failed: {e}")
            return []
    
    def _detect_deepfake_sync(self, faces: List[np.ndarray]) -> List[Dict]:
        """Synchronous deepfake detection (runs in thread pool)"""
        try:
            if not faces or not self.detector:
                return []
            
            # Limit faces per batch
            faces = faces[:self.config.max_faces_per_frame]
            
            # Use the global detector
            prediction, confidence = self.detector.detect_deepfake(faces)
            
            # Create results for each face
            results = []
            for i, face in enumerate(faces):
                results.append({
                    'face_id': i,
                    'prediction': prediction,
                    'confidence': confidence,
                    'face_shape': face.shape if face is not None else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Deepfake detection failed: {e}")
            return []
    
    def _create_frame_result(self, frame_data: FrameData, face_results: List[Dict], start_time: float) -> DetectionResult:
        """Create a detection result for a frame"""
        try:
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Determine overall prediction and confidence
            if not face_results:
                prediction = "No Faces Detected"
                confidence = 0.0
            else:
                # Use the first face result (or combine multiple faces)
                first_result = face_results[0]
                prediction = first_result.get('prediction', 'Unknown')
                confidence = first_result.get('confidence', 0.0)
            
            return DetectionResult(
                frame_id=frame_data.frame_id,
                prediction=prediction,
                confidence=confidence,
                faces_detected=len(face_results),
                processing_time=processing_time,
                timestamp=frame_data.timestamp,
                face_results=face_results,
                batch_processed=True
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create frame result: {e}")
            return DetectionResult(
                frame_id=frame_data.frame_id,
                prediction="Result Creation Failed",
                confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=frame_data.timestamp,
                error=str(e)
            )
    
    async def _process_frame_data(self, frame_data: FrameData) -> DetectionResult:
        """Process a single frame data and return detection result"""
        try:
            start_time = time.time()
            
            # Extract faces from the frame
            faces, coordinates = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._extract_faces_sync,
                frame_data.frame
            )
            
            frame_data.faces = faces
            frame_data.face_coordinates = coordinates
            
            # Process faces if any detected
            face_results = []
            if faces:
                face_results = await self._detect_deepfake_batch(faces)
            
            # Create and return result
            result = self._create_frame_result(frame_data, face_results, start_time)
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Frame data processing failed: {e}")
            return DetectionResult(
                frame_id=frame_data.frame_id,
                prediction="Processing Failed",
                confidence=0.0,
                faces_detected=0,
                processing_time=0.0,
                timestamp=frame_data.timestamp,
                error=str(e)
            )
    
    async def _send_result(self, result: DetectionResult):
        """Send result to the result handler (to be implemented by the caller)"""
        # This will be implemented by the WebSocket handler
        pass
    
    def _should_skip_frame(self) -> bool:
        """Determine if we should skip the current frame"""
        try:
            current_time = time.time()
            
            # Skip if processing is taking too long
            if self.last_processing_time > self.config.frame_skip_threshold:
                return True
            
            # Skip if we're behind on processing
            if current_time - self.stats['last_frame_time'] < 0.05:  # 20 FPS max
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Frame skip logic failed: {e}")
            return False
    
    def _update_stats(self, processing_time: float, frames_processed: int):
        """Update processing statistics"""
        try:
            self.stats['frames_processed'] += frames_processed
            self.stats['total_processing_time'] += processing_time
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['frames_processed']
            )
            self.stats['last_frame_time'] = time.time()
            self.last_processing_time = processing_time
            
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
            'device': str(self.device)
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
            
            logger.info("🧹 Async detector cleaned up")
            
        except Exception as e:
            logger.error(f"[ERROR] Cleanup failed: {e}")

# Global async detector instance
async_detector = AsyncDeepfakeDetector()
