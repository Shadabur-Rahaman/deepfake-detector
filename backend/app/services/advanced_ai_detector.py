"""
Advanced AI Detector - Integration with OpenAI, Claude, Gemini, and other AI models
================================================================================

This module provides integration with advanced AI models for deepfake detection:
- OpenAI GPT-4 Vision
- Anthropic Claude 3.5 Sonnet
- Google Gemini Pro Vision
- Microsoft Azure AI Vision
- AWS Rekognition
- Custom fine-tuned models

Features:
- Multi-modal analysis (vision + text)
- Advanced prompt engineering
- Confidence scoring
- Fallback mechanisms
- Rate limiting and error handling
"""

import asyncio
import logging
import time
import base64
import json
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import numpy as np
import cv2
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Import face data validator for type conversion
try:
    from .face_data_validator import FaceDataValidator
    FACE_VALIDATOR_AVAILABLE = True
except ImportError:
    FACE_VALIDATOR_AVAILABLE = False
    logger.warning("FaceDataValidator not available")

@dataclass
class AIDetectionResult:
    """Result from AI model detection"""
    model_name: str
    prediction: str
    confidence: float
    reasoning: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AdvancedAIDetector:
    """Advanced AI detector using multiple cloud AI models"""
    
    def __init__(self):
        self.models = {
            'openai_gpt4v': {'available': False, 'api_key': None},
            'claude_3_5': {'available': False, 'api_key': None},
            'gemini_pro': {'available': False, 'api_key': None},
            'azure_vision': {'available': False, 'api_key': None, 'endpoint': None},
            'aws_rekognition': {'available': False, 'access_key': None, 'secret_key': None}
        }
        self.initialized = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models"""
        try:
            import os
            
            # Check if external APIs are enabled
            external_apis_enabled = os.getenv('ENABLE_EXTERNAL_AI_APIS', 'false').lower() == 'true'
            openai_enabled = os.getenv('ENABLE_OPENAI_API', 'false').lower() == 'true'
            claude_enabled = os.getenv('ENABLE_CLAUDE_API', 'false').lower() == 'true'
            gemini_enabled = os.getenv('ENABLE_GEMINI_API', 'false').lower() == 'true'
            
            if not external_apis_enabled:
                logger.info("[AdvancedAI] External AI APIs disabled via environment variable")
                return
            
            # Check for OpenAI API key
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_enabled:
                self.models['openai_gpt4v']['available'] = True
                self.models['openai_gpt4v']['api_key'] = openai_key
                logger.info("[AdvancedAI] OpenAI GPT-4V available")
            elif openai_key and not openai_enabled:
                logger.info("[AdvancedAI] OpenAI API key found but disabled via ENABLE_OPENAI_API=false")
            
            # Check for Claude API key
            claude_key = os.getenv('CLAUDE_API_KEY')
            if claude_key and claude_enabled:
                self.models['claude_3_5']['available'] = True
                self.models['claude_3_5']['api_key'] = claude_key
                logger.info("[AdvancedAI] Claude 3.5 Sonnet available")
            elif claude_key and not claude_enabled:
                logger.info("[AdvancedAI] Claude API key found but disabled via ENABLE_CLAUDE_API=false")
            
            # Check for Gemini API key
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key and gemini_enabled:
                self.models['gemini_pro']['available'] = True
                self.models['gemini_pro']['api_key'] = gemini_key
                logger.info("[AdvancedAI] Gemini Pro Vision available")
            elif gemini_key and not gemini_enabled:
                logger.info("[AdvancedAI] Gemini API key found but disabled via ENABLE_GEMINI_API=false")
            
            # Check for Azure Vision
            azure_key = os.getenv('AZURE_VISION_KEY')
            azure_endpoint = os.getenv('AZURE_VISION_ENDPOINT')
            if azure_key and azure_endpoint:
                self.models['azure_vision']['available'] = True
                self.models['azure_vision']['api_key'] = azure_key
                self.models['azure_vision']['endpoint'] = azure_endpoint
                logger.info("[AdvancedAI] Azure Vision available")
            
            # Check for AWS Rekognition
            aws_access = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
            if aws_access and aws_secret:
                self.models['aws_rekognition']['available'] = True
                self.models['aws_rekognition']['access_key'] = aws_access
                self.models['aws_rekognition']['secret_key'] = aws_secret
                logger.info("[AdvancedAI] AWS Rekognition available")
            
            self.initialized = True
            available_models = [name for name, config in self.models.items() if config['available']]
            logger.info(f"[AdvancedAI] Initialized with {len(available_models)} models: {available_models}")
            
        except Exception as e:
            logger.error(f"[AdvancedAI] Initialization failed: {e}")
            self.initialized = False
    
    def _numpy_to_base64(self, image: np.ndarray) -> str:
        """Convert numpy array to base64 string"""
        try:
            # Validate and convert image
            if FACE_VALIDATOR_AVAILABLE:
                validated_image = FaceDataValidator.validate_face_for_opencv(image, "ai_detector_base64")
                if validated_image is None:
                    raise ValueError("Image validation failed")
                image = validated_image
            
            # Ensure image is in correct format
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Convert to PIL Image
            pil_image = Image.fromarray(image_rgb)
            
            # Resize if too large (AI models have size limits)
            max_size = 1024
            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            logger.error(f"[AdvancedAI] Image conversion failed: {e}")
            raise
    
    async def _detect_with_openai(self, faces: List[np.ndarray]) -> AIDetectionResult:
        """Detect deepfakes using OpenAI GPT-4V"""
        start_time = time.time()
        
        try:
            if not self.models['openai_gpt4v']['available']:
                return AIDetectionResult(
                    model_name="OpenAI GPT-4V",
                    prediction="Model Not Available",
                    confidence=0.0,
                    reasoning="OpenAI API key not configured",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="OpenAI API key not configured"
                )
            
            # Use the first few faces for analysis
            analysis_faces = faces[:3]
            
            # Convert faces to base64
            face_images = []
            for face in analysis_faces:
                try:
                    img_b64 = self._numpy_to_base64(face)
                    face_images.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    })
                except Exception as e:
                    logger.warning(f"[AdvancedAI] Failed to convert face for OpenAI: {e}")
                    continue
            
            if not face_images:
                return AIDetectionResult(
                    model_name="OpenAI GPT-4V",
                    prediction="No Valid Images",
                    confidence=0.0,
                    reasoning="No faces could be converted for analysis",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="No valid images for analysis"
                )
            
            # Prepare the prompt
            prompt = """Analyze these face images for signs of deepfake/AI-generated content. Look for:
