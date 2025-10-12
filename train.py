# # train.py
# import os
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import DataLoader
# from torchvision.datasets import ImageFolder
# from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
# from torchvision import transforms

# # --- 1. CONFIGURATION ---
# # (Adjust these settings as needed)

# # Paths
# DATASET_DIR = "processed_faces/train"  # Point to the 'train' folder created by prepare_dataset.py
# MODEL_SAVE_PATH = "deepfake_detector_finetuned.pth" # Where to save the final model

# # Hyperparameters
# LEARNING_RATE = 0.001
# BATCH_SIZE = 32
# NUM_EPOCHS = 5  # Start with 5-10 and increase if needed

# # --- 2. SETUP ---

# # Set the device to your GPU if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"Using device: {device}")

# # --- 3. DATA PREPARATION ---

# # Define the transformations for the images
# # We add data augmentation (RandomHorizontalFlip) to make the model more robust
# data_transforms = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.RandomHorizontalFlip(),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
# ])

# print("Loading dataset...")
# # Load the dataset using ImageFolder
# # This automatically finds the 'real' and 'fake' subfolders and assigns labels
# full_dataset = ImageFolder(DATASET_DIR, transform=data_transforms)

# # Create a DataLoader to feed data to the model in batches
# train_loader = DataLoader(full_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
# print(f"Dataset loaded. Found {len(full_dataset)} images belonging to classes: {full_dataset.class_to_idx}")


# # --- 4. MODEL SETUP ---

# print("Setting up the model...")
# # Load the pre-trained EfficientNet-B0 model
# weights = EfficientNet_B0_Weights.DEFAULT
# model = efficientnet_b0(weights=weights)

# # Replace the final layer for our binary classification task (Real vs. Fake)
# num_ftrs = model.classifier[1].in_features
# model.classifier[1] = nn.Linear(num_ftrs, 1)

# # Move the model to the GPU
# model = model.to(device)

# # Define the loss function and optimizer
# # BCEWithLogitsLoss is perfect for binary classification as it includes a sigmoid
# criterion = nn.BCEWithLogitsLoss()
# optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)


# # --- 5. TRAINING LOOP ---

# print("Starting model training...")
# # Set the model to training mode
# model.train()

# for epoch in range(NUM_EPOCHS):
#     running_loss = 0.0
#     for i, (inputs, labels) in enumerate(train_loader):
#         # Move inputs and labels to the GPU
#         inputs = inputs.to(device)
#         labels = labels.to(device)

#         # 1. Clear the gradients
#         optimizer.zero_grad()

#         # 2. Forward pass: get model predictions
#         outputs = model(inputs)
        
#         # 3. Calculate the loss
#         loss = criterion(outputs.squeeze(), labels.float())
        
#         # 4. Backward pass: compute gradients
#         loss.backward()
        
#         # 5. Update the model's weights
#         optimizer.step()

#         running_loss += loss.item()
        
#         # Print progress every 10 batches
#         if (i + 1) % 10 == 0:
#             print(f'Epoch [{epoch+1}/{NUM_EPOCHS}], Batch [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}')

#     epoch_loss = running_loss / len(train_loader)
#     print(f"--- End of Epoch {epoch+1}, Average Loss: {epoch_loss:.4f} ---")


# # --- 6. SAVE THE TRAINED MODEL ---

# print("Training finished. Saving the fine-tuned model...")
# torch.save(model.state_dict(), MODEL_SAVE_PATH)
# print(f"Model saved to {MODEL_SAVE_PATH}")


