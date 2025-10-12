# # prepare_dataset.py
# import os
# import cv2
# from mtcnn.mtcnn import MTCNN
# import tensorflow as tf  # <-- Add this import
# # --- Configuration ---
# # Path to the Celeb-DF-v2 dataset directory
# # DATASET_PATH = r"E:\AL FATTAH\ML AI DL\New folder\datasets\Celeb-DF-v2"
# # New Linux Path
# DATASET_PATH = "/mnt/e/AL FATTAH/ML AI DL/New folder/datasets/Celeb-DF-v2"
# # Path to the file that lists which videos are real/fake
# LIST_FILE_PATH = os.path.join(DATASET_PATH, "List_of_testing_videos.txt")
# # Directory where we will save the extracted face images
# OUTPUT_DIR = "processed_faces"

# # --- Add these two lines to check for the GPU ---
# print("Checking for GPU...")
# print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
# # --- Main Script ---

# def process_videos():
#     """
#     Reads the video list, extracts faces using MTCNN, and saves them
#     into organized 'train/real', 'train/fake', 'test/real', and 'test/fake' folders.
#     """
#     print("Starting dataset preparation...")
    
#     # Initialize the MTCNN face detector
#     detector = MTCNN()

#     # Create the main output directory
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
    
#     # Check if the list file exists
#     if not os.path.exists(LIST_FILE_PATH):
#         print(f"ERROR: List file not found at {LIST_FILE_PATH}")
#         return

#     # Read the list of videos and their labels
#     with open(LIST_FILE_PATH, 'r') as f:
#         lines = f.readlines()

#     print(f"Found {len(lines)} videos to process from the list file.")

#     # Process each video from the list
#     for i, line in enumerate(lines):
#         # The file format is: "label video_path" e.g., "1 Celeb-real/id0_0000.mp4"
#         parts = line.strip().split()
#         label = int(parts[0])
#         relative_video_path = parts[1]
        
#         video_path = os.path.join(DATASET_PATH, relative_video_path.replace('/', os.sep))
        
#         # Determine if this is a 'real' or 'fake' video
#         # In Celeb-DF, '1' is real, '0' is fake.
#         label_name = "real" if label == 1 else "fake"
        
#         # For simplicity, we'll put everything into a 'train' set.
#         # A more advanced setup would use the list to create train/validation/test splits.
#         output_subfolder = os.path.join(OUTPUT_DIR, "train", label_name)
#         os.makedirs(output_subfolder, exist_ok=True)

#         print(f"\nProcessing video {i+1}/{len(lines)}: {video_path}")
        
#         if not os.path.exists(video_path):
#             print(f"  > Warning: Video file not found, skipping.")
#             continue
            
#         cap = cv2.VideoCapture(video_path)
#         frame_number = 0
        
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
                
#             # Process every 15th frame to save time and get diverse faces
#             if frame_number % 30 == 0:  # instead of 15
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
#                 # Detect faces
#                 faces = detector.detect_faces(rgb_frame)
                
#                 for face_count, face_data in enumerate(faces):
#                     if face_data['confidence'] > 0.98:
#                         x, y, w, h = face_data['box']
#                         x, y = abs(x), abs(y)
                        
#                         face_img = frame[y:y+h, x:x+w]
                        
#                         if face_img.size > 0:
#                             # Construct a unique filename for each face
#                             video_name = os.path.splitext(os.path.basename(video_path))[0]
#                             save_path = os.path.join(output_subfolder, f"{video_name}_frame{frame_number}_face{face_count}.png")
#                             cv2.imwrite(save_path, face_img)
            
#             frame_number += 1
            
#         cap.release()
#         print(f"  > Finished processing video. Faces saved to '{output_subfolder}'")
        
#     print("\nDataset preparation complete!")

# if __name__ == "__main__":
#     process_videos()

# # prepare_dataset.py (Final Version - Uses PyTorch for GPU Face Detection)
# import os
# import cv2
# import torch
# from facenet_pytorch import MTCNN
# from tqdm import tqdm
# import numpy as np

# # --- 1. SETUP ---
# # Set the device to your GPU for face detection
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"Checking for GPU... Using device: {device}")