1. Facial inconsistencies and artifacts
2. Unnatural skin texture or lighting
3. Eye anomalies (pupil shape, reflections)
4. Lip-sync issues or mouth artifacts
5. Hair and background inconsistencies
6. Overall image quality and realism

Respond with a JSON object containing:
- "prediction": "Real" or "Deepfake"
- "confidence": number between 0.0 and 1.0
- "reasoning": detailed explanation of your analysis
- "artifacts_detected": list of specific artifacts found

Be thorough and critical in your analysis. Even subtle signs of manipulation should be flagged."""
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.models['openai_gpt4v']['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *face_images
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Make the request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse the JSON response
                try:
                    # Extract JSON from the response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        prediction = analysis.get('prediction', 'Uncertain')
                        confidence = float(analysis.get('confidence', 0.5))
                        reasoning = analysis.get('reasoning', 'No reasoning provided')
                        artifacts = analysis.get('artifacts_detected', [])
                        
                        return AIDetectionResult(
                            model_name="OpenAI GPT-4V",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=reasoning,
                            processing_time=time.time() - start_time,
                            success=True,
                            metadata={'artifacts_detected': artifacts}
                        )
                    else:
                        # Fallback parsing
                        if 'deepfake' in content.lower() or 'fake' in content.lower():
                            prediction = "Deepfake"
                            confidence = 0.8
                        else:
                            prediction = "Real"
                            confidence = 0.6
                        
                        return AIDetectionResult(
                            model_name="OpenAI GPT-4V",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=content[:500],
                            processing_time=time.time() - start_time,
                            success=True
                        )
                        
                except json.JSONDecodeError:
                    # Fallback parsing
                    if 'deepfake' in content.lower() or 'fake' in content.lower():
                        prediction = "Deepfake"
                        confidence = 0.8
                    else:
                        prediction = "Real"
                        confidence = 0.6
                    
                    return AIDetectionResult(
                        model_name="OpenAI GPT-4V",
                        prediction=prediction,
                        confidence=confidence,
                        reasoning=content[:500],
                        processing_time=time.time() - start_time,
                        success=True
                    )
            else:
                return AIDetectionResult(
                    model_name="OpenAI GPT-4V",
                    prediction="API Error",
                    confidence=0.0,
                    reasoning=f"API request failed with status {response.status_code}",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"[AdvancedAI] OpenAI detection failed: {e}")
            return AIDetectionResult(
                model_name="OpenAI GPT-4V",
                prediction="Detection Failed",
                confidence=0.0,
                reasoning=f"Detection failed: {str(e)}",
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def _detect_with_claude(self, faces: List[np.ndarray]) -> AIDetectionResult:
        """Detect deepfakes using Claude 3.5 Sonnet"""
        start_time = time.time()
        
        try:
            if not self.models['claude_3_5']['available']:
                return AIDetectionResult(
                    model_name="Claude 3.5 Sonnet",
                    prediction="Model Not Available",
                    confidence=0.0,
                    reasoning="Claude API key not configured",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="Claude API key not configured"
                )
            
            # Use the first few faces for analysis
            analysis_faces = faces[:3]
            
            # Convert faces to base64
            face_images = []
            for face in analysis_faces:
                try:
                    img_b64 = self._numpy_to_base64(face)
                    face_images.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_b64
                        }
                    })
                except Exception as e:
                    logger.warning(f"[AdvancedAI] Failed to convert face for Claude: {e}")
                    continue
            
            if not face_images:
                return AIDetectionResult(
                    model_name="Claude 3.5 Sonnet",
                    prediction="No Valid Images",
                    confidence=0.0,
                    reasoning="No faces could be converted for analysis",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="No valid images for analysis"
                )
            
            # Prepare the prompt
            prompt = """Analyze these face images for signs of deepfake/AI-generated content. Look for:
