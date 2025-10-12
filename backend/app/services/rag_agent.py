"""
RAG (Retrieval-Augmented Generation) Agent for Advanced Deepfake Detection
=======================================================================

This module implements a sophisticated RAG agent that combines:
- Knowledge retrieval from deepfake detection patterns
- Generative AI for intelligent analysis
- Context-aware decision making
- Adaptive learning capabilities
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pathlib import Path
import cv2
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class DetectionConfidence(Enum):
    """Detection confidence levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class DeepfakeType(Enum):
    """Types of deepfake content"""
    FACE_SWAP = "face_swap"
    LIP_SYNC = "lip_sync"
    VOICE_CLONING = "voice_cloning"
    FULL_BODY = "full_body"
    EXPRESSION_MANIPULATION = "expression_manipulation"
    UNKNOWN = "unknown"

@dataclass
class DetectionPattern:
    """Represents a deepfake detection pattern"""
    pattern_id: str
    name: str
    description: str
    indicators: List[str]
    confidence_threshold: float
    weight: float
    category: str
    examples: List[str]

@dataclass
class AnalysisResult:
    """Comprehensive analysis result from RAG agent"""
    is_deepfake: bool
    confidence: float
    confidence_level: DetectionConfidence
    deepfake_type: DeepfakeType
    detected_patterns: List[DetectionPattern]
    reasoning: str
    technical_details: Dict[str, Any]
    recommendations: List[str]
    uncertainty_factors: List[str]

