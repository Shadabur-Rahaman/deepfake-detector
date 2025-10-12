import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class IntelligentTitleClassifier:
    """Advanced title-based classification for modern AI tools"""
    
    def __init__(self):
        self.deepfake_keywords = {
            'direct': [
                'deepfake', 'deep fake', 'deep-fake',
                'face swap', 'faceswap', 'fake', 'artificial',
                'generated', 'ai generated', 'synthetic',
                'ai video', 'ai art', 'aiart'
            ],
            'ai_tools': [
                # Video Generation Tools
                'veo', 'veo3', 'veo 3', 'google veo',
                'sora', 'openai sora', 'sora ai',
                'runway', 'runwayml', 'gen-2', 'gen2',
                'pika', 'pika labs', 'pika ai',
                'luma', 'luma dream', 'luma ai',
                
                # Image Generation Tools
                'midjourney', 'midjourney ai', 'mj',
                'dall-e', 'dalle', 'dall e',
                'stable diffusion', 'sd', 'leonardo',
                'ideogram', 'flux', 'black forest'
            ],
            'technical': [
                'neural network', 'machine learning', 'ml',
                'diffusion model', 'gan', 'generative',
                'transformer', 'ai model', 'neural rendering',
                'aftereffects', 'ae', 'adobe after effects'
            ]
        }
        
        self.authentic_keywords = [
            'real', 'actual', 'genuine', 'authentic',
            'behind the scenes', 'interview', 'documentary',
            'news', 'live', 'uncut', 'raw footage'
        ]
    
    def classify_by_title(self, title: str, description: str = "") -> Dict:
        """Intelligent title classification with high accuracy"""
        
        if not title:
            return {'is_ai_generated': False, 'confidence': 0.0}
        
        text = f"{title} {description}".lower()
        # Keep hashtags and @ symbols for better detection
        text = re.sub(r'[^\w\s#@]', ' ', text)
        
        # Direct keyword matching
        ai_score = 0.0
        authentic_score = 0.0
        detected_keywords = []
        
        for category, keywords in self.deepfake_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected_keywords.append(keyword)
                    weight = {'direct': 1.0, 'ai_tools': 0.9, 'technical': 0.7}
                    ai_score += weight.get(category, 0.5)
        
        for keyword in self.authentic_keywords:
            if keyword in text:
                authentic_score += 0.8
        
        # Pattern matching for variations
        patterns = [
            (r'\bai\s+generated?\b', 1.0),
            (r'\bdeep\s*fake\b', 1.0),
            (r'\b(veo|sora|midjourney|runway)\s*(v\d+|pro|demo)?\b', 0.9),
            (r'\bnot\s+real\b', 0.95),
            (r'\bfake\s+video\b', 0.95),
            (r'\bai\s+video\b', 0.8),  # Add specific pattern for "ai video"
            (r'\bai\s+art\b', 0.7),    # Add pattern for "ai art"
            (r'\b#ai\b', 0.6),         # Add pattern for hashtag #ai
            (r'\b#aiart\b', 0.8),      # Add pattern for hashtag #aiart
            (r'\b#edit\b', 0.3),       # Edit hashtag often indicates AI content
            (r'\b#aftereffects\b', 0.4), # After Effects often used with AI
            (r'\b#trending\b', 0.2)    # Trending often with AI content
        ]
        
        for pattern, weight in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                ai_score += weight
        
        # ✅ BIAS FIX: Complete bias removal - use raw evidence without artificial adjustments
        # Calculate raw evidence score without any artificial scaling or penalties
        final_score = ai_score  # Use raw AI evidence score without subtracting authentic score
        
        # ✅ BIAS FIX: Use balanced scaling for proper confidence range
        # Convert to 0-100% range based on actual evidence strength
        confidence = min(final_score * 60, 100.0)  # Balanced scaling for full confidence range
        
        # ✅ BIAS FIX: No artificial minimum confidence - use calculated value
        # Allow full range of confidence based on actual evidence strength
        
        # ✅ BIAS FIX: Balanced threshold for binary classification
        is_ai_generated = confidence >= 50  # Standard 50% threshold for binary classification
        
        return {
            'is_ai_generated': is_ai_generated,
            'confidence': confidence,
            'detected_keywords': detected_keywords[:5],
            'likely_ai_tool': self._identify_tool(detected_keywords)
        }
    
    def _identify_tool(self, keywords: List[str]) -> str:
        """Identify most likely AI tool from keywords"""
        tool_patterns = {
            'veo3': ['veo', 'google veo'],
            'sora': ['sora', 'openai'],
            'midjourney': ['midjourney', 'mj'],
            'runway': ['runway', 'gen-2', 'gen2'],
            'stable_diffusion': ['stable', 'sd']
        }
        
        for tool, patterns in tool_patterns.items():
            if any(pattern in ' '.join(keywords) for pattern in patterns):
                return tool
        
        return 'unknown'

intelligent_title_classifier = IntelligentTitleClassifier()