# # Initialize the MTCNN face detector and move it to the GPU
# # This will be much faster than the previous version.
# mtcnn = MTCNN(
#     keep_all=True,
#     device=device,
#     min_face_size=20,
#     thresholds=[0.6, 0.7, 0.7]
# )

# # --- 2. CONFIGURATION ---
# # Path to the main Celeb-DF-v2 dataset directory (using Linux path for WSL)
# DATASET_PATH = "/mnt/e/AL FATTAH/ML AI DL/New folder/datasets/Celeb-DF-v2"
# # Directory where we will save the extracted face images
# OUTPUT_DIR = "processed_faces"

# # --- 3. MAIN SCRIPT ---

# def process_videos_from_folder(video_folder_path, label_name, detector):
#     """
#     Processes all videos in a given folder, extracts faces using the PyTorch MTCNN, and saves them.
#     """
#     output_subfolder = os.path.join(OUTPUT_DIR, "train", label_name)
#     os.makedirs(output_subfolder, exist_ok=True)

#     videos = [v for v in os.listdir(video_folder_path) if v.endswith('.mp4')]
#     print(f"\nFound {len(videos)} videos in '{label_name}' folder. Starting processing...")

#     for video_name in tqdm(videos, desc=f"Processing {label_name} videos"):
#         video_path = os.path.join(video_folder_path, video_name)
        
#         cap = cv2.VideoCapture(video_path)
#         frame_number = 0
        
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
                
#             # Process every 15th frame
#             if frame_number % 15 == 0:
#                 # Convert BGR (OpenCV) to RGB for MTCNN
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
#                 try:
#                     # Detect faces using facenet-pytorch MTCNN
#                     boxes, _ = detector.detect(rgb_frame)
                    
#                     if boxes is not None:
#                         for i, box in enumerate(boxes):
#                             x1, y1, x2, y2 = [int(b) for b in box]
#                             # Ensure coordinates are valid
#                             x1, y1 = max(0, x1), max(0, y1)
                            
#                             face_img = frame[y1:y2, x1:x2]
                            
#                             if face_img.size > 0:
#                                 base_video_name = os.path.splitext(video_name)[0]
#                                 save_path = os.path.join(output_subfolder, f"{base_video_name}_frame{frame_number}_face{i}.png")
#                                 cv2.imwrite(save_path, face_img)
#                 except Exception as e:
#                     print(f"\nSkipping a frame in {video_name} due to an error: {e}")
            
#             frame_number += 1
            
#         cap.release()
        
# def run_preparation():
#     """Main function to run the full dataset preparation."""
#     print("Starting full dataset preparation with PyTorch...")

#     real_videos_path = os.path.join(DATASET_PATH, "Celeb-real")
#     fake_videos_path = os.path.join(DATASET_PATH, "Celeb-synthesis")

#     process_videos_from_folder(real_videos_path, "real", mtcnn)
#     process_videos_from_folder(fake_videos_path, "fake", mtcnn)

#     print("\nFull dataset preparation complete!")

# if __name__ == "__main__":
#     run_preparation()



# optimized_preprocess.py
# optimized_preprocess.py
import os
import cv2
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN
from tqdm import tqdm
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import albumentations as A
from pathlib import Path
import gc
import threading

# Configuration
DATASET_PATH = "/mnt/e/AL FATTAH/ML AI DL/New folder/datasets/Celeb-DF-v2"

OUTPUT_DIR = "processed_faces_optimized"
TARGET_SIZE = 224
MAX_FACES_PER_VIDEO = 15  # Increased slightly for better data diversity
FRAME_SKIP = 15  # Process every 15th frame for better coverage
CONFIDENCE_THRESHOLD = 0.90  # Lower threshold for better face detection


# GPU setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

print(torch.cuda.is_available())  # Should print True if GPU detected
print(torch.cuda.get_device_name(0))  # Should print your GPU name, e.g. "NVIDIA GeForce RTX 3050"

# Thread lock for MTCNN to avoid conflicts
mtcnn_lock = threading.Lock()