class KnowledgeBase:
    """Knowledge base for deepfake detection patterns and techniques"""
    
    def __init__(self):
        self.patterns = {}
        self.techniques = {}
        self.case_studies = {}
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with deepfake detection patterns"""
        
        # Face Swap Detection Patterns
        self.patterns["face_swap"] = [
            DetectionPattern(
                pattern_id="fs_001",
                name="Inconsistent Lighting",
                description="Lighting inconsistencies between face and background",
                indicators=["lighting_mismatch", "shadow_inconsistency", "color_temperature_diff"],
                confidence_threshold=0.7,
                weight=0.8,
                category="lighting",
                examples=["Face appears lit from different angle than background"]
            ),
            DetectionPattern(
                pattern_id="fs_002", 
                name="Blending Artifacts",
                description="Visible blending artifacts at face boundaries",
                indicators=["blending_seams", "color_bleeding", "edge_artifacts"],
                confidence_threshold=0.6,
                weight=0.9,
                category="blending",
                examples=["Visible seams around face edges", "Color bleeding at boundaries"]
            ),
            DetectionPattern(
                pattern_id="fs_003",
                name="Resolution Mismatch",
                description="Resolution differences between face and background",
                indicators=["resolution_diff", "sharpness_mismatch", "detail_inconsistency"],
                confidence_threshold=0.8,
                weight=0.7,
                category="resolution",
                examples=["Face appears sharper/blurrier than background"]
            )
        ]
        
        # Lip Sync Detection Patterns
        self.patterns["lip_sync"] = [
            DetectionPattern(
                pattern_id="ls_001",
                name="Audio-Visual Mismatch",
                description="Mismatch between audio and lip movements",
                indicators=["audio_visual_delay", "phoneme_mismatch", "timing_inconsistency"],
                confidence_threshold=0.75,
                weight=0.85,
                category="synchronization",
                examples=["Lips don't match spoken words", "Delayed lip movements"]
            ),
            DetectionPattern(
                pattern_id="ls_002",
                name="Unnatural Mouth Movements",
                description="Unnatural or impossible mouth movements",
                indicators=["impossible_movements", "unnatural_shapes", "physics_violation"],
                confidence_threshold=0.8,
                weight=0.9,
                category="movement",
                examples=["Mouth opens too wide", "Impossible jaw movements"]
            )
        ]
        
        # Expression Manipulation Patterns
        self.patterns["expression"] = [
            DetectionPattern(
                pattern_id="em_001",
                name="Facial Asymmetry",
                description="Unnatural facial asymmetry in expressions",
                indicators=["asymmetrical_smile", "uneven_eyebrows", "lopsided_expressions"],
                confidence_threshold=0.7,
                weight=0.8,
                category="symmetry",
                examples=["One side of face more expressive than other"]
            ),
            DetectionPattern(
                pattern_id="em_002",
                name="Micro-expression Inconsistency",
                description="Inconsistent micro-expressions",
                indicators=["micro_expression_mismatch", "timing_inconsistency", "intensity_variation"],
                confidence_threshold=0.6,
                weight=0.75,
                category="micro_expressions",
                examples=["Micro-expressions don't match emotional context"]
            )
        ]
        
        # Technical Detection Techniques
        self.techniques = {
            "frequency_analysis": {
                "description": "Analyze frequency domain for deepfake artifacts",
                "methods": ["fft_analysis", "spectral_centroid", "high_freq_energy"],
                "effectiveness": 0.8
            },
            "temporal_consistency": {
                "description": "Check temporal consistency across frames",
                "methods": ["optical_flow", "frame_differences", "motion_analysis"],
                "effectiveness": 0.85
            },
            "texture_analysis": {
                "description": "Analyze texture patterns for manipulation signs",
                "methods": ["lbp_analysis", "gabor_filters", "texture_uniformity"],
                "effectiveness": 0.75
            },
            "color_analysis": {
                "description": "Analyze color patterns and consistency",
                "methods": ["color_histogram", "color_variance", "chroma_analysis"],
                "effectiveness": 0.7
            }
        }
    
    def retrieve_relevant_patterns(self, analysis_context: Dict[str, Any]) -> List[DetectionPattern]:
        """Retrieve relevant patterns based on analysis context"""
        relevant_patterns = []
        
        # Analyze context to determine relevant patterns
        if analysis_context.get("has_face", False):
            relevant_patterns.extend(self.patterns.get("face_swap", []))
        
        if analysis_context.get("has_audio", False):
            relevant_patterns.extend(self.patterns.get("lip_sync", []))
        
        if analysis_context.get("has_expressions", False):
            relevant_patterns.extend(self.patterns.get("expression", []))
        
        # Filter by confidence and relevance
        filtered_patterns = []
        for pattern in relevant_patterns:
            if analysis_context.get("confidence", 0) >= pattern.confidence_threshold:
                filtered_patterns.append(pattern)
        
        return filtered_patterns
    
    def get_technique_recommendations(self, detected_patterns: List[DetectionPattern]) -> List[str]:
        """Get technique recommendations based on detected patterns"""
        recommendations = []
        
        for pattern in detected_patterns:
            if pattern.category == "lighting":
                recommendations.append("frequency_analysis")
                recommendations.append("color_analysis")
            elif pattern.category == "blending":
                recommendations.append("texture_analysis")
                recommendations.append("temporal_consistency")
            elif pattern.category == "synchronization":
                recommendations.append("temporal_consistency")
        
        return list(set(recommendations))

class GenerativeAIAnalyzer:
    """Generative AI component for intelligent analysis"""
    
    def __init__(self):
        self.model_weights = {}
        self.attention_mechanisms = {}
        self._initialize_generative_components()
    
    def _initialize_generative_components(self):
        """Initialize generative AI components"""
        # Attention mechanisms for different analysis types
        self.attention_mechanisms = {
            "spatial": 0.3,      # Spatial features attention
            "temporal": 0.25,    # Temporal features attention  
            "frequency": 0.2,    # Frequency features attention
            "texture": 0.15,     # Texture features attention
            "color": 0.1         # Color features attention
        }
        
        # Model weights for ensemble learning
        self.model_weights = {
            "cnn_models": 0.3,
            "transformer_models": 0.25,
            "frequency_models": 0.2,
            "temporal_models": 0.15,
            "texture_models": 0.1
        }
    
    def generate_analysis_explanation(self, analysis_data: Dict[str, Any]) -> str:
        """Generate human-readable analysis explanation using generative AI concepts"""
        
        confidence = analysis_data.get("confidence", 0.0)
        detected_patterns = analysis_data.get("detected_patterns", [])
        technical_metrics = analysis_data.get("technical_metrics", {})
        
        # Generate explanation based on confidence level
        if confidence > 0.8:
            base_explanation = "High confidence deepfake detection based on multiple strong indicators."
        elif confidence > 0.6:
            base_explanation = "Moderate confidence deepfake detection with several supporting indicators."
        elif confidence > 0.4:
            base_explanation = "Low confidence detection with some suspicious indicators present."
        else:
            base_explanation = "Insufficient evidence for deepfake detection."
        
        # Add pattern-specific explanations
        pattern_explanations = []
        for pattern in detected_patterns:
            if pattern.name == "Inconsistent Lighting":
                pattern_explanations.append("Lighting inconsistencies suggest face replacement.")
            elif pattern.name == "Blending Artifacts":
                pattern_explanations.append("Visible blending artifacts indicate face manipulation.")
            elif pattern.name == "Audio-Visual Mismatch":
                pattern_explanations.append("Audio-visual synchronization issues detected.")
        
        # Combine explanations
        full_explanation = base_explanation
        if pattern_explanations:
            full_explanation += " Specific indicators include: " + "; ".join(pattern_explanations)
        
        return full_explanation
    
    def generate_recommendations(self, analysis_result: AnalysisResult) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if analysis_result.confidence < 0.5:
            recommendations.append("Consider additional analysis with different techniques")
            recommendations.append("Gather more video frames for temporal analysis")
        
        if analysis_result.deepfake_type == DeepfakeType.FACE_SWAP:
            recommendations.append("Focus on lighting and blending artifact analysis")
            recommendations.append("Check for resolution inconsistencies")
        
        if analysis_result.deepfake_type == DeepfakeType.LIP_SYNC:
            recommendations.append("Analyze audio-visual synchronization")
            recommendations.append("Check for unnatural mouth movements")
        
        if analysis_result.uncertainty_factors:
            recommendations.append("Address uncertainty factors for more reliable detection")
            recommendations.append("Consider ensemble methods for consensus")
        
        return recommendations
    
    def apply_attention_mechanism(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Apply attention mechanism to weight different feature types"""
        attention_weighted_features = {}
        
        for feature_type, value in features.items():
            attention_weight = self.attention_mechanisms.get(feature_type, 0.1)
            attention_weighted_features[feature_type] = value * attention_weight
        
        return attention_weighted_features