# train.py - Complete Training Script for Deepfake Detection
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import GradScaler, autocast
from torchvision import transforms
from torchvision.models import efficientnet_b0
import cv2
import numpy as np
from pathlib import Path
import time
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import json
import argparse
from datetime import datetime
import gc
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepfakeDataset(Dataset):
    """Dataset class for loading preprocessed face images"""
    
    def __init__(self, data_dir, split='train', transform=None, max_samples=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.split = split
        self.max_samples = max_samples
        
        # Load image paths and labels
        self.samples = []
        self._load_samples()
        
        # Apply max_samples limit if specified
        if self.max_samples and len(self.samples) > self.max_samples:
            random.shuffle(self.samples)
            self.samples = self.samples[:self.max_samples]
        
        logger.info(f"Loaded {len(self.samples)} samples for {split}")
        
    def _load_samples(self):
        """Load all image paths and create labels with proper train/val split"""
        
        # Check if we have train subdirectory structure
        train_dir = self.data_dir / "train"
        if train_dir.exists():
            # Use train subdirectory structure
            if self.split == 'train':
                real_dir = train_dir / "real"
                fake_dir = train_dir / "fake"
            else:
                # For validation, look for val directory or create split from train
                val_dir = self.data_dir / "val"
                if val_dir.exists():
                    real_dir = val_dir / "real"
                    fake_dir = val_dir / "fake"
                else:
                    # Create validation split from train data (20% split)
                    train_real_dir = train_dir / "real"
                    train_fake_dir = train_dir / "fake"
                    self._create_val_split(train_real_dir, train_fake_dir)
                    return
            logger.info(f"Using train subdirectory structure for {self.split}")
        else:
            # Fallback to direct structure with manual split
            real_dir = self.data_dir / "real"
            fake_dir = self.data_dir / "fake"
            logger.info(f"Using direct structure for {self.split}")
        
        # Load real images (label = 0)
        if real_dir.exists():
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            for ext in image_extensions:
                for img_path in real_dir.glob(ext):
                    self.samples.append((str(img_path), 0))
        
        # Load fake images (label = 1)  
        if fake_dir.exists():
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            for ext in image_extensions:
                for img_path in fake_dir.glob(ext):
                    self.samples.append((str(img_path), 1))
        
        logger.info(f"Found {len([s for s in self.samples if s[1] == 0])} real images")
        logger.info(f"Found {len([s for s in self.samples if s[1] == 1])} fake images")
        
        if len(self.samples) == 0:
            raise ValueError(f"No images found in {real_dir} or {fake_dir}")
    
    def _create_val_split(self, train_real_dir, train_fake_dir):
        """Create validation split from training data (80/20 split)"""
        all_samples = []
        
        # Collect all samples
        if train_real_dir.exists():
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            for ext in image_extensions:
                for img_path in train_real_dir.glob(ext):
                    all_samples.append((str(img_path), 0))
        
        if train_fake_dir.exists():
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            for ext in image_extensions:
                for img_path in train_fake_dir.glob(ext):
                    all_samples.append((str(img_path), 1))
        
        # Shuffle and split
        random.shuffle(all_samples)
        split_idx = int(0.8 * len(all_samples))
        
        if self.split == 'train':
            self.samples = all_samples[:split_idx]
        else:
            self.samples = all_samples[split_idx:]
                
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # Load image
        try:
            image = cv2.imread(img_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if self.transform:
                image = self.transform(image)
                
            return image, torch.tensor(label, dtype=torch.float32)
            
        except Exception as e:
            logger.warning(f"Error loading {img_path}: {e}")
            # Return a black image as fallback
            if self.transform:
                black_img = self.transform(np.zeros((224, 224, 3), dtype=np.uint8))
            else:
                black_img = torch.zeros(3, 224, 224)
            return black_img, torch.tensor(label, dtype=torch.float32)

class EfficientNetDeepfake(nn.Module):
    """EfficientNet-B0 model for deepfake detection"""
    
    def __init__(self, num_classes=1, pretrained=True):
        super(EfficientNetDeepfake, self).__init__()
        
        # Load EfficientNet-B0 backbone
        self.backbone = efficientnet_b0(weights='IMAGENET1K_V1' if pretrained else None)
        
        # Replace classifier for binary classification
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.2),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.1),
            nn.Linear(128, num_classes)
        )
        
        # Enable gradient checkpointing if available
        if hasattr(self.backbone, 'gradient_checkpointing_enable'):
            self.backbone.gradient_checkpointing_enable()
        
    def forward(self, x):
        return self.backbone(x)

def get_transforms():
    """Define data augmentation transforms"""
    
    train_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform

def clear_gpu_cache():
    """Clear GPU cache and collect garbage"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def print_gpu_memory():
    """Print current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        logger.info(f"GPU Memory - Allocated: {allocated:.2f} GB, Reserved: {reserved:.2f} GB")

def calculate_metrics(y_true, y_pred, y_probs=None):
    """Calculate comprehensive metrics"""
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='binary')
    recall = recall_score(y_true, y_pred, average='binary')
    f1 = f1_score(y_true, y_pred, average='binary')
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
    }
    
    if y_probs is not None:
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(y_true, y_probs)
        metrics['auc'] = auc
    
    return metrics

