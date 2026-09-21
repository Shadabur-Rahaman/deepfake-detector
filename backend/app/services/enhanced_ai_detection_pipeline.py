"""
Enhanced AI Detection Pipeline with Multi-Stage AI API Integration
================================================================

This service implements a sophisticated multi-stage detection pipeline that combines:
1. Traditional deepfake detection models (EfficientNet, Custom Trained)
2. Modern AI models (Vision Transformer, CLIP)
3. AI API models (Claude, OpenAI, Gemini) for cross-validation
4. Ensemble fusion for final decision

Author: Deepfake Detection System
Version: 4.0.0
"""

import asyncio
import base64
import json
import logging
import time
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import aiohttp
import cv2
import numpy as np
from PIL import Image
import io
from dataclasses import dataclass
from enum import Enum
import torch

# Load environment variables from config.env
try:
    from dotenv import load_dotenv
    load_dotenv('config.env')
except ImportError:
    pass

logger = logging.getLogger(__name__)

class DetectionStage(Enum):
    TRADITIONAL = "traditional"
    MODERN_AI = "modern_ai"
    AI_API = "ai_api"
    ENSEMBLE = "ensemble"

@dataclass
class DetectionResult:
    stage: DetectionStage
    model_name: str
    prediction: str
    confidence: float
    reasoning: str
    processing_time: float
    metadata: Dict[str, Any] = None

@dataclass
class PipelineResult:
    final_prediction: str
    final_confidence: float
    stage_results: List[DetectionResult]
    ensemble_weights: Dict[str, float]
    processing_time: float
    ai_api_used: bool
    cross_validation_score: float

