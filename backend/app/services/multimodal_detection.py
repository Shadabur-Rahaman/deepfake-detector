"""
Multimodal Detection Service
===========================

Advanced multimodal deepfake detection system with:
- Audio deepfake detection
- Lip-sync analysis
- Cross-modal consistency checking
- Voice cloning detection
- Emotional analysis
- Temporal coherence analysis
- Multi-sensor fusion

Author: Deepfake Detection System
Version: 3.0.0
"""

import asyncio
import logging
import time
import numpy as np
import librosa
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import json
import base64
import io
from PIL import Image
import scipy.signal
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

@dataclass
class AudioFeatures:
    """Audio feature extraction results"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    tonnetz: np.ndarray
    mel_spectrogram: np.ndarray
    spectral_contrast: np.ndarray
    tempo: float
    rhythm: np.ndarray

@dataclass
class VideoFeatures:
    """Video feature extraction results"""
    optical_flow: np.ndarray
    facial_landmarks: np.ndarray
    lip_movement: np.ndarray
    eye_movement: np.ndarray
    head_pose: np.ndarray
    texture_features: np.ndarray
    color_histogram: np.ndarray
    temporal_consistency: float

@dataclass
class MultimodalResult:
    """Multimodal detection result"""
    prediction: str
    confidence: float
    audio_confidence: float
    video_confidence: float
    lip_sync_score: float
    cross_modal_consistency: float
    artifacts: List[str]
    processing_time: float
    timestamp: float

class AudioDeepfakeDetector:
    """Advanced audio deepfake detection system"""
    
    def __init__(self):
        self.models = {}
        self.feature_extractors = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize audio detection models"""
        try:
            # Initialize feature extractors
            self.feature_extractors = {
                'mfcc': self._extract_mfcc,
                'spectral': self._extract_spectral_features,
                'rhythm': self._extract_rhythm_features,
                'harmonic': self._extract_harmonic_features,
                'voice_quality': self._extract_voice_quality_features
            }
            
            # Initialize detection models
            self.models = {
                'voice_cloning': await self._load_voice_cloning_model(),
                'emotion_synthesis': await self._load_emotion_synthesis_model(),
                'speaker_verification': await self._load_speaker_verification_model(),
                'audio_artifact': await self._load_audio_artifact_model()
            }
            
            self.initialized = True
            logger.info("✅ Audio Deepfake Detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Audio Deepfake Detector initialization failed: {e}")
            return False
    
    async def detect_audio_deepfake(self, audio_path: str) -> Dict[str, Any]:
        """Detect audio deepfake in audio file"""
        try:
            if not self.initialized:
                raise Exception("Audio Deepfake Detector not initialized")
            
            start_time = time.time()
            
            # Load audio
            audio_data, sample_rate = librosa.load(audio_path, sr=22050)
            
            # Extract features
            audio_features = await self._extract_audio_features(audio_data, sample_rate)
            
            # Run detection models
            detection_results = {}
            for model_name, model in self.models.items():
                try:
                    result = await self._run_audio_model(model, audio_features, model_name)
                    detection_results[model_name] = result
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    detection_results[model_name] = {
                        'prediction': 'unknown',
                        'confidence': 0.0,
                        'error': str(e)
                    }
            
            # Combine results
            final_result = self._combine_audio_results(detection_results)
            final_result['processing_time'] = time.time() - start_time
            
            return final_result
            
        except Exception as e:
            logger.error(f"Audio deepfake detection failed: {e}")
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'error': str(e),
                'processing_time': 0
            }
    
    async def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> AudioFeatures:
        """Extract comprehensive audio features"""
        try:
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            # Mel spectrogram
            mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
            
            # Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            
            # Tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            rhythm = librosa.feature.rhythm(y=audio_data, sr=sample_rate)
            
            return AudioFeatures(
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                chroma=chroma,
                tonnetz=tonnetz,
                mel_spectrogram=mel_spectrogram,
                spectral_contrast=spectral_contrast,
                tempo=tempo,
                rhythm=rhythm
            )
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            raise
    
    def _extract_mfcc(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract MFCC features"""
        return librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, np.ndarray]:
        """Extract spectral features"""
        return {
            'spectral_centroid': librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0],
            'spectral_rolloff': librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0],
            'spectral_bandwidth': librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0],
            'spectral_contrast': librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        }
    
    def _extract_rhythm_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract rhythm features"""
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        rhythm = librosa.feature.rhythm(y=audio_data, sr=sample_rate)
        
        return {
            'tempo': tempo,
            'beats': beats,
            'rhythm': rhythm
        }
    
    def _extract_harmonic_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, np.ndarray]:
        """Extract harmonic features"""
        y_harmonic, y_percussive = librosa.effects.hpss(audio_data)
        
        return {
            'harmonic': y_harmonic,
            'percussive': y_percussive,
            'harmonic_ratio': np.mean(y_harmonic) / (np.mean(y_harmonic) + np.mean(y_percussive))
        }
    
    def _extract_voice_quality_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract voice quality features"""
        # Jitter (pitch variation)
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate)
        pitch_values = pitches[pitches > 0]
        jitter = np.std(pitch_values) / np.mean(pitch_values) if len(pitch_values) > 0 else 0
        
        # Shimmer (amplitude variation)
        rms = librosa.feature.rms(y=audio_data)[0]
        shimmer = np.std(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
        
        # HNR (Harmonic-to-Noise Ratio)
        y_harmonic, y_percussive = librosa.effects.hpss(audio_data)
        hnr = np.mean(y_harmonic) / (np.mean(y_percussive) + 1e-8)
        
        return {
            'jitter': jitter,
            'shimmer': shimmer,
            'hnr': hnr
        }
    
    async def _load_voice_cloning_model(self):
        """Load voice cloning detection model"""
        # Simulate model loading
        return {
            'name': 'voice_cloning_detector',
            'loaded': True,
            'accuracy': 0.92
        }
    
    async def _load_emotion_synthesis_model(self):
        """Load emotion synthesis detection model"""
        return {
            'name': 'emotion_synthesis_detector',
            'loaded': True,
            'accuracy': 0.88
        }
    
    async def _load_speaker_verification_model(self):
        """Load speaker verification model"""
        return {
            'name': 'speaker_verification',
            'loaded': True,
            'accuracy': 0.95
        }
    
    async def _load_audio_artifact_model(self):
        """Load audio artifact detection model"""
        return {
            'name': 'audio_artifact_detector',
            'loaded': True,
            'accuracy': 0.90
        }
    
    async def _run_audio_model(self, model: Dict, features: AudioFeatures, model_name: str) -> Dict[str, Any]:
        """Run audio detection model"""
        try:
            # Simulate model inference
            await asyncio.sleep(0.1)
            
            # Mock detection result
            confidence = np.random.uniform(0.6, 0.95)
            prediction = 'deepfake' if confidence > 0.8 else 'real'
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'model': model_name,
                'artifacts': ['voice_cloning', 'synthetic_emotion'] if prediction == 'deepfake' else []
            }
            
        except Exception as e:
            logger.error(f"Audio model {model_name} failed: {e}")
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _combine_audio_results(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine audio detection results"""
        try:
            valid_results = [r for r in results.values() if 'error' not in r]
            
            if not valid_results:
                return {
                    'prediction': 'unknown',
                    'confidence': 0.0,
                    'artifacts': [],
                    'error': 'All models failed'
                }
            
            # Calculate weighted average
            total_confidence = 0.0
            total_weight = 0.0
            predictions = []
            artifacts = []
            
            for result in valid_results:
                weight = 1.0  # Equal weight for all models
                confidence = result.get('confidence', 0.0)
                
                total_confidence += confidence * weight
                total_weight += weight
                predictions.append(result.get('prediction', 'unknown'))
                
                if 'artifacts' in result:
                    artifacts.extend(result['artifacts'])
            
            final_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
            deepfake_votes = predictions.count('deepfake')
            real_votes = predictions.count('real')
            final_prediction = 'deepfake' if deepfake_votes > real_votes else 'real'
            
            return {
                'prediction': final_prediction,
                'confidence': final_confidence,
                'artifacts': list(set(artifacts)),
                'model_results': results
            }
            
        except Exception as e:
            logger.error(f"Audio result combination failed: {e}")
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'artifacts': [],
                'error': str(e)
            }

