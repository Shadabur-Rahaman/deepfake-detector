#!/usr/bin/env python3
"""
Model Output Verifier - Test and calibrate trained model outputs
Determines correct interpretation of model outputs and optimal thresholds
"""

import os
import logging
import numpy as np
import torch
import cv2
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class ModelCalibrationResult:
    """Result from model calibration"""
    model_path: str
    output_interpretation: str  # "high_values_real" or "high_values_fake"
    optimal_threshold: float
    confidence_interval: Tuple[float, float]
    test_samples_used: int
    calibration_accuracy: float
    raw_outputs: Dict[str, List[float]]
    calibration_timestamp: float

class ModelOutputVerifier:
    """
    Verifies and calibrates trained model outputs to determine correct interpretation
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.calibration_cache = {}
        self.calibration_dir = "logs/model_calibration"
        os.makedirs(self.calibration_dir, exist_ok=True)
        
        logger.info(f"🔍 ModelOutputVerifier initialized on device: {self.device}")
    
    def create_test_samples(self) -> Dict[str, List[np.ndarray]]:
        """
        Create synthetic test samples to verify model output interpretation
        Returns samples with known ground truth labels
        """
        test_samples = {
            'real_samples': [],
            'fake_samples': []
        }
        
        # Create synthetic real-like samples (natural looking faces)
        for i in range(10):
            # Generate natural-looking face-like patterns
            face = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
            
            # Add some structure to make it more face-like
            # Add eye-like regions
            face[80:100, 60:90] = [100, 120, 140]  # Left eye
            face[80:100, 134:164] = [100, 120, 140]  # Right eye
            
            # Add nose-like region
            face[120:160, 100:124] = [120, 140, 160]  # Nose
            
            # Add mouth-like region
            face[180:200, 90:134] = [80, 100, 120]  # Mouth
            
            # Add some natural variation
            noise = np.random.normal(0, 10, face.shape).astype(np.int16)
            face = np.clip(face.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            test_samples['real_samples'].append(face)
        
        # Create synthetic fake-like samples (artificial patterns)
        for i in range(10):
            # Generate more artificial-looking patterns
            face = np.random.randint(100, 255, (224, 224, 3), dtype=np.uint8)
            
            # Add very regular, artificial patterns
            # Perfectly symmetric eyes
            face[80:100, 60:90] = [200, 220, 240]  # Left eye
            face[80:100, 134:164] = [200, 220, 240]  # Right eye (perfectly symmetric)
            
            # Very regular nose
            face[120:160, 100:124] = [220, 240, 255]  # Nose
            
            # Perfectly straight mouth
            face[180:200, 90:134] = [180, 200, 220]  # Mouth
            
            # Add artificial sharp edges and high contrast
            face = cv2.GaussianBlur(face, (3, 3), 0)  # Slight blur to make it less artificial
            face = np.clip(face * 1.2, 0, 255).astype(np.uint8)  # Increase contrast
            
            test_samples['fake_samples'].append(face)
        
        logger.info(f"✅ Created {len(test_samples['real_samples'])} real and {len(test_samples['fake_samples'])} fake test samples")
        return test_samples
    
    def calibrate_from_videos(self, real_video_path: str, fake_video_path: str) -> Optional[ModelCalibration]:
        """
        Calibrate model using actual extracted faces from known real and fake videos.
        This is much more accurate than synthetic samples.
        """
        try:
            if not os.path.exists(real_video_path):
                logger.error(f"Real video not found: {real_video_path}")
                return None
            if not os.path.exists(fake_video_path):
                logger.error(f"Fake video not found: {fake_video_path}")
                return None
            
            logger.info(f"🎯 Starting real video calibration...")
            logger.info(f"   Real video: {os.path.basename(real_video_path)}")
            logger.info(f"   Fake video: {os.path.basename(fake_video_path)}")
            
            # Extract faces from both videos
            from ..video_processor import extract_faces_from_video_sync
            
            # Extract faces from real video
            real_faces, _ = extract_faces_from_video_sync(real_video_path, frames_to_process=15, frame_interval=3)
            fake_faces, _ = extract_faces_from_video_sync(fake_video_path, frames_to_process=15, frame_interval=3)
            
            if not real_faces or not fake_faces:
                logger.error("Failed to extract faces from calibration videos")
                return None
            
            logger.info(f"✅ Extracted {len(real_faces)} real faces and {len(fake_faces)} fake faces")
            
            # Load model for testing
            model = self._load_model_for_calibration()
            if not model:
                return None
            
            # Test real faces
            real_outputs = []
            for face_data in real_faces[:10]:  # Use first 10 faces
                face = face_data['face'] if isinstance(face_data, dict) else face_data
                output = self._test_single_face(model, face)
                if output is not None:
                    real_outputs.append(output)
            
            # Test fake faces
            fake_outputs = []
            for face_data in fake_faces[:10]:  # Use first 10 faces
                face = face_data['face'] if isinstance(face_data, dict) else face_data
                output = self._test_single_face(model, face)
                if output is not None:
                    fake_outputs.append(output)
            
            if not real_outputs or not fake_outputs:
                logger.error("Failed to get model outputs from calibration faces")
                return None
            
            # Analyze distributions
            real_mean = np.mean(real_outputs)
            real_std = np.std(real_outputs)
            fake_mean = np.mean(fake_outputs)
            fake_std = np.std(fake_outputs)
            
            logger.info(f"📊 Real faces - Mean: {real_mean:.3f}, Std: {real_std:.3f}")
            logger.info(f"📊 Fake faces - Mean: {fake_mean:.3f}, Std: {fake_std:.3f}")
            
            # Check if distributions are well separated
            separation = abs(fake_mean - real_mean)
            if separation < 0.1:
                logger.warning(f"⚠️ Poor separation between real/fake distributions: {separation:.3f}")
                logger.warning("   Model may not be well-calibrated for this data")
            
            # Determine interpretation and optimal threshold
            if fake_mean > real_mean + 0.05:  # Clear separation favoring fake > real
                interpretation = "high_values_fake"
                optimal_threshold = (real_mean + fake_mean) / 2
                logger.info(f"🎯 INTERPRETATION: High values = Fake faces, Low values = Real faces")
            elif real_mean > fake_mean + 0.05:  # Clear separation favoring real > fake
                interpretation = "high_values_real"
                optimal_threshold = (real_mean + fake_mean) / 2
                logger.info(f"🎯 INTERPRETATION: High values = Real faces, Low values = Fake faces")
            else:
                # Ambiguous - use default
                interpretation = "high_values_fake"
                optimal_threshold = 0.5
                logger.warning(f"⚠️ Ambiguous model behavior, using default interpretation")
            
            # Calculate calibration accuracy
            correct_predictions = 0
            total_predictions = len(real_outputs) + len(fake_outputs)
            
            for output in real_outputs:
                if interpretation == "high_values_real":
                    if output >= optimal_threshold:
                        correct_predictions += 1
                else:
                    if output < optimal_threshold:
                        correct_predictions += 1
            
            for output in fake_outputs:
                if interpretation == "high_values_fake":
                    if output >= optimal_threshold:
                        correct_predictions += 1
                else:
                    if output < optimal_threshold:
                        correct_predictions += 1
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
            
            logger.info(f"🎯 CALIBRATION RESULT:")
            logger.info(f"   Interpretation: {interpretation}")
            logger.info(f"   Optimal threshold: {optimal_threshold:.3f}")
            logger.info(f"   Calibration accuracy: {accuracy:.3f}")
            logger.info(f"   Separation: {separation:.3f}")
            
            return ModelCalibration(
                output_interpretation=interpretation,
                optimal_threshold=optimal_threshold,
                accuracy=accuracy,
                precision=accuracy,  # Simplified for now
                recall=accuracy,     # Simplified for now
                f1_score=accuracy   # Simplified for now
            )
            
        except Exception as e:
            logger.error(f"Real video calibration failed: {e}")
            return None
    
    def _test_single_face(self, model, face: np.ndarray) -> Optional[float]:
        """Test a single face through the model and return output"""
        try:
            # Convert face to tensor
            if isinstance(face, torch.Tensor):
                face_tensor = face.unsqueeze(0) if face.dim() == 3 else face
            else:
                # Convert numpy to tensor
                import cv2
                face_resized = cv2.resize(face, (224, 224))
                face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                face_tensor = torch.from_numpy(face_rgb).float() / 255.0
                face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0)
            
            face_tensor = face_tensor.to(self.device)
            
            with torch.no_grad():
                output = model(face_tensor)
                probability = torch.sigmoid(output).item()
                return probability
                
        except Exception as e:
            logger.debug(f"Failed to test single face: {e}")
            return None
    
    def load_trained_model(self, model_path: str) -> Optional[torch.nn.Module]:
        """Load the trained model for testing"""
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model not found at: {model_path}")
                return None
            
            # Load your trained EfficientNet model
            from torchvision import models
            import torch.nn as nn
            
            model = models.efficientnet_b0(weights=None)
            num_ftrs = model.classifier[1].in_features
            model.classifier = nn.Sequential(nn.Dropout(p=0.2, inplace=True), nn.Linear(num_ftrs, 1))
            
            # Load trained weights
            state_dict = torch.load(model_path, map_location=self.device)
            if any(key.startswith('module.') for key in state_dict.keys()):
                state_dict = {key.replace('module.', ''): value for key, value in state_dict.items()}
            
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            
            logger.info(f"✅ Trained model loaded from: {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load trained model: {e}")
            return None
    
    def _load_model_for_calibration(self) -> Optional[torch.nn.Module]:
        """Load model for calibration using the same path as the main detector"""
        try:
            # Use the same model path as the main detector
            model_path = os.path.join(os.path.dirname(__file__), '../../../ml_artifacts/deepfake_detector_finetuned1.pth')
            return self.load_trained_model(model_path)
        except Exception as e:
            logger.error(f"Failed to load model for calibration: {e}")
            return None
    
    def test_model_outputs(self, model: torch.nn.Module, test_samples: Dict[str, List[np.ndarray]]) -> Dict[str, Any]:
        """
        Test model outputs on known samples to determine interpretation
        """
        logger.info("🧪 Testing model outputs on known samples...")
        
        results = {
            'real_outputs': [],
            'fake_outputs': [],
            'raw_predictions': []
        }
        
        with torch.no_grad():
            # Test real samples
            for i, face in enumerate(test_samples['real_samples']):
                try:
                    # Convert to tensor
                    face_resized = cv2.resize(face, (224, 224))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    face_tensor = torch.from_numpy(face_rgb).float() / 255.0
                    face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
                    
                    # Get model output
                    output = model(face_tensor)
                    prob = torch.sigmoid(output).cpu().item()
                    
                    results['real_outputs'].append(prob)
                    results['raw_predictions'].append({
                        'sample_type': 'real',
                        'sample_index': i,
                        'raw_output': output.cpu().item(),
                        'sigmoid_prob': prob
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing real sample {i}: {e}")
            
            # Test fake samples
            for i, face in enumerate(test_samples['fake_samples']):
                try:
                    # Convert to tensor
                    face_resized = cv2.resize(face, (224, 224))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    face_tensor = torch.from_numpy(face_rgb).float() / 255.0
                    face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
                    
                    # Get model output
                    output = model(face_tensor)
                    prob = torch.sigmoid(output).cpu().item()
                    
                    results['fake_outputs'].append(prob)
                    results['raw_predictions'].append({
                        'sample_type': 'fake',
                        'sample_index': i,
                        'raw_output': output.cpu().item(),
                        'sigmoid_prob': prob
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing fake sample {i}: {e}")
        
        logger.info(f"✅ Tested {len(results['real_outputs'])} real and {len(results['fake_outputs'])} fake samples")
        return results
    
    def analyze_output_patterns(self, test_results: Dict[str, Any]) -> ModelCalibrationResult:
        """
        Analyze test results to determine correct output interpretation
        """
        real_outputs = test_results['real_outputs']
        fake_outputs = test_results['fake_outputs']
        
        if not real_outputs or not fake_outputs:
            logger.error("Insufficient test data for analysis")
            return None
        
        # Calculate statistics
        real_mean = np.mean(real_outputs)
        fake_mean = np.mean(fake_outputs)
        real_std = np.std(real_outputs)
        fake_std = np.std(fake_outputs)
        
        logger.info(f"📊 Real samples - Mean: {real_mean:.3f}, Std: {real_std:.3f}")
        logger.info(f"📊 Fake samples - Mean: {fake_mean:.3f}, Std: {fake_std:.3f}")
        
        # Determine interpretation based on which group has higher values
        if real_mean > fake_mean:
            interpretation = "high_values_real"
            logger.info("🎯 INTERPRETATION: High values = Real faces, Low values = Fake faces")
        else:
            interpretation = "high_values_fake"
            logger.info("🎯 INTERPRETATION: High values = Fake faces, Low values = Real faces")
        
        # Calculate optimal threshold
        # Use the midpoint between the two distributions
        optimal_threshold = (real_mean + fake_mean) / 2.0
        
        # Calculate confidence interval (95% of samples within 2 std devs)
        real_ci = (real_mean - 2*real_std, real_mean + 2*real_std)
        fake_ci = (fake_mean - 2*fake_std, fake_mean + 2*fake_std)
        
        # Calculate calibration accuracy
        correct_predictions = 0
        total_predictions = len(real_outputs) + len(fake_outputs)
        
        for prob in real_outputs:
            if interpretation == "high_values_real":
                if prob >= optimal_threshold:
                    correct_predictions += 1
            else:
                if prob < optimal_threshold:
                    correct_predictions += 1
        
        for prob in fake_outputs:
            if interpretation == "high_values_fake":
                if prob >= optimal_threshold:
                    correct_predictions += 1
            else:
                if prob < optimal_threshold:
                    correct_predictions += 1
        
        calibration_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        result = ModelCalibrationResult(
            model_path="deepfake_detector_finetuned1.pth",
            output_interpretation=interpretation,
            optimal_threshold=optimal_threshold,
            confidence_interval=(min(real_ci[0], fake_ci[0]), max(real_ci[1], fake_ci[1])),
            test_samples_used=total_predictions,
            calibration_accuracy=calibration_accuracy,
            raw_outputs=test_results,
            calibration_timestamp=time.time()
        )
        
        logger.info(f"🎯 CALIBRATION RESULT:")
        logger.info(f"   Interpretation: {interpretation}")
        logger.info(f"   Optimal threshold: {optimal_threshold:.3f}")
        logger.info(f"   Calibration accuracy: {calibration_accuracy:.3f}")
        logger.info(f"   Confidence interval: {result.confidence_interval}")
        
        return result
    
    def save_calibration_result(self, result: ModelCalibrationResult, model_path: str):
        """Save calibration result to file"""
        try:
            # Create filename based on model path
            model_name = os.path.basename(model_path).replace('.pth', '')
            timestamp = int(result.calibration_timestamp)
            filename = f"{model_name}_calibration_{timestamp}.json"
            filepath = os.path.join(self.calibration_dir, filename)
            
            # Convert to serializable format
            data = {
                'model_path': result.model_path,
                'output_interpretation': result.output_interpretation,
                'optimal_threshold': result.optimal_threshold,
                'confidence_interval': result.confidence_interval,
                'test_samples_used': result.test_samples_used,
                'calibration_accuracy': result.calibration_accuracy,
                'calibration_timestamp': result.calibration_timestamp,
                'raw_outputs': result.raw_outputs
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Calibration result saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save calibration result: {e}")
    
    def load_calibration_result(self, model_path: str) -> Optional[ModelCalibrationResult]:
        """Load existing calibration result if available"""
        try:
            model_name = os.path.basename(model_path).replace('.pth', '')
            
            # Look for existing calibration files
            if os.path.exists(self.calibration_dir):
                for filename in os.listdir(self.calibration_dir):
                    if filename.startswith(f"{model_name}_calibration_") and filename.endswith('.json'):
                        filepath = os.path.join(self.calibration_dir, filename)
                        
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        
                        result = ModelCalibrationResult(
                            model_path=data['model_path'],
                            output_interpretation=data['output_interpretation'],
                            optimal_threshold=data['optimal_threshold'],
                            confidence_interval=tuple(data['confidence_interval']),
                            test_samples_used=data['test_samples_used'],
                            calibration_accuracy=data['calibration_accuracy'],
                            raw_outputs=data['raw_outputs'],
                            calibration_timestamp=data['calibration_timestamp']
                        )
                        
                        logger.info(f"📂 Loaded existing calibration result from: {filepath}")
                        return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load calibration result: {e}")
            return None
    
    def verify_model(self, model_path: str, force_recalibration: bool = False) -> ModelCalibrationResult:
        """
        Main method to verify and calibrate model outputs
        """
        logger.info(f"🔍 Starting model verification for: {model_path}")
        
        # Check for existing calibration
        if not force_recalibration:
            existing_result = self.load_calibration_result(model_path)
            if existing_result:
                logger.info("✅ Using existing calibration result")
                return existing_result
        
        # Load model
        model = self.load_trained_model(model_path)
        if not model:
            logger.error("Failed to load model for verification")
            return None
        
        # Create test samples
        test_samples = self.create_test_samples()
        
        # Test model outputs
        test_results = self.test_model_outputs(model, test_samples)
        
        # Analyze patterns
        calibration_result = self.analyze_output_patterns(test_results)
        
        if calibration_result:
            # Save result
            self.save_calibration_result(calibration_result, model_path)
            
            # Cache result
            self.calibration_cache[model_path] = calibration_result
        
        return calibration_result

# Global instance
model_verifier = ModelOutputVerifier()

def get_model_calibration(model_path: str, force_recalibration: bool = False) -> Optional[ModelCalibrationResult]:
    """
    Get model calibration result, performing verification if needed
    """
    return model_verifier.verify_model(model_path, force_recalibration)
