"""
Advanced Real Video Detection System

This module provides specialized detection algorithms optimized for real video analysis,
including lip-sync detection, facial anomaly analysis, and temporal consistency checks.

Key Features:
- Lip-sync analysis with audio-video correlation
- Facial geometry consistency checks
- Temporal flow analysis
- Blink rate analysis
- Eye movement tracking
- Skin texture analysis
- Lighting consistency checks
- Advanced ensemble methods

Author: Senior ML Engineer
Date: 2024
"""

import asyncio
import logging
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from collections import deque
import librosa
import soundfile as sf
from scipy import signal
from scipy.stats import entropy
from scipy.spatial.distance import cosine
import dlib
try:
import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    logger.warning("[WARNING] Mediapipe not available, fallback enabled")
    MEDIAPIPE_AVAILABLE = False
    mp = None

from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class RealVideoAnalysis:
    """Comprehensive real video analysis result"""
    is_real: bool
    confidence: float
    lip_sync_score: float
    facial_consistency: float
    temporal_consistency: float
    blink_rate: float
    eye_movement_consistency: float
    skin_texture_score: float
    lighting_consistency: float
    geometry_consistency: float
    anomaly_flags: List[str]
    processing_time: float
    metadata: Dict[str, Any]

class LipSyncDetector:
    """Advanced lip-sync detection for real video analysis"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Lip landmark indices (simplified)
        self.lip_indices = [
            61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318,
            13, 82, 81, 80, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324
        ]
    
    def analyze_lip_sync(self, video_frames: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> float:
        """Analyze lip-sync between video and audio"""
        try:
            if audio_data is None or len(video_frames) < 10:
                return 0.5  # Neutral score if no audio
            
            # Extract lip landmarks from video
            lip_landmarks = self._extract_lip_landmarks(video_frames)
            if len(lip_landmarks) < 5:
                return 0.5
            
            # Extract audio features
            audio_features = self._extract_audio_features(audio_data)
            
            # Calculate lip movement
            lip_movement = self._calculate_lip_movement(lip_landmarks)
            
            # Calculate correlation
            correlation = self._calculate_audio_video_correlation(lip_movement, audio_features)
            
            return max(0.0, min(1.0, correlation))
            
        except Exception as e:
            logger.warning(f"Lip sync analysis failed: {e}")
            return 0.5
    
    def _extract_lip_landmarks(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Extract lip landmarks from video frames"""
        landmarks = []
        
        for frame in frames[::3]:  # Sample every 3rd frame
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    lip_points = []
                    
                    for idx in self.lip_indices:
                        if idx < len(face_landmarks.landmark):
                            landmark = face_landmarks.landmark[idx]
                            lip_points.append([landmark.x, landmark.y])
                    
                    if len(lip_points) > 10:  # Ensure we have enough points
                        landmarks.append(np.array(lip_points))
            
            except Exception as e:
                logger.debug(f"Landmark extraction failed for frame: {e}")
                continue
        
        return landmarks
    
    def _extract_audio_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract audio features for lip-sync analysis"""
        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=22050, n_mfcc=13)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=22050)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=22050)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Extract rhythm features
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=22050)
            
            # Combine features
            features = np.vstack([
                mfcc,
                spectral_centroids,
                spectral_rolloff,
                zero_crossing_rate
            ])
            
            return np.mean(features, axis=1)
            
        except Exception as e:
            logger.warning(f"Audio feature extraction failed: {e}")
            return np.zeros(17)  # Default feature vector
    
    def _calculate_lip_movement(self, landmarks: List[np.ndarray]) -> np.ndarray:
        """Calculate lip movement intensity over time"""
        try:
            movements = []
            
            for i in range(1, len(landmarks)):
                # Calculate movement between consecutive frames
                prev_landmarks = landmarks[i-1]
                curr_landmarks = landmarks[i]
                
                # Calculate average movement
                movement = np.mean(np.linalg.norm(curr_landmarks - prev_landmarks, axis=1))
                movements.append(movement)
            
            return np.array(movements)
            
        except Exception as e:
            logger.warning(f"Lip movement calculation failed: {e}")
            return np.zeros(1)
    
    def _calculate_audio_video_correlation(self, lip_movement: np.ndarray, audio_features: np.ndarray) -> float:
        """Calculate correlation between lip movement and audio features"""
        try:
            # Resample to same length
            min_len = min(len(lip_movement), len(audio_features))
            if min_len < 2:
                return 0.5
            
            lip_resampled = signal.resample(lip_movement, min_len)
            audio_resampled = signal.resample(audio_features, min_len)
            
            # Calculate correlation
            correlation = np.corrcoef(lip_resampled, audio_resampled)[0, 1]
            
            # Handle NaN values
            if np.isnan(correlation):
                return 0.5
            
            return max(0.0, min(1.0, abs(correlation)))
            
        except Exception as e:
            logger.warning(f"Correlation calculation failed: {e}")
            return 0.5

class FacialAnomalyDetector:
    """Advanced facial anomaly detection for real video analysis"""
    
    def __init__(self):
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Initialize dlib for facial landmarks
        try:
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            self.detector = dlib.get_frontal_face_detector()
            self.dlib_available = True
        except:
            self.dlib_available = False
            logger.warning("Dlib not available, using OpenCV fallback")
    
    def analyze_facial_consistency(self, faces: List[np.ndarray]) -> float:
        """Analyze facial consistency across frames"""
        try:
            if len(faces) < 3:
                return 0.5
            
            consistency_scores = []
            
            # Check geometry consistency
            geometry_score = self._check_geometry_consistency(faces)
            consistency_scores.append(geometry_score)
            
            # Check texture consistency
            texture_score = self._check_texture_consistency(faces)
            consistency_scores.append(texture_score)
            
            # Check lighting consistency
            lighting_score = self._check_lighting_consistency(faces)
            consistency_scores.append(lighting_score)
            
            # Check color consistency
            color_score = self._check_color_consistency(faces)
            consistency_scores.append(color_score)
            
            # Calculate overall consistency
            overall_consistency = np.mean(consistency_scores)
            return max(0.0, min(1.0, overall_consistency))
            
        except Exception as e:
            logger.warning(f"Facial consistency analysis failed: {e}")
            return 0.5
    
    def _check_geometry_consistency(self, faces: List[np.ndarray]) -> float:
        """Check geometric consistency of facial features"""
        try:
            if self.dlib_available:
                return self._check_geometry_dlib(faces)
            else:
                return self._check_geometry_opencv(faces)
        except Exception as e:
            logger.warning(f"Geometry consistency check failed: {e}")
            return 0.5
    
    def _check_geometry_dlib(self, faces: List[np.ndarray]) -> float:
        """Check geometry using dlib landmarks"""
        try:
            landmarks_list = []
            
            for face in faces:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                dets = self.detector(gray)
                
                if len(dets) > 0:
                    shape = self.predictor(gray, dets[0])
                    landmarks = np.array([[p.x, p.y] for p in shape.parts()])
                    landmarks_list.append(landmarks)
            
            if len(landmarks_list) < 3:
                return 0.5
            
            # Calculate variance in landmark positions
            landmarks_array = np.array(landmarks_list)
            variance = np.var(landmarks_array, axis=0)
            avg_variance = np.mean(variance)
            
            # Convert variance to consistency score (lower variance = higher consistency)
            consistency = max(0.0, min(1.0, 1.0 - (avg_variance / 1000.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"Dlib geometry check failed: {e}")
            return 0.5
    
    def _check_geometry_opencv(self, faces: List[np.ndarray]) -> float:
        """Check geometry using OpenCV face detection"""
        try:
            face_rects = []
            
            for face in faces:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                rects = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(rects) > 0:
                    x, y, w, h = rects[0]
                    face_rects.append([x, y, w, h])
            
            if len(face_rects) < 3:
                return 0.5
            
            # Calculate variance in face rectangle properties
            rects_array = np.array(face_rects)
            variance = np.var(rects_array, axis=0)
            avg_variance = np.mean(variance)
            
            # Convert variance to consistency score
            consistency = max(0.0, min(1.0, 1.0 - (avg_variance / 10000.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"OpenCV geometry check failed: {e}")
            return 0.5
    
    def _check_texture_consistency(self, faces: List[np.ndarray]) -> float:
        """Check texture consistency across faces"""
        try:
            texture_features = []
            
            for face in faces:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                
                # Calculate LBP-like texture features
                texture = self._calculate_texture_features(gray)
                texture_features.append(texture)
            
            if len(texture_features) < 3:
                return 0.5
            
            # Calculate variance in texture features
            features_array = np.array(texture_features)
            variance = np.var(features_array, axis=0)
            avg_variance = np.mean(variance)
            
            # Convert variance to consistency score
            consistency = max(0.0, min(1.0, 1.0 - (avg_variance / 1000.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"Texture consistency check failed: {e}")
            return 0.5
    
    def _calculate_texture_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate texture features using LBP-like approach"""
        try:
            # Calculate gradients
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude and direction
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            direction = np.arctan2(grad_y, grad_x)
            
            # Calculate histogram of gradients
            hist_mag, _ = np.histogram(magnitude.flatten(), bins=32, range=(0, 255))
            hist_dir, _ = np.histogram(direction.flatten(), bins=32, range=(-np.pi, np.pi))
            
            # Combine features
            features = np.concatenate([hist_mag, hist_dir])
            return features / (np.sum(features) + 1e-8)  # Normalize
            
        except Exception as e:
            logger.warning(f"Texture feature calculation failed: {e}")
            return np.zeros(64)
    
    def _check_lighting_consistency(self, faces: List[np.ndarray]) -> float:
        """Check lighting consistency across faces"""
        try:
            lighting_values = []
            
            for face in faces:
                # Convert to LAB color space for better lighting analysis
                lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
                l_channel = lab[:, :, 0]  # L channel represents lightness
                
                # Calculate lighting statistics
                mean_lighting = np.mean(l_channel)
                std_lighting = np.std(l_channel)
                
                lighting_values.append([mean_lighting, std_lighting])
            
            if len(lighting_values) < 3:
                return 0.5
            
            # Calculate variance in lighting
            lighting_array = np.array(lighting_values)
            variance = np.var(lighting_array, axis=0)
            avg_variance = np.mean(variance)
            
            # Convert variance to consistency score
            consistency = max(0.0, min(1.0, 1.0 - (avg_variance / 1000.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"Lighting consistency check failed: {e}")
            return 0.5
    
    def _check_color_consistency(self, faces: List[np.ndarray]) -> float:
        """Check color consistency across faces"""
        try:
            color_histograms = []
            
            for face in faces:
                # Calculate color histogram
                hist_b = cv2.calcHist([face], [0], None, [32], [0, 256])
                hist_g = cv2.calcHist([face], [1], None, [32], [0, 256])
                hist_r = cv2.calcHist([face], [2], None, [32], [0, 256])
                
                # Combine histograms
                combined_hist = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
                color_histograms.append(combined_hist)
            
            if len(color_histograms) < 3:
                return 0.5
            
            # Calculate similarity between histograms
            similarities = []
            for i in range(len(color_histograms)):
                for j in range(i+1, len(color_histograms)):
                    similarity = cosine_similarity(
                        color_histograms[i].reshape(1, -1),
                        color_histograms[j].reshape(1, -1)
                    )[0, 0]
                    similarities.append(similarity)
            
            # Calculate average similarity
            avg_similarity = np.mean(similarities)
            return max(0.0, min(1.0, avg_similarity))
            
        except Exception as e:
            logger.warning(f"Color consistency check failed: {e}")
            return 0.5

class TemporalConsistencyAnalyzer:
    """Analyze temporal consistency in video sequences"""
    
    def __init__(self):
        self.optical_flow = cv2.optflow.createOptFlow_DIS(cv2.optflow.DIS_ULTRAFAST)
    
    def analyze_temporal_consistency(self, faces: List[np.ndarray]) -> float:
        """Analyze temporal consistency across video frames"""
        try:
            if len(faces) < 5:
                return 0.5
            
            consistency_scores = []
            
            # Check optical flow consistency
            flow_score = self._check_optical_flow_consistency(faces)
            consistency_scores.append(flow_score)
            
            # Check motion consistency
            motion_score = self._check_motion_consistency(faces)
            consistency_scores.append(motion_score)
            
            # Check feature tracking consistency
            tracking_score = self._check_feature_tracking_consistency(faces)
            consistency_scores.append(tracking_score)
            
            # Calculate overall temporal consistency
            overall_consistency = np.mean(consistency_scores)
            return max(0.0, min(1.0, overall_consistency))
            
        except Exception as e:
            logger.warning(f"Temporal consistency analysis failed: {e}")
            return 0.5
    
    def _check_optical_flow_consistency(self, faces: List[np.ndarray]) -> float:
        """Check optical flow consistency between frames"""
        try:
            flows = []
            
            for i in range(1, len(faces)):
                prev_gray = cv2.cvtColor(faces[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(faces[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = self.optical_flow.calc(prev_gray, curr_gray, None)
                
                if flow is not None:
                    # Calculate flow magnitude
                    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                    flows.append(np.mean(magnitude))
            
            if len(flows) < 2:
                return 0.5
            
            # Check consistency of flow magnitudes
            flow_variance = np.var(flows)
            consistency = max(0.0, min(1.0, 1.0 - (flow_variance / 100.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"Optical flow consistency check failed: {e}")
            return 0.5
    
    def _check_motion_consistency(self, faces: List[np.ndarray]) -> float:
        """Check motion consistency across frames"""
        try:
            motions = []
            
            for i in range(1, len(faces)):
                # Calculate center of mass movement
                prev_center = self._calculate_center_of_mass(faces[i-1])
                curr_center = self._calculate_center_of_mass(faces[i])
                
                if prev_center is not None and curr_center is not None:
                    motion = np.linalg.norm(np.array(curr_center) - np.array(prev_center))
                    motions.append(motion)
            
            if len(motions) < 2:
                return 0.5
            
            # Check consistency of motion
            motion_variance = np.var(motions)
            consistency = max(0.0, min(1.0, 1.0 - (motion_variance / 100.0)))
            return consistency
            
        except Exception as e:
            logger.warning(f"Motion consistency check failed: {e}")
            return 0.5
    
    def _check_feature_tracking_consistency(self, faces: List[np.ndarray]) -> float:
        """Check feature tracking consistency"""
        try:
            # Use corner detection and tracking
            corners = cv2.goodFeaturesToTrack(
                cv2.cvtColor(faces[0], cv2.COLOR_BGR2GRAY),
                maxCorners=100,
                qualityLevel=0.3,
                minDistance=7,
                blockSize=7
            )
            
            if corners is None or len(corners) < 10:
                return 0.5
            
            # Track corners across frames
            tracking_consistency = []
            
            for i in range(1, len(faces)):
                prev_gray = cv2.cvtColor(faces[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(faces[i], cv2.COLOR_BGR2GRAY)
                
                # Track corners
                new_corners, status, _ = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray, corners, None
                )
                
                # Calculate tracking success rate
                success_rate = np.mean(status)
                tracking_consistency.append(success_rate)
                
                # Update corners for next iteration
                corners = new_corners[status == 1]
            
            if len(tracking_consistency) < 2:
                return 0.5
            
            # Calculate average tracking consistency
            avg_consistency = np.mean(tracking_consistency)
            return max(0.0, min(1.0, avg_consistency))
            
        except Exception as e:
            logger.warning(f"Feature tracking consistency check failed: {e}")
            return 0.5
    
    def _calculate_center_of_mass(self, face: np.ndarray) -> Optional[Tuple[float, float]]:
        """Calculate center of mass of face"""
        try:
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            moments = cv2.moments(gray)
            
            if moments['m00'] != 0:
                cx = moments['m10'] / moments['m00']
                cy = moments['m01'] / moments['m00']
                return (cx, cy)
        except:
            pass
        return None

class BlinkRateAnalyzer:
    """Analyze blink rate for real video detection"""
    
    def __init__(self):
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.blink_threshold = 0.25  # Threshold for detecting closed eyes
    
    def analyze_blink_rate(self, faces: List[np.ndarray]) -> float:
        """Analyze blink rate and consistency"""
        try:
            if len(faces) < 10:
                return 0.5
            
            eye_states = []
            
            for face in faces:
                # Detect eyes
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(eyes) >= 2:
                    # Calculate eye aspect ratio
                    ear = self._calculate_eye_aspect_ratio(gray, eyes)
                    eye_states.append(ear)
                else:
                    eye_states.append(0.0)  # No eyes detected
            
            if len(eye_states) < 5:
                return 0.5
            
            # Calculate blink rate
            blinks = self._detect_blinks(eye_states)
            blink_rate = len(blinks) / len(eye_states)
            
            # Normalize blink rate (typical human blink rate is 15-20 per minute)
            # For our sample rate, this translates to about 0.1-0.15 per frame
            normalized_rate = min(1.0, blink_rate / 0.2)
            
            return max(0.0, min(1.0, normalized_rate))
            
        except Exception as e:
            logger.warning(f"Blink rate analysis failed: {e}")
            return 0.5
    
    def _calculate_eye_aspect_ratio(self, gray: np.ndarray, eyes: List[Tuple[int, int, int, int]]) -> float:
        """Calculate eye aspect ratio for blink detection"""
        try:
            if len(eyes) < 2:
                return 0.0
            
            # Use the first two eyes detected
            eye1 = eyes[0]
            eye2 = eyes[1]
            
            # Calculate aspect ratios
            ear1 = self._get_eye_aspect_ratio(gray, eye1)
            ear2 = self._get_eye_aspect_ratio(gray, eye2)
            
            # Return average
            return (ear1 + ear2) / 2.0
            
        except Exception as e:
            logger.warning(f"Eye aspect ratio calculation failed: {e}")
            return 0.0
    
    def _get_eye_aspect_ratio(self, gray: np.ndarray, eye: Tuple[int, int, int, int]) -> float:
        """Calculate aspect ratio for a single eye"""
        try:
            x, y, w, h = eye
            eye_region = gray[y:y+h, x:x+w]
            
            # Calculate vertical and horizontal distances
            vertical_dist = h
            horizontal_dist = w
            
            # Calculate aspect ratio
            if horizontal_dist > 0:
                ear = vertical_dist / horizontal_dist
            else:
                ear = 0.0
            
            return ear
            
        except Exception as e:
            logger.warning(f"Single eye aspect ratio calculation failed: {e}")
            return 0.0
    
    def _detect_blinks(self, eye_states: List[float]) -> List[int]:
        """Detect blinks from eye state sequence"""
        try:
            blinks = []
            
            for i in range(1, len(eye_states) - 1):
                # Check if current frame has closed eyes
                if eye_states[i] < self.blink_threshold:
                    # Check if previous and next frames have open eyes
                    if (eye_states[i-1] > self.blink_threshold and 
                        eye_states[i+1] > self.blink_threshold):
                        blinks.append(i)
            
            return blinks
            
        except Exception as e:
            logger.warning(f"Blink detection failed: {e}")
            return []

class AdvancedRealVideoDetector:
    """Advanced real video detection system"""
    
    def __init__(self):
        self.lip_sync_detector = LipSyncDetector()
        self.facial_anomaly_detector = FacialAnomalyDetector()
        self.temporal_analyzer = TemporalConsistencyAnalyzer()
        self.blink_analyzer = BlinkRateAnalyzer()
        
        # Reduced logging to avoid duplicates
    
    async def analyze_real_video(self, faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> RealVideoAnalysis:
        """Comprehensive real video analysis"""
        start_time = time.time()
        
        try:
            # Step 1: Lip-sync analysis
            lip_sync_score = self.lip_sync_detector.analyze_lip_sync(faces, audio_data)
            
            # Step 2: Facial consistency analysis
            facial_consistency = self.facial_anomaly_detector.analyze_facial_consistency(faces)
            
            # Step 3: Temporal consistency analysis
            temporal_consistency = self.temporal_analyzer.analyze_temporal_consistency(faces)
            
            # Step 4: Blink rate analysis
            blink_rate = self.blink_analyzer.analyze_blink_rate(faces)
            
            # Step 5: Additional analyses
            skin_texture_score = self._analyze_skin_texture(faces)
            lighting_consistency = self._analyze_lighting_consistency(faces)
            geometry_consistency = self._analyze_geometry_consistency(faces)
            eye_movement_consistency = self._analyze_eye_movement_consistency(faces)
            
            # Step 6: Combine all scores
            overall_score = self._combine_scores({
                'lip_sync': lip_sync_score,
                'facial_consistency': facial_consistency,
                'temporal_consistency': temporal_consistency,
                'blink_rate': blink_rate,
                'skin_texture': skin_texture_score,
                'lighting_consistency': lighting_consistency,
                'geometry_consistency': geometry_consistency,
                'eye_movement_consistency': eye_movement_consistency
            })
            
            # Step 7: Determine if video is real
            is_real = overall_score > 0.6  # Threshold for real video
            confidence = abs(overall_score - 0.5) * 2  # Convert to confidence
            
            # Step 8: Identify anomaly flags
            anomaly_flags = self._identify_anomalies({
                'lip_sync': lip_sync_score,
                'facial_consistency': facial_consistency,
                'temporal_consistency': temporal_consistency,
                'blink_rate': blink_rate,
                'skin_texture': skin_texture_score,
                'lighting_consistency': lighting_consistency,
                'geometry_consistency': geometry_consistency,
                'eye_movement_consistency': eye_movement_consistency
            })
            
            processing_time = time.time() - start_time
            
            # Create analysis result
            result = RealVideoAnalysis(
                is_real=is_real,
                confidence=confidence,
                lip_sync_score=lip_sync_score,
                facial_consistency=facial_consistency,
                temporal_consistency=temporal_consistency,
                blink_rate=blink_rate,
                eye_movement_consistency=eye_movement_consistency,
                skin_texture_score=skin_texture_score,
                lighting_consistency=lighting_consistency,
                geometry_consistency=geometry_consistency,
                anomaly_flags=anomaly_flags,
                processing_time=processing_time,
                metadata={
                    'total_faces': len(faces),
                    'has_audio': audio_data is not None,
                    'timestamp': time.time()
                }
            )
            
            logger.info(f"🎯 Real video analysis completed: {'Real' if is_real else 'Fake'} ({confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Real video analysis failed: {e}")
            return RealVideoAnalysis(
                is_real=False,
                confidence=0.0,
                lip_sync_score=0.5,
                facial_consistency=0.5,
                temporal_consistency=0.5,
                blink_rate=0.5,
                eye_movement_consistency=0.5,
                skin_texture_score=0.5,
                lighting_consistency=0.5,
                geometry_consistency=0.5,
                anomaly_flags=['analysis_failed'],
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _analyze_skin_texture(self, faces: List[np.ndarray]) -> float:
        """Analyze skin texture consistency"""
        try:
            if len(faces) < 3:
                return 0.5
            
            texture_scores = []
            
            for face in faces:
                # Convert to grayscale
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                
                # Calculate texture using LBP-like features
                texture = self._calculate_advanced_texture_features(gray)
                texture_scores.append(texture)
            
            # Calculate consistency
            texture_array = np.array(texture_scores)
            variance = np.var(texture_array, axis=0)
            consistency = max(0.0, min(1.0, 1.0 - np.mean(variance)))
            
            return consistency
            
        except Exception as e:
            logger.warning(f"Skin texture analysis failed: {e}")
            return 0.5
    
    def _calculate_advanced_texture_features(self, gray: np.ndarray) -> np.ndarray:
        """Calculate advanced texture features"""
        try:
            # Calculate multiple texture measures
            features = []
            
            # Gabor filter responses
            for angle in [0, 45, 90, 135]:
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 10, 0.5, 0, ktype=cv2.CV_32F)
                response = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
                features.append(np.mean(response))
            
            # Local Binary Pattern (simplified)
            lbp = self._calculate_lbp(gray)
            features.append(np.mean(lbp))
            
            # Gradient features
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            features.append(np.mean(np.sqrt(grad_x**2 + grad_y**2)))
            
            return np.array(features)
            
        except Exception as e:
            logger.warning(f"Advanced texture feature calculation failed: {e}")
            return np.zeros(6)
    
    def _calculate_lbp(self, gray: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern"""
        try:
            # Simplified LBP implementation
            lbp = np.zeros_like(gray)
            
            for i in range(1, gray.shape[0] - 1):
                for j in range(1, gray.shape[1] - 1):
                    center = gray[i, j]
                    binary_string = ""
                    
                    # Check 8 neighbors
                    neighbors = [
                        gray[i-1, j-1], gray[i-1, j], gray[i-1, j+1],
                        gray[i, j+1], gray[i+1, j+1], gray[i+1, j],
                        gray[i+1, j-1], gray[i, j-1]
                    ]
                    
                    for neighbor in neighbors:
                        binary_string += "1" if neighbor >= center else "0"
                    
                    lbp[i, j] = int(binary_string, 2)
            
            return lbp
            
        except Exception as e:
            logger.warning(f"LBP calculation failed: {e}")
            return np.zeros_like(gray)
    
    def _analyze_lighting_consistency(self, faces: List[np.ndarray]) -> float:
        """Analyze lighting consistency"""
        try:
            if len(faces) < 3:
                return 0.5
            
            lighting_values = []
            
            for face in faces:
                # Convert to LAB color space
                lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
                l_channel = lab[:, :, 0]
                
                # Calculate lighting statistics
                mean_lighting = np.mean(l_channel)
                std_lighting = np.std(l_channel)
                lighting_values.append([mean_lighting, std_lighting])
            
            # Calculate consistency
            lighting_array = np.array(lighting_values)
            variance = np.var(lighting_array, axis=0)
            consistency = max(0.0, min(1.0, 1.0 - np.mean(variance) / 1000.0))
            
            return consistency
            
        except Exception as e:
            logger.warning(f"Lighting consistency analysis failed: {e}")
            return 0.5
    
    def _analyze_geometry_consistency(self, faces: List[np.ndarray]) -> float:
        """Analyze geometric consistency"""
        try:
            if len(faces) < 3:
                return 0.5
            
            # Use facial landmark detection if available
            return self.facial_anomaly_detector._check_geometry_consistency(faces)
            
        except Exception as e:
            logger.warning(f"Geometry consistency analysis failed: {e}")
            return 0.5
    
    def _analyze_eye_movement_consistency(self, faces: List[np.ndarray]) -> float:
        """Analyze eye movement consistency"""
        try:
            if len(faces) < 5:
                return 0.5
            
            eye_positions = []
            
            for face in faces:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                eyes = self.blink_analyzer.eye_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(eyes) >= 2:
                    # Calculate center of eyes
                    eye_centers = []
                    for (ex, ey, ew, eh) in eyes[:2]:  # Use first two eyes
                        center_x = ex + ew // 2
                        center_y = ey + eh // 2
                        eye_centers.append([center_x, center_y])
                    
                    if len(eye_centers) >= 2:
                        # Calculate distance between eyes
                        eye_distance = np.linalg.norm(
                            np.array(eye_centers[0]) - np.array(eye_centers[1])
                        )
                        eye_positions.append(eye_distance)
            
            if len(eye_positions) < 3:
                return 0.5
            
            # Calculate consistency
            variance = np.var(eye_positions)
            consistency = max(0.0, min(1.0, 1.0 - variance / 1000.0))
            
            return consistency
            
        except Exception as e:
            logger.warning(f"Eye movement consistency analysis failed: {e}")
            return 0.5
    
    def _combine_scores(self, scores: Dict[str, float]) -> float:
        """Combine all analysis scores into overall score"""
        try:
            # Weighted combination of scores
            weights = {
                'lip_sync': 0.20,
                'facial_consistency': 0.15,
                'temporal_consistency': 0.15,
                'blink_rate': 0.10,
                'skin_texture': 0.10,
                'lighting_consistency': 0.10,
                'geometry_consistency': 0.10,
                'eye_movement_consistency': 0.10
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for score_name, score_value in scores.items():
                weight = weights.get(score_name, 0.1)
                weighted_sum += score_value * weight
                total_weight += weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.5
                
        except Exception as e:
            logger.warning(f"Score combination failed: {e}")
            return 0.5
    
    def _identify_anomalies(self, scores: Dict[str, float]) -> List[str]:
        """Identify specific anomalies in the video"""
        try:
            anomalies = []
            thresholds = {
                'lip_sync': 0.3,
                'facial_consistency': 0.4,
                'temporal_consistency': 0.4,
                'blink_rate': 0.2,
                'skin_texture': 0.4,
                'lighting_consistency': 0.4,
                'geometry_consistency': 0.4,
                'eye_movement_consistency': 0.4
            }
            
            for score_name, score_value in scores.items():
                threshold = thresholds.get(score_name, 0.5)
                if score_value < threshold:
                    anomalies.append(f"low_{score_name}")
            
            return anomalies
            
        except Exception as e:
            logger.warning(f"Anomaly identification failed: {e}")
            return []

# Global detector instance
_real_video_detector = None

def get_real_video_detector() -> AdvancedRealVideoDetector:
    """Get global real video detector instance"""
    global _real_video_detector
    if _real_video_detector is None:
        _real_video_detector = AdvancedRealVideoDetector()
    return _real_video_detector

async def analyze_real_video(faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> RealVideoAnalysis:
    """Main function for real video analysis"""
    detector = get_real_video_detector()
    return await detector.analyze_real_video(faces, audio_data)