def plot_confusion_matrix(y_true, y_pred, save_path):
    """Plot and save confusion matrix"""
    
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def train_epoch(model, dataloader, criterion, optimizer, device, epoch, scaler=None):
    """Train for one epoch with mixed precision support"""
    
    model.train()
    running_loss = 0.0
    all_predictions = []
    all_labels = []
    
    pbar = tqdm(dataloader, desc=f'Epoch {epoch+1} [Train]')
    
    for batch_idx, (images, labels) in enumerate(pbar):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        
        # Zero gradients
        optimizer.zero_grad()
        
        if scaler:
            # Mixed precision training
            with autocast():
                outputs = model(images).squeeze()
                loss = criterion(outputs, labels)
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            # Standard training
            outputs = model(images).squeeze()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        # Statistics - properly detach tensors
        running_loss += loss.detach().cpu().item()
        predictions = torch.sigmoid(outputs.detach()) > 0.5
        all_predictions.extend(predictions.cpu().numpy())
        all_labels.extend(labels.detach().cpu().numpy())
        
        # Update progress bar
        pbar.set_postfix({
            'Loss': f'{loss.detach().cpu().item():.4f}',
            'Avg Loss': f'{running_loss/(batch_idx+1):.4f}'
        })
        
        # Clear cache periodically
        if batch_idx % 50 == 0:
            clear_gpu_cache()
    
    # Calculate epoch metrics
    epoch_loss = running_loss / len(dataloader)
    epoch_metrics = calculate_metrics(all_labels, all_predictions)
    
    return epoch_loss, epoch_metrics

def validate_epoch(model, dataloader, criterion, device, epoch):
    """Validate for one epoch with proper memory management"""
    
    model.eval()
    running_loss = 0.0
    all_predictions = []
    all_labels = []
    all_probabilities = []
    
    pbar = tqdm(dataloader, desc=f'Epoch {epoch+1} [Val]')
    
    with torch.no_grad():  # Context manager for validation
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            # Forward pass
            outputs = model(images).squeeze()
            loss = criterion(outputs, labels)
            
            # Statistics - properly detach tensors
            running_loss += loss.detach().cpu().item()
            probabilities = torch.sigmoid(outputs.detach())
            predictions = probabilities > 0.5
            
            all_predictions.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())
            
            # Update progress bar
            pbar.set_postfix({
                'Loss': f'{loss.detach().cpu().item():.4f}',
                'Avg Loss': f'{running_loss/(batch_idx+1):.4f}'
            })
            
            # Clear cache periodically
            if batch_idx % 50 == 0:
                clear_gpu_cache()
    
    # Calculate epoch metrics
    epoch_loss = running_loss / len(dataloader)
    epoch_metrics = calculate_metrics(all_labels, all_predictions, all_probabilities)
    
    return epoch_loss, epoch_metrics, all_labels, all_predictions

def save_checkpoint(model, optimizer, epoch, loss, metrics, filepath):
    """Save model checkpoint"""
    
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    }
    
    torch.save(checkpoint, filepath)
    logger.info(f"Checkpoint saved: {filepath}")

def profile_memory_usage(model, sample_input, device):
    """Profile memory usage for debugging"""
    if torch.cuda.is_available():
        try:
            import torch.profiler
            
            with torch.profiler.profile(
                activities=[torch.profiler.ProfilerActivity.CUDA],
                record_shapes=True,
                profile_memory=True,
            ) as prof:
                with torch.no_grad():
                    output = model(sample_input.to(device))
            
            print(prof.key_averages().table(sort_by="cuda_memory_usage", row_limit=10))
        except ImportError:
            logger.warning("torch.profiler not available for memory profiling")

