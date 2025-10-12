# app/main.py (Final Corrected Version)
import os
import traceback
from typing import Dict
from fastapi import FastAPI, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import DetectionStatus, VideoUploadResponse

from app.services.deepfake_detector import detect_deepfake_in_frames  
from app.services.video_processor import extract_faces_from_video
from app.storage import delete_video_file, save_uploaded_video

# In-memory storage for detection results
DETECTION_RESULTS: Dict[str, Dict] = {}

# Initialize FastAPI app
app = FastAPI(
    title="Deepfake Detection API",
    description="API for uploading videos and detecting deepfakes.",
    version="1.0.0"
)

# Add CORS middleware
# Update CORS origins to include your Next.js app
origins = [
    "http://localhost:3000",      # Next.js default port
    "http://127.0.0.1:3000",     # Alternative localhost
    "http://localhost:3001",      # In case you're using port 3001
    "http://127.0.0.1:3001",
    "http://localhost",
    "http://localhost:8080", 
    "http://127.0.0.1:8000",
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_deepfake_detection_task(video_id: str, video_path: str):
    """Background task for deepfake detection"""
    print(f"Starting deepfake detection for video_id: {video_id}")
    
    DETECTION_RESULTS[video_id] = {
        "status": "processing", 
        "result": None, 
        "confidence": None, 
        "error": None
    }
    
    try:
        # Extract faces from video
        print(f"[{video_id}] Extracting faces...")
        faces = extract_faces_from_video(video_path)
        
        if not faces:
            DETECTION_RESULTS[video_id] = {
                "status": "completed",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "error": None
            }
            print(f"[{video_id}] No faces found in video.")
            return
        
        # Perform deepfake detection
        print(f"[{video_id}] Performing deepfake inference...")
        result_text, confidence_score = await detect_deepfake_in_frames(faces)
        
        DETECTION_RESULTS[video_id] = {
            "status": "completed",
            "result": result_text,
            "confidence": confidence_score,
            "error": None
        }
        
        print(f"[{video_id}] Detection completed. Result: {result_text}, Confidence: {confidence_score:.4f}")
        
    except Exception as e:
        error_msg = f"Detection failed for {video_id}: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        
        DETECTION_RESULTS[video_id] = {
            "status": "failed",
            "result": None,
            "confidence": None,
            "error": str(e)
        }
    
    finally:
        # Clean up uploaded video file
        if os.path.exists(video_path):
            delete_video_file(video_path)

@app.get("/health", summary="Health Check")
async def health_check():
    """Check if the API is running"""
    return {"status": "ok", "message": "Deepfake Detection API is healthy"}

@app.post("/upload-video", response_model=VideoUploadResponse, summary="Upload Video")
async def upload_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...)
):
    """Upload a video file for deepfake detection"""
    
    # Validate file type
    if not video_file.content_type or not video_file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a video file."
        )
    
    try:
        # Save uploaded video
        video_id, video_path = await save_uploaded_video(video_file)
        
        # Start background detection task
        background_tasks.add_task(run_deepfake_detection_task, video_id, video_path)
        
        return VideoUploadResponse(
            video_id=video_id,
            message=f"Video '{video_file.filename}' uploaded successfully. Detection started."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload video: {str(e)}"
        )

@app.get("/detection-status/{video_id}", response_model=DetectionStatus, summary="Get Detection Status")
async def get_detection_status(video_id: str):
    """Get the status and result of a deepfake detection task"""
    
    result = DETECTION_RESULTS.get(video_id)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Video ID not found."
        )
    
    return DetectionStatus(**result, video_id=video_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)