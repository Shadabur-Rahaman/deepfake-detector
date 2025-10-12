import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from typing import Dict, List
import numpy as np

class ResNet50Detector:
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
            
            logger.info("ResNet-50 spatial detector loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading ResNet-50 model: {str(e)}")
            raise
    
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
                    if len(face.shape) == 3:
                        face_tensor = self.transform(face).unsqueeze(0)
                        batch_tensors.append(face_tensor)
                
                if batch_tensors:
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
            
            # Combine all features
            all_features = np.vstack(batch_features) if batch_features else np.array([])
            
            # Calculate overall confidence
            avg_artifact_score = np.mean(artifact_scores) if artifact_scores else 0.5
            
            result = {
                'confidence': float(avg_artifact_score),
                'features': all_features,
                'artifact_scores': artifact_scores,
                'feature_dimension': 2048,
                'faces_analyzed': len(face_crops),
                'processing_time': time.time() - start_time,
                'spatial_consistency_score': self.calculate_consistency_score(all_features)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ResNet-50 spatial analysis error: {str(e)}")
            raise
    
    def calculate_consistency_score(self, features: np.ndarray) -> float:
        """Calculate spatial consistency across detected faces"""
        if len(features) < 2:
            return 1.0
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                similarity = np.dot(features[i], features[j]) / (
                    np.linalg.norm(features[i]) * np.linalg.norm(features[j])
                )
                similarities.append(similarity)
        
        return float(np.mean(similarities)) if similarities else 1.0