def main():
    parser = argparse.ArgumentParser(description='Train Deepfake Detection Model')
    parser.add_argument('--data_dir', type=str, default='processed_faces_optimized',
                       help='Directory containing processed face data')
    parser.add_argument('--batch_size', type=int, default=8,  # Reduced default batch size
                       help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=1e-4,
                       help='Learning rate')
    parser.add_argument('--output_dir', type=str, default='training_outputs',
                       help='Directory to save outputs')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to checkpoint to resume from')
    parser.add_argument('--max_samples', type=int, default=None,
                       help='Maximum number of samples to use (for debugging)')
    parser.add_argument('--mixed_precision', action='store_true',
                       help='Use mixed precision training')
    parser.add_argument('--profile_memory', action='store_true',
                       help='Profile memory usage')
    
    args = parser.parse_args()
    
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name()}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print_gpu_memory()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Data transforms
    train_transform, val_transform = get_transforms()
    
    # Datasets with proper train/val split
    train_dataset = DeepfakeDataset(args.data_dir, split='train', transform=train_transform, max_samples=args.max_samples)
    val_dataset = DeepfakeDataset(args.data_dir, split='val', transform=val_transform, max_samples=args.max_samples)
    
    # Data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=args.batch_size, 
        shuffle=True, 
        num_workers=2,  # Reduced num_workers to save memory
        pin_memory=True if torch.cuda.is_available() else False,
        drop_last=True  # Drop last incomplete batch
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=args.batch_size, 
        shuffle=False, 
        num_workers=2,  # Reduced num_workers to save memory
        pin_memory=True if torch.cuda.is_available() else False,
        drop_last=False
    )
    
    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Validation samples: {len(val_dataset)}")
    
    # Model
    model = EfficientNetDeepfake(num_classes=1, pretrained=True)
    model = model.to(device)
    
    # Mixed precision scaler
    scaler = GradScaler() if args.mixed_precision else None
    if args.mixed_precision:
        logger.info("Using mixed precision training")
    
    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    # Memory profiling if requested
    if args.profile_memory and torch.cuda.is_available():
        sample_input = torch.randn(1, 3, 224, 224)
        logger.info("Memory profiling:")
        profile_memory_usage(model, sample_input, device)
    
    # Resume from checkpoint if specified
    start_epoch = 0
    best_val_accuracy = 0.0
    
    if args.resume:
        logger.info(f"Resuming from checkpoint: {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        best_val_accuracy = checkpoint['metrics'].get('accuracy', 0.0)
    
    # Training history
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_accuracy': [],
        'val_accuracy': [],
        'val_f1': [],
        'val_auc': []
    }
    
    logger.info("Starting training...")
    
    for epoch in range(start_epoch, args.epochs):
        epoch_start_time = time.time()
        
        # Clear GPU cache at the start of each epoch
        clear_gpu_cache()
        print_gpu_memory()
        
        # Train
        train_loss, train_metrics = train_epoch(model, train_loader, criterion, optimizer, device, epoch, scaler)
        
        # Clear GPU cache after training
        clear_gpu_cache()
        
        # Validate
        val_loss, val_metrics, val_labels, val_predictions = validate_epoch(model, val_loader, criterion, device, epoch)
        
        # Clear GPU cache after validation
        clear_gpu_cache()
        
        # Update learning rate
        scheduler.step(val_loss)
        
        # Update history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_accuracy'].append(train_metrics['accuracy'])
        history['val_accuracy'].append(val_metrics['accuracy'])
        history['val_f1'].append(val_metrics['f1_score'])
        if 'auc' in val_metrics:
            history['val_auc'].append(val_metrics['auc'])
        
        epoch_time = time.time() - epoch_start_time
        
        # Log results
        logger.info(f"\nEpoch {epoch+1}/{args.epochs} - {epoch_time:.2f}s")
        logger.info(f"Train Loss: {train_loss:.4f} | Train Acc: {train_metrics['accuracy']:.4f}")
        logger.info(f"Val Loss: {val_loss:.4f} | Val Acc: {val_metrics['accuracy']:.4f}")
        logger.info(f"Val F1: {val_metrics['f1_score']:.4f} | Val Precision: {val_metrics['precision']:.4f}")
        logger.info(f"Val Recall: {val_metrics['recall']:.4f}")
        if 'auc' in val_metrics:
            logger.info(f"Val AUC: {val_metrics['auc']:.4f}")
        logger.info(f"Learning Rate: {optimizer.param_groups[0]['lr']:.2e}")
        print_gpu_memory()
        
        # Save best model
        if val_metrics['accuracy'] > best_val_accuracy:
            best_val_accuracy = val_metrics['accuracy']
            best_model_path = output_dir / 'best_model.pth'
            torch.save(model.state_dict(), best_model_path)
            logger.info(f"New best model saved! Accuracy: {best_val_accuracy:.4f}")
            
            # Save confusion matrix for best model
            cm_path = output_dir / f'confusion_matrix_epoch_{epoch+1}.png'
            plot_confusion_matrix(val_labels, val_predictions, cm_path)
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = output_dir / f'checkpoint_epoch_{epoch+1}.pth'
            save_checkpoint(model, optimizer, epoch, val_loss, val_metrics, checkpoint_path)
        
        # Save training history
        history_path = output_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
    
    # Final model save
    final_model_path = output_dir / 'deepfake_detector_finetuned.pth'
    torch.save(model.state_dict(), final_model_path)
    logger.info(f"Final model saved: {final_model_path}")
    
    # Plot training curves
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 3, 2)
    plt.plot(history['train_accuracy'], label='Train Accuracy')
    plt.plot(history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.subplot(1, 3, 3)
    plt.plot(history['val_f1'], label='Validation F1')
    if history['val_auc']:
        plt.plot(history['val_auc'], label='Validation AUC')
    plt.title('Validation Metrics')
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'training_curves.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("Training completed!")
    logger.info(f"Best validation accuracy: {best_val_accuracy:.4f}")
    logger.info(f"Outputs saved in: {output_dir}")

if __name__ == '__main__':
    main()
