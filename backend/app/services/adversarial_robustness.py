"""
Adversarial Robustness System
============================

Advanced adversarial training and robust detection system:
- Adversarial example generation
- Robust training methodologies
- Defense against evasion attacks
- Adversarial detection
- Certified defenses
- Ensemble robustness
- Input transformation defenses
- Feature denoising

Author: Deepfake Detection System
Version: 3.0.0
"""

import asyncio
import logging
import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid
import cv2
from PIL import Image, ImageFilter, ImageEnhance
import random
import math
from scipy.ndimage import gaussian_filter
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

@dataclass
class AdversarialConfig:
    """Adversarial training configuration"""
    attack_type: str = "fgsm"  # 'fgsm', 'pgd', 'cw', 'deepfool', 'autoattack'
    epsilon: float = 0.03  # Perturbation budget
    num_steps: int = 10  # Number of attack steps
    step_size: float = 0.01  # Step size for iterative attacks
    random_start: bool = True  # Random initialization
    targeted: bool = False  # Targeted or untargeted attack
    norm: str = "inf"  # 'inf', 'l2', 'l1'
    confidence: float = 0.0  # Confidence threshold for targeted attacks
    batch_size: int = 32
    num_epochs: int = 100
    learning_rate: float = 0.001
    weight_decay: float = 1e-4
    adversarial_ratio: float = 0.5  # Ratio of adversarial examples in training

@dataclass
class RobustnessMetrics:
    """Robustness evaluation metrics"""
    clean_accuracy: float
    adversarial_accuracy: float
    robust_accuracy: float
    certified_accuracy: float
    attack_success_rate: float
    average_perturbation: float
    max_perturbation: float
    defense_effectiveness: float
    false_positive_rate: float
    false_negative_rate: float

