# Create: app/services/external_ai_validators.py
class ExternalAIValidator:
    def __init__(self):
        self.openai_available = self._check_openai_api()
        self.gemini_available = self._check_gemini_api()
        
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