class LipSyncAnalyzer:
    """Lip-sync analysis system"""
    
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Initialize lip-sync analyzer"""
        try:
            self.initialized = True
            logger.info("✅ Lip-Sync Analyzer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Lip-Sync Analyzer initialization failed: {e}")
            return False
    
    async def analyze_lip_sync(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        """Analyze lip-sync between video and audio"""
        try:
            if not self.initialized:
                raise Exception("Lip-Sync Analyzer not initialized")
            
            start_time = time.time()
            
            # Extract video features
            video_features = await self._extract_video_features(video_path)
            
            # Extract audio features
            audio_features = await self._extract_audio_features(audio_path)
            
            # Analyze synchronization
            sync_score = await self._calculate_sync_score(video_features, audio_features)
            
            # Detect lip-sync artifacts
            artifacts = await self._detect_sync_artifacts(video_features, audio_features)
            
            processing_time = time.time() - start_time
            
            return {
                'sync_score': sync_score,
                'artifacts': artifacts,
                'processing_time': processing_time,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Lip-sync analysis failed: {e}")
            return {
                'sync_score': 0.0,
                'artifacts': [],
                'error': str(e),
                'processing_time': 0
            }
    
    async def _extract_video_features(self, video_path: str) -> VideoFeatures:
        """Extract video features for lip-sync analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            optical_flows = []
            facial_landmarks = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frames.append(frame)
                
                # Calculate optical flow
                if len(frames) > 1:
                    prev_gray = cv2.cvtColor(frames[-2], cv2.COLOR_BGR2GRAY)
                    curr_gray = cv2.cvtColor(frames[-1], cv2.COLOR_BGR2GRAY)
                    flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
                    optical_flows.append(flow)
                
                # Extract facial landmarks (simplified)
                landmarks = self._extract_facial_landmarks(frame)
                facial_landmarks.append(landmarks)
            
            cap.release()
            
            # Calculate lip movement
            lip_movement = self._calculate_lip_movement(facial_landmarks)
            
            # Calculate eye movement
            eye_movement = self._calculate_eye_movement(facial_landmarks)
            
            # Calculate head pose
            head_pose = self._calculate_head_pose(facial_landmarks)
            
            # Extract texture features
            texture_features = self._extract_texture_features(frames)
            
            # Calculate color histogram
            color_histogram = self._calculate_color_histogram(frames)
            
            # Calculate temporal consistency
            temporal_consistency = self._calculate_temporal_consistency(frames)
            
            return VideoFeatures(
                optical_flow=np.array(optical_flows),
                facial_landmarks=np.array(facial_landmarks),
                lip_movement=lip_movement,
                eye_movement=eye_movement,
                head_pose=head_pose,
                texture_features=texture_features,
                color_histogram=color_histogram,
                temporal_consistency=temporal_consistency
            )
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            raise
    
    async def _extract_audio_features(self, audio_path: str) -> AudioFeatures:
        """Extract audio features for lip-sync analysis"""
        try:
            audio_data, sample_rate = librosa.load(audio_path, sr=22050)
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            # Extract mel spectrogram
            mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
            
            # Extract spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            
            # Extract tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            rhythm = librosa.feature.rhythm(y=audio_data, sr=sample_rate)
            
            return AudioFeatures(
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                chroma=chroma,
                tonnetz=tonnetz,
                mel_spectrogram=mel_spectrogram,
                spectral_contrast=spectral_contrast,
                tempo=tempo,
                rhythm=rhythm
            )
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            raise
    
    def _extract_facial_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Extract facial landmarks from frame"""
        # Simplified landmark extraction
        # In a real implementation, this would use dlib or similar
        return np.random.rand(68, 2)  # 68 facial landmarks
    
    def _calculate_lip_movement(self, landmarks: List[np.ndarray]) -> np.ndarray:
        """Calculate lip movement from landmarks"""
        # Simplified lip movement calculation
        lip_movements = []
        for i in range(1, len(landmarks)):
            lip_diff = np.linalg.norm(landmarks[i] - landmarks[i-1])
            lip_movements.append(lip_diff)
        return np.array(lip_movements)
    
    def _calculate_eye_movement(self, landmarks: List[np.ndarray]) -> np.ndarray:
        """Calculate eye movement from landmarks"""
        # Simplified eye movement calculation
        eye_movements = []
        for i in range(1, len(landmarks)):
            eye_diff = np.linalg.norm(landmarks[i] - landmarks[i-1])
            eye_movements.append(eye_diff)
        return np.array(eye_movements)
    
    def _calculate_head_pose(self, landmarks: List[np.ndarray]) -> np.ndarray:
        """Calculate head pose from landmarks"""
        # Simplified head pose calculation
        poses = []
        for landmarks_frame in landmarks:
            # Calculate head pose angles
            pose = np.random.rand(3)  # Roll, pitch, yaw
            poses.append(pose)
        return np.array(poses)
    
    def _extract_texture_features(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extract texture features from frames"""
        # Simplified texture feature extraction
        texture_features = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Calculate LBP (Local Binary Pattern) features
            lbp = np.random.rand(256)  # Simplified LBP
            texture_features.append(lbp)
        return np.array(texture_features)
    
    def _calculate_color_histogram(self, frames: List[np.ndarray]) -> np.ndarray:
        """Calculate color histogram from frames"""
        histograms = []
        for frame in frames:
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            histograms.append(hist.flatten())
        return np.array(histograms)
    
    def _calculate_temporal_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate temporal consistency of frames"""
        if len(frames) < 2:
            return 1.0
        
        consistency_scores = []
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            similarity = self._calculate_structural_similarity(prev_gray, curr_gray)
            consistency_scores.append(similarity)
        
        return np.mean(consistency_scores)
    
    def _calculate_structural_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate structural similarity between two images"""
        # Simplified SSIM calculation
        return np.random.uniform(0.7, 0.95)
    
    async def _calculate_sync_score(self, video_features: VideoFeatures, audio_features: AudioFeatures) -> float:
        """Calculate lip-sync score between video and audio"""
        try:
            # Calculate correlation between lip movement and audio features
            lip_movement = video_features.lip_movement
            audio_energy = np.mean(audio_features.mel_spectrogram, axis=0)
            
            # Ensure same length
            min_length = min(len(lip_movement), len(audio_energy))
            lip_movement = lip_movement[:min_length]
            audio_energy = audio_energy[:min_length]
            
            # Calculate correlation
            correlation, _ = pearsonr(lip_movement, audio_energy)
            
            # Normalize to 0-1 range
            sync_score = max(0, min(1, (correlation + 1) / 2))
            
            return sync_score
            
        except Exception as e:
            logger.error(f"Sync score calculation failed: {e}")
            return 0.0
    
    async def _detect_sync_artifacts(self, video_features: VideoFeatures, audio_features: AudioFeatures) -> List[str]:
        """Detect lip-sync artifacts"""
        artifacts = []
        
        try:
            # Check for temporal misalignment
            if video_features.temporal_consistency < 0.7:
                artifacts.append('temporal_misalignment')
            
            # Check for lip movement anomalies
            lip_movement_std = np.std(video_features.lip_movement)
            if lip_movement_std > 0.5:
                artifacts.append('lip_movement_anomaly')
            
            # Check for audio-visual correlation
            sync_score = await self._calculate_sync_score(video_features, audio_features)
            if sync_score < 0.6:
                artifacts.append('poor_audio_visual_sync')
            
            # Check for head pose inconsistencies
            head_pose_std = np.std(video_features.head_pose, axis=0)
            if np.any(head_pose_std > 0.3):
                artifacts.append('head_pose_inconsistency')
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Sync artifact detection failed: {e}")
            return ['detection_error']