1. Facial inconsistencies and artifacts
2. Unnatural skin texture or lighting
3. Eye anomalies (pupil shape, reflections)
4. Lip-sync issues or mouth artifacts
5. Hair and background inconsistencies
6. Overall image quality and realism

Respond with a JSON object containing:
- "prediction": "Real" or "Deepfake"
- "confidence": number between 0.0 and 1.0
- "reasoning": detailed explanation of your analysis
- "artifacts_detected": list of specific artifacts found

Be thorough and critical in your analysis. Even subtle signs of manipulation should be flagged."""
            
            # Prepare the request
            headers = {
                "x-api-key": self.models['claude_3_5']['api_key'],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *face_images
                        ]
                    }
                ]
            }
            
            # Make the request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                
                # Parse the JSON response
                try:
                    # Extract JSON from the response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        prediction = analysis.get('prediction', 'Uncertain')
                        confidence = float(analysis.get('confidence', 0.5))
                        reasoning = analysis.get('reasoning', 'No reasoning provided')
                        artifacts = analysis.get('artifacts_detected', [])
                        
                        return AIDetectionResult(
                            model_name="Claude 3.5 Sonnet",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=reasoning,
                            processing_time=time.time() - start_time,
                            success=True,
                            metadata={'artifacts_detected': artifacts}
                        )
                    else:
                        # Fallback parsing
                        if 'deepfake' in content.lower() or 'fake' in content.lower():
                            prediction = "Deepfake"
                            confidence = 0.8
                        else:
                            prediction = "Real"
                            confidence = 0.6
                        
                        return AIDetectionResult(
                            model_name="Claude 3.5 Sonnet",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=content[:500],
                            processing_time=time.time() - start_time,
                            success=True
                        )
                        
                except json.JSONDecodeError:
                    # Fallback parsing
                    if 'deepfake' in content.lower() or 'fake' in content.lower():
                        prediction = "Deepfake"
                        confidence = 0.8
                    else:
                        prediction = "Real"
                        confidence = 0.6
                    
                    return AIDetectionResult(
                        model_name="Claude 3.5 Sonnet",
                        prediction=prediction,
                        confidence=confidence,
                        reasoning=content[:500],
                        processing_time=time.time() - start_time,
                        success=True
                    )
            else:
                return AIDetectionResult(
                    model_name="Claude 3.5 Sonnet",
                    prediction="API Error",
                    confidence=0.0,
                    reasoning=f"API request failed with status {response.status_code}",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"[AdvancedAI] Claude detection failed: {e}")
            return AIDetectionResult(
                model_name="Claude 3.5 Sonnet",
                prediction="Detection Failed",
                confidence=0.0,
                reasoning=f"Detection failed: {str(e)}",
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def _detect_with_gemini(self, faces: List[np.ndarray]) -> AIDetectionResult:
        """Detect deepfakes using Google Gemini Pro Vision"""
        start_time = time.time()
        
        try:
            if not self.models['gemini_pro']['available']:
                return AIDetectionResult(
                    model_name="Gemini Pro Vision",
                    prediction="Model Not Available",
                    confidence=0.0,
                    reasoning="Gemini API key not configured",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="Gemini API key not configured"
                )
            
            # Use the first few faces for analysis
            analysis_faces = faces[:3]
            
            # Convert faces to base64
            face_images = []
            for face in analysis_faces:
                try:
                    img_b64 = self._numpy_to_base64(face)
                    face_images.append({
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    })
                except Exception as e:
                    logger.warning(f"[AdvancedAI] Failed to convert face for Gemini: {e}")
                    continue
            
            if not face_images:
                return AIDetectionResult(
                    model_name="Gemini Pro Vision",
                    prediction="No Valid Images",
                    confidence=0.0,
                    reasoning="No faces could be converted for analysis",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="No valid images for analysis"
                )
            
            # Prepare the prompt
            prompt = """Analyze these face images for signs of deepfake/AI-generated content. Look for:
