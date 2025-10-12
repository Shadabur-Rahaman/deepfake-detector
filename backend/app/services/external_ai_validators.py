# Create: app/services/external_ai_validators.py
import os
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

class ExternalAIValidator:
    def __init__(self):
        self.openai_available = self._check_openai_api()
        self.gemini_available = self._check_gemini_api()
        
    def _check_openai_api(self) -> bool:
        """Check if OpenAI API key is available"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key.strip() == "":
            logger.info("ℹ️ OpenAI API key not provided. OpenAI detection will use fallback analysis. Set OPENAI_API_KEY environment variable to enable full GPT-4V analysis.")
            logger.info("💡 To get an OpenAI API key: https://platform.openai.com/api-keys")
            return False
        
        # Test if the API key is valid by trying to create a client
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            logger.info("[OK] OpenAI API key is configured and valid")
            return True
        except ImportError:
            logger.warning("[WARNING] OpenAI library not installed. Install with: pip install openai")
            return False
        except Exception as e:
            logger.warning(f"[WARNING] OpenAI API key validation failed: {e}")
            logger.info("💡 Please check your API key at: https://platform.openai.com/api-keys")
            return False
    
    def _check_gemini_api(self) -> bool:
        """Check if Gemini API key is available"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.strip() == "":
            logger.info("ℹ️ Gemini API key not provided. Gemini detection will use fallback analysis. Set GEMINI_API_KEY environment variable to enable full Gemini analysis.")
            logger.info("💡 To get a Gemini API key: https://makersuite.google.com/app/apikey")
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            logger.info("[OK] Gemini API key is configured and valid")
            return True
        except ImportError:
            logger.warning("[WARNING] Google Generative AI library not installed. Install with: pip install google-generativeai")
            return False
        except Exception as e:
            logger.warning(f"[WARNING] Gemini API key validation failed: {e}")
            logger.info("💡 Please check your API key at: https://makersuite.google.com/app/apikey")
            return False
        
    async def openai_visual_analysis(self, video_frames: List[np.ndarray]) -> Dict:
        """GPT-4V visual analysis for premium validation"""
        if not self.openai_available:
            return {'available': False}
            
        try:
            import openai
            
            # Analyze key frames with GPT-4V
            frame_analysis = []
            for i, frame in enumerate(video_frames[:5]):  # Analyze 5 key frames
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4-vision-preview",
                    messages=[{
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "Analyze this video frame for signs of AI generation, deepfake artifacts, or synthetic content. Look for: 1) Facial inconsistencies 2) Unnatural textures 3) Temporal artifacts 4) Digital manipulation signs"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self._frame_to_base64(frame)}"}}
                        ]
                    }],
                    max_tokens=300
                )
                
                frame_analysis.append(response.choices[0].message.content)
            
            # Aggregate GPT-4V analysis
            return {
                'available': True,
                'analysis': frame_analysis,
                'confidence': self._extract_confidence_from_gpt_response(frame_analysis),
                'artifacts_detected': self._extract_artifacts_from_gpt_response(frame_analysis)
            }
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return {'available': False, 'error': str(e)}
    
    def _frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert frame to base64 string"""
        import cv2
        import base64
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64
    
    def _extract_confidence_from_gpt_response(self, responses: List[str]) -> float:
        """Extract confidence score from GPT responses"""
        # Simple confidence extraction - look for numbers in responses
        confidences = []
        for response in responses:
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                # Take the first number that looks like a confidence score
                for num in numbers:
                    conf = int(num)
                    if 0 <= conf <= 100:
                        confidences.append(conf)
                        break
        
        return np.mean(confidences) if confidences else 75.0
    
    def _extract_artifacts_from_gpt_response(self, responses: List[str]) -> List[str]:
        """Extract detected artifacts from GPT responses"""
        artifacts = []
        for response in responses:
            # Look for common artifact keywords
            artifact_keywords = ['inconsistency', 'artifact', 'unnatural', 'synthetic', 'generated', 'manipulation']
            for keyword in artifact_keywords:
                if keyword.lower() in response.lower():
                    artifacts.append(keyword)
        
        return list(set(artifacts))  # Remove duplicates