class EnhancedAIDetectionPipeline:
    """
    Enhanced AI Detection Pipeline with Multi-Stage AI API Integration
    
    This pipeline implements a sophisticated approach:
    1. Traditional models for fast, reliable detection
    2. Modern AI models for advanced feature analysis
    3. AI API models for cross-validation and final decision
    4. Ensemble fusion for optimal results
    """
    
    def __init__(self):
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'claude': os.getenv('CLAUDE_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY')
        }
        
        self.api_enabled = {
            'openai': os.getenv('ENABLE_OPENAI_API', 'true').lower() == 'true' and bool(self.api_keys['openai']),
            'claude': os.getenv('ENABLE_CLAUDE_API', 'true').lower() == 'true' and bool(self.api_keys['claude']),
            'gemini': os.getenv('ENABLE_GEMINI_API', 'true').lower() == 'true' and bool(self.api_keys['gemini'])
        }
        
        # Stage weights for ensemble fusion
        self.stage_weights = {
            'traditional': 0.25,  # 25% - Fast, reliable baseline
            'modern_ai': 0.35,    # 35% - Advanced feature analysis
            'ai_api': 0.40        # 40% - Cross-validation and final decision
        }
        
        logger.info(f"Enhanced AI Detection Pipeline initialized")
        logger.info(f"API Status - OpenAI: {self.api_enabled['openai']}, Claude: {self.api_enabled['claude']}, Gemini: {self.api_enabled['gemini']}")
    
    async def detect_deepfake_multi_stage(self, video_path: str, faces: List[np.ndarray], video_id: str = None) -> PipelineResult:
        """
        Multi-stage deepfake detection with AI API integration
        
        Args:
            video_path: Path to the video file
            faces: List of extracted face images
            video_id: Optional video ID for tracking
            
        Returns:
            PipelineResult with comprehensive detection analysis
        """
        start_time = time.time()
        stage_results = []
        
        logger.info(f"🚀 Starting multi-stage AI detection for {video_id or 'unknown'}")
        
        # Stage 1: Traditional Models (Fast, Reliable)
        traditional_results = await self._stage_traditional_models(faces, video_path)
        stage_results.extend(traditional_results)
        
        # Stage 2: Modern AI Models (Advanced Features)
        modern_ai_results = await self._stage_modern_ai_models(faces, video_path)
        stage_results.extend(modern_ai_results)
        
        # Stage 3: AI API Models (Cross-validation)
        ai_api_results = await self._stage_ai_api_models(faces, video_path)
        stage_results.extend(ai_api_results)
        
        # Stage 4: Ensemble Fusion
        final_result = await self._stage_ensemble_fusion(stage_results, video_path)
        
        processing_time = time.time() - start_time
        
        # Calculate cross-validation score
        cross_validation_score = self._calculate_cross_validation_score(stage_results)
        
        result = PipelineResult(
            final_prediction=final_result['prediction'],
            final_confidence=final_result['confidence'],
            stage_results=stage_results,
            ensemble_weights=self.stage_weights,
            processing_time=processing_time,
            ai_api_used=any(self.api_enabled.values()),
            cross_validation_score=cross_validation_score
        )
        
        logger.info(f"✅ Multi-stage detection completed: {result.final_prediction} ({result.final_confidence:.1f}%)")
        logger.info(f"📊 Cross-validation score: {cross_validation_score:.3f}")
        logger.info(f"⏱️ Total processing time: {processing_time:.2f}s")
        
        return result
    
    async def _stage_traditional_models(self, faces: List[np.ndarray], video_path: str) -> List[DetectionResult]:
        """Stage 1: Traditional deepfake detection models"""
        logger.info("🔧 Stage 1: Running traditional models...")
        results = []
        
        try:
            # EfficientNet detection
            from services.deepfake_detector import detect_deepfake_in_frames
            start_time = time.time()
            
            # Use the existing detection system
            prediction, confidence = await detect_deepfake_in_frames(faces)
            processing_time = time.time() - start_time
            
            # Convert to our format
            is_deepfake = 'Deepfake' in prediction
            final_confidence = confidence if is_deepfake else (1.0 - confidence)
            
            results.append(DetectionResult(
                stage=DetectionStage.TRADITIONAL,
                model_name="EfficientNet + Custom Trained",
                prediction="Deepfake Detected" if is_deepfake else "Real Video",
                confidence=final_confidence,
                reasoning=f"Traditional model ensemble analysis",
                processing_time=processing_time,
                metadata={'raw_prediction': prediction, 'raw_confidence': confidence}
            ))
            
            logger.info(f"✅ Traditional models: {results[-1].prediction} ({results[-1].confidence:.3f})")
            
        except Exception as e:
            logger.warning(f"⚠️ Traditional models failed: {e}")
            results.append(DetectionResult(
                stage=DetectionStage.TRADITIONAL,
                model_name="EfficientNet + Custom Trained",
                prediction="Analysis Failed",
                confidence=0.5,
                reasoning=f"Traditional model analysis failed: {e}",
                processing_time=0.0
            ))
        
        # MesoNet Model
        try:
            from services.mesonet_detector import MesoNetDetector
            mesonet = MesoNetDetector()
            
            if faces:
                # Convert faces to tensor format for MesoNet
                face_tensors = []
                for face in faces:
                    if face is not None and face.size > 0:
                        # Convert to tensor format (C, H, W)
                        face_tensor = torch.from_numpy(face).permute(2, 0, 1).float() / 255.0
                        face_tensors.append(face_tensor)
                
                if face_tensors:
                    # Run MesoNet detection
                    mesonet_result = mesonet.predict(face_tensors)
                    
                    results.append(DetectionResult(
                        stage=DetectionStage.TRADITIONAL,
                        model_name="MesoNet",
                        prediction=mesonet_result.get('prediction', 'uncertain'),
                        confidence=mesonet_result.get('confidence', 0.5),
                        reasoning="MesoNet specialized deepfake detection architecture",
                        processing_time=0.0,  # MesoNet doesn't provide timing
                        metadata={'model_type': 'mesonet'}
                    ))
                    logger.info(f"✅ MesoNet: {mesonet_result.get('prediction', 'uncertain')} ({mesonet_result.get('confidence', 0.5):.3f})")
                else:
                    logger.warning("⚠️ No valid faces for MesoNet analysis")
            else:
                logger.warning("⚠️ No faces available for MesoNet analysis")
                
        except Exception as e:
            logger.warning(f"⚠️ MesoNet failed: {e}")
        
        return results
    
    async def _stage_modern_ai_models(self, faces: List[np.ndarray], video_path: str) -> List[DetectionResult]:
        """Stage 2: Modern AI models (Vision Transformer, CLIP)"""
        logger.info("🧠 Stage 2: Running modern AI models...")
        results = []
        
        # Vision Transformer
        try:
            from services.vision_transformer_detector import VisionTransformerDetector
            start_time = time.time()
            
            vt_detector = VisionTransformerDetector()
            vt_result = vt_detector.analyze_faces(faces)
            processing_time = time.time() - start_time
            
            results.append(DetectionResult(
                stage=DetectionStage.MODERN_AI,
                model_name="Vision Transformer",
                prediction=vt_result.get('prediction', 'Unknown'),
                confidence=vt_result.get('confidence', 0.5),
                reasoning="Vision Transformer global attention analysis",
                processing_time=processing_time,
                metadata=vt_result
            ))
            
            logger.info(f"✅ Vision Transformer: {results[-1].prediction} ({results[-1].confidence:.3f})")
            
        except Exception as e:
            logger.warning(f"⚠️ Vision Transformer failed: {e}")
            results.append(DetectionResult(
                stage=DetectionStage.MODERN_AI,
                model_name="Vision Transformer",
                prediction="Analysis Failed",
                confidence=0.5,
                reasoning=f"Vision Transformer analysis failed: {e}",
                processing_time=0.0
            ))
        
        # CLIP Detector
        try:
            from services.clip_detector import CLIPDetector
            start_time = time.time()
            
            clip_detector = CLIPDetector()
            clip_result = clip_detector.analyze_faces(faces)
            processing_time = time.time() - start_time
            
            results.append(DetectionResult(
                stage=DetectionStage.MODERN_AI,
                model_name="CLIP Vision-Language",
                prediction=clip_result.get('prediction', 'Unknown'),
                confidence=clip_result.get('confidence', 0.5),
                reasoning="CLIP vision-language understanding analysis",
                processing_time=processing_time,
                metadata=clip_result
            ))
            
            logger.info(f"✅ CLIP Detector: {results[-1].prediction} ({results[-1].confidence:.3f})")
            
        except Exception as e:
            logger.warning(f"⚠️ CLIP Detector failed: {e}")
            results.append(DetectionResult(
                stage=DetectionStage.MODERN_AI,
                model_name="CLIP Vision-Language",
                prediction="Analysis Failed",
                confidence=0.5,
                reasoning=f"CLIP analysis failed: {e}",
                processing_time=0.0
            ))
        
        return results
    
    async def _stage_ai_api_models(self, faces: List[np.ndarray], video_path: str) -> List[DetectionResult]:
        """Stage 3: AI API models for cross-validation"""
        logger.info("🌐 Stage 3: Running AI API models...")
        results = []
        
        # Prepare face images for API analysis
        face_images = []
        for i, face in enumerate(faces[:3]):  # Limit to 3 faces for API efficiency
            try:
                # Convert numpy array to PIL Image
                if face.dtype != np.uint8:
                    face = (face * 255).astype(np.uint8)
                
                pil_image = Image.fromarray(face)
                
                # Resize for API efficiency
                pil_image = pil_image.resize((512, 512), Image.Resampling.LANCZOS)
                face_images.append(pil_image)
            except Exception as e:
                logger.warning(f"⚠️ Failed to prepare face {i} for API: {e}")
        
        if not face_images:
            logger.warning("⚠️ No valid face images for API analysis")
            return results
        
        # OpenAI GPT-4 Vision
        if self.api_enabled['openai']:
            try:
                result = await self._analyze_with_openai(face_images[0], "deepfake detection")
                results.append(DetectionResult(
                    stage=DetectionStage.AI_API,
                    model_name="OpenAI GPT-4 Vision",
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    reasoning=result['reasoning'],
                    processing_time=result['processing_time'],
                    metadata=result.get('metadata', {})
                ))
                logger.info(f"✅ OpenAI GPT-4: {result['prediction']} ({result['confidence']:.3f})")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI API failed: {e}")
        
        # Claude 3.5 Sonnet
        if self.api_enabled['claude']:
            try:
                result = await self._analyze_with_claude(face_images[0], "deepfake detection")
                results.append(DetectionResult(
                    stage=DetectionStage.AI_API,
                    model_name="Claude 3.5 Sonnet",
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    reasoning=result['reasoning'],
                    processing_time=result['processing_time'],
                    metadata=result.get('metadata', {})
                ))
                logger.info(f"✅ Claude 3.5: {result['prediction']} ({result['confidence']:.3f})")
            except Exception as e:
                logger.warning(f"⚠️ Claude API failed: {e}")
        
        # Gemini 2.0 Flash
        if self.api_enabled['gemini']:
            try:
                result = await self._analyze_with_gemini(face_images[0], "deepfake detection")
                results.append(DetectionResult(
                    stage=DetectionStage.AI_API,
                    model_name="Gemini 2.0 Flash",
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    reasoning=result['reasoning'],
                    processing_time=result['processing_time'],
                    metadata=result.get('metadata', {})
                ))
                logger.info(f"✅ Gemini 2.0: {result['prediction']} ({result['confidence']:.3f})")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API failed: {e}")
        
        return results
    
    async def _analyze_with_openai(self, image: Image.Image, task: str) -> Dict:
        """Analyze image with OpenAI GPT-4 Vision"""
        start_time = time.time()
        
        try:
            # Convert image to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this image for {task}. Look for signs of AI generation, deepfake artifacts, or synthetic content. Respond with JSON format: {{\"prediction\": \"Real\" or \"Deepfake\", \"confidence\": 0.0-1.0, \"reasoning\": \"detailed explanation\"}}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post("https://api.openai.com/v1/chat/completions", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parse JSON response
                        try:
                            result = json.loads(content)
                            return {
                                'prediction': result.get('prediction', 'Unknown'),
                                'confidence': float(result.get('confidence', 0.5)),
                                'reasoning': result.get('reasoning', 'OpenAI analysis'),
                                'processing_time': time.time() - start_time,
                                'metadata': {'api_response': data}
                            }
                        except json.JSONDecodeError:
                            # Fallback parsing
                            if 'deepfake' in content.lower() or 'fake' in content.lower():
                                return {
                                    'prediction': 'Deepfake Detected',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                            else:
                                return {
                                    'prediction': 'Real Video',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"OpenAI API analysis failed: {e}")
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.5,
                'reasoning': f'OpenAI API error: {e}',
                'processing_time': time.time() - start_time
            }
    
    async def _analyze_with_claude(self, image: Image.Image, task: str) -> Dict:
        """Analyze image with Claude 3.5 Sonnet"""
        start_time = time.time()
        
        try:
            # Convert image to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            headers = {
                "Authorization": f"Bearer {self.api_keys['claude']}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this image for {task}. Look for signs of AI generation, deepfake artifacts, or synthetic content. Respond with JSON format: {{\"prediction\": \"Real\" or \"Deepfake\", \"confidence\": 0.0-1.0, \"reasoning\": \"detailed explanation\"}}"
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post("https://api.anthropic.com/v1/messages", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['content'][0]['text']
                        
                        # Parse JSON response
                        try:
                            result = json.loads(content)
                            return {
                                'prediction': result.get('prediction', 'Unknown'),
                                'confidence': float(result.get('confidence', 0.5)),
                                'reasoning': result.get('reasoning', 'Claude analysis'),
                                'processing_time': time.time() - start_time,
                                'metadata': {'api_response': data}
                            }
                        except json.JSONDecodeError:
                            # Fallback parsing
                            if 'deepfake' in content.lower() or 'fake' in content.lower():
                                return {
                                    'prediction': 'Deepfake Detected',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                            else:
                                return {
                                    'prediction': 'Real Video',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Claude API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Claude API analysis failed: {e}")
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.5,
                'reasoning': f'Claude API error: {e}',
                'processing_time': time.time() - start_time
            }
    
    async def _analyze_with_gemini(self, image: Image.Image, task: str) -> Dict:
        """Analyze image with Gemini 2.0 Flash"""
        start_time = time.time()
        
        try:
            # Convert image to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_keys['gemini']}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"Analyze this image for {task}. Look for signs of AI generation, deepfake artifacts, or synthetic content. Respond with JSON format: {{\"prediction\": \"Real\" or \"Deepfake\", \"confidence\": 0.0-1.0, \"reasoning\": \"detailed explanation\"}}"
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 500
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['candidates'][0]['content']['parts'][0]['text']
                        
                        # Parse JSON response
                        try:
                            result = json.loads(content)
                            return {
                                'prediction': result.get('prediction', 'Unknown'),
                                'confidence': float(result.get('confidence', 0.5)),
                                'reasoning': result.get('reasoning', 'Gemini analysis'),
                                'processing_time': time.time() - start_time,
                                'metadata': {'api_response': data}
                            }
                        except json.JSONDecodeError:
                            # Fallback parsing
                            if 'deepfake' in content.lower() or 'fake' in content.lower():
                                return {
                                    'prediction': 'Deepfake Detected',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                            else:
                                return {
                                    'prediction': 'Real Video',
                                    'confidence': 0.7,
                                    'reasoning': content[:200],
                                    'processing_time': time.time() - start_time
                                }
                    else:
                        raise Exception(f"Gemini API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Gemini API analysis failed: {e}")
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.5,
                'reasoning': f'Gemini API error: {e}',
                'processing_time': time.time() - start_time
            }
    
    async def _stage_ensemble_fusion(self, stage_results: List[DetectionResult], video_path: str) -> Dict:
        """Stage 4: Ensemble fusion of all results"""
        logger.info("🎯 Stage 4: Ensemble fusion...")
        
        # Group results by stage
        traditional_results = [r for r in stage_results if r.stage == DetectionStage.TRADITIONAL]
        modern_ai_results = [r for r in stage_results if r.stage == DetectionStage.MODERN_AI]
        ai_api_results = [r for r in stage_results if r.stage == DetectionStage.AI_API]
        
        # Calculate stage averages
        traditional_avg = self._calculate_stage_average(traditional_results)
        modern_ai_avg = self._calculate_stage_average(modern_ai_results)
        ai_api_avg = self._calculate_stage_average(ai_api_results)
        
        # Weighted ensemble fusion
        weights = self.stage_weights
        total_weight = 0
        weighted_sum = 0
        
        if traditional_avg is not None:
            weighted_sum += traditional_avg * weights['traditional']
            total_weight += weights['traditional']
        
        if modern_ai_avg is not None:
            weighted_sum += modern_ai_avg * weights['modern_ai']
            total_weight += weights['modern_ai']
        
        if ai_api_avg is not None:
            weighted_sum += ai_api_avg * weights['ai_api']
            total_weight += weights['ai_api']
        
        # Normalize by total weight
        if total_weight > 0:
            final_confidence = weighted_sum / total_weight
        else:
            final_confidence = 0.5
        
        # Determine final prediction
        if final_confidence > 0.6:
            final_prediction = "Deepfake Detected"
        elif final_confidence < 0.4:
            final_prediction = "Real Video"
        else:
            final_prediction = "Uncertain - Requires Manual Review"
        
        logger.info(f"✅ Ensemble fusion: {final_prediction} ({final_confidence:.3f})")
        traditional_str = f"{traditional_avg:.3f}" if traditional_avg is not None else "N/A"
        modern_ai_str = f"{modern_ai_avg:.3f}" if modern_ai_avg is not None else "N/A"
        ai_api_str = f"{ai_api_avg:.3f}" if ai_api_avg is not None else "N/A"
        logger.info(f"📊 Stage contributions - Traditional: {traditional_str}, Modern AI: {modern_ai_str}, AI API: {ai_api_str}")
        
        return {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'stage_averages': {
                'traditional': traditional_avg,
                'modern_ai': modern_ai_avg,
                'ai_api': ai_api_avg
            }
        }
    
    def _calculate_stage_average(self, results: List[DetectionResult]) -> Optional[float]:
        """Calculate average confidence for a stage"""
        if not results:
            return None
        
        valid_results = [r for r in results if r.confidence is not None and r.prediction != "Analysis Failed"]
        if not valid_results:
            return None
        
        # Convert predictions to confidence scores
        confidence_scores = []
        for result in valid_results:
            if "Deepfake" in result.prediction:
                confidence_scores.append(result.confidence)
            elif "Real" in result.prediction:
                confidence_scores.append(1.0 - result.confidence)
            else:
                confidence_scores.append(result.confidence)
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _calculate_cross_validation_score(self, stage_results: List[DetectionResult]) -> float:
        """Calculate cross-validation score based on agreement between stages"""
        if len(stage_results) < 2:
            return 0.5
        
        # Group by stage
        traditional_results = [r for r in stage_results if r.stage == DetectionStage.TRADITIONAL]
        modern_ai_results = [r for r in stage_results if r.stage == DetectionStage.MODERN_AI]
        ai_api_results = [r for r in stage_results if r.stage == DetectionStage.AI_API]
        
        # Calculate stage averages
        traditional_avg = self._calculate_stage_average(traditional_results)
        modern_ai_avg = self._calculate_stage_average(modern_ai_results)
        ai_api_avg = self._calculate_stage_average(ai_api_results)
        
        # Calculate agreement
        scores = [s for s in [traditional_avg, modern_ai_avg, ai_api_avg] if s is not None]
        if len(scores) < 2:
            return 0.5
        
        # Calculate variance (lower variance = higher agreement)
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Convert variance to agreement score (0-1, higher is better)
        agreement_score = max(0, 1 - variance * 4)  # Scale factor for reasonable range
        
        return agreement_score

# Global instance
enhanced_ai_pipeline = EnhancedAIDetectionPipeline()