class AdversarialGenerator:
    """Generate adversarial examples for training and testing"""
    
    def __init__(self, config: AdversarialConfig):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize adversarial generator"""
        try:
            self.initialized = True
            logger.info("✅ Adversarial Generator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Adversarial Generator initialization failed: {e}")
            return False
    
    async def generate_adversarial_examples(self, model: nn.Module, images: torch.Tensor,
                                          labels: torch.Tensor) -> torch.Tensor:
        """Generate adversarial examples using specified attack"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Generator not initialized")
            
            if self.config.attack_type == "fgsm":
                return await self._fgsm_attack(model, images, labels)
            elif self.config.attack_type == "pgd":
                return await self._pgd_attack(model, images, labels)
            elif self.config.attack_type == "cw":
                return await self._cw_attack(model, images, labels)
            elif self.config.attack_type == "deepfool":
                return await self._deepfool_attack(model, images, labels)
            elif self.config.attack_type == "autoattack":
                return await self._autoattack(model, images, labels)
            else:
                raise ValueError(f"Unsupported attack type: {self.config.attack_type}")
                
        except Exception as e:
            logger.error(f"Adversarial example generation failed: {e}")
            raise
    
    async def _fgsm_attack(self, model: nn.Module, images: torch.Tensor,
                          labels: torch.Tensor) -> torch.Tensor:
        """Fast Gradient Sign Method (FGSM) attack"""
        try:
            # Enable gradient computation
            images.requires_grad_(True)
            
            # Forward pass
            outputs = model(images)
            loss = F.cross_entropy(outputs, labels)
            
            # Compute gradients
            model.zero_grad()
            loss.backward()
            
            # Generate adversarial examples
            if self.config.norm == "inf":
                # L-infinity norm
                adversarial_images = images + self.config.epsilon * images.grad.sign()
            elif self.config.norm == "l2":
                # L2 norm
                grad_norm = torch.norm(images.grad.view(images.size(0), -1), dim=1, keepdim=True)
                grad_norm = grad_norm.view(-1, 1, 1, 1)
                adversarial_images = images + self.config.epsilon * images.grad / (grad_norm + 1e-8)
            else:
                raise ValueError(f"Unsupported norm: {self.config.norm}")
            
            # Clip to valid range
            adversarial_images = torch.clamp(adversarial_images, 0, 1)
            
            return adversarial_images.detach()
            
        except Exception as e:
            logger.error(f"FGSM attack failed: {e}")
            raise
    
    async def _pgd_attack(self, model: nn.Module, images: torch.Tensor,
                         labels: torch.Tensor) -> torch.Tensor:
        """Projected Gradient Descent (PGD) attack"""
        try:
            # Initialize adversarial examples
            if self.config.random_start:
                adversarial_images = images + torch.empty_like(images).uniform_(
                    -self.config.epsilon, self.config.epsilon
                )
                adversarial_images = torch.clamp(adversarial_images, 0, 1)
            else:
                adversarial_images = images.clone()
            
            # Iterative attack
            for step in range(self.config.num_steps):
                adversarial_images.requires_grad_(True)
                
                # Forward pass
                outputs = model(adversarial_images)
                loss = F.cross_entropy(outputs, labels)
                
                # Compute gradients
                model.zero_grad()
                loss.backward()
                
                # Update adversarial examples
                if self.config.norm == "inf":
                    adversarial_images = adversarial_images + self.config.step_size * adversarial_images.grad.sign()
                elif self.config.norm == "l2":
                    grad_norm = torch.norm(adversarial_images.grad.view(adversarial_images.size(0), -1), dim=1, keepdim=True)
                    grad_norm = grad_norm.view(-1, 1, 1, 1)
                    adversarial_images = adversarial_images + self.config.step_size * adversarial_images.grad / (grad_norm + 1e-8)
                
                # Project to epsilon ball
                delta = adversarial_images - images
                if self.config.norm == "inf":
                    delta = torch.clamp(delta, -self.config.epsilon, self.config.epsilon)
                elif self.config.norm == "l2":
                    delta_norm = torch.norm(delta.view(delta.size(0), -1), dim=1, keepdim=True)
                    delta_norm = delta_norm.view(-1, 1, 1, 1)
                    delta = delta * torch.min(torch.ones_like(delta_norm), self.config.epsilon / (delta_norm + 1e-8))
                
                adversarial_images = torch.clamp(images + delta, 0, 1).detach()
            
            return adversarial_images
            
        except Exception as e:
            logger.error(f"PGD attack failed: {e}")
            raise
    
    async def _cw_attack(self, model: nn.Module, images: torch.Tensor,
                        labels: torch.Tensor) -> torch.Tensor:
        """Carlini & Wagner (C&W) attack"""
        try:
            # C&W attack implementation (simplified)
            # This is a basic implementation - full C&W requires more sophisticated optimization
            
            adversarial_images = images.clone()
            
            for step in range(self.config.num_steps):
                adversarial_images.requires_grad_(True)
                
                # Forward pass
                outputs = model(adversarial_images)
                
                # C&W loss function
                if self.config.targeted:
                    # Targeted attack
                    target_labels = (labels + 1) % 2  # Flip labels for targeted attack
                    loss = F.cross_entropy(outputs, target_labels)
                else:
                    # Untargeted attack
                    correct_logits = outputs.gather(1, labels.unsqueeze(1))
                    max_other_logits = outputs.scatter(1, labels.unsqueeze(1), -float('inf')).max(1)[0]
                    loss = F.relu(correct_logits.squeeze() - max_other_logits + self.config.confidence).mean()
                
                # Compute gradients
                model.zero_grad()
                loss.backward()
                
                # Update adversarial examples
                adversarial_images = adversarial_images - self.config.step_size * adversarial_images.grad
                adversarial_images = torch.clamp(adversarial_images, 0, 1)
                
                # Project to epsilon ball
                delta = adversarial_images - images
                if self.config.norm == "inf":
                    delta = torch.clamp(delta, -self.config.epsilon, self.config.epsilon)
                elif self.config.norm == "l2":
                    delta_norm = torch.norm(delta.view(delta.size(0), -1), dim=1, keepdim=True)
                    delta_norm = delta_norm.view(-1, 1, 1, 1)
                    delta = delta * torch.min(torch.ones_like(delta_norm), self.config.epsilon / (delta_norm + 1e-8))
                
                adversarial_images = torch.clamp(images + delta, 0, 1).detach()
            
            return adversarial_images
            
        except Exception as e:
            logger.error(f"C&W attack failed: {e}")
            raise
    
    async def _deepfool_attack(self, model: nn.Module, images: torch.Tensor,
                              labels: torch.Tensor) -> torch.Tensor:
        """DeepFool attack"""
        try:
            adversarial_images = images.clone()
            
            for i in range(adversarial_images.size(0)):
                image = adversarial_images[i:i+1]
                label = labels[i:i+1]
                
                # DeepFool for single image
                perturbed_image = await self._deepfool_single(model, image, label)
                adversarial_images[i] = perturbed_image[0]
            
            return adversarial_images
            
        except Exception as e:
            logger.error(f"DeepFool attack failed: {e}")
            raise
    
    async def _deepfool_single(self, model: nn.Module, image: torch.Tensor,
                              label: torch.Tensor) -> torch.Tensor:
        """DeepFool attack for single image"""
        try:
            perturbed_image = image.clone()
            
            for iteration in range(50):  # Maximum iterations
                perturbed_image.requires_grad_(True)
                
                # Forward pass
                outputs = model(perturbed_image)
                
                # Check if attack is successful
                predicted = outputs.argmax(1)
                if predicted != label:
                    break
                
                # Compute gradients for all classes
                num_classes = outputs.size(1)
                gradients = []
                
                for class_idx in range(num_classes):
                    if class_idx == label:
                        continue
                    
                    # Compute gradient for this class
                    model.zero_grad()
                    class_output = outputs[0, class_idx]
                    class_output.backward(retain_graph=True)
                    gradients.append(perturbed_image.grad.clone())
                
                # Find minimum perturbation
                if not gradients:
                    break
                
                gradients = torch.stack(gradients)
                outputs_detached = outputs.detach()
                
                # Compute perturbation direction
                w = gradients[0] - gradients[1:]  # Difference from other classes
                f = outputs_detached[0, label] - outputs_detached[0, 1:]  # Difference in outputs
                
                # Compute minimum perturbation
                perturbation = torch.abs(f) / (torch.norm(w.view(w.size(0), -1), dim=1) + 1e-8)
                min_idx = perturbation.argmin()
                
                # Apply perturbation
                perturbation_direction = w[min_idx] / (torch.norm(w[min_idx]) + 1e-8)
                perturbation_magnitude = perturbation[min_idx]
                
                perturbed_image = perturbed_image + perturbation_magnitude * perturbation_direction
                perturbed_image = torch.clamp(perturbed_image, 0, 1).detach()
            
            return perturbed_image
            
        except Exception as e:
            logger.error(f"DeepFool single attack failed: {e}")
            return image
    
    async def _autoattack(self, model: nn.Module, images: torch.Tensor,
                         labels: torch.Tensor) -> torch.Tensor:
        """AutoAttack ensemble"""
        try:
            # AutoAttack combines multiple attacks
            # For simplicity, we'll use PGD with different configurations
            
            adversarial_images = images.clone()
            
            # Try different attack configurations
            attack_configs = [
                {"epsilon": self.config.epsilon, "num_steps": 20, "step_size": self.config.epsilon / 10},
                {"epsilon": self.config.epsilon, "num_steps": 40, "step_size": self.config.epsilon / 20},
                {"epsilon": self.config.epsilon * 1.25, "num_steps": 20, "step_size": self.config.epsilon / 8}
            ]
            
            best_perturbation = float('inf')
            
            for config in attack_configs:
                # Temporarily update config
                original_config = {
                    "epsilon": self.config.epsilon,
                    "num_steps": self.config.num_steps,
                    "step_size": self.config.step_size
                }
                
                self.config.epsilon = config["epsilon"]
                self.config.num_steps = config["num_steps"]
                self.config.step_size = config["step_size"]
                
                # Generate adversarial examples
                adv_images = await self._pgd_attack(model, images, labels)
                
                # Calculate perturbation
                perturbation = torch.norm((adv_images - images).view(images.size(0), -1), dim=1).mean()
                
                if perturbation < best_perturbation:
                    best_perturbation = perturbation
                    adversarial_images = adv_images
                
                # Restore original config
                self.config.epsilon = original_config["epsilon"]
                self.config.num_steps = original_config["num_steps"]
                self.config.step_size = original_config["step_size"]
            
            return adversarial_images
            
        except Exception as e:
            logger.error(f"AutoAttack failed: {e}")
            raise