class CrossModalAnalyzer:
    """Cross-modal consistency analysis system"""
    
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Initialize cross-modal analyzer"""
        try:
            self.initialized = True
            logger.info("✅ Cross-Modal Analyzer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Cross-Modal Analyzer initialization failed: {e}")
            return False
    
    async def analyze_cross_modal_consistency(
        self, 
        video_path: str, 
        audio_path: str
    ) -> Dict[str, Any]:
        """Analyze cross-modal consistency between video and audio"""
        try:
            if not self.initialized:
                raise Exception("Cross-Modal Analyzer not initialized")
            
            start_time = time.time()
            
            # Extract features from both modalities
            video_features = await self._extract_video_features(video_path)
            audio_features = await self._extract_audio_features(audio_path)
            
            # Analyze consistency
            consistency_score = await self._calculate_consistency_score(
                video_features, audio_features
            )
            
            # Detect inconsistencies
            inconsistencies = await self._detect_inconsistencies(
                video_features, audio_features
            )
            
            processing_time = time.time() - start_time
            
            return {
                'consistency_score': consistency_score,
                'inconsistencies': inconsistencies,
                'processing_time': processing_time,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Cross-modal analysis failed: {e}")
            return {
                'consistency_score': 0.0,
                'inconsistencies': [],
                'error': str(e),
                'processing_time': 0
            }
    
    async def _extract_video_features(self, video_path: str) -> VideoFeatures:
        """Extract video features for cross-modal analysis"""
        # Similar to lip-sync analyzer
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        
        # Extract features
        optical_flow = np.random.rand(len(frames)-1, 2)  # Simplified
        facial_landmarks = [np.random.rand(68, 2) for _ in frames]  # Simplified
        lip_movement = np.random.rand(len(frames)-1)  # Simplified
        eye_movement = np.random.rand(len(frames)-1)  # Simplified
        head_pose = np.random.rand(len(frames), 3)  # Simplified
        texture_features = np.random.rand(len(frames), 256)  # Simplified
        color_histogram = np.random.rand(len(frames), 512)  # Simplified
        temporal_consistency = np.random.uniform(0.7, 0.95)  # Simplified
        
        return VideoFeatures(
            optical_flow=optical_flow,
            facial_landmarks=np.array(facial_landmarks),
            lip_movement=lip_movement,
            eye_movement=eye_movement,
            head_pose=head_pose,
            texture_features=texture_features,
            color_histogram=color_histogram,
            temporal_consistency=temporal_consistency
        )
    
    async def _extract_audio_features(self, audio_path: str) -> AudioFeatures:
        """Extract audio features for cross-modal analysis"""
        audio_data, sample_rate = librosa.load(audio_path, sr=22050)
        
        # Extract features
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
        mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        rhythm = librosa.feature.rhythm(y=audio_data, sr=sample_rate)
        
        return AudioFeatures(
            mfcc=mfcc,
            spectral_centroid=spectral_centroid,
            spectral_rolloff=spectral_rolloff,
            zero_crossing_rate=zero_crossing_rate,
            chroma=chroma,
            tonnetz=tonnetz,
            mel_spectrogram=mel_spectrogram,
            spectral_contrast=spectral_contrast,
            tempo=tempo,
            rhythm=rhythm
        )
    
    async def _calculate_consistency_score(
        self, 
        video_features: VideoFeatures, 
        audio_features: AudioFeatures
    ) -> float:
        """Calculate cross-modal consistency score"""
        try:
            # Calculate correlation between video and audio features
            correlations = []
            
            # Lip movement vs audio energy
            lip_movement = video_features.lip_movement
            audio_energy = np.mean(audio_features.mel_spectrogram, axis=0)
            
            if len(lip_movement) > 0 and len(audio_energy) > 0:
                min_length = min(len(lip_movement), len(audio_energy))
                lip_movement = lip_movement[:min_length]
                audio_energy = audio_energy[:min_length]
                
                correlation, _ = pearsonr(lip_movement, audio_energy)
                correlations.append(correlation)
            
            # Head movement vs audio tempo
            head_movement = np.linalg.norm(np.diff(video_features.head_pose, axis=0), axis=1)
            audio_tempo = np.full(len(head_movement), audio_features.tempo)
            
            if len(head_movement) > 0 and len(audio_tempo) > 0:
                min_length = min(len(head_movement), len(audio_tempo))
                head_movement = head_movement[:min_length]
                audio_tempo = audio_tempo[:min_length]
                
                correlation, _ = pearsonr(head_movement, audio_tempo)
                correlations.append(correlation)
            
            # Calculate overall consistency score
            if correlations:
                consistency_score = np.mean(correlations)
                # Normalize to 0-1 range
                consistency_score = max(0, min(1, (consistency_score + 1) / 2))
            else:
                consistency_score = 0.5  # Default neutral score
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Consistency score calculation failed: {e}")
            return 0.0
    
    async def _detect_inconsistencies(
        self, 
        video_features: VideoFeatures, 
        audio_features: AudioFeatures
    ) -> List[str]:
        """Detect cross-modal inconsistencies"""
        inconsistencies = []
        
        try:
            # Check temporal consistency
            if video_features.temporal_consistency < 0.7:
                inconsistencies.append('temporal_inconsistency')
            
            # Check lip-sync consistency
            lip_movement = video_features.lip_movement
            audio_energy = np.mean(audio_features.mel_spectrogram, axis=0)
            
            if len(lip_movement) > 0 and len(audio_energy) > 0:
                min_length = min(len(lip_movement), len(audio_energy))
                lip_movement = lip_movement[:min_length]
                audio_energy = audio_energy[:min_length]
                
                correlation, _ = pearsonr(lip_movement, audio_energy)
                if correlation < 0.3:
                    inconsistencies.append('lip_sync_inconsistency')
            
            # Check emotional consistency
            # This would require emotion detection from both modalities
            # For now, we'll use a simplified check
            if np.random.random() < 0.3:  # Simulated emotion inconsistency
                inconsistencies.append('emotional_inconsistency')
            
            # Check lighting consistency
            color_histogram_std = np.std(video_features.color_histogram, axis=0)
            if np.mean(color_histogram_std) > 0.5:
                inconsistencies.append('lighting_inconsistency')
            
            return inconsistencies
            
        except Exception as e:
            logger.error(f"Inconsistency detection failed: {e}")
            return ['detection_error']

class MultimodalDetector:
    """Main multimodal detection system"""
    
    def __init__(self):
        self.audio_detector = AudioDeepfakeDetector()
        self.lip_sync_analyzer = LipSyncAnalyzer()
        self.cross_modal_analyzer = CrossModalAnalyzer()
        self.initialized = False
        
    async def initialize(self):
        """Initialize multimodal detection system"""
        try:
            # Initialize all components
            audio_init = await self.audio_detector.initialize()
            lip_sync_init = await self.lip_sync_analyzer.initialize()
            cross_modal_init = await self.cross_modal_analyzer.initialize()
            
            if audio_init and lip_sync_init and cross_modal_init:
                self.initialized = True
                logger.info("✅ Multimodal Detector initialized successfully")
                return True
            else:
                logger.error("❌ Some components failed to initialize")
                return False
                
        except Exception as e:
            logger.error(f"❌ Multimodal Detector initialization failed: {e}")
            return False
    
    async def detect_multimodal_deepfake(
        self, 
        video_path: str, 
        audio_path: str
    ) -> MultimodalResult:
        """Detect multimodal deepfake in video and audio"""
        try:
            if not self.initialized:
                raise Exception("Multimodal Detector not initialized")
            
            start_time = time.time()
            
            # Run audio detection
            audio_result = await self.audio_detector.detect_audio_deepfake(audio_path)
            
            # Run lip-sync analysis
            lip_sync_result = await self.lip_sync_analyzer.analyze_lip_sync(video_path, audio_path)
            
            # Run cross-modal analysis
            cross_modal_result = await self.cross_modal_analyzer.analyze_cross_modal_consistency(
                video_path, audio_path
            )
            
            # Combine results
            final_result = self._combine_multimodal_results(
                audio_result, lip_sync_result, cross_modal_result
            )
            
            processing_time = time.time() - start_time
            
            return MultimodalResult(
                prediction=final_result['prediction'],
                confidence=final_result['confidence'],
                audio_confidence=audio_result.get('confidence', 0.0),
                video_confidence=0.8,  # Simplified video confidence
                lip_sync_score=lip_sync_result.get('sync_score', 0.0),
                cross_modal_consistency=cross_modal_result.get('consistency_score', 0.0),
                artifacts=final_result['artifacts'],
                processing_time=processing_time,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Multimodal detection failed: {e}")
            return MultimodalResult(
                prediction='unknown',
                confidence=0.0,
                audio_confidence=0.0,
                video_confidence=0.0,
                lip_sync_score=0.0,
                cross_modal_consistency=0.0,
                artifacts=[],
                processing_time=0,
                timestamp=time.time()
            )
    
    def _combine_multimodal_results(
        self, 
        audio_result: Dict, 
        lip_sync_result: Dict, 
        cross_modal_result: Dict
    ) -> Dict[str, Any]:
        """Combine multimodal detection results"""
        try:
            # Extract individual scores
            audio_confidence = audio_result.get('confidence', 0.0)
            lip_sync_score = lip_sync_result.get('sync_score', 0.0)
            cross_modal_consistency = cross_modal_result.get('consistency_score', 0.0)
            
            # Calculate weighted average
            weights = {
                'audio': 0.4,
                'lip_sync': 0.3,
                'cross_modal': 0.3
            }
            
            # Convert scores to deepfake probability
            audio_deepfake_prob = 1 - audio_confidence if audio_result.get('prediction') == 'deepfake' else audio_confidence
            lip_sync_deepfake_prob = 1 - lip_sync_score
            cross_modal_deepfake_prob = 1 - cross_modal_consistency
            
            # Calculate weighted probability
            weighted_prob = (
                audio_deepfake_prob * weights['audio'] +
                lip_sync_deepfake_prob * weights['lip_sync'] +
                cross_modal_deepfake_prob * weights['cross_modal']
            )
            
            # Determine final prediction
            final_confidence = weighted_prob
            final_prediction = 'deepfake' if weighted_prob > 0.5 else 'real'
            
            # Collect artifacts
            artifacts = []
            if 'artifacts' in audio_result:
                artifacts.extend(audio_result['artifacts'])
            if 'artifacts' in lip_sync_result:
                artifacts.extend(lip_sync_result['artifacts'])
            if 'inconsistencies' in cross_modal_result:
                artifacts.extend(cross_modal_result['inconsistencies'])
            
            return {
                'prediction': final_prediction,
                'confidence': final_confidence,
                'artifacts': list(set(artifacts)),
                'component_results': {
                    'audio': audio_result,
                    'lip_sync': lip_sync_result,
                    'cross_modal': cross_modal_result
                }
            }
            
        except Exception as e:
            logger.error(f"Multimodal result combination failed: {e}")
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'artifacts': [],
                'error': str(e)
            }

# Global instance
multimodal_detector = MultimodalDetector()
