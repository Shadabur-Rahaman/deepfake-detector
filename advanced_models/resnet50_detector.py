# advanced_models/resnet50_detector.py - FIXED VERSION
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from typing import Dict, List
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)

class AdvancedResNet50Detector:
    """
    ResNet-50 based spatial artifact detector
    Extracts 2048-D feature vectors and detects spatial inconsistencies
    """
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.model_loaded = False
        
    async def load_model(self):
        """Load pre-trained ResNet-50 model with custom classifier"""
        try:
            # Load pre-trained ResNet-50
            self.model = models.resnet50(pretrained=True)
            
            # Modify for deepfake detection (binary classification)
            num_features = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 2)  # Real vs Fake
            )
            
            self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            
            logger.info("✅ ResNet-50 spatial detector loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading ResNet-50 model: {str(e)}")
            self.model_loaded = False
    
    async def detect(self, faces: List) -> Dict:
        """Detect deepfakes using ResNet-50 spatial analysis"""
        try:
            if not self.model_loaded:
                await self.load_model()
            
            if not faces:
                return {
                    "prediction": "No Faces Detected",
                    "confidence": 0.0,
                    "faces_analyzed": 0,
                    "model_used": "Advanced ResNet-50 Detector"
                }
            
            # Analyze spatial features
            analysis_result = await self.analyze_spatial_features(faces)
            
            # Determine prediction based on ResNet-50 analysis
            confidence = analysis_result.get('confidence', 0.5)
            
            if confidence > 0.6:
                prediction = "Deepfake Detected"
                final_confidence = confidence * 100
            elif confidence > 0.4:
                prediction = "Suspicious"
                final_confidence = 60.0
            else:
                prediction = "Real Video"
                final_confidence = (1.0 - confidence) * 100
            
            return {
                "prediction": prediction,
                "confidence": final_confidence,
                "faces_analyzed": len(faces),
                "model_used": "Advanced ResNet-50 Detector",
                "spatial_analysis": analysis_result,
                "processing_complete": True
            }
            
        except Exception as e:
            logger.error(f"ResNet-50 detection error: {str(e)}")
            return {
                "prediction": "Analysis Error",
                "confidence": 0.0,
                "faces_analyzed": 0,
                "model_used": "Advanced ResNet-50 Detector",
                "error": str(e)
            }
    
    async def analyze_spatial_features(self, face_crops: List[np.ndarray]) -> Dict:
        """
        Analyze spatial artifacts and inconsistencies in face crops
        """
        start_time = time.time()
        
        try:
            if not face_crops:
                return {
                    'confidence': 0.5,
                    'features': np.array([]),
                    'artifact_scores': [],
                    'processing_time': time.time() - start_time
                }
            
            batch_features = []
            artifact_scores = []
            
            # Process faces in batches for efficiency
            batch_size = 8
            for i in range(0, len(face_crops), batch_size):
                batch = face_crops[i:i+batch_size]
                batch_tensors = []
                
                for face in batch:
                    if isinstance(face, np.ndarray) and len(face.shape) == 3:
                        try:
                            face_tensor = self.transform(face).unsqueeze(0)
                            batch_tensors.append(face_tensor)
                        except Exception as e:
                            logger.warning(f"Face transform error: {e}")
                            continue
                
                if batch_tensors:
                    try:
                        batch_input = torch.cat(batch_tensors).to(self.device)
                        
                        with torch.no_grad():
                            # Extract features from the layer before classification
                            features = self.model.avgpool(self.model.layer4(
                                self.model.layer3(self.model.layer2(
                                    self.model.layer1(self.model.maxpool(
                                        self.model.relu(self.model.bn1(self.model.conv1(batch_input)))
                                    ))
                                ))
                            ))
                            
                            # Flatten features (2048-D feature vectors)
                            features = features.view(features.size(0), -1)
                            batch_features.append(features.cpu().numpy())
                            
                            # Get classification scores for artifact detection
                            outputs = self.model.fc(features)
                            probabilities = torch.softmax(outputs, dim=1)
                            fake_probabilities = probabilities[:, 1].cpu().numpy()
                            artifact_scores.extend(fake_probabilities)
                    except Exception as e:
                        logger.warning(f"Batch processing error: {e}")
                        continue
            
            # Combine results
            if batch_features:
                all_features = np.vstack(batch_features)
                avg_artifact_score = np.mean(artifact_scores) if artifact_scores else 0.5
            else:
                all_features = np.array([])
                avg_artifact_score = 0.5
            
            result = {
                'confidence': float(avg_artifact_score),
                'features': all_features.tolist() if hasattr(all_features, 'tolist') else all_features,
                'artifact_scores': artifact_scores,
                'processing_time': time.time() - start_time,
                'feature_dimension': all_features.shape[1] if all_features.size > 0 else 0,
                'faces_processed': len(artifact_scores)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ResNet-50 spatial analysis error: {str(e)}")
            return {
                'confidence': 0.5,
                'features': [],
                'artifact_scores': [],
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    def extract_spatial_features(self, face_crop: np.ndarray) -> np.ndarray:
        """Extract spatial features from a single face crop"""
        try:
            if not isinstance(face_crop, np.ndarray) or len(face_crop.shape) != 3:
                return np.zeros(2048)
            
            # Transform face crop
            face_tensor = self.transform(face_crop).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Extract features from intermediate layer
                features = self.model.avgpool(self.model.layer4(
                    self.model.layer3(self.model.layer2(
                        self.model.layer1(self.model.maxpool(
                            self.model.relu(self.model.bn1(self.model.conv1(face_tensor)))
                        ))
                    ))
                ))
                
                # Flatten and return
                features = features.view(features.size(0), -1)
                return features.cpu().numpy().flatten()
                
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return np.zeros(2048)
    
    def detect_spatial_artifacts(self, features: np.ndarray) -> Dict:
        """Detect spatial artifacts in extracted features"""
        try:
            if features.size == 0:
                return {'artifact_score': 0.5, 'artifact_type': 'none'}
            
            # Simple artifact detection based on feature statistics
            feature_mean = np.mean(features)
            feature_std = np.std(features)
            feature_range = np.ptp(features)
            
            # Calculate artifact score based on feature characteristics
            artifact_score = 0.5
            
            # High variance might indicate artifacts
            if feature_std > 0.5:
                artifact_score += 0.2
            
            # Unusual feature ranges might indicate artifacts
            if feature_range > 2.0:
                artifact_score += 0.2
            
            # Extreme values might indicate artifacts
            if np.any(np.abs(features) > 3.0):
                artifact_score += 0.1
            
            artifact_score = min(max(artifact_score, 0.0), 1.0)
            
            # Determine artifact type
            if artifact_score > 0.7:
                artifact_type = 'high'
            elif artifact_score > 0.5:
                artifact_type = 'medium'
            else:
                artifact_type = 'low'
            
            return {
                'artifact_score': float(artifact_score),
                'artifact_type': artifact_type,
                'feature_statistics': {
                    'mean': float(feature_mean),
                    'std': float(feature_std),
                    'range': float(feature_range)
                }
            }
            
        except Exception as e:
            logger.error(f"Artifact detection error: {e}")
            return {'artifact_score': 0.5, 'artifact_type': 'error', 'error': str(e)}

# Initialize detector instance
# Don't create global instance - let the importing module handle instantiation