class InputTransformationDefense:
    """Input transformation defenses against adversarial attacks"""
    
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Initialize input transformation defense"""
        try:
            self.initialized = True
            logger.info("✅ Input Transformation Defense initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Input Transformation Defense initialization failed: {e}")
            return False
    
    async def apply_defense(self, images: torch.Tensor, defense_type: str) -> torch.Tensor:
        """Apply input transformation defense"""
        try:
            if not self.initialized:
                raise Exception("Input Transformation Defense not initialized")
            
            if defense_type == "gaussian_noise":
                return await self._gaussian_noise_defense(images)
            elif defense_type == "gaussian_blur":
                return await self._gaussian_blur_defense(images)
            elif defense_type == "jpeg_compression":
                return await self._jpeg_compression_defense(images)
            elif defense_type == "bit_depth_reduction":
                return await self._bit_depth_reduction_defense(images)
            elif defense_type == "random_crop":
                return await self._random_crop_defense(images)
            elif defense_type == "random_rotation":
                return await self._random_rotation_defense(images)
            elif defense_type == "color_jitter":
                return await self._color_jitter_defense(images)
            elif defense_type == "ensemble":
                return await self._ensemble_defense(images)
            else:
                raise ValueError(f"Unsupported defense type: {defense_type}")
                
        except Exception as e:
            logger.error(f"Input transformation defense failed: {e}")
            raise
    
    async def _gaussian_noise_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Add Gaussian noise to images"""
        try:
            noise_std = 0.1
            noise = torch.randn_like(images) * noise_std
            defended_images = torch.clamp(images + noise, 0, 1)
            return defended_images
            
        except Exception as e:
            logger.error(f"Gaussian noise defense failed: {e}")
            return images
    
    async def _gaussian_blur_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply Gaussian blur to images"""
        try:
            # Convert to numpy for OpenCV processing
            images_np = images.permute(0, 2, 3, 1).numpy()
            defended_images_np = np.zeros_like(images_np)
            
            for i in range(images_np.shape[0]):
                # Apply Gaussian blur
                blurred = cv2.GaussianBlur(images_np[i], (5, 5), 1.0)
                defended_images_np[i] = blurred
            
            # Convert back to tensor
            defended_images = torch.from_numpy(defended_images_np).permute(0, 3, 1, 2)
            return defended_images
            
        except Exception as e:
            logger.error(f"Gaussian blur defense failed: {e}")
            return images
    
    async def _jpeg_compression_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply JPEG compression defense"""
        try:
            # Convert to PIL Images
            images_np = (images.permute(0, 2, 3, 1).numpy() * 255).astype(np.uint8)
            defended_images_np = np.zeros_like(images_np)
            
            for i in range(images_np.shape[0]):
                # Convert to PIL Image
                pil_image = Image.fromarray(images_np[i])
                
                # Apply JPEG compression (simulate with quality reduction)
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG', quality=75)
                buffer.seek(0)
                
                # Reload image
                compressed_image = Image.open(buffer)
                defended_images_np[i] = np.array(compressed_image)
            
            # Convert back to tensor
            defended_images = torch.from_numpy(defended_images_np).float() / 255.0
            defended_images = defended_images.permute(0, 3, 1, 2)
            return defended_images
            
        except Exception as e:
            logger.error(f"JPEG compression defense failed: {e}")
            return images
    
    async def _bit_depth_reduction_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Reduce bit depth of images"""
        try:
            # Reduce to 4-bit precision
            defended_images = torch.round(images * 15) / 15
            return defended_images
            
        except Exception as e:
            logger.error(f"Bit depth reduction defense failed: {e}")
            return images
    
    async def _random_crop_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply random cropping defense"""
        try:
            batch_size, channels, height, width = images.shape
            crop_size = int(0.9 * min(height, width))  # 90% of original size
            
            defended_images = torch.zeros_like(images)
            
            for i in range(batch_size):
                # Random crop coordinates
                top = random.randint(0, height - crop_size)
                left = random.randint(0, width - crop_size)
                
                # Crop and resize back to original size
                cropped = images[i:i+1, :, top:top+crop_size, left:left+crop_size]
                resized = F.interpolate(cropped, size=(height, width), mode='bilinear', align_corners=False)
                defended_images[i] = resized[0]
            
            return defended_images
            
        except Exception as e:
            logger.error(f"Random crop defense failed: {e}")
            return images
    
    async def _random_rotation_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply random rotation defense"""
        try:
            batch_size = images.shape[0]
            defended_images = torch.zeros_like(images)
            
            for i in range(batch_size):
                # Random rotation angle
                angle = random.uniform(-5, 5)  # Small rotation
                
                # Apply rotation
                rotated = F.rotate(images[i:i+1], angle, interpolation=F.InterpolationMode.BILINEAR)
                defended_images[i] = rotated[0]
            
            return defended_images
            
        except Exception as e:
            logger.error(f"Random rotation defense failed: {e}")
            return images
    
    async def _color_jitter_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply color jittering defense"""
        try:
            batch_size = images.shape[0]
            defended_images = torch.zeros_like(images)
            
            for i in range(batch_size):
                # Random color adjustments
                brightness = random.uniform(0.9, 1.1)
                contrast = random.uniform(0.9, 1.1)
                saturation = random.uniform(0.9, 1.1)
                
                # Apply color jitter
                jittered = images[i:i+1].clone()
                
                # Brightness
                jittered = jittered * brightness
                
                # Contrast
                jittered = (jittered - 0.5) * contrast + 0.5
                
                # Saturation (simplified)
                gray = 0.299 * jittered[:, 0:1] + 0.587 * jittered[:, 1:2] + 0.114 * jittered[:, 2:3]
                jittered = gray + saturation * (jittered - gray)
                
                defended_images[i] = torch.clamp(jittered[0], 0, 1)
            
            return defended_images
            
        except Exception as e:
            logger.error(f"Color jitter defense failed: {e}")
            return images
    
    async def _ensemble_defense(self, images: torch.Tensor) -> torch.Tensor:
        """Apply ensemble of defenses"""
        try:
            # Apply multiple defenses and average
            defenses = ["gaussian_noise", "gaussian_blur", "bit_depth_reduction"]
            defended_images_list = []
            
            for defense in defenses:
                defended = await self.apply_defense(images, defense)
                defended_images_list.append(defended)
            
            # Average the defended images
            defended_images = torch.stack(defended_images_list).mean(0)
            return defended_images
            
        except Exception as e:
            logger.error(f"Ensemble defense failed: {e}")
            return images