# Initialize MTCNN with optimized settings
mtcnn = MTCNN(
    keep_all=True,
    device=device,
    min_face_size=30,  # Smaller minimum face size
    thresholds=[0.6, 0.7, 0.7],  # Slightly relaxed thresholds
    post_process=False,
    image_size=TARGET_SIZE,
    margin=20  # Add margin around detected faces
)

def cleanup_gpu_memory():
    """Clean up GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def process_single_video(video_info):
    """Process a single video and extract faces"""
    video_path, label_name, video_idx, total_videos = video_info
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return f"Failed to open {video_path}"
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        face_count = 0
        video_name = Path(video_path).stem
        
        # Create output directory
        output_subfolder = Path(OUTPUT_DIR) / "train" / label_name
        output_subfolder.mkdir(parents=True, exist_ok=True)
        
        while cap.isOpened() and face_count < MAX_FACES_PER_VIDEO:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % FRAME_SKIP == 0:
                try:
                    # Resize frame for processing (maintain aspect ratio)
                    height, width = frame.shape[:2]
                    if width > 800:
                        scale = 800 / width
                        new_width = 800
                        new_height = int(height * scale)
                        frame_resized = cv2.resize(frame, (new_width, new_height))
                    else:
                        frame_resized = frame
                    
                    rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    # Thread-safe MTCNN detection
                    with mtcnn_lock:
                        boxes, probs = mtcnn.detect(rgb_frame)
                        cleanup_gpu_memory()  # Clean up after detection
                    
                    if boxes is not None and len(boxes) > 0:
                        for i, (box, prob) in enumerate(zip(boxes, probs)):
                            if prob > CONFIDENCE_THRESHOLD and face_count < MAX_FACES_PER_VIDEO:
                                x1, y1, x2, y2 = box.astype(int)
                                
                                # Add padding and ensure bounds
                                padding = 10
                                x1 = max(0, x1 - padding)
                                y1 = max(0, y1 - padding)
                                x2 = min(rgb_frame.shape[1], x2 + padding)
                                y2 = min(rgb_frame.shape[0], y2 + padding)
                                
                                # Check face size
                                face_width = x2 - x1
                                face_height = y2 - y1
                                
                                if face_width > 50 and face_height > 50:  # Minimum face size
                                    face_img = rgb_frame[y1:y2, x1:x2]
                                    
                                    # Resize to target size
                                    face_img_resized = cv2.resize(face_img, (TARGET_SIZE, TARGET_SIZE), 
                                                                 interpolation=cv2.INTER_LANCZOS4)
                                    
                                    # Convert back to BGR for saving
                                    face_bgr = cv2.cvtColor(face_img_resized, cv2.COLOR_RGB2BGR)
                                    
                                    # Use PNG format to match existing preprocessing
                                    save_path = output_subfolder / f"{video_name}_frame{frame_count}_face{i}.png"
                                    cv2.imwrite(str(save_path), face_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 6])
                                    face_count += 1
                                    
                except Exception as e:
                    print(f"Error processing frame {frame_count} in {video_name}: {str(e)}")
                    continue
            
            frame_count += 1
            
            # Progress update for long videos
            if frame_count % 1000 == 0:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"Processing {video_name}: {progress:.1f}% complete, {face_count} faces extracted")
        
        cap.release()
        return f"✓ {video_name}: {face_count} faces extracted from {frame_count} frames"
        
    except Exception as e:
        return f"✗ Error processing {video_path}: {str(e)}"

def get_video_files():
    """Get all video files from the dataset"""
    video_tasks = []
    dataset_path = Path(DATASET_PATH)
    
    # Real videos from Celeb-real directory
    celeb_real_path = dataset_path / "Celeb-real"
    if celeb_real_path.exists():
        real_videos = list(celeb_real_path.glob("*.mp4"))
        print(f"Found {len(real_videos)} real videos in Celeb-real")
        for i, video_path in enumerate(real_videos):
            video_tasks.append((str(video_path), "real", i, len(real_videos)))
    
    # Real videos from YouTube-real directory
    youtube_real_path = dataset_path / "YouTube-real"
    if youtube_real_path.exists():
        youtube_videos = list(youtube_real_path.glob("*.mp4"))
        print(f"Found {len(youtube_videos)} real videos in YouTube-real")
        for i, video_path in enumerate(youtube_videos):
            video_tasks.append((str(video_path), "real", i + len(real_videos), len(youtube_videos)))
    
    # Fake videos from Celeb-synthesis directory
    celeb_synthesis_path = dataset_path / "Celeb-synthesis"
    if celeb_synthesis_path.exists():
        fake_videos = list(celeb_synthesis_path.glob("*.mp4"))
        print(f"Found {len(fake_videos)} fake videos in Celeb-synthesis")
        
        # Calculate how many real videos we have total
        total_real = len(real_videos) + len(youtube_videos) if 'real_videos' in locals() and 'youtube_videos' in locals() else len(fake_videos)
        
        # Limit fake videos to maintain reasonable balance (1.5:1 fake to real ratio)
        max_fake_videos = min(len(fake_videos), int(total_real * 1.5))
        fake_videos = fake_videos[:max_fake_videos]
        print(f"Using {len(fake_videos)} fake videos for balanced training")
        
        for i, video_path in enumerate(fake_videos):
            video_tasks.append((str(video_path), "fake", i, len(fake_videos)))
    
    return video_tasks

def process_videos_parallel():
    """Process videos in parallel for faster preprocessing"""
    
    # Create output directories
    output_path = Path(OUTPUT_DIR)
    (output_path / "train" / "real").mkdir(parents=True, exist_ok=True)
    (output_path / "train" / "fake").mkdir(parents=True, exist_ok=True)
    
    # Get all video files
    video_tasks = get_video_files()
    
    if not video_tasks:
        print("No video files found! Please check the dataset path.")
        return
    
    print(f"\nProcessing {len(video_tasks)} videos...")
    print(f"Output directory: {output_path.absolute()}")
    print(f"Target image size: {TARGET_SIZE}x{TARGET_SIZE}")
    print(f"Frame skip: {FRAME_SKIP} (processing every {FRAME_SKIP}th frame)")
    print(f"Max faces per video: {MAX_FACES_PER_VIDEO}")
    
    # Process with limited workers to avoid memory issues
    max_workers = 2 if device.type == 'cuda' else 4
    
    successful_processes = 0
    failed_processes = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with tqdm(total=len(video_tasks), desc="Processing videos") as pbar:
            futures = {executor.submit(process_single_video, task): task for task in video_tasks}
            
            for future in futures:
                try:
                    result = future.result()
                    if "✓" in result:
                        successful_processes += 1
                    else:
                        failed_processes += 1
                        print(f"\n{result}")
                    pbar.set_postfix({
                        'Success': successful_processes,
                        'Failed': failed_processes
                    })
                except Exception as e:
                    failed_processes += 1
                    task = futures[future]
                    print(f"\nUnexpected error with {task[0]}: {str(e)}")
                
                pbar.update(1)
                
                # Periodic cleanup
                if (successful_processes + failed_processes) % 10 == 0:
                    cleanup_gpu_memory()
    
    # Final cleanup
    cleanup_gpu_memory()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PROCESSING COMPLETE!")
    print(f"{'='*60}")
    print(f"Successfully processed: {successful_processes}")
    print(f"Failed to process: {failed_processes}")
    print(f"Total videos: {len(video_tasks)}")
    
    # Count extracted faces
    real_faces = len(list((output_path / "train" / "real").glob("*.png")))
    fake_faces = len(list((output_path / "train" / "fake").glob("*.png")))
    
    print(f"\nExtracted faces:")
    print(f"Real faces: {real_faces}")
    print(f"Fake faces: {fake_faces}")
    print(f"Total faces: {real_faces + fake_faces}")
    
    if real_faces > 0 and fake_faces > 0:
        ratio = fake_faces / real_faces
        print(f"Fake to Real ratio: {ratio:.2f}:1")


if __name__ == "__main__":
    print("Starting optimized deepfake preprocessing...")
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Using device: {device}")
    
    # Check if dataset path exists
    if not Path(DATASET_PATH).exists():
        print(f"Error: Dataset path does not exist: {DATASET_PATH}")
        exit(1)
    
    process_videos_parallel()
    print("\nOptimized preprocessing complete!")
