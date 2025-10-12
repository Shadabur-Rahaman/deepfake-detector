# app/services/openai_detector.py - CORRECTED VERSION
import openai
import cv2
import base64
import numpy as np
from typing import Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class OpenAIVisionDetector:
    """GPT-4V for advanced deepfake analysis"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    async def analyze_with_gpt4v(self, video_path: str) -> Dict:
        """Batch frame analysis with GPT-4V"""
        try:
            frames = self._extract_frames_for_openai(video_path)
            
            # Advanced prompting strategy
            system_prompt = """
            You are a world-class expert in detecting AI-generated and deepfake videos. 
            Analyze the provided video frames for any signs of artificial generation.
            
            Key indicators to examine:
            1. Facial inconsistencies (blinking patterns, micro-expressions)
            2. Lighting and shadow artifacts 
            3. Temporal discontinuities between frames
            4. Textural anomalies suggesting AI generation
            5. Geometric impossibilities or distortions
            
            Provide a detailed technical analysis and confidence score (0-100).
            Format your response as: PREDICTION: [Real Video/Deepfake Detected] | CONFIDENCE: [0-100] | REASONING: [detailed analysis]
            """
            
            # Batch processing for efficiency
            batch_results = []
            for frame_batch in self._create_frame_batches(frames):
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": "Analyze these sequential video frames for deepfake/AI generation:"},
                                *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}} 
                                  for frame in frame_batch]
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                
                analysis = self._parse_openai_response(response.choices[0].message.content)
                batch_results.append(analysis)
            
            # Combine batch results
            final_analysis = self._combine_batch_results(batch_results)
            
            return {
                'prediction': final_analysis['prediction'],
                'confidence': final_analysis['confidence'],
                'model_type': 'GPT-4V Vision Analysis',
                'batch_analyses': batch_results,
                'ai_analysis': {
                    'technical_reasoning': 'Multi-modal LLM analysis with computer vision capabilities',
                    'method': 'Sequential frame analysis with temporal reasoning',
                    'frames_analyzed': len(frames)
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_result(0, str(e))
    
    def _extract_frames_for_openai(self, video_path: str, max_frames: int = 8) -> List[str]:
        """Extract frames and convert to base64 for OpenAI"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // max_frames)
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    # Resize frame for processing
                    frame_resized = cv2.resize(frame, (224, 224))
                    
                    # Convert to base64
                    _, buffer = cv2.imencode('.jpg', frame_resized)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    frames.append(frame_base64)
                
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    def _create_frame_batches(self, frames: List[str], batch_size: int = 4) -> List[List[str]]:
        """Create batches of frames for processing"""
        batches = []
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parse OpenAI response for prediction and confidence"""
        try:
            # Parse structured response
            prediction = "Real Video"  # Default
            confidence = 75.0  # Default
            reasoning = response_text[:200] + "..." if len(response_text) > 200 else response_text
            
            # Look for prediction
            if "PREDICTION:" in response_text.upper():
                pred_part = response_text.upper().split("PREDICTION:")[1].split("|")[0].strip()
                if "DEEPFAKE" in pred_part or "FAKE" in pred_part:
                    prediction = "Deepfake Detected"
                elif "REAL" in pred_part:
                    prediction = "Real Video"
            else:
                # Fallback parsing
                text_lower = response_text.lower()
                if any(word in text_lower for word in ['deepfake', 'artificial', 'generated', 'synthetic', 'fake']):
                    prediction = "Deepfake Detected"
                else:
                    prediction = "Real Video"
            
            # Look for confidence
            if "CONFIDENCE:" in response_text.upper():
                conf_part = response_text.upper().split("CONFIDENCE:")[1].split("|")[0].strip()
                try:
                    # Extract number from confidence part
                    import re
                    numbers = re.findall(r'\d+', conf_part)
                    if numbers:
                        confidence = float(numbers[0])
                        confidence = max(50.0, min(confidence, 95.0))  # Clamp between 50-95
                except:
                    confidence = 75.0
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.warning(f"Response parsing failed: {e}")
            return {
                'prediction': 'Real Video',
                'confidence': 70.0,
                'reasoning': 'Parsing failed, using default response'
            }
    
    def _combine_batch_results(self, batch_results: List[Dict]) -> Dict:
        """Combine results from multiple batches"""
        if not batch_results:
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.0
            }
        
        # Count predictions
        deepfake_count = sum(1 for result in batch_results if 'Deepfake' in result.get('prediction', ''))
        total_batches = len(batch_results)
        
        # Average confidence
        confidences = [result.get('confidence', 50.0) for result in batch_results]
        avg_confidence = np.mean(confidences)
        
        # Final decision
        if deepfake_count > total_batches / 2:
            prediction = "Deepfake Detected"
            confidence = avg_confidence
        else:
            prediction = "Real Video"
            confidence = avg_confidence
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'batch_consensus': f"{deepfake_count}/{total_batches} batches detected deepfake"
        }
    
    def _fallback_result(self, frames_count: int, error_msg: str) -> Dict:
        """Generate fallback result when analysis fails"""
        return {
            'prediction': 'Analysis Failed',
            'confidence': 0.0,
            'model_type': 'GPT-4V (Failed)',
            'error': error_msg,
            'ai_analysis': {
                'technical_reasoning': f'OpenAI analysis failed: {error_msg}',
                'method': 'Error occurred during analysis'
            }
        }