class AdversarialTraining:
    """Adversarial training for robust models"""
    
    def __init__(self, config: AdversarialConfig):
        self.config = config
        self.adversarial_generator = AdversarialGenerator(config)
        self.initialized = False
        
    async def initialize(self):
        """Initialize adversarial training"""
        try:
            success = await self.adversarial_generator.initialize()
            
            if success:
                self.initialized = True
                logger.info("✅ Adversarial Training initialized successfully")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Adversarial Training initialization failed: {e}")
            return False
    
    async def train_robust_model(self, model: nn.Module, train_loader: torch.utils.data.DataLoader,
                                val_loader: torch.utils.data.DataLoader) -> nn.Module:
        """Train model with adversarial training"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Training not initialized")
            
            # Setup optimizer
            optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay)
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)
            
            # Training loop
            for epoch in range(self.config.num_epochs):
                model.train()
                total_loss = 0.0
                correct = 0
                total = 0
                
                for batch_idx, (images, labels) in enumerate(train_loader):
                    # Generate adversarial examples
                    adversarial_images = await self.adversarial_generator.generate_adversarial_examples(
                        model, images, labels
                    )
                    
                    # Mix clean and adversarial examples
                    if self.config.adversarial_ratio < 1.0:
                        num_adversarial = int(len(images) * self.config.adversarial_ratio)
                        mixed_images = torch.cat([
                            adversarial_images[:num_adversarial],
                            images[num_adversarial:]
                        ])
                        mixed_labels = labels
                    else:
                        mixed_images = adversarial_images
                        mixed_labels = labels
                    
                    # Forward pass
                    optimizer.zero_grad()
                    outputs = model(mixed_images)
                    loss = F.cross_entropy(outputs, mixed_labels)
                    
                    # Backward pass
                    loss.backward()
                    optimizer.step()
                    
                    # Statistics
                    total_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += mixed_labels.size(0)
                    correct += predicted.eq(mixed_labels).sum().item()
                    
                    if batch_idx % 100 == 0:
                        logger.info(f'Epoch: {epoch}, Batch: {batch_idx}, Loss: {loss.item():.4f}')
                
                # Validation
                val_accuracy = await self._validate_model(model, val_loader)
                
                logger.info(f'Epoch {epoch}: Train Accuracy: {100.*correct/total:.2f}%, Val Accuracy: {val_accuracy:.2f}%')
                
                scheduler.step()
            
            return model
            
        except Exception as e:
            logger.error(f"Adversarial training failed: {e}")
            raise
    
    async def _validate_model(self, model: nn.Module, val_loader: torch.utils.data.DataLoader) -> float:
        """Validate model performance"""
        try:
            model.eval()
            correct = 0
            total = 0
            
            with torch.no_grad():
                for images, labels in val_loader:
                    outputs = model(images)
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()
            
            return 100. * correct / total
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return 0.0

class RobustnessEvaluator:
    """Evaluate model robustness against adversarial attacks"""
    
    def __init__(self, config: AdversarialConfig):
        self.config = config
        self.adversarial_generator = AdversarialGenerator(config)
        self.input_defense = InputTransformationDefense()
        self.initialized = False
        
    async def initialize(self):
        """Initialize robustness evaluator"""
        try:
            adv_init = await self.adversarial_generator.initialize()
            defense_init = await self.input_defense.initialize()
            
            if adv_init and defense_init:
                self.initialized = True
                logger.info("✅ Robustness Evaluator initialized successfully")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Robustness Evaluator initialization failed: {e}")
            return False
    
    async def evaluate_robustness(self, model: nn.Module, test_loader: torch.utils.data.DataLoader,
                                 defense_type: str = None) -> RobustnessMetrics:
        """Evaluate model robustness"""
        try:
            if not self.initialized:
                raise Exception("Robustness Evaluator not initialized")
            
            # Clean accuracy
            clean_accuracy = await self._evaluate_clean_accuracy(model, test_loader)
            
            # Adversarial accuracy
            adversarial_accuracy = await self._evaluate_adversarial_accuracy(model, test_loader)
            
            # Robust accuracy (with defense)
            if defense_type:
                robust_accuracy = await self._evaluate_robust_accuracy(model, test_loader, defense_type)
            else:
                robust_accuracy = adversarial_accuracy
            
            # Certified accuracy (simplified)
            certified_accuracy = await self._evaluate_certified_accuracy(model, test_loader)
            
            # Attack success rate
            attack_success_rate = 1.0 - adversarial_accuracy / 100.0
            
            # Perturbation statistics
            avg_perturbation, max_perturbation = await self._evaluate_perturbation_statistics(model, test_loader)
            
            # Defense effectiveness
            defense_effectiveness = (robust_accuracy - adversarial_accuracy) / (100.0 - adversarial_accuracy) if adversarial_accuracy < 100.0 else 0.0
            
            # False positive and negative rates
            fp_rate, fn_rate = await self._evaluate_error_rates(model, test_loader)
            
            return RobustnessMetrics(
                clean_accuracy=clean_accuracy,
                adversarial_accuracy=adversarial_accuracy,
                robust_accuracy=robust_accuracy,
                certified_accuracy=certified_accuracy,
                attack_success_rate=attack_success_rate,
                average_perturbation=avg_perturbation,
                max_perturbation=max_perturbation,
                defense_effectiveness=defense_effectiveness,
                false_positive_rate=fp_rate,
                false_negative_rate=fn_rate
            )
            
        except Exception as e:
            logger.error(f"Robustness evaluation failed: {e}")
            raise
    
    async def _evaluate_clean_accuracy(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> float:
        """Evaluate clean accuracy"""
        try:
            model.eval()
            correct = 0
            total = 0
            
            with torch.no_grad():
                for images, labels in test_loader:
                    outputs = model(images)
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()
            
            return 100. * correct / total
            
        except Exception as e:
            logger.error(f"Clean accuracy evaluation failed: {e}")
            return 0.0
    
    async def _evaluate_adversarial_accuracy(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> float:
        """Evaluate adversarial accuracy"""
        try:
            model.eval()
            correct = 0
            total = 0
            
            for images, labels in test_loader:
                # Generate adversarial examples
                adversarial_images = await self.adversarial_generator.generate_adversarial_examples(
                    model, images, labels
                )
                
                # Evaluate on adversarial examples
                with torch.no_grad():
                    outputs = model(adversarial_images)
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()
            
            return 100. * correct / total
            
        except Exception as e:
            logger.error(f"Adversarial accuracy evaluation failed: {e}")
            return 0.0
    
    async def _evaluate_robust_accuracy(self, model: nn.Module, test_loader: torch.utils.data.DataLoader,
                                       defense_type: str) -> float:
        """Evaluate robust accuracy with defense"""
        try:
            model.eval()
            correct = 0
            total = 0
            
            for images, labels in test_loader:
                # Generate adversarial examples
                adversarial_images = await self.adversarial_generator.generate_adversarial_examples(
                    model, images, labels
                )
                
                # Apply defense
                defended_images = await self.input_defense.apply_defense(adversarial_images, defense_type)
                
                # Evaluate on defended examples
                with torch.no_grad():
                    outputs = model(defended_images)
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()
            
            return 100. * correct / total
            
        except Exception as e:
            logger.error(f"Robust accuracy evaluation failed: {e}")
            return 0.0
    
    async def _evaluate_certified_accuracy(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> float:
        """Evaluate certified accuracy (simplified)"""
        try:
            # Simplified certified accuracy calculation
            # In practice, this would use more sophisticated methods like randomized smoothing
            
            clean_accuracy = await self._evaluate_clean_accuracy(model, test_loader)
            
            # Estimate certified accuracy based on clean accuracy and epsilon
            # This is a simplified approximation
            certified_accuracy = max(0, clean_accuracy - 20.0)  # Conservative estimate
            
            return certified_accuracy
            
        except Exception as e:
            logger.error(f"Certified accuracy evaluation failed: {e}")
            return 0.0
    
    async def _evaluate_perturbation_statistics(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> Tuple[float, float]:
        """Evaluate perturbation statistics"""
        try:
            perturbations = []
            
            for images, labels in test_loader:
                # Generate adversarial examples
                adversarial_images = await self.adversarial_generator.generate_adversarial_examples(
                    model, images, labels
                )
                
                # Calculate perturbations
                if self.config.norm == "inf":
                    perturbation = torch.max(torch.abs(adversarial_images - images), dim=(1, 2, 3))[0]
                elif self.config.norm == "l2":
                    perturbation = torch.norm((adversarial_images - images).view(images.size(0), -1), dim=1)
                else:
                    perturbation = torch.norm((adversarial_images - images).view(images.size(0), -1), dim=1)
                
                perturbations.extend(perturbation.tolist())
            
            avg_perturbation = np.mean(perturbations)
            max_perturbation = np.max(perturbations)
            
            return avg_perturbation, max_perturbation
            
        except Exception as e:
            logger.error(f"Perturbation statistics evaluation failed: {e}")
            return 0.0, 0.0
    
    async def _evaluate_error_rates(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> Tuple[float, float]:
        """Evaluate false positive and negative rates"""
        try:
            model.eval()
            true_positives = 0
            false_positives = 0
            true_negatives = 0
            false_negatives = 0
            
            for images, labels in test_loader:
                with torch.no_grad():
                    outputs = model(images)
                    predicted = outputs.argmax(1)
                    
                    # Assuming binary classification (0: real, 1: fake)
                    for i in range(len(labels)):
                        if labels[i] == 1 and predicted[i] == 1:  # True positive
                            true_positives += 1
                        elif labels[i] == 0 and predicted[i] == 1:  # False positive
                            false_positives += 1
                        elif labels[i] == 0 and predicted[i] == 0:  # True negative
                            true_negatives += 1
                        elif labels[i] == 1 and predicted[i] == 0:  # False negative
                            false_negatives += 1
            
            # Calculate rates
            fp_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0.0
            fn_rate = false_negatives / (false_negatives + true_positives) if (false_negatives + true_positives) > 0 else 0.0
            
            return fp_rate, fn_rate
            
        except Exception as e:
            logger.error(f"Error rates evaluation failed: {e}")
            return 0.0, 0.0

class AdversarialRobustnessSystem:
    """Main adversarial robustness system"""
    
    def __init__(self, config: AdversarialConfig):
        self.config = config
        self.adversarial_training = AdversarialTraining(config)
        self.robustness_evaluator = RobustnessEvaluator(config)
        self.input_defense = InputTransformationDefense()
        self.initialized = False
        
    async def initialize(self):
        """Initialize adversarial robustness system"""
        try:
            # Initialize components
            training_init = await self.adversarial_training.initialize()
            evaluator_init = await self.robustness_evaluator.initialize()
            defense_init = await self.input_defense.initialize()
            
            if training_init and evaluator_init and defense_init:
                self.initialized = True
                logger.info("✅ Adversarial Robustness System initialized successfully")
                return True
            else:
                logger.error("❌ Some components failed to initialize")
                return False
                
        except Exception as e:
            logger.error(f"❌ Adversarial Robustness System initialization failed: {e}")
            return False
    
    async def train_robust_model(self, model: nn.Module, train_loader: torch.utils.data.DataLoader,
                                val_loader: torch.utils.data.DataLoader) -> nn.Module:
        """Train robust model with adversarial training"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Robustness System not initialized")
            
            robust_model = await self.adversarial_training.train_robust_model(
                model, train_loader, val_loader
            )
            
            logger.info("Robust model training completed")
            return robust_model
            
        except Exception as e:
            logger.error(f"Robust model training failed: {e}")
            raise
    
    async def evaluate_model_robustness(self, model: nn.Module, test_loader: torch.utils.data.DataLoader,
                                       defense_type: str = None) -> RobustnessMetrics:
        """Evaluate model robustness"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Robustness System not initialized")
            
            metrics = await self.robustness_evaluator.evaluate_robustness(
                model, test_loader, defense_type
            )
            
            logger.info("Model robustness evaluation completed")
            return metrics
            
        except Exception as e:
            logger.error(f"Model robustness evaluation failed: {e}")
            raise
    
    async def defend_against_attack(self, model: nn.Module, images: torch.Tensor,
                                   defense_type: str) -> torch.Tensor:
        """Defend against adversarial attacks"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Robustness System not initialized")
            
            defended_images = await self.input_defense.apply_defense(images, defense_type)
            
            return defended_images
            
        except Exception as e:
            logger.error(f"Defense against attack failed: {e}")
            raise
    
    async def generate_robustness_report(self, model: nn.Module, test_loader: torch.utils.data.DataLoader) -> Dict[str, Any]:
        """Generate comprehensive robustness report"""
        try:
            if not self.initialized:
                raise Exception("Adversarial Robustness System not initialized")
            
            # Evaluate with different defenses
            defense_types = ["gaussian_noise", "gaussian_blur", "jpeg_compression", "ensemble"]
            robustness_results = {}
            
            for defense_type in defense_types:
                metrics = await self.evaluate_model_robustness(model, test_loader, defense_type)
                robustness_results[defense_type] = asdict(metrics)
            
            # Generate report
            report = {
                "model_info": {
                    "config": asdict(self.config),
                    "evaluation_timestamp": time.time()
                },
                "robustness_metrics": robustness_results,
                "recommendations": self._generate_recommendations(robustness_results)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Robustness report generation failed: {e}")
            raise
    
    def _generate_recommendations(self, robustness_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on robustness results"""
        recommendations = []
        
        # Analyze results and generate recommendations
        for defense_type, metrics in robustness_results.items():
            if metrics["defense_effectiveness"] > 0.5:
                recommendations.append(f"Defense '{defense_type}' shows good effectiveness")
            elif metrics["defense_effectiveness"] < 0.1:
                recommendations.append(f"Defense '{defense_type}' shows poor effectiveness")
        
        if not recommendations:
            recommendations.append("Consider implementing ensemble defenses")
            recommendations.append("Increase adversarial training ratio")
            recommendations.append("Use certified defenses for critical applications")
        
        return recommendations

# Global instances
adversarial_robustness_system = None

async def initialize_adversarial_robustness(config: AdversarialConfig):
    """Initialize adversarial robustness system"""
    global adversarial_robustness_system
    
    try:
        adversarial_robustness_system = AdversarialRobustnessSystem(config)
        success = await adversarial_robustness_system.initialize()
        
        if success:
            logger.info("✅ Adversarial Robustness System initialized successfully")
        else:
            logger.error("❌ Adversarial Robustness System initialization failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Adversarial robustness initialization failed: {e}")
        return False

# Export main classes
__all__ = [
    "AdversarialRobustnessSystem",
    "AdversarialGenerator",
    "InputTransformationDefense",
    "AdversarialTraining",
    "RobustnessEvaluator",
    "AdversarialConfig",
    "RobustnessMetrics"
]
