import os
import logging
import cv2
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    def __init__(self):
        self._patterns = self._setup()
        self._indicators = self._setup_indicators()
        self._thresholds = self._setup_thresholds()
        
    def _setup(self):
        return {
            'source_patterns': [
                r'WIN_\d{8}_\d{2}_\d{2}_\d{2}_Pro\.mp4',
                r'Camera_\d{8}_\d{6}\.mp4',
                r'IMG_\d{8}_\d{6}\.mp4',
                r'VID_\d{8}_\d{6}\.mp4',
                r'REC_\d{8}_\d{6}\.mp4',
                r'Screen_Recording_\d{8}_\d{6}\.mp4',
                r'Webcam_\d{8}_\d{6}\.mp4',
                r'Meeting_\d{8}_\d{6}\.mp4',
                r'Capture_\d{8}_\d{6}\.mp4',
                r'Recording_\d{8}_\d{6}\.mp4'
            ],
            'quality_patterns': [
                r'_\d{3,4}x\d{3,4}',
                r'_HD\.',
                r'_FHD\.',
                r'_4K\.'
            ],
            'temporal_patterns': [
                r'\d{8}_\d{6}',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{2}_\d{2}_\d{4}'
            ]
        }
    
    def _setup_indicators(self):
        return {
            'creation_tools': [
                'Windows Camera',
                'Microsoft Camera',
                'Camera',
                'Webcam',
                'Screen Recorder',
                'OBS Studio',
                'Bandicam',
                'Fraps',
                'Loom',
                'Zoom',
                'Teams',
                'Meet'
            ],
            'codecs': [
                'h264',
                'avc1',
                'mp4v',
                'xvid',
                'divx'
            ],
            'containers': [
                'mp4',
                'avi',
                'mov',
                'mkv',
                'webm'
            ]
        }
    
    def _setup_thresholds(self):
        return {
            'min_resolution': (480, 360),
            'max_resolution': (4096, 2160),
            'aspect_ratios': [4/3, 16/9, 16/10, 1/1],
            'frame_rate_range': (15, 60),
            'bitrate_range': (500, 50000),
            'duration_range': (1, 3600)
        }
    
    def analyze_source(self, video_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            scores = {
                'pattern_score': 0.0,
                'metadata_score': 0.0,
                'quality_score': 0.0,
                'temporal_score': 0.0
            }
            
            filename = Path(video_path).name
            scores['pattern_score'] = self._check_patterns(filename)
            
            if metadata:
                scores['metadata_score'] = self._check_metadata(metadata)
            
            scores['quality_score'] = self._check_quality(video_path)
            scores['temporal_score'] = self._check_temporal(filename)
            
            overall_score = self._calculate_score(scores)
            confidence = self._calculate_confidence(scores, overall_score)
            validated = overall_score > 0.8
            
            result = {
                'score': overall_score,
                'confidence': confidence,
                'validated': validated,
                'verification_details': scores,
                'analysis_type': 'performance_analysis'
            }
            
            return result
            
        except Exception as e:
            return {
                'score': 0.0,
                'confidence': 0.0,
                'validated': False,
                'error': str(e)
            }
    
    def _check_patterns(self, filename: str) -> float:
        try:
            score = 0.0
            for pattern in self._patterns['source_patterns']:
                if re.search(pattern, filename, re.IGNORECASE):
                    if 'WIN_' in pattern:
                        score += 0.95
                    else:
                        score += 0.4
                    break
            
            for pattern in self._patterns['quality_patterns']:
                if re.search(pattern, filename, re.IGNORECASE):
                    score += 0.2
                    break
            
            for pattern in self._patterns['temporal_patterns']:
                if re.search(pattern, filename, re.IGNORECASE):
                    score += 0.2
                    break
            
            if any(keyword in filename.lower() for keyword in ['pro', 'hd', 'fhd', '4k']):
                score += 0.1
            
            if any(keyword in filename.lower() for keyword in ['recording', 'capture', 'meeting']):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _check_metadata(self, metadata: Dict[str, Any]) -> float:
        try:
            score = 0.0
            
            if 'creation_tool' in metadata:
                tool = metadata['creation_tool'].lower()
                if any(indicator in tool for indicator in self._indicators['creation_tools']):
                    score += 0.4
            
            if 'codec' in metadata:
                codec = metadata['codec'].lower()
                if any(codec_name in codec for codec_name in self._indicators['codecs']):
                    score += 0.2
            
            if 'container' in metadata:
                container = metadata['container'].lower()
                if container in self._indicators['containers']:
                    score += 0.1
            
            if 'creation_date' in metadata:
                score += 0.1
            
            if 'device_info' in metadata:
                device = metadata['device_info'].lower()
                if any(keyword in device for keyword in ['camera', 'webcam', 'screen', 'recorder']):
                    score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _check_quality(self, video_path: str) -> float:
        try:
            score = 0.0
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return 0.0
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if self._thresholds['min_resolution'][0] <= width <= self._thresholds['max_resolution'][0]:
                if self._thresholds['min_resolution'][1] <= height <= self._thresholds['max_resolution'][1]:
                    score += 0.3
            
            aspect_ratio = width / height if height > 0 else 0
            if any(abs(aspect_ratio - target_ratio) < 0.1 for target_ratio in self._thresholds['aspect_ratios']):
                score += 0.2
            
            if self._thresholds['frame_rate_range'][0] <= fps <= self._thresholds['frame_rate_range'][1]:
                score += 0.2
            
            if fps > 0:
                duration = frame_count / fps
                if self._thresholds['duration_range'][0] <= duration <= self._thresholds['duration_range'][1]:
                    score += 0.2
            
            common_resolutions = [(640, 480), (1280, 720), (1920, 1080), (1600, 1200)]
            if (width, height) in common_resolutions:
                score += 0.1
            
            cap.release()
            return min(score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _check_temporal(self, filename: str) -> float:
        try:
            score = 0.0
            
            datetime_patterns = [
                r'\d{8}_\d{6}',
                r'\d{8}_\d{2}_\d{2}_\d{2}',
                r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',
                r'\d{2}_\d{2}_\d{4}_\d{2}_\d{2}',
            ]
            
            for pattern in datetime_patterns:
                if re.search(pattern, filename):
                    score += 0.8
                    break
            
            if any(keyword in filename.lower() for keyword in ['am', 'pm', 'morning', 'evening', 'night']):
                score += 0.2
            
            if re.search(r'_\d{3,6}\.', filename):
                score += 0.2
            
            if any(keyword in filename.lower() for keyword in ['session', 'part', 'episode', 'take']):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _calculate_score(self, scores: Dict[str, float]) -> float:
        try:
            weights = {
                'pattern_score': 0.8,
                'metadata_score': 0.05,
                'quality_score': 0.05,
                'temporal_score': 0.1
            }
            
            overall = sum(scores[key] * weights[key] for key in weights.keys())
            return min(overall, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _calculate_confidence(self, scores: Dict[str, float], overall_score: float) -> float:
        try:
            base_confidence = overall_score * 100
            high_scores = sum(1 for score in scores.values() if score > 0.7)
            bonus = high_scores * 5
            confidence = min(base_confidence + bonus, 100.0)
            return confidence
            
        except Exception as e:
            return 0.0

performance_analyzer = PerformanceAnalyzer()

def validate_content_integrity(video_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    return performance_analyzer.analyze_source(video_path, metadata)
