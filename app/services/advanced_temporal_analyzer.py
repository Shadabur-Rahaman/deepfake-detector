# app/services/advanced_temporal_analyzer.py - FIXED: TIMEOUT PROTECTION

import cv2
import numpy as np
import torch
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)

class UltraTemporalAnalyzer:
    """FIXED: Timeout-protected analyzer to enhance robustness"""

    def __init__(self):
        self.max_analysis_time = 45  # overall max analysis time in seconds
        self.max_frames_to_process = 15  # number of frames to extract and process

    async def comprehensive_analysis(self, video_path: str, faces=None):
        """Main method to perform full temporal analysis with timeout protection"""
        try:
            logger.info(f"Starting temporal analysis with timeout {self.max_analysis_time}s")
            return await asyncio.wait_for(
                self._run_analysis(video_path, faces), 
                timeout=self.max_analysis_time
            )
        except asyncio.TimeoutError:
            logger.warning("Temporal analysis timed out")
            return {
                'ai_probability': 0.4,
                'confidence': 60.0,
                'artifacts': ['analysis_timeout'],
                'error': 'Analysis timed out',
                'frames_processed': 0
            }
        except Exception as e:
            logger.error(f"Temporal analysis failed: {str(e)}")
            return {
                'ai_probability': 0.35,
                'confidence': 55.0,
                'artifacts': ['analysis_failed'],
                'error': str(e),
                'frames_processed': 0
            }

    async def _run_analysis(self, video_path: str, faces):
        """Core analysis workflow"""
        frames = await self._extract_frames(video_path)
        if len(frames) < 3:
            logger.warning("Insufficient frames extracted for temporal analysis")
            return {
                'ai_probability': 0.3,
                'confidence': 50.0,
                'artifacts': ['insufficient_frames'],
                'frames_processed': len(frames)
            }

        analyses = {}
        try:
            # Run core analyses with individual timeouts
            analyses['frame_difference'] = await asyncio.wait_for(
                self._frame_difference(frames), timeout=10.0
            )
            analyses['optical_flow'] = await asyncio.wait_for(
                self._optical_flow(frames), timeout=15.0
            )
            analyses['edge_consistency'] = await asyncio.wait_for(
                self._edge_consistency(frames), timeout=10.0
            )

            # Optional motion vector analysis if time permits
            remaining_time = self.max_analysis_time - 35
            if remaining_time > 5:
                try:
                    analyses['motion_vector'] = await asyncio.wait_for(
                        self._motion_vector(frames), timeout=remaining_time
                    )
                except asyncio.TimeoutError:
                    logger.warning("Motion vector analysis skipped due to timeout")
        except asyncio.TimeoutError as e:
            logger.warning(f"Some analyses timed out: {str(e)}")

        return self._ensemble_decision(analyses, len(frames))

    async def _extract_frames(self, video_path: str):
        """Extract frames with timeout protection"""
        def extract_frames_sync():
            frames = []
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return frames

                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                frame_interval = max(1, total_frames // self.max_frames_to_process)
                read_count = 0
                extracted_count = 0

                while extracted_count < self.max_frames_to_process:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if read_count % frame_interval == 0:
                        resized = cv2.resize(frame, (224, 224))
                        frames.append(resized)
                        extracted_count += 1
                    read_count += 1
                    # Safety check to prevent infinite loops
                    if read_count > total_frames * 2:
                        break

                cap.release()
            except Exception as e:
                logger.error(f"Error during frame extraction: {str(e)}")
            return frames

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(extract_frames_sync)
                frames = await asyncio.wait_for(
                    asyncio.wrap_future(future), timeout=20.0
                )
                return frames
        except (asyncio.TimeoutError, FuturesTimeoutError):
            logger.warning("Frame extraction timed out")
            return []
        except Exception as e:
            logger.error(f"Failed to extract frames: {str(e)}")
            return []

    async def _frame_difference(self, frames):
        """Analyze frame-to-frame differences"""
        try:
            differences = []
            for i in range(min(len(frames) - 1, 8)):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY).astype(np.float32)
                differences.append(np.mean(np.abs(gray1 - gray2)))

            if differences:
                var = np.var(differences)
                consistency = 1.0 / (1.0 + var / 100.0)
                return {
                    'score': min(consistency, 0.8),
                    'artifacts': ['consistent_differences'] if consistency > 0.6 else []
                }
            return {'score': 0.3, 'artifacts': []}
        except Exception as e:
            logger.warning(f"Error in frame difference analysis: {str(e)}")
            return {'score': 0.35, 'artifacts': ['analysis_failed']}

    async def _optical_flow(self, frames):
        """Analyze optical flow patterns"""
        try:
            consistencies = []
            for i in range(min(len(frames) - 1, 6)):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(
                    gray1, gray2, None, 0.5, 2, 10, 2, 3, 1.1, 0
                )
                if flow is not None and flow.size > 0:
                    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                    consistencies.append(np.std(magnitude) / (np.mean(magnitude) + 1e-8))

            if consistencies:
                avg = np.mean(consistencies)
                score = 0.7 if avg < 0.5 else 0.3 if avg < 2.0 else 0.2
                return {
                    'score': score,
                    'artifacts': ['smooth_optical_flow'] if score > 0.5 else []
                }
            return {'score': 0.3, 'artifacts': []}
        except Exception as e:
            logger.warning(f"Error in optical flow analysis: {str(e)}")
            return {'score': 0.35, 'artifacts': ['analysis_failed']}

    async def _edge_consistency(self, frames):
        """Analyze edge temporal consistency"""
        try:
            correlations = []
            for i in range(min(len(frames) - 1, 5)):
                edge1 = cv2.Canny(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY), 50, 150)
                edge2 = cv2.Canny(cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY), 50, 150)
                corr = np.corrcoef(edge1.flatten(), edge2.flatten())[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)

            if correlations:
                avg_corr = np.mean(correlations)
                score = 0.6 if avg_corr > 0.95 else 0.3 if avg_corr > 0.8 else 0.2
                return {
                    'score': score,
                    'artifacts': ['overly_consistent_edges'] if score > 0.5 else []
                }
            return {'score': 0.3, 'artifacts': []}
        except Exception as e:
            logger.warning(f"Error in edge consistency analysis: {str(e)}")
            return {'score': 0.35, 'artifacts': ['analysis_failed']}

    async def _motion_vector(self, frames):
        """Analyze motion vector patterns"""
        try:
            motion_scores = []
            for i in range(min(len(frames) - 1, 4)):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                corners = cv2.goodFeaturesToTrack(
                    gray1, maxCorners=50, qualityLevel=0.3, minDistance=7
                )
                
                if corners is not None and len(corners) > 10:
                    next_pts, status, _ = cv2.calcOpticalFlowPyrLK(gray1, gray2, corners, None)
                    good_new = next_pts[status == 1]
                    good_old = corners[status == 1]
                    
                    if len(good_new) > 5:
                        motion_vectors = good_new - good_old
                        motion_scores.append(np.var(np.linalg.norm(motion_vectors, axis=1)))

            if motion_scores:
                avg_motion = np.mean(motion_scores)
                score = 0.7 if avg_motion < 1.0 else 0.3
                return {
                    'score': score,
                    'artifacts': ['artificial_motion'] if score > 0.5 else []
                }
            return {'score': 0.3, 'artifacts': []}
        except Exception as e:
            logger.warning(f"Error in motion vector analysis: {str(e)}")
            return {'score': 0.35, 'artifacts': ['analysis_failed']}

    def _ensemble_decision(self, analyses, frames_processed):
        """Make ensemble decision from all analyses"""
        if not analyses:
            return {
                'ai_probability': 0.35,
                'confidence': 55.0,
                'artifacts': ['no_analyses_done'],
                'frames_processed': frames_processed
            }

        weights = {
            'frame_difference': 0.3,
            'optical_flow': 0.3,
            'edge_consistency': 0.25,
            'motion_vector': 0.15
        }

        total_score = 0.0
        total_weight = 0.0
        artifacts = []

        for analysis_name, result in analyses.items():
            if analysis_name in weights and isinstance(result, dict):
                score = result.get('score', 0.3)
                weight = weights[analysis_name]
                total_score += score * weight
                total_weight += weight
                artifacts.extend(result.get('artifacts', []))

        final_score = total_score / total_weight if total_weight else 0.35
        final_score = max(0.15, min(final_score, 0.85))
        confidence = min(final_score * 100 + 20, 95.0)

        logger.info(f"Final ensemble confidence: {confidence}")

        return {
            'ai_probability': final_score,
            'confidence': confidence,
            'artifacts': list(set(artifacts)),
            'analyses_done': list(analyses.keys()),
            'frames_processed': frames_processed
        }


# Create global instance for easy import
ultra_temporal_analyzer = UltraTemporalAnalyzer()
