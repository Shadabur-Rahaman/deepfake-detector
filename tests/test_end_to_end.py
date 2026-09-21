"""
Integration Tests for End-to-End Detection Modes
===============================================

Tests the complete detection pipeline across all modes to ensure
proper differentiation and functionality.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.mvp_detection_modes_2025 import (
    MVPAggressiveDetector2025,
    MVPHybridDetector2025,
    MVPConservativeDetector2025,
    DetectionMode,
    TitleAnalysisResult,
    AIToolType
)

class TestEndToEndDetection:
    """Test end-to-end detection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.aggressive_detector = MVPAggressiveDetector2025()
        self.hybrid_detector = MVPHybridDetector2025()
        self.conservative_detector = MVPConservativeDetector2025()
        
        # Mock face data
        self.mock_faces = [np.random.rand(224, 224, 3) for _ in range(3)]
    
    @pytest.mark.asyncio
    async def test_mode_differentiation_borderline_case(self):
        """Test that different modes produce different results for borderline cases"""
        # Create a borderline confidence that should trigger different classifications
        borderline_confidence = 0.52  # Between aggressive (45%) and conservative (55%)
        
        # Mock ensemble results
        mock_ensemble_result = Mock()
        mock_ensemble_result.prediction = "AI-Generated Content Detected"
        mock_ensemble_result.confidence = borderline_confidence
        mock_ensemble_result.model_agreement = 0.8
        mock_ensemble_result.ensemble_variance = 0.1
        
        # Mock detection scores
        detection_scores = [('test_model', borderline_confidence, 1.0)]
        
        # Mock title analysis
        mock_title_analysis = TitleAnalysisResult(
            is_ai_generated=False,
            confidence=30.0,
            detected_keywords=[],
            likely_ai_tool=AIToolType.UNKNOWN,
            title_boost=0.0,
            analysis_method="test"
        )
        
        # Test all three modes
        aggressive_result = self.aggressive_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        hybrid_result = self.hybrid_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        conservative_result = self.conservative_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        # Verify mode differentiation
        assert aggressive_result.prediction == "AI-Generated Content Detected"  # 52% > 45%
        assert hybrid_result.prediction == "AI-Generated Content Detected"      # 52% > 50%
        assert conservative_result.prediction == "Authentic Video"              # 52% < 55%
        
        # Verify modes are actually different
        assert aggressive_result.prediction != conservative_result.prediction
    
    @pytest.mark.asyncio
    async def test_metadata_weighting_hybrid_mode(self):
        """Test that hybrid mode uses metadata weighting"""
        # Create title analysis indicating AI content
        ai_title_analysis = TitleAnalysisResult(
            is_ai_generated=True,
            confidence=85.0,
            detected_keywords=['SORA', 'AI generated'],
            likely_ai_tool=AIToolType.SORA,
            title_boost=0.3,
            analysis_method="test"
        )
        
        # Mock ensemble with low confidence (should be overridden by metadata)
        mock_ensemble_result = Mock()
        mock_ensemble_result.prediction = "Authentic Video"
        mock_ensemble_result.confidence = 0.3  # Low confidence
        mock_ensemble_result.model_agreement = 0.6
        mock_ensemble_result.ensemble_variance = 0.2
        
        # Mock detection scores with low confidence
        detection_scores = [('test_model', 0.3, 1.0)]
        
        # Test hybrid mode with metadata weighting
        hybrid_result = self.hybrid_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        # Verify metadata weighting is applied
        assert hybrid_result.title_analysis is not None
        assert hybrid_result.title_analysis.is_ai_generated == True
        assert hybrid_result.ai_tool_detected == AIToolType.SORA
        
        # With strong metadata signal, hybrid should detect as AI-generated
        # even with low visual confidence (due to 30% metadata weight)
        assert hybrid_result.prediction == "AI-Generated Content Detected"
    
    @pytest.mark.asyncio
    async def test_aggressive_mode_features(self):
        """Test that aggressive mode has enhanced features enabled"""
        # Verify aggressive mode configuration
        assert self.aggressive_detector.enable_frequency_analysis == True
        assert self.aggressive_detector.enable_texture_analysis == True
        assert self.aggressive_detector.early_exit_threshold == 0.75
        assert self.aggressive_detector.bias_multiplier == 1.2
        
        # Test early exit functionality
        high_confidence = 0.80  # Above early exit threshold
        
        mock_ensemble_result = Mock()
        mock_ensemble_result.prediction = "AI-Generated Content Detected"
        mock_ensemble_result.confidence = high_confidence
        mock_ensemble_result.model_agreement = 0.9
        mock_ensemble_result.ensemble_variance = 0.05
        
        detection_scores = [('test_model', high_confidence, 1.0)]
        
        aggressive_result = self.aggressive_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        # Should detect as AI-generated due to high confidence
        assert aggressive_result.prediction == "AI-Generated Content Detected"
        assert aggressive_result.confidence > 80.0  # High confidence
    
    @pytest.mark.asyncio
    async def test_temporal_consistency_hybrid_mode(self):
        """Test that hybrid mode includes temporal consistency analysis"""
        # Verify hybrid mode has temporal analyzer
        assert hasattr(self.hybrid_detector, 'temporal_analyzer')
        assert self.hybrid_detector.temporal_analyzer is not None
        
        # Test temporal consistency analysis
        frame_predictions = [
            (np.random.rand(224, 224, 3), 0.4),
            (np.random.rand(224, 224, 3), 0.42),
            (np.random.rand(224, 224, 3), 0.38),
            (np.random.rand(224, 224, 3), 0.41),
            (np.random.rand(224, 224, 3), 0.39)
        ]
        
        temporal_metrics = await self.hybrid_detector.temporal_analyzer.analyze_temporal_consistency(
            frame_predictions, frame_interval=1
        )
        
        # Verify temporal metrics structure
        required_fields = ['consistency_score', 'variance', 'stability', 'temporal_drift', 'num_frames']
        for field in required_fields:
            assert field in temporal_metrics, f"Missing field {field} in temporal metrics"
        
        # Should have good consistency for similar predictions
        assert temporal_metrics['consistency_score'] > 0.5, "Should have good temporal consistency"
        assert temporal_metrics['variance'] < 0.1, "Should have low variance"
        assert temporal_metrics['stability'] > 0.8, "Should have high stability"
    
    @pytest.mark.asyncio
    async def test_ground_truth_weighting_adjustment(self):
        """Test that ground truth validation uses 20%/80% weighting"""
        # Mock ground truth validation result
        mock_validation_result = Mock()
        mock_validation_result.is_authentic = True
        mock_validation_result.confidence = 0.9  # High confidence authentic
        mock_validation_result.reasoning = "Clear authentic content"
        
        # Mock ensemble result (says fake)
        mock_ensemble_result = Mock()
        mock_ensemble_result.prediction = "AI-Generated Content Detected"
        mock_ensemble_result.confidence = 0.7  # High confidence fake
        mock_ensemble_result.model_agreement = 0.8
        mock_ensemble_result.ensemble_variance = 0.1
        
        detection_scores = [('test_model', 0.7, 1.0)]
        
        # Test aggressive mode with ground truth conflict
        aggressive_result = self.aggressive_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=mock_validation_result,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        # Verify ground truth validation is included
        assert aggressive_result.ground_truth_validation is not None
        
        # With 20% GT weight vs 80% model weight, model should dominate
        # but GT should have some influence
        assert aggressive_result.prediction == "AI-Generated Content Detected"  # Model dominates
    
    def test_detection_mode_enum_values(self):
        """Test that detection mode enums have correct values"""
        assert DetectionMode.AGGRESSIVE_2025.value == "aggressive_2025"
        assert DetectionMode.HYBRID_2025.value == "hybrid_2025"
        assert DetectionMode.CONSERVATIVE_2025.value == "conservative_2025"
    
    def test_result_structure_completeness(self):
        """Test that detection results have complete structure"""
        mock_ensemble_result = Mock()
        mock_ensemble_result.prediction = "AI-Generated Content Detected"
        mock_ensemble_result.confidence = 0.6
        mock_ensemble_result.model_agreement = 0.8
        mock_ensemble_result.ensemble_variance = 0.1
        
        detection_scores = [('test_model', 0.6, 1.0)]
        
        result = self.aggressive_detector._finalize_decision(
            ensemble_result=mock_ensemble_result,
            validation_result=None,
            detection_scores=detection_scores,
            processing_time=1.0,
            faces_detected=3
        )
        
        # Verify all required fields are present
        required_fields = [
            'prediction', 'confidence', 'confidence_level', 'status_emoji',
            'detection_mode', 'model_agreement', 'ensemble_variance',
            'face_quality_score', 'temporal_consistency', 'ai_tool_detected',
            'title_analysis', 'processing_time', 'faces_detected',
            'interpretable_output', 'detailed_breakdown', 'ensemble_scores'
        ]
        
        for field in required_fields:
            assert hasattr(result, field), f"Missing field {field} in detection result"
            assert getattr(result, field) is not None, f"Field {field} should not be None"

if __name__ == "__main__":
    pytest.main([__file__])