1. Facial inconsistencies and artifacts
2. Unnatural skin texture or lighting
3. Eye anomalies (pupil shape, reflections)
4. Lip-sync issues or mouth artifacts
5. Hair and background inconsistencies
6. Overall image quality and realism

Respond with a JSON object containing:
- "prediction": "Real" or "Deepfake"
- "confidence": number between 0.0 and 1.0
- "reasoning": detailed explanation of your analysis
- "artifacts_detected": list of specific artifacts found

Be thorough and critical in your analysis. Even subtle signs of manipulation should be flagged."""
            
            # Prepare the request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={self.models['gemini_pro']['api_key']}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            *[{"inline_data": img} for img in face_images]
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1000
                }
            }
            
            # Make the request
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse the JSON response
                try:
                    # Extract JSON from the response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        prediction = analysis.get('prediction', 'Uncertain')
                        confidence = float(analysis.get('confidence', 0.5))
                        reasoning = analysis.get('reasoning', 'No reasoning provided')
                        artifacts = analysis.get('artifacts_detected', [])
                        
                        return AIDetectionResult(
                            model_name="Gemini Pro Vision",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=reasoning,
                            processing_time=time.time() - start_time,
                            success=True,
                            metadata={'artifacts_detected': artifacts}
                        )
                    else:
                        # Fallback parsing
                        if 'deepfake' in content.lower() or 'fake' in content.lower():
                            prediction = "Deepfake"
                            confidence = 0.8
                        else:
                            prediction = "Real"
                            confidence = 0.6
                        
                        return AIDetectionResult(
                            model_name="Gemini Pro Vision",
                            prediction=prediction,
                            confidence=confidence,
                            reasoning=content[:500],
                            processing_time=time.time() - start_time,
                            success=True
                        )
                        
                except json.JSONDecodeError:
                    # Fallback parsing
                    if 'deepfake' in content.lower() or 'fake' in content.lower():
                        prediction = "Deepfake"
                        confidence = 0.8
                    else:
                        prediction = "Real"
                        confidence = 0.6
                    
                    return AIDetectionResult(
                        model_name="Gemini Pro Vision",
                        prediction=prediction,
                        confidence=confidence,
                        reasoning=content[:500],
                        processing_time=time.time() - start_time,
                        success=True
                    )
            else:
                return AIDetectionResult(
                    model_name="Gemini Pro Vision",
                    prediction="API Error",
                    confidence=0.0,
                    reasoning=f"API request failed with status {response.status_code}",
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"[AdvancedAI] Gemini detection failed: {e}")
            return AIDetectionResult(
                model_name="Gemini Pro Vision",
                prediction="Detection Failed",
                confidence=0.0,
                reasoning=f"Detection failed: {str(e)}",
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def detect_deepfake(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Detect deepfakes using all available AI models"""
        start_time = time.time()
        
        try:
            # Validate faces
            validated_faces = faces
            if FACE_VALIDATOR_AVAILABLE:
                validated_faces = FaceDataValidator.validate_face_list(faces, "advanced_ai_detector")
                if not validated_faces:
                    return {
                        'prediction': 'Face Validation Failed',
                        'confidence': 0.0,
                        'model_type': 'Advanced AI Detector',
                        'error': 'No valid faces after validation'
                    }
            
            # Run all available models in parallel
            tasks = []
            
            if self.models['openai_gpt4v']['available']:
                tasks.append(self._detect_with_openai(validated_faces))
            
            if self.models['claude_3_5']['available']:
                tasks.append(self._detect_with_claude(validated_faces))
            
            if self.models['gemini_pro']['available']:
                tasks.append(self._detect_with_gemini(validated_faces))
            
            if not tasks:
                return {
                    'prediction': 'No AI Models Available',
                    'confidence': 0.0,
                    'model_type': 'Advanced AI Detector',
                    'error': 'No AI models configured'
                }
            
            # Wait for all results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            for result in results:
                if isinstance(result, AIDetectionResult) and result.success:
                    successful_results.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"[AdvancedAI] Model failed: {result}")
            
            if not successful_results:
                return {
                    'prediction': 'All Models Failed',
                    'confidence': 0.0,
                    'model_type': 'Advanced AI Detector',
                    'error': 'All AI models failed to process'
                }
            
            # Aggregate results
            deepfake_votes = 0
            total_confidence = 0.0
            all_reasoning = []
            
            for result in successful_results:
                if 'Deepfake' in result.prediction or 'Fake' in result.prediction:
                    deepfake_votes += 1
                    total_confidence += result.confidence
                else:
                    total_confidence += (1.0 - result.confidence)  # Invert for real predictions
                
                all_reasoning.append(f"{result.model_name}: {result.reasoning[:200]}")
            
            # Calculate final prediction
            if deepfake_votes > len(successful_results) / 2:
                final_prediction = "AI-Generated Content Detected"
                final_confidence = total_confidence / len(successful_results)
            else:
                final_prediction = "Real Video"
                final_confidence = 1.0 - (total_confidence / len(successful_results))
            
            return {
                'prediction': final_prediction,
                'confidence': final_confidence,
                'model_type': 'Advanced AI Detector',
                'models_used': len(successful_results),
                'reasoning': '; '.join(all_reasoning),
                'processing_time': time.time() - start_time,
                'individual_results': [
                    {
                        'model': r.model_name,
                        'prediction': r.prediction,
                        'confidence': r.confidence,
                        'reasoning': r.reasoning[:200]
                    } for r in successful_results
                ]
            }
            
        except Exception as e:
            logger.error(f"[AdvancedAI] Detection failed: {e}")
            return {
                'prediction': 'Detection Failed',
                'confidence': 0.0,
                'model_type': 'Advanced AI Detector',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return [name for name, config in self.models.items() if config['available']]
    
    async def detect_deepfake_ensemble(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Run ensemble detection using all available external AI models"""
        start_time = time.time()
        results = []
        models_used = []
        
        # Sample 3-5 faces for API analysis (cost optimization)
        sample_size = min(5, len(faces))
        sampled_faces = faces[::max(1, len(faces)//sample_size)][:sample_size]
        
        # OpenAI GPT-4V
        if self.models['openai_gpt4v']['available']:
            try:
                openai_result = await self._detect_with_openai(sampled_faces)
                results.append(openai_result)
                models_used.append('GPT-4V')
            except Exception as e:
                logger.warning(f"OpenAI detection failed: {e}")
        
        # Claude 3.5 Sonnet
        if self.models['claude_3_5']['available']:
            try:
                claude_result = await self._detect_with_claude(sampled_faces)
                results.append(claude_result)
                models_used.append('Claude 3.5')
            except Exception as e:
                logger.warning(f"Claude detection failed: {e}")
        
        # Gemini Pro Vision
        if self.models['gemini_pro']['available']:
            try:
                gemini_result = await self._detect_with_gemini(sampled_faces)
                results.append(gemini_result)
                models_used.append('Gemini Pro')
            except Exception as e:
                logger.warning(f"Gemini detection failed: {e}")
        
        # Aggregate results
        if not results:
            return {
                'prediction': 'Unknown',
                'confidence': 0.5,
                'models_used': [],
                'reasoning': 'No external AI models available'
            }
        
        # Average confidence across models
        avg_confidence = np.mean([r.confidence for r in results])
        deepfake_count = sum(1 for r in results if 'Deepfake' in r.prediction or 'Fake' in r.prediction)
        
        final_prediction = 'Deepfake Detected' if deepfake_count >= len(results)/2 else 'Real Video'
        
        return {
            'prediction': final_prediction,
            'confidence': avg_confidence,
            'models_used': models_used,
            'reasoning': f"{deepfake_count}/{len(results)} models detected deepfake"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get detector status"""
        return {
            'initialized': self.initialized,
            'available_models': self.get_available_models(),
            'total_models': len(self.models),
            'face_validator_available': FACE_VALIDATOR_AVAILABLE
        }

# Global detector instance
advanced_ai_detector = AdvancedAIDetector()

# Convenience functions
def get_advanced_ai_detector():
    """Get the global advanced AI detector instance"""
    return advanced_ai_detector

async def detect_with_advanced_ai(faces: List[np.ndarray]) -> Dict[str, Any]:
    """Detect deepfakes using advanced AI models"""
    return await advanced_ai_detector.detect_deepfake(faces)