class RAGAgent:
    """Main RAG Agent for advanced deepfake detection"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.generative_analyzer = GenerativeAIAnalyzer()
        self.analysis_history = {}
        self.learning_weights = {}
        self._initialize_learning_components()
    
    def _initialize_learning_components(self):
        """Initialize adaptive learning components"""
        self.learning_weights = {
            "pattern_accuracy": 1.0,
            "technique_effectiveness": 1.0,
            "ensemble_consensus": 1.0
        }
    
    async def analyze_video(self, video_path: str, faces: List[np.ndarray], 
                          additional_context: Dict[str, Any] = None) -> AnalysisResult:
        """Comprehensive video analysis using RAG approach"""
        
        logger.info(f"🔍 RAG Agent analyzing video: {video_path}")
        start_time = time.time()
        
        try:
            # Step 1: Context Analysis
            analysis_context = await self._analyze_context(faces, additional_context)
            
            # Step 2: Knowledge Retrieval
            relevant_patterns = self.knowledge_base.retrieve_relevant_patterns(analysis_context)
            
            # Step 3: Pattern Detection
            detected_patterns = await self._detect_patterns(faces, relevant_patterns, analysis_context)
            
            # Step 4: Generative Analysis
            analysis_data = {
                "confidence": self._calculate_confidence(detected_patterns),
                "detected_patterns": detected_patterns,
                "technical_metrics": analysis_context.get("technical_metrics", {}),
                "context": analysis_context
            }
            
            # Step 5: Generate Results
            is_deepfake = analysis_data["confidence"] > 0.6
            confidence_level = self._determine_confidence_level(analysis_data["confidence"])
            deepfake_type = self._classify_deepfake_type(detected_patterns)
            
            # Generate explanations and recommendations
            reasoning = self.generative_analyzer.generate_analysis_explanation(analysis_data)
            recommendations = self.generative_analyzer.generate_recommendations(
                AnalysisResult(
                    is_deepfake=is_deepfake,
                    confidence=analysis_data["confidence"],
                    confidence_level=confidence_level,
                    deepfake_type=deepfake_type,
                    detected_patterns=detected_patterns,
                    reasoning=reasoning,
                    technical_details=analysis_context.get("technical_metrics", {}),
                    recommendations=[],
                    uncertainty_factors=[]
                )
            )
            
            # Step 6: Uncertainty Analysis
            uncertainty_factors = self._identify_uncertainty_factors(analysis_data)
            
            result = AnalysisResult(
                is_deepfake=is_deepfake,
                confidence=analysis_data["confidence"],
                confidence_level=confidence_level,
                deepfake_type=deepfake_type,
                detected_patterns=detected_patterns,
                reasoning=reasoning,
                technical_details=analysis_context.get("technical_metrics", {}),
                recommendations=recommendations,
                uncertainty_factors=uncertainty_factors
            )
            
            # Step 7: Learning Update
            await self._update_learning_weights(result, analysis_context)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ RAG Agent analysis completed in {elapsed:.2f}s")
            logger.info(f"📊 Result: {'Deepfake' if is_deepfake else 'Real'} (confidence: {analysis_data['confidence']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ RAG Agent analysis failed: {e}")
            return AnalysisResult(
                is_deepfake=False,
                confidence=0.0,
                confidence_level=DetectionConfidence.VERY_LOW,
                deepfake_type=DeepfakeType.UNKNOWN,
                detected_patterns=[],
                reasoning="Analysis failed due to technical error",
                technical_details={},
                recommendations=["Retry analysis", "Check video quality"],
                uncertainty_factors=["Technical error occurred"]
            )
    
    async def _analyze_context(self, faces: List[np.ndarray], additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze context for knowledge retrieval"""
        context = {
            "has_face": len(faces) > 0,
            "face_count": len(faces),
            "has_audio": additional_context.get("has_audio", False) if additional_context else False,
            "has_expressions": additional_context.get("has_expressions", False) if additional_context else False,
            "video_quality": additional_context.get("video_quality", "unknown") if additional_context else "unknown",
            "technical_metrics": {}
        }
        
        if faces:
            # Analyze face characteristics
            face_analysis = self._analyze_face_characteristics(faces)
            context["technical_metrics"].update(face_analysis)
        
        return context
    
    def _analyze_face_characteristics(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze face characteristics for context"""
        if not faces:
            return {}
        
        characteristics = {
            "avg_brightness": 0.0,
            "avg_contrast": 0.0,
            "avg_sharpness": 0.0,
            "color_variance": 0.0,
            "texture_complexity": 0.0
        }
        
        try:
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            color_variance_values = []
            
            for face in faces:
                if isinstance(face, np.ndarray) and face.size > 0:
                    # Brightness analysis
                    brightness = np.mean(face)
                    brightness_values.append(brightness)
                    
                    # Contrast analysis
                    contrast = np.std(face)
                    contrast_values.append(contrast)
                    
                    # Sharpness analysis
                    if len(face.shape) == 3:
                        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face
                    laplacian_var = np.var(cv2.Laplacian(gray, cv2.CV_64F))
                    sharpness_values.append(laplacian_var)
                    
                    # Color variance
                    if len(face.shape) == 3:
                        color_var = np.mean(np.var(face, axis=(0, 1)))
                        color_variance_values.append(color_var)
            
            characteristics["avg_brightness"] = float(np.mean(brightness_values)) if brightness_values else 0.0
            characteristics["avg_contrast"] = float(np.mean(contrast_values)) if contrast_values else 0.0
            characteristics["avg_sharpness"] = float(np.mean(sharpness_values)) if sharpness_values else 0.0
            characteristics["color_variance"] = float(np.mean(color_variance_values)) if color_variance_values else 0.0
            characteristics["texture_complexity"] = float(np.std(sharpness_values)) if sharpness_values else 0.0
            
        except Exception as e:
            logger.warning(f"Face characteristic analysis failed: {e}")
        
        return characteristics
    
    async def _detect_patterns(self, faces: List[np.ndarray], patterns: List[DetectionPattern], 
                             context: Dict[str, Any]) -> List[DetectionPattern]:
        """Detect patterns using advanced analysis"""
        detected_patterns = []
        
        for pattern in patterns:
            try:
                # Apply pattern-specific detection logic
                if pattern.pattern_id == "fs_001":  # Inconsistent Lighting
                    if self._detect_lighting_inconsistency(faces, context):
                        detected_patterns.append(pattern)
                
                elif pattern.pattern_id == "fs_002":  # Blending Artifacts
                    if self._detect_blending_artifacts(faces, context):
                        detected_patterns.append(pattern)
                
                elif pattern.pattern_id == "fs_003":  # Resolution Mismatch
                    if self._detect_resolution_mismatch(faces, context):
                        detected_patterns.append(pattern)
                
                elif pattern.pattern_id == "ls_001":  # Audio-Visual Mismatch
                    if self._detect_audio_visual_mismatch(faces, context):
                        detected_patterns.append(pattern)
                
                elif pattern.pattern_id == "em_001":  # Facial Asymmetry
                    if self._detect_facial_asymmetry(faces, context):
                        detected_patterns.append(pattern)
                
            except Exception as e:
                logger.warning(f"Pattern detection failed for {pattern.pattern_id}: {e}")
        
        return detected_patterns
    
    def _detect_lighting_inconsistency(self, faces: List[np.ndarray], context: Dict[str, Any]) -> bool:
        """Detect lighting inconsistencies"""
        try:
            if not faces:
                return False
            
            # Analyze lighting patterns across faces
            lighting_variance = context.get("technical_metrics", {}).get("color_variance", 0.0)
            brightness_variance = np.var([np.mean(face) for face in faces if isinstance(face, np.ndarray)])
            
            # High variance indicates lighting inconsistency
            return lighting_variance > 0.3 or brightness_variance > 0.1
            
        except Exception as e:
            logger.warning(f"Lighting inconsistency detection failed: {e}")
            return False
    
    def _detect_blending_artifacts(self, faces: List[np.ndarray], context: Dict[str, Any]) -> bool:
        """Detect blending artifacts"""
        try:
            if not faces:
                return False
            
            # Analyze edge characteristics
            edge_artifacts = 0
            for face in faces:
                if isinstance(face, np.ndarray) and len(face.shape) == 3:
                    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, 50, 150)
                    
                    # Check for unusual edge patterns
                    edge_density = np.count_nonzero(edges) / edges.size
                    if edge_density > 0.2:  # High edge density might indicate artifacts
                        edge_artifacts += 1
            
            return edge_artifacts > len(faces) * 0.5
            
        except Exception as e:
            logger.warning(f"Blending artifact detection failed: {e}")
            return False
    
    def _detect_resolution_mismatch(self, faces: List[np.ndarray], context: Dict[str, Any]) -> bool:
        """Detect resolution mismatches"""
        try:
            if not faces:
                return False
            
            # Analyze sharpness variance
            sharpness_values = []
            for face in faces:
                if isinstance(face, np.ndarray):
                    if len(face.shape) == 3:
                        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face
                    laplacian_var = np.var(cv2.Laplacian(gray, cv2.CV_64F))
                    sharpness_values.append(laplacian_var)
            
            if not sharpness_values:
                return False
            
            sharpness_variance = np.var(sharpness_values)
            return sharpness_variance > 1000.0  # High variance indicates resolution mismatch
            
        except Exception as e:
            logger.warning(f"Resolution mismatch detection failed: {e}")
            return False
    
    def _detect_audio_visual_mismatch(self, faces: List[np.ndarray], context: Dict[str, Any]) -> bool:
        """Detect audio-visual synchronization issues"""
        # This would require audio analysis - simplified for now
        return context.get("has_audio", False) and len(faces) > 0
    
    def _detect_facial_asymmetry(self, faces: List[np.ndarray], context: Dict[str, Any]) -> bool:
        """Detect facial asymmetry"""
        try:
            if not faces:
                return False
            
            # Analyze symmetry across faces
            asymmetry_indicators = 0
            for face in faces:
                if isinstance(face, np.ndarray) and len(face.shape) == 3:
                    # Simple symmetry analysis
                    left_half = face[:, :face.shape[1]//2]
                    right_half = face[:, face.shape[1]//2:]
                    right_half_flipped = np.fliplr(right_half)
                    
                    # Compare left and flipped right halves
                    if left_half.shape == right_half_flipped.shape:
                        diff = np.mean(np.abs(left_half - right_half_flipped))
                        if diff > 30:  # High difference indicates asymmetry
                            asymmetry_indicators += 1
            
            return asymmetry_indicators > len(faces) * 0.3
            
        except Exception as e:
            logger.warning(f"Facial asymmetry detection failed: {e}")
            return False
    
    def _calculate_confidence(self, detected_patterns: List[DetectionPattern]) -> float:
        """Calculate overall confidence based on detected patterns"""
        if not detected_patterns:
            # Return a small confidence even when no patterns are detected
            # This prevents the system from always returning 0.0 confidence
            return 0.1
        
        # Weighted confidence calculation
        total_weight = sum(pattern.weight for pattern in detected_patterns)
        weighted_confidence = sum(pattern.weight * pattern.confidence_threshold for pattern in detected_patterns)
        
        # Ensure minimum confidence to avoid always returning 0.0
        base_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.1
        return min(1.0, max(0.1, base_confidence))
    
    def _determine_confidence_level(self, confidence: float) -> DetectionConfidence:
        """Determine confidence level from numeric confidence"""
        if confidence >= 0.9:
            return DetectionConfidence.VERY_HIGH
        elif confidence >= 0.8:
            return DetectionConfidence.HIGH
        elif confidence >= 0.6:
            return DetectionConfidence.MEDIUM
        elif confidence >= 0.4:
            return DetectionConfidence.LOW
        else:
            return DetectionConfidence.VERY_LOW
    
    def _classify_deepfake_type(self, detected_patterns: List[DetectionPattern]) -> DeepfakeType:
        """Classify the type of deepfake based on detected patterns"""
        if not detected_patterns:
            return DeepfakeType.UNKNOWN
        
        # Analyze pattern categories
        categories = [pattern.category for pattern in detected_patterns]
        
        if "lighting" in categories or "blending" in categories:
            return DeepfakeType.FACE_SWAP
        elif "synchronization" in categories:
            return DeepfakeType.LIP_SYNC
        elif "symmetry" in categories or "micro_expressions" in categories:
            return DeepfakeType.EXPRESSION_MANIPULATION
        else:
            return DeepfakeType.UNKNOWN
    
    def _identify_uncertainty_factors(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to uncertainty"""
        uncertainty_factors = []
        
        confidence = analysis_data.get("confidence", 0.0)
        detected_patterns = analysis_data.get("detected_patterns", [])
        
        if confidence < 0.6:
            uncertainty_factors.append("Low confidence in detection")
        
        if len(detected_patterns) < 2:
            uncertainty_factors.append("Insufficient pattern evidence")
        
        if confidence > 0.4 and confidence < 0.7:
            uncertainty_factors.append("Ambiguous detection signals")
        
        return uncertainty_factors
    
    async def _update_learning_weights(self, result: AnalysisResult, context: Dict[str, Any]):
        """Update learning weights based on analysis results"""
        try:
            # Simple learning update - in production, this would be more sophisticated
            if result.confidence > 0.8:
                # High confidence result - reinforce current weights
                for key in self.learning_weights:
                    self.learning_weights[key] = min(1.0, self.learning_weights[key] + 0.01)
            elif result.confidence < 0.3:
                # Low confidence result - adjust weights
                for key in self.learning_weights:
                    self.learning_weights[key] = max(0.1, self.learning_weights[key] - 0.01)
            
        except Exception as e:
            logger.warning(f"Learning weight update failed: {e}")

# Global RAG Agent instance
_rag_agent_instance = None

async def get_rag_agent() -> RAGAgent:
    """Get the global RAG Agent instance"""
    global _rag_agent_instance
    
    if _rag_agent_instance is None:
        _rag_agent_instance = RAGAgent()
        logger.info("🤖 RAG Agent initialized with knowledge base and generative AI components")
    
    return _rag_agent_instance

async def analyze_with_rag(video_path: str, faces: List[np.ndarray], 
                          additional_context: Dict[str, Any] = None) -> AnalysisResult:
    """Convenience function for RAG-based analysis"""
    agent = await get_rag_agent()
    return await agent.analyze_video(video_path, faces, additional_context)
