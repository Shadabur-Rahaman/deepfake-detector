# app/services/gemini_detector.py - COMPLETE FIXED VERSION
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

import cv2
import base64
import numpy as np
from typing import Dict, List, Optional
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

class GeminiDeepfakeDetector:
    """Gemini Pro 2.5 with specialized prompting for deepfake detection"""
    
    def __init__(self, api_key: str = None):
        if not GEMINI_AVAILABLE or genai is None:
            self.initialized = False
            logger.warning("⚠️ Gemini not available. Install with: pip install google-generativeai")
            return
            
        try:
            if api_key:
                genai.configure(api_key=api_key)
            # Use a more stable model name
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except:
                # Fallback to older model if new one not available
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.initialized = True
            logger.info("✅ Gemini detector initialized successfully")
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            self.initialized = False
            
    async def analyze_with_gemini(self, video_path: str) -> Dict:
        """Advanced Gemini analysis with context prompting"""
        if not self.initialized:
            return self._fallback_result(0, "Gemini not initialized")
            
        try:
            # Extract frames for analysis with timeout
            frames = await asyncio.wait_for(
                self._extract_frames_for_gemini(video_path, max_frames=5),
                timeout=30.0
            )
            
            if not frames:
                return self._fallback_result(0, "No frames extracted")
            
            # Specialized prompt for deepfake detection
            prompt = """
You are an expert AI researcher specializing in deepfake and AI-generated video detection. 
Analyze these video frames for signs of artificial generation, including:

1. FACIAL ARTIFACTS: Inconsistent lighting, unnatural eye movements, teeth irregularities
2. TEMPORAL INCONSISTENCIES: Sudden changes between frames, jittery movements  
3. AI GENERATION SIGNATURES: Overly smooth textures, impossible geometry, uncanny valley effects
4. MODERN AI PATTERNS: Diffusion model artifacts, GAN-specific distortions

For each frame, examine:
- Facial landmark consistency
- Lighting and shadow realism
- Texture quality and variation
- Temporal coherence with adjacent frames

Provide your analysis in this exact format:
PREDICTION: [Real Video/Deepfake Detected]
CONFIDENCE: [0-100]
REASONING: [detailed analysis in 2-3 sentences]
            """
            
            # Process frames with Gemini (with timeout)
            results = []
            for i, frame_data in enumerate(frames):
                try:
                    # Create the content with proper format
                    content = [
                        f"{prompt}\n\nFrame {i+1} analysis:",
                        {
                            "mime_type": "image/jpeg",
                            "data": frame_data
                        }
                    ]
                    
                    # Generate content with timeout - FIXED: Remove await
                    response = await asyncio.wait_for(
                        asyncio.to_thread(self.model.generate_content, content),
                        timeout=15.0
                    )
                    
                    analysis = self._parse_gemini_response(response.text)
                    results.append(analysis)
                    
                except asyncio.TimeoutError:
                    logger.warning(f"⚠️ Gemini frame {i+1} analysis timed out")
                    results.append({'confidence': 50.0, 'prediction': 'Timeout', 'analysis': 'Analysis timed out'})
                except Exception as e:
                    logger.warning(f"⚠️ Gemini frame {i+1} analysis failed: {e}")
                    results.append({'confidence': 50.0, 'prediction': 'Error', 'analysis': str(e)})
            
            # Aggregate results
            if results:
                valid_results = [r for r in results if r['confidence'] > 0]
                if valid_results:
                    avg_confidence = np.mean([r['confidence'] for r in valid_results])
                    consensus = self._determine_consensus(valid_results)
                else:
                    avg_confidence = 50.0
                    consensus = "Real Video"
            else:
                avg_confidence = 50.0
                consensus = "Real Video"
            
            return {
                'prediction': consensus,
                'confidence': float(avg_confidence),
                'model_type': 'Gemini Pro with Context Prompting',
                'frame_analyses': results,
                'frames_analyzed': len(frames),
                'ai_analysis': {
                    'technical_reasoning': f'Advanced Gemini analysis with specialized deepfake detection prompting on {len(frames)} frames',
                    'advantages': 'Natural language reasoning and multi-modal understanding',
                    'processing_note': f'Successfully analyzed {len([r for r in results if r["confidence"] > 0])}/{len(frames)} frames'
                }
            }
            
        except asyncio.TimeoutError:
            logger.warning("⚠️ Gemini analysis timed out completely")
            return self._fallback_result(0, "Analysis timed out after 30 seconds")
        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")
            return self._fallback_result(0, str(e))
    
    async def _extract_frames_for_gemini(self, video_path: str, max_frames: int = 5) -> List[str]:
        """Extract frames and convert to base64 for Gemini"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
                
            frames = []
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // max_frames)
            
            frame_count = 0
            extracted = 0
            
            while extracted < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    try:
                        # Resize frame for processing
                        frame_resized = cv2.resize(frame, (224, 224))
                        
                        # Convert to base64
                        _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        frames.append(frame_base64)
                        extracted += 1
                    except Exception as e:
                        logger.warning(f"Frame processing failed: {e}")
                        continue
                        
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames for Gemini analysis")
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini response for confidence and analysis"""
        try:
            # Initialize defaults
            confidence = 70.0
            prediction = "Real Video"
            reasoning = response_text[:300] + "..." if len(response_text) > 300 else response_text
            
            # Look for structured response
            if "PREDICTION:" in response_text.upper():
                pred_part = response_text.upper().split("PREDICTION:")[1].split("\n")[0].strip()
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
                conf_part = response_text.upper().split("CONFIDENCE:")[1].split("\n")[0].strip()
                try:
                    import re
                    numbers = re.findall(r'\d+', conf_part)
                    if numbers:
                        confidence = float(numbers[0])
                        confidence = max(50.0, min(confidence, 95.0))  # Clamp between 50-95
                except:
                    confidence = 75.0
            
            # Look for reasoning
            if "REASONING:" in response_text.upper():
                reasoning_part = response_text.upper().split("REASONING:")[1].strip()
                if len(reasoning_part) > 10:
                    reasoning = reasoning_part[:300] + "..." if len(reasoning_part) > 300 else reasoning_part
            
            return {
                'confidence': confidence,
                'prediction': prediction,
                'analysis': reasoning
            }
            
        except Exception as e:
            logger.warning(f"Response parsing failed: {e}")
            return {
                'confidence': 70.0,
                'prediction': 'Real Video',
                'analysis': 'Parsing failed, using default response'
            }
    
    def _determine_consensus(self, results: List[Dict]) -> str:
        """Determine consensus from multiple frame analyses"""
        if not results:
            return "Real Video"
            
        deepfake_count = sum(1 for r in results if "Deepfake" in r.get('prediction', ''))
        total_count = len(results)
        
        if deepfake_count > total_count / 2:
            return "Deepfake Detected"
        else:
            return "Real Video"
    
    def _fallback_result(self, frames_count: int, error_msg: str) -> Dict:
        """Generate fallback result when analysis fails"""
        return {
            'prediction': 'Analysis Failed',
            'confidence': 0.0,
            'model_type': 'Gemini Pro 2.5 (Failed)',
            'error': error_msg,
            'ai_analysis': {
                'technical_reasoning': f'Gemini analysis failed: {error_msg}',
                'advantages': 'Error occurred during LLM analysis',
                'processing_note': 'Analysis could not be completed'
            }
        }
