# app/main.py (UPDATED)
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import traceback # For better error logging

from app.models import VideoUploadResponse, DetectionStatus
from app.storage import save_uploaded_video, get_video_path, delete_video_file
from app.services.video_processor import extract_faces_from_video # New Import
from app.services.deepfake_detector import detect_deepfake_in_frames # New Import

# Placeholder for deepfake detection results (in-memory for this demo)
DETECTION_RESULTS: Dict[str, Dict] = {}

app = FastAPI(
    title="Deepfake Detection API",
    description="API for uploading videos and detecting deepfakes.",
    version="0.1.0"
)

# --- Background Deepfake Detection Task ---
async def run_deepfake_detection_task(video_id: str, video_path: str):
    """
    Processes the video for deepfake detection.
    """
    print(f"Starting deepfake detection for video_id: {video_id} from {video_path}")
    DETECTION_RESULTS[video_id] = {"status": "processing", "result": None, "confidence": None, "error": None}

    try:
        # Step 1: Extract and preprocess faces from the video
        print(f"[{video_id}] Extracting faces...")
        faces = extract_faces_from_video(video_path, frames_to_process=20, frame_interval=5) # Process up to 20 faces, every 5th frame
        print(f"[{video_id}] Extracted {len(faces)} faces.")

        if not faces:
            DETECTION_RESULTS[video_id]["status"] = "completed"
            DETECTION_RESULTS[video_id]["result"] = "No Faces Detected"
            DETECTION_RESULTS[video_id]["confidence"] = 0.0
            print(f"[{video_id}] No faces found in video.")
            return

        # Step 2: Perform deepfake inference on the extracted faces
        print(f"[{video_id}] Performing deepfake inference...")
        result_text, confidence_score = await detect_deepfake_in_frames(faces) # Await the mock inference
        print(f"[{video_id}] Inference completed. Result: {result_text}, Confidence: {confidence_score:.2f}")

        DETECTION_RESULTS[video_id]["status"] = "completed"
        DETECTION_RESULTS[video_id]["result"] = result_text
        DETECTION_RESULTS[video_id]["confidence"] = confidence_score

    except FileNotFoundError as e:
        error_msg = f"Required file not found: {e}"
        print(f"[{video_id}] Error: {error_msg}")
        DETECTION_RESULTS[video_id]["status"] = "failed"
        DETECTION_RESULTS[video_id]["error"] = error_msg
    except Exception as e:
        error_msg = f"Deepfake detection for {video_id} failed: {e}\n{traceback.format_exc()}"
        print(error_msg)
        DETECTION_RESULTS[video_id]["status"] = "failed"
        DETECTION_RESULTS[video_id]["error"] = str(e)
    finally:
        # Clean up the video file after processing (optional, depending on retention policy)
        if os.path.exists(video_path):
            delete_video_file(video_path)


# --- API Endpoints (remain largely the same) ---

@app.get("/health", summary="Health Check")
async def health_check():
    """
    Returns a simple success message to indicate the API is running.
    """
    return {"status": "ok", "message": "Deepfake Detection API is healthy"}

@app.post("/upload-video", response_model=VideoUploadResponse, summary="Upload Video for Deepfake Detection")
async def upload_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="Video file to analyze for deepfakes (max 500MB)")
):
    """
    Uploads a video file. The deepfake detection process will be initiated
    as a background task.
    """
    if not video_file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")

    try:
        video_id, video_path = await save_uploaded_video(video_file)
        background_tasks.add_task(run_deepfake_detection_task, video_id, video_path)

        return VideoUploadResponse(
            video_id=video_id,
            message=f"Video '{video_file.filename}' uploaded successfully. Detection started in background."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")

@app.get("/detection-status/{video_id}", response_model=DetectionStatus, summary="Get Deepfake Detection Status")
async def get_detection_status(video_id: str):
    """
    Retrieves the current status and results of a deepfake detection task
    for a given video ID.
    """
    result = DETECTION_RESULTS.get(video_id)
    if not result:
        raise HTTPException(status_code=404, detail="Video ID not found or detection not started.")

    return DetectionStatus(
        video_id=video_id,
        status=result["status"],
        result=result.get("result"),
        confidence=result.get("confidence"),
        error=result.get("error")
    )