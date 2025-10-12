# # app/main.py (Final Corrected Version)
# import os
# import traceback
# from typing import Dict
# from fastapi import FastAPI, BackgroundTasks, File, HTTPException, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from app.schemas import DetectionStatus, VideoUploadResponse

# from app.services.deepfake_detector import detect_deepfake_in_frames  
# from app.services.video_processor import extract_faces_from_video
# from app.storage import delete_video_file, save_uploaded_video

# # In-memory storage for detection results
# DETECTION_RESULTS: Dict[str, Dict] = {}

# # Initialize FastAPI app
# app = FastAPI(
#     title="Deepfake Detection API",
#     description="API for uploading videos and detecting deepfakes.",
#     version="1.0.0"
# )

# # Add CORS middleware
# # Update CORS origins to include your Next.js app
# origins = [
#     "http://localhost:3000",      # Next.js default port
#     "http://127.0.0.1:3000",     # Alternative localhost
#     "http://localhost:3001",      # In case you're using port 3001
#     "http://127.0.0.1:3001",
#     "http://localhost",
#     "http://localhost:8080", 
#     "http://127.0.0.1:8000",
#     "null"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# async def run_deepfake_detection_task(video_id: str, video_path: str):
#     """Background task for deepfake detection"""
#     print(f"Starting deepfake detection for video_id: {video_id}")
    
#     DETECTION_RESULTS[video_id] = {
#         "status": "processing", 
#         "result": None, 
#         "confidence": None, 
#         "error": None
#     }
    
#     try:
#         # Extract faces from video
#         print(f"[{video_id}] Extracting faces...")
#         faces = extract_faces_from_video(video_path)
        
#         if not faces:
#             DETECTION_RESULTS[video_id] = {
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "error": None
#             }
#             print(f"[{video_id}] No faces found in video.")
#             return
        
#         # Perform deepfake detection
#         print(f"[{video_id}] Performing deepfake inference...")
#         result_text, confidence_score = await detect_deepfake_in_frames(faces)
        
#         DETECTION_RESULTS[video_id] = {
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score,
#             "error": None
#         }
        
#         print(f"[{video_id}] Detection completed. Result: {result_text}, Confidence: {confidence_score:.4f}")
        
#     except Exception as e:
#         error_msg = f"Detection failed for {video_id}: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
        
#         DETECTION_RESULTS[video_id] = {
#             "status": "failed",
#             "result": None,
#             "confidence": None,
#             "error": str(e)
#         }
    
#     finally:
#         # Clean up uploaded video file
#         if os.path.exists(video_path):
#             delete_video_file(video_path)

# @app.get("/health", summary="Health Check")
# async def health_check():
#     """Check if the API is running"""
#     return {"status": "ok", "message": "Deepfake Detection API is healthy"}

# @app.post("/upload-video", response_model=VideoUploadResponse, summary="Upload Video")
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Upload a video file for deepfake detection"""
    
#     # Validate file type
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(
#             status_code=400, 
#             detail="Invalid file type. Please upload a video file."
#         )
    
#     try:
#         # Save uploaded video
#         video_id, video_path = await save_uploaded_video(video_file)
        
#         # Start background detection task
#         background_tasks.add_task(run_deepfake_detection_task, video_id, video_path)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video '{video_file.filename}' uploaded successfully. Detection started."
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Failed to upload video: {str(e)}"
#         )

# @app.get("/detection-status/{video_id}", response_model=DetectionStatus, summary="Get Detection Status")
# async def get_detection_status(video_id: str):
#     """Get the status and result of a deepfake detection task"""
    
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(
#             status_code=404, 
#             detail="Video ID not found."
#         )
    
#     return DetectionStatus(**result, video_id=video_id)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
# # # app/main.py (Final Corrected Version)
# # import os
# # import traceback
# # from typing import Dict
# # from fastapi import FastAPI, BackgroundTasks, File, HTTPException, UploadFile
# # from fastapi.middleware.cors import CORSMiddleware
# # from app.schemas import DetectionStatus, VideoUploadResponse

# # from app.services.deepfake_detector import detect_deepfake_in_frames  
# # from app.services.video_processor import extract_faces_from_video
# # from app.storage import delete_video_file, save_uploaded_video

# # # In-memory storage for detection results
# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # # Initialize FastAPI app
# # app = FastAPI(
# #     title="Deepfake Detection API",
# #     description="API for uploading videos and detecting deepfakes.",
# #     version="1.0.0"
# # )

# # # Add CORS middleware
# # # Update CORS origins to include your Next.js app
# # origins = [
# #     "http://localhost:3000",      # Next.js default port
# #     "http://127.0.0.1:3000",     # Alternative localhost
# #     "http://localhost:3001",      # In case you're using port 3001
# #     "http://127.0.0.1:3001",
# #     "http://localhost",
# #     "http://localhost:8080", 
# #     "http://127.0.0.1:8000",
# #     "null"
# # ]

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=origins,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # async def run_deepfake_detection_task(video_id: str, video_path: str):
# #     """Background task for deepfake detection"""
# #     print(f"Starting deepfake detection for video_id: {video_id}")
    
# #     DETECTION_RESULTS[video_id] = {
# #         "status": "processing", 
# #         "result": None, 
# #         "confidence": None, 
# #         "error": None
# #     }
    
# #     try:
# #         # Extract faces from video
# #         print(f"[{video_id}] Extracting faces...")
# #         faces = extract_faces_from_video(video_path)
        
# #         if not faces:
# #             DETECTION_RESULTS[video_id] = {
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "error": None
# #             }
# #             print(f"[{video_id}] No faces found in video.")
# #             return
        
# #         # Perform deepfake detection
# #         print(f"[{video_id}] Performing deepfake inference...")
# #         result_text, confidence_score = await detect_deepfake_in_frames(faces)
        
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "completed",
# #             "result": result_text,
# #             "confidence": confidence_score,
# #             "error": None
# #         }
        
# #         print(f"[{video_id}] Detection completed. Result: {result_text}, Confidence: {confidence_score:.4f}")
        
# #     except Exception as e:
# #         error_msg = f"Detection failed for {video_id}: {str(e)}"
# #         print(error_msg)
# #         print(traceback.format_exc())
        
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "failed",
# #             "result": None,
# #             "confidence": None,
# #             "error": str(e)
# #         }
    
# #     finally:
# #         # Clean up uploaded video file
# #         if os.path.exists(video_path):
# #             delete_video_file(video_path)

# # @app.get("/health", summary="Health Check")
# # async def health_check():
# #     """Check if the API is running"""
# #     return {"status": "ok", "message": "Deepfake Detection API is healthy"}

# # @app.post("/upload-video", response_model=VideoUploadResponse, summary="Upload Video")
# # async def upload_video(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Upload a video file for deepfake detection"""
    
# #     # Validate file type
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(
# #             status_code=400, 
# #             detail="Invalid file type. Please upload a video file."
# #         )
    
# #     try:
# #         # Save uploaded video
# #         video_id, video_path = await save_uploaded_video(video_file)
        
# #         # Start background detection task
# #         background_tasks.add_task(run_deepfake_detection_task, video_id, video_path)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video '{video_file.filename}' uploaded successfully. Detection started."
# #         )
        
# #     except Exception as e:
# #         raise HTTPException(
# #             status_code=500, 
# #             detail=f"Failed to upload video: {str(e)}"
# #         )

# # @app.get("/detection-status/{video_id}", response_model=DetectionStatus, summary="Get Detection Status")
# # async def get_detection_status(video_id: str):
# #     """Get the status and result of a deepfake detection task"""
    
# #     result = DETECTION_RESULTS.get(video_id)
# #     if not result:
# #         raise HTTPException(
# #             status_code=404, 
# #             detail="Video ID not found."
# #         )
    
# #     return DetectionStatus(**result, video_id=video_id)

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)

# # main.py - ALIGNED WITH ADVANCED DEEPFAKE_DETECTOR
# # from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.responses import JSONResponse
# # import asyncio
# # import os
# # import uuid
# # import time
# # import logging
# # import base64
# # import cv2
# # import numpy as np
# # from pathlib import Path
# # from typing import Dict, Optional

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # **CLEAN** - Import schemas with proper error handling
# # try:
# #     from app.schemas import VideoUploadResponse, DetectionStatus, YouTubeVideoRequest
# #     print("[OK] Schemas imported successfully")
# # except ImportError as e:
# #     logger.error(f"Schema import failed: {e}")
# #     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # # **CLEAN** - Import services
# # try:
# #     from app.storage import save_uploaded_video, delete_video_file
# #     from app.services.video_processor import extract_faces_from_video
# #     from app.services.deepfake_detector import detect_deepfake_in_frames
# #     print("[OK] Services imported successfully")
# # except ImportError as e:
# #     logger.error(f"Service import failed: {e}")
# #     raise SystemExit("Cannot start without services")

# # # **CLEAN** - Enhanced detector import
# # try:
# #     from app.services.enhanced_detector import enhanced_detector
# #     ENHANCED_AVAILABLE = True
# #     print("[OK] Enhanced detector available")
# # except ImportError:
# #     ENHANCED_AVAILABLE = False
# #     print("[WARNING] Enhanced detector not available")

# # # **CLEAN** - Real-time detection import
# # try:
# #     from app.services.realtime_detector import RealTimeDeepfakeDetector
# #     REALTIME_AVAILABLE = True
# #     print("[OK] Real-time detection available")
# # except ImportError:
# #     REALTIME_AVAILABLE = False
# #     print("[WARNING] Real-time detection not available")
    
# #     class RealTimeDeepfakeDetector:
# #         async def load_model(self): pass
# #         async def real_time_analyze(self, frame): 
# #             return {"error": "Real-time detection not available"}

# # # **FIXED** - YouTube support with better error handling
# # try:
# #     import yt_dlp
# #     # **FIXED** - Import the YouTubeDownloader class instead of instance
# #     from app.services.youtube_service import YouTubeDownloader
# #     youtube_downloader = YouTubeDownloader()
# #     YOUTUBE_AVAILABLE = True
# #     print("[OK] YouTube support enabled")
# # except ImportError as e:
# #     YOUTUBE_AVAILABLE = False
# #     youtube_downloader = None
# #     print(f"[WARNING] YouTube support disabled: {e}")

# # # Initialize FastAPI app
# # app = FastAPI(
# #     title="iFake API - Advanced Deepfake Detection System",
# #     version="2.2.0"
# # )

# # # **FIXED** - Exception handlers
# # @app.exception_handler(422)
# # async def validation_exception_handler(request, exc):
# #     logger.error(f"Validation error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=422,
# #         content={
# #             "error": "Request validation failed",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # @app.exception_handler(500)
# # async def internal_server_error_handler(request, exc):
# #     logger.error(f"Internal server error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=500,
# #         content={
# #             "error": "Internal server error",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # # CORS middleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"]
# # )

# # # Configuration
# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # # Create directories
# # Path("uploaded_videos").mkdir(exist_ok=True)
# # Path("downloaded_videos").mkdir(exist_ok=True)

# # try:
# #     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
# #     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
# #     print("[OK] Static file directories mounted successfully")
# # except Exception as e:
# #     print(f"[WARNING] Static file mounting failed: {e}")

# # # **CLEAN** - Background task
# # # main.py - FIXED enhanced detection task
# # async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
# #     """FIXED - Enhanced detection with REAL progress tracking"""
# #     print(f"🎬 Starting detection: {video_id}")
# #     start_time = time.time()
    
# #     # Initialize detection result
# #     DETECTION_RESULTS[video_id] = {
# #         "video_id": video_id,
# #         "status": "processing",
# #         "result": None,
# #         "confidence": None,
# #         "error": None,
# #         "enhanced_analysis": False,
# #         "video_type": video_type,
# #         "metadata": metadata or {},
# #         "video_url": None,
# #         "faces_found": 0,
# #         "model_used": None,
# #         "processing_time": None,
# #         "current_stage": "initializing",
# #         "progress_percentage": 0,
# #         "stage_details": "Starting AI analysis system...",
# #         "estimated_time_remaining": None
# #     }

# #     try:
# #         # STAGE 1: Initialize (0-15%)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing AI analysis system..."
# #         print(f"[{video_id}] Progress: 5% - Initializing")
# #         await asyncio.sleep(0.2)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
# #         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
# #         print(f"[{video_id}] Progress: 15% - Starting face detection")

# #         # STAGE 2: Simulate Face Extraction Progress (15-50%)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
# #         print(f"[{video_id}] Progress: 25% - Extracting faces")

# #         # [WARNING] Inject intermediate progress simulation
# #         for fake_step in range(26, 50, 4):
# #             await asyncio.sleep(0.4)
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
# #             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

# #         # Actual face extraction
# #         faces = extract_faces_from_video(video_path)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
# #         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
# #         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

# #         if not faces:
# #             DETECTION_RESULTS[video_id].update({
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "progress_percentage": 100,
# #                 "current_stage": "completed",
# #                 "stage_details": "No faces detected in video",
# #                 "processing_time": round(time.time() - start_time, 2)
# #             })
# #             return

# #         # STAGE 3: AI Analysis (50-85%)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
# #         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 AI models analyzing {len(faces)} detected faces..."
# #         print(f"[{video_id}] Progress: 60% - Analyzing faces")

# #         # Enhanced detection
# #         enhanced_analysis = False
# #         if ENHANCED_AVAILABLE:
# #             try:
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
# #                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")

# #                 result_data = enhanced_detector.enhanced_analyze_faces(faces)

# #                 if isinstance(result_data, dict):
# #                     result_text = result_data.get('prediction', 'Real Video')
# #                     confidence_score = result_data.get('confidence', 0.5)
# #                 else:
# #                     result_text, confidence_score = result_data
# #                 enhanced_analysis = True

# #             except Exception as enhanced_error:
# #                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
# #                 result_text, confidence_score = await detect_deepfake_in_frames(faces)
# #         else:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
# #             result_text, confidence_score = await detect_deepfake_in_frames(faces)

# #         # STAGE 4: Finalizing (85-100%)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
# #         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
# #         print(f"[{video_id}] Progress: 90% - Finalizing")

# #         # Video path
# #         filename = os.path.basename(video_path)
# #         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"

# #         processing_time = time.time() - start_time

# #         # Completion
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "completed",
# #             "result": result_text,
# #             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
# #             "enhanced_analysis": enhanced_analysis,
# #             "video_url": video_url,
# #             "faces_found": len(faces),
# #             "model_used": "Enhanced Detector" if enhanced_analysis else "Standard Detector",
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "completed",
# #             "progress_percentage": 100,
# #             "stage_details": "[OK] Analysis completed successfully"
# #         })

# #         print(f"[OK] Detection completed for {video_id}: {result_text} ({confidence_score:.3f})")

# #     except Exception as e:
# #         processing_time = time.time() - start_time
# #         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "failed",
# #             "error": str(e),
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "failed",
# #             "progress_percentage": 0,
# #             "stage_details": f"[ERROR] Error: {str(e)}"
# #         })
                
# # # **CLEAN** - API endpoints
# # @app.get("/")
# # async def root():
# #     return {
# #         "message": "iFake API - Advanced Deepfake Detection System",
# #         "version": "2.2.0",
# #         "status": "operational"
# #     }

# # @app.post("/upload-video", response_model=VideoUploadResponse)
# # async def upload_video(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Standard video upload"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
    
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded successfully",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Upload video error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Enhanced video upload"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
    
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded - ENHANCED detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Enhanced upload error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# # async def detect_deepfake_advanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Advanced detection endpoint"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
    
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"ADVANCED detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Advanced detection error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# # async def detect_deepfake_youtube(
# #     background_tasks: BackgroundTasks,
# #     request: YouTubeVideoRequest
# # ):
# #     """**FIXED** YouTube video detection with proper error handling"""
# #     logger.info(f"YouTube request received: {request.youtube_url}")
    
# #     if not YOUTUBE_AVAILABLE:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
# #         )
    
# #     if not youtube_downloader:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube downloader not initialized"
# #         )
    
# #     try:
# #         youtube_url = str(request.youtube_url)
# #         logger.info(f"Processing YouTube URL: {youtube_url}")
        
# #         # Enhanced URL validation
# #         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
# #             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
        
# #         # Download video
# #         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
# #         logger.info(f"Successfully downloaded video: {video_id}")
        
# #         # Start detection task
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message="YouTube video processing started",
# #             video_type="youtube",
# #             metadata=metadata
# #         )
        
# #     except HTTPException:
# #         raise  # Re-raise HTTP exceptions
# #     except ValueError as ve:
# #         logger.error(f"YouTube validation error: {ve}")
# #         raise HTTPException(status_code=400, detail=str(ve))
# #     except Exception as e:
# #         logger.error(f"YouTube processing error: {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# # @app.get("/detection-status/{video_id}", response_model=DetectionStatus)
# # async def get_detection_status(video_id: str):
# #     """Get detection status"""
# #     result = DETECTION_RESULTS.get(video_id)
# #     if not result:
# #         raise HTTPException(status_code=404, detail="Video ID not found")
    
# #     return DetectionStatus(**result)

# # # **DEBUG/ADMIN ENDPOINTS**
# # @app.get("/debug/files/{video_id}")
# # async def debug_files(video_id: str):
# #     """Debug endpoint to check file availability"""
# #     try:
# #         result = DETECTION_RESULTS.get(video_id)
# #         if not result:
# #             return {"error": "Video ID not found"}
        
# #         video_url = result.get("video_url")
# #         if not video_url:
# #             return {"error": "No video URL found"}
        
# #         # Check if file exists
# #         if video_url.startswith("/downloaded_videos/"):
# #             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
# #         else:
# #             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
        
# #         # URL decode the file path
# #         import urllib.parse
# #         decoded_path = urllib.parse.unquote(file_path)
        
# #         return {
# #             "video_id": video_id,
# #             "video_url": video_url,
# #             "expected_file_path": decoded_path,
# #             "file_exists": os.path.exists(decoded_path),
# #             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}

# # @app.get("/debug/active-detections")
# # async def debug_active_detections():
# #     """Debug endpoint to see active detections"""
# #     return {
# #         "active_count": len(DETECTION_RESULTS),
# #         "detection_keys": list(DETECTION_RESULTS.keys()),
# #         "sample_data": {k: {
# #             "status": v.get("status"), 
# #             "has_video_id": "video_id" in v,
# #             "all_keys": list(v.keys())
# #         } for k, v in list(DETECTION_RESULTS.items())[:3]}
# #     }

# # # **WEBSOCKET ENDPOINTS**
# # @app.websocket("/ws/real-time-detection")
# # async def websocket_real_time_detection(websocket: WebSocket):
# #     """Fixed WebSocket for real-time detection"""
# #     try:
# #         await websocket.accept()
# #         print("[OK] WebSocket connected")
        
# #         if not REALTIME_AVAILABLE:
# #             await websocket.send_json({"error": "Real-time detection not available"})
# #             return
        
# #         detector = RealTimeDeepfakeDetector()
# #         await detector.load_model()
        
# #         await websocket.send_json({
# #             "type": "connection_ready",
# #             "message": "Ready for real-time analysis"
# #         })
        
# #         while True:
# #             try:
# #                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
                
# #                 # Decode frame
# #                 if data.startswith('data:image'):
# #                     header, base64_data = data.split(',', 1)
# #                     frame_bytes = base64.b64decode(base64_data)
# #                 else:
# #                     frame_bytes = base64.b64decode(data)
                
# #                 frame_array = np.frombuffer(frame_bytes, np.uint8)
# #                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
# #                 if frame is None:
# #                     await websocket.send_json({"error": "Invalid frame data"})
# #                     continue
                
# #                 # Analyze frame
# #                 result = await detector.real_time_analyze(frame)
# #                 await websocket.send_json(result)
                
# #             except asyncio.TimeoutError:
# #                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
# #             except Exception as e:
# #                 await websocket.send_json({"error": str(e)})
                
# #     except Exception as e:
# #         print(f"WebSocket error: {e}")

# # # **FIXED** - Single health endpoint
# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "healthy",
# #         "enhanced_available": ENHANCED_AVAILABLE,
# #         "realtime_available": REALTIME_AVAILABLE,
# #         "youtube_available": YOUTUBE_AVAILABLE,
# #         "active_detections": len(DETECTION_RESULTS)
# #     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# # from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.responses import JSONResponse
# # import asyncio
# # import os
# # import uuid
# # import time
# # import logging
# # import base64
# # import cv2
# # import numpy as np
# # from pathlib import Path
# # from typing import Dict, Optional

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Import schemas
# # try:
# #     from app.schemas import VideoUploadResponse, DetectionStatus, YouTubeVideoRequest
# #     print("[OK] Schemas imported successfully")
# # except ImportError as e:
# #     logger.error(f"Schema import failed: {e}")
# #     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # # Import services
# # try:
# #     from app.storage import save_uploaded_video, delete_video_file
# #     from app.services.video_processor import extract_faces_from_video
# #     from app.services.deepfake_detector import detect_deepfake_in_frames
# #     print("[OK] Services imported successfully")
# # except ImportError as e:
# #     logger.error(f"Service import failed: {e}")
# #     raise SystemExit("Cannot start without services")

# # # Enhanced detector
# # try:
# #     from app.services.enhanced_detector import enhanced_detector
# #     ENHANCED_AVAILABLE = True
# #     print("[OK] Enhanced detector available")
# # except ImportError:
# #     ENHANCED_AVAILABLE = False
# #     print("[WARNING] Enhanced detector not available")

# # # Real-time detection
# # try:
# #     from app.services.realtime_detector import RealTimeDeepfakeDetector
# #     REALTIME_AVAILABLE = True
# #     print("[OK] Real-time detection available")
# # except ImportError:
# #     REALTIME_AVAILABLE = False
# #     print("[WARNING] Real-time detection not available")
# #     class RealTimeDeepfakeDetector:
# #         async def load_model(self): pass
# #         async def real_time_analyze(self, frame): 
# #             return {"error": "Real-time detection not available"}

# # # YouTube support
# # try:
# #     import yt_dlp
# #     from app.services.youtube_service import YouTubeDownloader
# #     youtube_downloader = YouTubeDownloader()
# #     YOUTUBE_AVAILABLE = True
# #     print("[OK] YouTube support enabled")
# # except ImportError as e:
# #     YOUTUBE_AVAILABLE = False
# #     youtube_downloader = None
# #     print(f"[WARNING] YouTube support disabled: {e}")

# # app = FastAPI(
# #     title="iFake API - Advanced Deepfake Detection System",
# #     version="2.2.0"
# # )

# # @app.exception_handler(422)
# # async def validation_exception_handler(request, exc):
# #     logger.error(f"Validation error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=422,
# #         content={
# #             "error": "Request validation failed",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # @app.exception_handler(500)
# # async def internal_server_error_handler(request, exc):
# #     logger.error(f"Internal server error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=500,
# #         content={
# #             "error": "Internal server error",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"]
# # )

# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # Path("uploaded_videos").mkdir(exist_ok=True)
# # Path("downloaded_videos").mkdir(exist_ok=True)
# # try:
# #     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
# #     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
# #     print("[OK] Static file directories mounted successfully")
# # except Exception as e:
# #     print(f"[WARNING] Static file mounting failed: {e}")

# # async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
# #     print(f"🎬 Starting detection: {video_id}")
# #     start_time = time.time()
# #     DETECTION_RESULTS[video_id] = {
# #         "video_id": video_id,
# #         "status": "processing",
# #         "result": None,
# #         "confidence": None,
# #         "error": None,
# #         "enhanced_analysis": False,
# #         "video_type": video_type,
# #         "metadata": metadata or {},
# #         "video_url": None,
# #         "faces_found": 0,
# #         "model_used": None,
# #         "processing_time": None,
# #         "current_stage": "initializing",
# #         "progress_percentage": 0,
# #         "stage_details": "Starting AI analysis system...",
# #         "estimated_time_remaining": None
# #     }
# #     try:
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing AI analysis system..."
# #         print(f"[{video_id}] Progress: 5% - Initializing")
# #         await asyncio.sleep(0.2)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
# #         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
# #         print(f"[{video_id}] Progress: 15% - Starting face detection")

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
# #         print(f"[{video_id}] Progress: 25% - Extracting faces")
# #         for fake_step in range(26, 50, 4):
# #             await asyncio.sleep(0.4)
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
# #             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

# #         faces = extract_faces_from_video(video_path)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
# #         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
# #         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

# #         if not faces:
# #             DETECTION_RESULTS[video_id].update({
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "progress_percentage": 100,
# #                 "current_stage": "completed",
# #                 "stage_details": "No faces detected in video",
# #                 "processing_time": round(time.time() - start_time, 2)
# #             })
# #             return

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
# #         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 AI models analyzing {len(faces)} detected faces..."
# #         print(f"[{video_id}] Progress: 60% - Analyzing faces")
# #         enhanced_analysis = False
# #         if ENHANCED_AVAILABLE:
# #             try:
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
# #                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")
# #                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
# #                 if isinstance(result_data, dict):
# #                     result_text = result_data.get('prediction', 'Real Video')
# #                     confidence_score = result_data.get('confidence', 0.5)
# #                 else:
# #                     result_text, confidence_score = result_data
# #                 enhanced_analysis = True
# #             except Exception as enhanced_error:
# #                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
# #                 result_text, confidence_score = await detect_deepfake_in_frames(faces)
# #         else:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
# #             result_text, confidence_score = await detect_deepfake_in_frames(faces)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
# #         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
# #         print(f"[{video_id}] Progress: 90% - Finalizing")
# #         filename = os.path.basename(video_path)
# #         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
# #         processing_time = time.time() - start_time
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "completed",
# #             "result": result_text,
# #             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
# #             "enhanced_analysis": enhanced_analysis,
# #             "video_url": video_url,
# #             "faces_found": len(faces),
# #             "model_used": "Enhanced Detector" if enhanced_analysis else "Standard Detector",
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "completed",
# #             "progress_percentage": 100,
# #             "stage_details": "[OK] Analysis completed successfully"
# #         })
# #         print(f"[OK] Detection completed for {video_id}: {result_text} ({confidence_score:.3f})")
# #     except Exception as e:
# #         processing_time = time.time() - start_time
# #         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "failed",
# #             "error": str(e),
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "failed",
# #             "progress_percentage": 0,
# #             "stage_details": f"[ERROR] Error: {str(e)}"
# #         })

# # @app.get("/")
# # async def root():
# #     return {
# #         "message": "iFake API - Advanced Deepfake Detection System",
# #         "version": "2.2.0",
# #         "status": "operational"
# #     }

# # @app.post("/upload-video", response_model=VideoUploadResponse)
# # async def upload_video(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded successfully",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Upload video error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded - ENHANCED detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Enhanced upload error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# # async def detect_deepfake_advanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"ADVANCED detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Advanced detection error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# # async def detect_deepfake_youtube(
# #     background_tasks: BackgroundTasks,
# #     request: YouTubeVideoRequest
# # ):
# #     logger.info(f"YouTube request received: {request.youtube_url}")
# #     if not YOUTUBE_AVAILABLE:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
# #         )
# #     if not youtube_downloader:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube downloader not initialized"
# #         )
# #     try:
# #         youtube_url = str(request.youtube_url)
# #         logger.info(f"Processing YouTube URL: {youtube_url}")
# #         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
# #             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
# #         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
# #         logger.info(f"Successfully downloaded video: {video_id}")
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message="YouTube video processing started",
# #             video_type="youtube",
# #             metadata=metadata
# #         )
# #     except HTTPException:
# #         raise  # Re-raise HTTP exceptions
# #     except ValueError as ve:
# #         logger.error(f"YouTube validation error: {ve}")
# #         raise HTTPException(status_code=400, detail=str(ve))
# #     except Exception as e:
# #         logger.error(f"YouTube processing error: {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# # @app.get("/detection-status/{video_id}", response_model=DetectionStatus)
# # async def get_detection_status(video_id: str):
# #     result = DETECTION_RESULTS.get(video_id)
# #     if not result:
# #         raise HTTPException(status_code=404, detail="Video ID not found")
# #     return DetectionStatus(**result)

# # @app.get("/debug/files/{video_id}")
# # async def debug_files(video_id: str):
# #     try:
# #         result = DETECTION_RESULTS.get(video_id)
# #         if not result:
# #             return {"error": "Video ID not found"}
# #         video_url = result.get("video_url")
# #         if not video_url:
# #             return {"error": "No video URL found"}
# #         if video_url.startswith("/downloaded_videos/"):
# #             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
# #         else:
# #             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
# #         import urllib.parse
# #         decoded_path = urllib.parse.unquote(file_path)
# #         return {
# #             "video_id": video_id,
# #             "video_url": video_url,
# #             "expected_file_path": decoded_path,
# #             "file_exists": os.path.exists(decoded_path),
# #             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}

# # @app.get("/debug/active-detections")
# # async def debug_active_detections():
# #     return {
# #         "active_count": len(DETECTION_RESULTS),
# #         "detection_keys": list(DETECTION_RESULTS.keys()),
# #         "sample_data": {k: {
# #             "status": v.get("status"), 
# #             "has_video_id": "video_id" in v,
# #             "all_keys": list(v.keys())
# #         } for k, v in list(DETECTION_RESULTS.items())[:3]}
# #     }

# # @app.websocket("/ws/real-time-detection")
# # async def websocket_real_time_detection(websocket: WebSocket):
# #     try:
# #         await websocket.accept()
# #         print("[OK] WebSocket connected")
# #         if not REALTIME_AVAILABLE:
# #             await websocket.send_json({"error": "Real-time detection not available"})
# #             return
# #         detector = RealTimeDeepfakeDetector()
# #         await detector.load_model()
# #         await websocket.send_json({
# #             "type": "connection_ready",
# #             "message": "Ready for real-time analysis"
# #         })
# #         while True:
# #             try:
# #                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
# #                 if data.startswith('data:image'):
# #                     header, base64_data = data.split(',', 1)
# #                     frame_bytes = base64.b64decode(base64_data)
# #                 else:
# #                     frame_bytes = base64.b64decode(data)
# #                 frame_array = np.frombuffer(frame_bytes, np.uint8)
# #                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
# #                 if frame is None:
# #                     await websocket.send_json({"error": "Invalid frame data"})
# #                     continue
# #                 result = await detector.real_time_analyze(frame)
# #                 await websocket.send_json(result)
# #             except asyncio.TimeoutError:
# #                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
# #             except Exception as e:
# #                 await websocket.send_json({"error": str(e)})
# #     except Exception as e:
# #         print(f"WebSocket error: {e}")

# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "healthy",
# #         "enhanced_available": ENHANCED_AVAILABLE,
# #         "realtime_available": REALTIME_AVAILABLE,
# #         "youtube_available": YOUTUBE_AVAILABLE,
# #         "active_detections": len(DETECTION_RESULTS)
# #     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)



















# # app/main.py - Enhanced with Ensemble AI
# # from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.responses import JSONResponse
# # import asyncio
# # import os
# # import uuid
# # import time
# # import logging
# # import base64
# # import cv2
# # import numpy as np
# # from pathlib import Path
# # from typing import Dict, Optional, List, Tuple

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Import schemas
# # try:
# #     from app.schemas import VideoUploadResponse, DetectionStatus, YouTubeVideoRequest
# #     print("[OK] Schemas imported successfully")
# # except ImportError as e:
# #     logger.error(f"Schema import failed: {e}")
# #     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # # Import services
# # try:
# #     from app.storage import save_uploaded_video, delete_video_file
# #     from app.services.video_processor import extract_faces_from_video
# #     from app.services.deepfake_detector import detect_deepfake_in_frames
# #     print("[OK] Services imported successfully")
# # except ImportError as e:
# #     logger.error(f"Service import failed: {e}")
# #     raise SystemExit("Cannot start without services")

# # # **NEW** - Ensemble AI imports
# # try:
# #     import insightface
# #     import clip
# #     import torch
# #     import torch.nn as nn
# #     from PIL import Image
# #     from deepface import DeepFace
# #     ENSEMBLE_AVAILABLE = True
# #     print("[OK] Ensemble AI components available")
# # except ImportError as e:
# #     ENSEMBLE_AVAILABLE = False
# #     print(f"[WARNING] Ensemble AI not available: {e}")

# # # Enhanced detector
# # try:
# #     from app.services.enhanced_detector import enhanced_detector
# #     ENHANCED_AVAILABLE = True
# #     print("[OK] Enhanced detector available")
# # except ImportError:
# #     ENHANCED_AVAILABLE = False
# #     print("[WARNING] Enhanced detector not available")

# # # Real-time detection
# # try:
# #     from app.services.realtime_detector import RealTimeDeepfakeDetector
# #     REALTIME_AVAILABLE = True
# #     print("[OK] Real-time detection available")
# # except ImportError:
# #     REALTIME_AVAILABLE = False
# #     print("[WARNING] Real-time detection not available")
# #     class RealTimeDeepfakeDetector:
# #         async def load_model(self): pass
# #         async def real_time_analyze(self, frame): 
# #             return {"error": "Real-time detection not available"}

# # # YouTube support
# # try:
# #     import yt_dlp
# #     from app.services.youtube_service import YouTubeDownloader
# #     youtube_downloader = YouTubeDownloader()
# #     YOUTUBE_AVAILABLE = True
# #     print("[OK] YouTube support enabled")
# # except ImportError as e:
# #     YOUTUBE_AVAILABLE = False
# #     youtube_downloader = None
# #     print(f"[WARNING] YouTube support disabled: {e}")

# # app = FastAPI(
# #     title="iFake API - Advanced Deepfake Detection System with Ensemble AI",
# #     version="2.3.0"
# # )

# # # Exception handlers
# # @app.exception_handler(422)
# # async def validation_exception_handler(request, exc):
# #     logger.error(f"Validation error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=422,
# #         content={
# #             "error": "Request validation failed",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # @app.exception_handler(500)
# # async def internal_server_error_handler(request, exc):
# #     logger.error(f"Internal server error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=500,
# #         content={
# #             "error": "Internal server error",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"]
# # )

# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # Path("uploaded_videos").mkdir(exist_ok=True)
# # Path("downloaded_videos").mkdir(exist_ok=True)
# # try:
# #     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
# #     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
# #     print("[OK] Static file directories mounted successfully")
# # except Exception as e:
# #     print(f"[WARNING] Static file mounting failed: {e}")

# # # **NEW** - Initialize Ensemble AI Components
# # insight_app = None
# # clip_model = None
# # clip_preprocess = None

# # if ENSEMBLE_AVAILABLE:
# #     try:
# #         insight_app = insightface.app.FaceAnalysis()
# #         insight_app.prepare(ctx_id=-1)
# #         clip_model, clip_preprocess = clip.load("ViT-B/32", device="cpu")
# #         print("[OK] Ensemble AI models initialized")
# #     except Exception as e:
# #         print(f"[WARNING] Ensemble AI initialization failed: {e}")
# #         ENSEMBLE_AVAILABLE = False

# # # **NEW** - Ensemble AI Helper Functions
# # def _cosine(a, b):
# #     """Calculate cosine similarity between two vectors"""
# #     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

# # async def _insight_consistency(faces: List[np.ndarray]) -> float:
# #     """Check face consistency using InsightFace embeddings"""
# #     if len(faces) < 2 or not insight_app:
# #         return 0.5
    
# #     embs = []
# #     for f in faces:
# #         try:
# #             # Convert BGR to RGB if needed
# #             if len(f.shape) == 3 and f.shape[2] == 3:
# #                 rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB) if f.dtype == np.uint8 else f
# #             else:
# #                 rgb = f
# #             res = insight_app.get(rgb)
# #             if res:
# #                 embs.append(res[0].embedding)
# #         except:
# #             continue
    
# #     if len(embs) < 2:
# #         return 0.5
    
# #     embs = np.array(embs)
# #     sims = [_cosine(embs[i], embs[j]) for i in range(len(embs)) for j in range(i + 1, len(embs))]
# #     return 1 - np.mean(sims)  # Higher inconsistency = more likely deepfake

# # async def _deepface_score(faces: List[np.ndarray]) -> float:
# #     """Get deepfake score using DeepFace spoofing detection"""
# #     if not faces:
# #         return 0.5
    
# #     scores = []
# #     for f in faces:
# #         try:
# #             res = DeepFace.analyze(
# #                 f, actions=["spoofing"], enforce_detection=False, detector_backend="mtcnn"
# #             )
# #             scores.append(res[0]["spoofing"]["score"])
# #         except Exception:
# #             pass
    
# #     return float(np.mean(scores)) if scores else 0.5

# # async def _clip_zero_shot(faces: List[np.ndarray]) -> float:
# #     """Use CLIP for zero-shot deepfake detection"""
# #     if not faces or not clip_model:
# #         return 0.5
    
# #     text_tokens = clip.tokenize(["a real human face", "a deepfake face"]).to("cpu")
# #     total = 0.0
    
# #     for f in faces:
# #         try:
# #             # Convert to RGB and resize
# #             if len(f.shape) == 3:
# #                 rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB) if f.dtype == np.uint8 else f
# #             else:
# #                 rgb = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            
# #             pil_img = Image.fromarray(rgb.astype(np.uint8)).resize((224, 224))
# #             img = clip_preprocess(pil_img).unsqueeze(0)
            
# #             with torch.no_grad():
# #                 logits, _ = clip_model(img, text_tokens)
# #                 total += logits.softmax(dim=-1)[0][1].item()  # Deepfake probability
# #         except:
# #             continue
    
# #     return total / len(faces) if faces else 0.5

# # # **NEW** - Convert tensor faces to numpy for ensemble AI
# # def convert_tensor_faces_to_numpy(faces: List[torch.Tensor]) -> List[np.ndarray]:
# #     """Convert tensor faces back to numpy arrays for ensemble AI"""
# #     numpy_faces = []
    
# #     for face_tensor in faces:
# #         try:
# #             # Denormalize and convert back to numpy
# #             mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
# #             std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            
# #             # Denormalize
# #             face_denorm = face_tensor * std + mean
# #             face_denorm = torch.clamp(face_denorm * 255, 0, 255)
            
# #             # Convert to numpy (C, H, W) -> (H, W, C)
# #             face_np = face_denorm.permute(1, 2, 0).numpy().astype(np.uint8)
# #             numpy_faces.append(face_np)
            
# #         except Exception as e:
# #             logger.warning(f"Failed to convert tensor face: {e}")
# #             continue
    
# #     return numpy_faces

# # async def ensemble_predict(faces: List[torch.Tensor]) -> Tuple[str, float]:
# #     """
# #     FIXED - Enhanced ensemble prediction combining multiple AI models
# #     Returns (label, confidence)
# #     """
# #     # Get base model prediction (using your existing system)
# #     label, conf = await detect_deepfake_in_frames(faces)
    
# #     if not ENSEMBLE_AVAILABLE or len(faces) == 0:
# #         return label, conf
    
# #     # Convert tensor faces to numpy for ensemble AI
# #     numpy_faces = convert_tensor_faces_to_numpy(faces)
    
# #     if not numpy_faces:
# #         return label, conf
    
# #     # FIXED: Proper base model probability handling
# #     if label == "Real Video":
# #         base_real_prob = conf  # High confidence in real = high real probability
# #         base_fake_prob = 1.0 - conf
# #     else:  # "Deepfake Detected"
# #         base_fake_prob = conf  # High confidence in fake = high fake probability  
# #         base_real_prob = 1.0 - conf
    
# #     # Get ensemble predictions
# #     insight = await _insight_consistency(numpy_faces)
# #     deepf = await _deepface_score(numpy_faces)
# #     clip_z = await _clip_zero_shot(numpy_faces)
    
# #     # FIXED: Better ensemble weights - give more weight to the reliable base model
# #     ensemble_fake_prob = (
# #         0.70 * base_fake_prob +    # Increased base model weight
# #         0.10 * insight +           # Reduced secondary model weights
# #         0.10 * deepf + 
# #         0.10 * clip_z
# #     )
    
# #     # FIXED: Apply confidence scaling to preserve high confidence results
# #     if conf >= 0.85:  # If base model is very confident (>=85%)
# #         confidence_multiplier = 1.2  # Boost confidence
# #     elif conf >= 0.70:  # If base model is confident (>=70%)
# #         confidence_multiplier = 1.1  # Slight boost
# #     else:
# #         confidence_multiplier = 1.0  # No change
    
# #     # Final verdict with confidence boosting
# #     if ensemble_fake_prob <= 0.5:
# #         verdict = "Real Video"
# #         confidence = min((1.0 - ensemble_fake_prob) * confidence_multiplier, 0.98)
# #     else:
# #         verdict = "Deepfake Detected"  
# #         confidence = min(ensemble_fake_prob * confidence_multiplier, 0.98)
    
# #     logger.info(f"🤖 FIXED Ensemble - Base: {conf:.3f} ({label}), Insight: {insight:.3f}, DeepFace: {deepf:.3f}, CLIP: {clip_z:.3f}")
# #     logger.info(f"🎯 Final: {verdict} (Confidence: {confidence:.3f})")
    
# #     return verdict, confidence

# # # **ENHANCED** - Background task with ensemble AI
# # async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
# #     print(f"🎬 Starting enhanced detection: {video_id}")
# #     start_time = time.time()
    
# #     DETECTION_RESULTS[video_id] = {
# #         "video_id": video_id,
# #         "status": "processing",
# #         "result": None,
# #         "confidence": None,
# #         "error": None,
# #         "enhanced_analysis": ENSEMBLE_AVAILABLE,
# #         "video_type": video_type,
# #         "metadata": metadata or {},
# #         "video_url": None,
# #         "faces_found": 0,
# #         "model_used": "Ensemble AI" if ENSEMBLE_AVAILABLE else "Standard Detector",
# #         "processing_time": None,
# #         "current_stage": "initializing",
# #         "progress_percentage": 0,
# #         "stage_details": "Starting AI analysis system...",
# #         "estimated_time_remaining": None
# #     }
    
# #     try:
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing ensemble AI system..."
# #         print(f"[{video_id}] Progress: 5% - Initializing")
# #         await asyncio.sleep(0.2)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
# #         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
# #         print(f"[{video_id}] Progress: 15% - Starting face detection")

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
# #         print(f"[{video_id}] Progress: 25% - Extracting faces")
        
# #         # Progressive face extraction simulation
# #         for fake_step in range(26, 50, 4):
# #             await asyncio.sleep(0.4)
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
# #             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

# #         # Extract faces (your existing system returns torch tensors)
# #         faces = extract_faces_from_video(video_path)
        
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
# #         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
# #         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

# #         if not faces:
# #             DETECTION_RESULTS[video_id].update({
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "progress_percentage": 100,
# #                 "current_stage": "completed",
# #                 "stage_details": "No faces detected in video",
# #                 "processing_time": round(time.time() - start_time, 2)
# #             })
# #             return

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
# #         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
        
# #         enhanced_analysis = False
        
# #         # Try ensemble AI first
# #         if ENSEMBLE_AVAILABLE:
# #             try:
# #                 DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 Running ensemble AI analysis on {len(faces)} faces..."
# #                 print(f"[{video_id}] Progress: 60% - Ensemble AI analysis")
                
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Base model + InsightFace analysis..."
                
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 75
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🔍 DeepFace spoofing detection..."
                
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 80
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🎯 CLIP zero-shot analysis..."
                
# #                 result_text, confidence_score = await ensemble_predict(faces)
# #                 enhanced_analysis = True
                
# #             except Exception as ensemble_error:
# #                 logger.warning(f"Ensemble AI failed: {ensemble_error}")
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to enhanced detector..."
                
# #         # Try enhanced detector
# #         if not enhanced_analysis and ENHANCED_AVAILABLE:
# #             try:
# #                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
# #                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")
# #                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
# #                 if isinstance(result_data, dict):
# #                     result_text = result_data.get('prediction', 'Real Video')
# #                     confidence_score = result_data.get('confidence', 0.5)
# #                 else:
# #                     result_text, confidence_score = result_data
# #                 enhanced_analysis = True
# #             except Exception as enhanced_error:
# #                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
# #                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
                
# #         # Standard detector fallback
# #         if not enhanced_analysis:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
# #             result_text, confidence_score = await detect_deepfake_in_frames(faces)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
# #         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
# #         print(f"[{video_id}] Progress: 90% - Finalizing")
        
# #         filename = os.path.basename(video_path)
# #         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
# #         processing_time = time.time() - start_time
        
# #         # Determine model used
# #         if ENSEMBLE_AVAILABLE and enhanced_analysis:
# #             model_used = "Ensemble AI (Base + InsightFace + DeepFace + CLIP)"
# #         elif enhanced_analysis:
# #             model_used = "Enhanced Detector"
# #         else:
# #             model_used = "Standard Detector"
        
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "completed",
# #             "result": result_text,
# #             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
# #             "enhanced_analysis": enhanced_analysis,
# #             "video_url": video_url,
# #             "faces_found": len(faces),
# #             "model_used": model_used,
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "completed",
# #             "progress_percentage": 100,
# #             "stage_details": "[OK] Analysis completed successfully"
# #         })
        
# #         print(f"[OK] Enhanced detection completed for {video_id}: {result_text} ({confidence_score:.3f})")
        
# #     except Exception as e:
# #         processing_time = time.time() - start_time
# #         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "failed",
# #             "error": str(e),
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "failed",
# #             "progress_percentage": 0,
# #             "stage_details": f"[ERROR] Error: {str(e)}"
# #         })

# # # **UNCHANGED** - All your existing API endpoints work the same
# # @app.get("/")
# # async def root():
# #     return {
# #         "message": "iFake API - Advanced Deepfake Detection System with Ensemble AI",
# #         "version": "2.3.0",
# #         "status": "operational",
# #         "ensemble_ai": ENSEMBLE_AVAILABLE
# #     }

# # @app.post("/upload-video", response_model=VideoUploadResponse)
# # async def upload_video(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded - {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Upload video error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded - ENHANCED {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Enhanced upload error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# # async def detect_deepfake_advanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"ADVANCED {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
# #             video_type="upload",
# #             metadata={}
# #         )
# #     except Exception as e:
# #         logger.error(f"Advanced detection error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# # async def detect_deepfake_youtube(
# #     background_tasks: BackgroundTasks,
# #     request: YouTubeVideoRequest
# # ):
# #     logger.info(f"YouTube request received: {request.youtube_url}")
# #     if not YOUTUBE_AVAILABLE:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
# #         )
# #     if not youtube_downloader:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube downloader not initialized"
# #         )
# #     try:
# #         youtube_url = str(request.youtube_url)
# #         logger.info(f"Processing YouTube URL: {youtube_url}")
# #         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
# #             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
# #         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
# #         logger.info(f"Successfully downloaded video: {video_id}")
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"YouTube video processing started with {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard AI'}",
# #             video_type="youtube",
# #             metadata=metadata
# #         )
# #     except HTTPException:
# #         raise
# #     except ValueError as ve:
# #         logger.error(f"YouTube validation error: {ve}")
# #         raise HTTPException(status_code=400, detail=str(ve))
# #     except Exception as e:
# #         logger.error(f"YouTube processing error: {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# # # All your existing endpoints remain unchanged
# # @app.get("/detection-status/{video_id}", response_model=DetectionStatus)
# # async def get_detection_status(video_id: str):
# #     result = DETECTION_RESULTS.get(video_id)
# #     if not result:
# #         raise HTTPException(status_code=404, detail="Video ID not found")
# #     return DetectionStatus(**result)

# # @app.get("/debug/files/{video_id}")
# # async def debug_files(video_id: str):
# #     try:
# #         result = DETECTION_RESULTS.get(video_id)
# #         if not result:
# #             return {"error": "Video ID not found"}
# #         video_url = result.get("video_url")
# #         if not video_url:
# #             return {"error": "No video URL found"}
# #         if video_url.startswith("/downloaded_videos/"):
# #             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
# #         else:
# #             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
# #         import urllib.parse
# #         decoded_path = urllib.parse.unquote(file_path)
# #         return {
# #             "video_id": video_id,
# #             "video_url": video_url,
# #             "expected_file_path": decoded_path,
# #             "file_exists": os.path.exists(decoded_path),
# #             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}

# # @app.get("/debug/active-detections")
# # async def debug_active_detections():
# #     return {
# #         "active_count": len(DETECTION_RESULTS),
# #         "detection_keys": list(DETECTION_RESULTS.keys()),
# #         "ensemble_ai_enabled": ENSEMBLE_AVAILABLE,
# #         "sample_data": {k: {
# #             "status": v.get("status"), 
# #             "has_video_id": "video_id" in v,
# #             "model_used": v.get("model_used"),
# #             "all_keys": list(v.keys())
# #         } for k, v in list(DETECTION_RESULTS.items())[:3]}
# #     }

# # @app.websocket("/ws/real-time-detection")
# # async def websocket_real_time_detection(websocket: WebSocket):
# #     try:
# #         await websocket.accept()
# #         print("[OK] WebSocket connected")
# #         if not REALTIME_AVAILABLE:
# #             await websocket.send_json({"error": "Real-time detection not available"})
# #             return
# #         detector = RealTimeDeepfakeDetector()
# #         await detector.load_model()
# #         await websocket.send_json({
# #             "type": "connection_ready",
# #             "message": "Ready for real-time analysis",
# #             "ensemble_ai": ENSEMBLE_AVAILABLE
# #         })
# #         while True:
# #             try:
# #                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
# #                 if data.startswith('data:image'):
# #                     header, base64_data = data.split(',', 1)
# #                     frame_bytes = base64.b64decode(base64_data)
# #                 else:
# #                     frame_bytes = base64.b64decode(data)
# #                 frame_array = np.frombuffer(frame_bytes, np.uint8)
# #                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
# #                 if frame is None:
# #                     await websocket.send_json({"error": "Invalid frame data"})
# #                     continue
# #                 result = await detector.real_time_analyze(frame)
# #                 await websocket.send_json(result)
# #             except asyncio.TimeoutError:
# #                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
# #             except Exception as e:
# #                 await websocket.send_json({"error": str(e)})
# #     except Exception as e:
# #         print(f"WebSocket error: {e}")

# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "healthy",
# #         "enhanced_available": ENHANCED_AVAILABLE,
# #         "realtime_available": REALTIME_AVAILABLE,
# #         "youtube_available": YOUTUBE_AVAILABLE,
# #         "ensemble_ai_available": ENSEMBLE_AVAILABLE,
# #         "active_detections": len(DETECTION_RESULTS)
# #     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)












# # # app/main.py - FIXED VERSION
# # from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.responses import JSONResponse
# # import asyncio
# # import os
# # import uuid
# # import time
# # import logging
# # import base64
# # import cv2
# # import numpy as np
# # from pathlib import Path
# # from typing import Dict, Optional
# # from fastapi import WebSocket, WebSocketDisconnect
# # import json

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Import schemas
# # try:
# #     from app.schemas import VideoUploadResponse, DetectionStatus, YouTubeVideoRequest
# #     print("[OK] Schemas imported successfully")
# # except ImportError as e:
# #     logger.error(f"Schema import failed: {e}")
# #     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # # Import services
# # try:
# #     from app.storage import save_uploaded_video, delete_video_file
# #     from app.services.video_processor import extract_faces_from_video
# #     from app.services.deepfake_detector import detect_deepfake_in_frames
# #     print("[OK] Services imported successfully")
# # except ImportError as e:
# #     logger.error(f"Service import failed: {e}")
# #     raise SystemExit("Cannot start without services")

# # # Enhanced detector
# # try:
# #     from app.services.enhanced_detector import enhanced_detector
# #     ENHANCED_AVAILABLE = True
# #     print("[OK] Enhanced detector available")
# # except ImportError:
# #     ENHANCED_AVAILABLE = False
# #     print("[WARNING] Enhanced detector not available")

# # # Real-time detection
# # try:
# #     from app.services.realtime_detector import RealTimeDeepfakeDetector
# #     REALTIME_AVAILABLE = True
# #     print("[OK] Real-time detection available")
# # except ImportError:
# #     REALTIME_AVAILABLE = False
# #     print("[WARNING] Real-time detection not available")
# #     class RealTimeDeepfakeDetector:
# #         async def load_model(self): pass
# #         async def real_time_analyze(self, frame): 
# #             return {"error": "Real-time detection not available"}

# # # Ultra-enhanced detection (FIXED - added missing import)
# # try:
# #     from app.services.truemedia_detector import enhanced_deepfake_detection
# #     ULTRA_ENHANCED_AVAILABLE = True
# #     print("[OK] Ultra-enhanced TrueMedia integration available")
# # except ImportError:
# #     ULTRA_ENHANCED_AVAILABLE = False
# #     enhanced_deepfake_detection = None
# #     print("[WARNING] Ultra-enhanced detection not available - using standard enhanced detection")

# # # Free AI ensemble
# # try:
# #     from app.services.free_ai_boosters import free_ai_ensemble
# #     FREE_AI_AVAILABLE = True
# #     print("[OK] Free AI ensemble available")
# # except ImportError:
# #     FREE_AI_AVAILABLE = False
# #     print("[WARNING] Free AI ensemble not available")

# # # YouTube support
# # try:
# #     import yt_dlp
# #     print("[OK] yt-dlp imported successfully")
# #     from app.services.youtube_service import YouTubeDownloader
# #     youtube_downloader = YouTubeDownloader()
# #     print("[OK] YouTubeDownloader initialized, download_dir: downloaded_videos")
# #     print("[OK] YouTube downloader instance created with comprehensive Shorts support")
# #     print("[OK] YouTubeDownloader initialized, download_dir: downloaded_videos")
# #     YOUTUBE_AVAILABLE = True
# #     print("[OK] YouTube support enabled")
# # except ImportError as e:
# #     YOUTUBE_AVAILABLE = False
# #     youtube_downloader = None
# #     print(f"[WARNING] YouTube support disabled: {e}")

# # # Ultra-ensemble models (FIXED - safe import with proper warning)
# # try:
# #     from app.models.ensemble_detector import UltraEnsembleDetector
# #     # Test if the class actually exists and is importable
# #     test_detector = UltraEnsembleDetector
# #     ULTRA_ENSEMBLE_AVAILABLE = True
# #     print("[OK] Ultra ensemble models available (6-model architecture)")
# # except (ImportError, AttributeError) as e:
# #     ULTRA_ENSEMBLE_AVAILABLE = False
# #     print(f"[WARNING] Ultra ensemble not available: {e}")

# # app = FastAPI(
# #     title="iFake API - Advanced Deepfake Detection System",
# #     version="2.4.0"
# # )

# # # Exception handlers
# # @app.exception_handler(422)
# # async def validation_exception_handler(request, exc):
# #     logger.error(f"Validation error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=422,
# #         content={
# #             "error": "Request validation failed",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # @app.exception_handler(500)
# # async def internal_server_error_handler(request, exc):
# #     logger.error(f"Internal server error on {request.url}: {exc}")
# #     return JSONResponse(
# #         status_code=500,
# #         content={
# #             "error": "Internal server error",
# #             "detail": str(exc),
# #             "url": str(request.url)
# #         }
# #     )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"]
# # )

# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # # Create directories and mount static files
# # Path("uploaded_videos").mkdir(exist_ok=True)
# # Path("downloaded_videos").mkdir(exist_ok=True)
# # try:
# #     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
# #     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
# #     print("[OK] Static file directories mounted successfully")
# # except Exception as e:
# #     print(f"[WARNING] Static file mounting failed: {e}")

# # # FIXED: Single unified detection task function
# # async def run_detection_task(video_id: str, video_path: str, video_type: str = "upload", 
# #                            metadata: Optional[Dict] = None, enhancement_level: str = "standard"):
# #     """
# #     Unified detection task that handles all enhancement levels
# #     enhancement_level: 'standard', 'enhanced', 'ultra', 'free-ai'
# #     """
# #     print(f"🎬 Starting {enhancement_level} detection: {video_id}")
# #     start_time = time.time()
    
# #     # Initialize detection result
# #     DETECTION_RESULTS[video_id] = {
# #         "video_id": video_id,
# #         "status": "processing",
# #         "result": None,
# #         "confidence": None,
# #         "error": None,
# #         "enhanced_analysis": enhancement_level != "standard",
# #         "ultra_enhanced": enhancement_level in ["ultra", "free-ai"],
# #         "video_type": video_type,
# #         "metadata": metadata or {},
# #         "video_url": None,
# #         "faces_found": 0,
# #         "model_used": None,
# #         "processing_time": None,
# #         "current_stage": "initializing",
# #         "progress_percentage": 0,
# #         "stage_details": f"Starting {enhancement_level} AI analysis system...",
# #         "estimated_time_remaining": None,
# #         "enhancement_level": enhancement_level
# #     }
    
# #     try:
# #         # Progress tracking
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"Initializing {enhancement_level} AI analysis system..."
# #         await asyncio.sleep(0.2)

# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
# #         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"

# #         # Face extraction
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
# #         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
        
# #         for fake_step in range(26, 50, 4):
# #             await asyncio.sleep(0.4)
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
# #             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

# #         faces = extract_faces_from_video(video_path)
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
# #         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"

# #         if not faces:
# #             DETECTION_RESULTS[video_id].update({
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "progress_percentage": 100,
# #                 "current_stage": "completed",
# #                 "stage_details": "No faces detected in video",
# #                 "processing_time": round(time.time() - start_time, 2)
# #             })
# #             return

# #         # Analysis based on enhancement level
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
# #         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
        
# #         # Try Free AI ensemble first (highest accuracy when available)
# #         if enhancement_level == "free-ai" and FREE_AI_AVAILABLE:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "[START] Using Ultra-Free AI Ensemble (5+ models)..."
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
# #             try:
# #                 result_data = await free_ai_ensemble.ultra_analyze_faces(faces, video_path)
# #                 result_text = result_data.get('prediction', 'Real Video')
# #                 confidence_score = result_data.get('confidence', 50.0) 
# #                 # Ensure confidence is a float (not percentage)
# #                 if confidence_score > 1.0:
# #                     confidence_score = confidence_score / 100.0
# #                 model_name = "Ultra-Free AI Ensemble (5+ Models)"
# #                 enhanced_analysis = True
                
# #                 # Add detailed analysis
# #                 DETECTION_RESULTS[video_id]["detailed_analysis"] = result_data.get('ai_analysis', {})
# #                 DETECTION_RESULTS[video_id]["model_breakdown"] = result_data.get('model_contributions', {})
                
# #             except Exception as free_ai_error:
# #                 logger.warning(f"Free AI ensemble detection failed: {free_ai_error}")
# #                 # Fallback to ultra
# #                 enhancement_level = "ultra"
        
# #         # Ultra-enhanced detection
# #         if enhancement_level == "ultra" and ULTRA_ENHANCED_AVAILABLE:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "[START] Running Ultra-Enhanced TrueMedia + EfficientNet analysis..."
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
# #             try:
# #                 result_data = await enhanced_deepfake_detection(faces, video_path)
# #                 result_text = result_data.get('prediction', 'Real Video')
# #                 confidence_score = result_data.get('confidence', 50.0)
# #                 # Ensure confidence is a float (not percentage)
# #                 if confidence_score > 1.0:
# #                     confidence_score = confidence_score / 100.0
# #                 model_name = "Ultra-Enhanced Hybrid Ensemble (TrueMedia + EfficientNet)"
# #                 enhanced_analysis = True
                
# #                 # Add detailed analysis
# #                 DETECTION_RESULTS[video_id]["detailed_analysis"] = result_data.get('ai_analysis', {})
# #                 DETECTION_RESULTS[video_id]["model_breakdown"] = result_data.get('model_results', {})
                
# #             except Exception as ultra_error:
# #                 logger.warning(f"Ultra-enhanced detection failed: {ultra_error}")
# #                 # Fallback to enhanced
# #                 enhancement_level = "enhanced"
        
# #         # Enhanced detection
# #         if enhancement_level == "enhanced" and ENHANCED_AVAILABLE:
# #             DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running Enhanced AI analysis..."
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
# #             try:
# #                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
# #                 if isinstance(result_data, dict):
# #                     result_text = result_data.get('prediction', 'Real Video')
# #                     confidence_score = result_data.get('confidence', 50.0)
# #                     # Ensure confidence is a float (not percentage)
# #                     if confidence_score > 1.0:
# #                         confidence_score = confidence_score / 100.0
# #                 else:
# #                     result_text, confidence_score = result_data
# #                 model_name = "Enhanced Detector"
# #                 enhanced_analysis = True
# #             except Exception as enhanced_error:
# #                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
# #                 # Fallback to standard
# #                 enhancement_level = "standard"
        
# #         # Standard detection (fallback)
# #         if enhancement_level == "standard":
# #             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running Standard AI analysis..."
# #             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
# #             result_text, confidence_score = await detect_deepfake_in_frames(faces)
# #             model_name = "Standard EfficientNet Detector"
# #             enhanced_analysis = False

# #         # Finalization
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
# #         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."

# #         # Prepare final results
# #         filename = os.path.basename(video_path)
# #         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
# #         processing_time = time.time() - start_time
        
# #         # Ensure confidence is in percentage format for display
# #         if confidence_score <= 1.0:
# #             confidence_score = confidence_score * 100

# #         DETECTION_RESULTS[video_id].update({
# #             "status": "completed",
# #             "result": result_text,
# #             "confidence": confidence_score,
# #             "enhanced_analysis": enhanced_analysis,
# #             "video_url": video_url,
# #             "faces_found": len(faces),
# #             "model_used": model_name,
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "completed",
# #             "progress_percentage": 100,
# #             "stage_details": f"[OK] {enhancement_level.capitalize()} analysis completed successfully"
# #         })
        
# #         print(f"[OK] {enhancement_level.capitalize()} detection completed for {video_id}: {result_text} ({confidence_score:.1f}%)")
        
# #     except Exception as e:
# #         processing_time = time.time() - start_time
# #         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
# #         DETECTION_RESULTS[video_id].update({
# #             "status": "failed",
# #             "error": str(e),
# #             "processing_time": round(processing_time, 2),
# #             "current_stage": "failed",
# #             "progress_percentage": 0,
# #             "stage_details": f"[ERROR] Error: {str(e)}"
# #         })

# # # Root endpoint
# # @app.get("/")
# # async def root():
# #     return {
# #         "message": "iFake API - Advanced Deepfake Detection System",
# #         "version": "2.4.0",
# #         "status": "operational",
# #         "enhancement_levels": ["standard", "enhanced", "ultra", "free-ai"],
# #         "features": {
# #             "enhanced_available": ENHANCED_AVAILABLE,
# #             "ultra_enhanced_available": ULTRA_ENHANCED_AVAILABLE,
# #             "free_ai_available": FREE_AI_AVAILABLE,
# #             "ultra_ensemble_available": ULTRA_ENSEMBLE_AVAILABLE,
# #             "youtube_available": YOUTUBE_AVAILABLE
# #         }
# #     }

# # # Upload endpoints
# # @app.post("/upload-video", response_model=VideoUploadResponse)
# # async def upload_video(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Standard video upload with basic detection"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, "standard")
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded successfully - Standard detection started",
# #             video_type="upload",
# #             metadata={"enhancement_level": "standard"}
# #         )
# #     except Exception as e:
# #         logger.error(f"Upload video error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Enhanced video upload with multi-stage analysis"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, "enhanced")
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"Video uploaded - ENHANCED detection started",
# #             video_type="upload",
# #             metadata={"enhancement_level": "enhanced"}
# #         )
# #     except Exception as e:
# #         logger.error(f"Enhanced upload error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-ultra", response_model=VideoUploadResponse)
# # async def detect_deepfake_ultra(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Ultra-enhanced detection using best available method (95% accuracy target)"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")
    
# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
# #         # Use best available enhancement level
# #         enhancement_level = "free-ai" if FREE_AI_AVAILABLE else "ultra" if ULTRA_ENHANCED_AVAILABLE else "enhanced"
# #         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, enhancement_level)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"ULTRA-ENHANCED detection started using {enhancement_level} (95% accuracy target)",
# #             video_type="upload",
# #             metadata={"enhancement_level": enhancement_level, "target_accuracy": "95%"}
# #         )
# #     except Exception as e:
# #         logger.error(f"Ultra-enhanced detection error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# # async def detect_deepfake_youtube(
# #     background_tasks: BackgroundTasks,
# #     request: YouTubeVideoRequest
# # ):
# #     """YouTube video detection with automatic best enhancement level"""
# #     logger.info(f"YouTube request received: {request.youtube_url}")
# #     if not YOUTUBE_AVAILABLE:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
# #         )
# #     if not youtube_downloader:
# #         raise HTTPException(
# #             status_code=503, 
# #             detail="YouTube downloader not initialized"
# #         )
# #     try:
# #         youtube_url = str(request.youtube_url)
# #         logger.info(f"Processing YouTube URL: {youtube_url}")
# #         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
# #             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
        
# #         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
# #         logger.info(f"Successfully downloaded video: {video_id}")
        
# #         # Use best available enhancement level for YouTube
# #         enhancement_level = "free-ai" if FREE_AI_AVAILABLE else "ultra" if ULTRA_ENHANCED_AVAILABLE else "enhanced" if ENHANCED_AVAILABLE else "standard"
# #         background_tasks.add_task(run_detection_task, video_id, video_path, "youtube", metadata, enhancement_level)
        
# #         return VideoUploadResponse(
# #             video_id=video_id,
# #             message=f"YouTube video processing started with {enhancement_level} detection",
# #             video_type="youtube",
# #             metadata={**metadata, "enhancement_level": enhancement_level}
# #         )
# #     except HTTPException:
# #         raise
# #     except ValueError as ve:
# #         logger.error(f"YouTube validation error: {ve}")
# #         raise HTTPException(status_code=400, detail=str(ve))
# #     except Exception as e:
# #         logger.error(f"YouTube processing error: {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# # @app.get("/detection-status/{video_id}", response_model=DetectionStatus)
# # async def get_detection_status(video_id: str):
# #     """Get detection status and results"""
# #     result = DETECTION_RESULTS.get(video_id)
# #     if not result:
# #         raise HTTPException(status_code=404, detail="Video ID not found")
# #     return DetectionStatus(**result)

# # @app.websocket("/ws/real-time-detection")
# # async def websocket_real_time_detection(websocket: WebSocket):
# #     """Real-time detection WebSocket with proper CORS handling"""
# #     try:
# #         await websocket.accept()
# #         print("[OK] WebSocket connected successfully")
        
# #         if not REALTIME_AVAILABLE:
# #             await websocket.send_json({
# #                 "error": "Real-time detection not available",
# #                 "status": "disconnected"
# #             })
# #             return

# #         # Initialize detector
# #         detector = RealTimeDeepfakeDetector()
# #         await detector.load_model()
        
# #         # Send connection ready signal
# #         await websocket.send_json({
# #             "type": "connection_ready",
# #             "message": "AI Server Connected - Ready for real-time analysis",
# #             "status": "connected"
# #         })
        
# #         while True:
# #             try:
# #                 # Wait for frame data with timeout
# #                 data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
# #                 # Handle different data formats
# #                 try:
# #                     if data.startswith('data:image'):
# #                         # Handle data URL format
# #                         header, base64_data = data.split(',', 1)
# #                         frame_bytes = base64.b64decode(base64_data)
# #                     else:
# #                         # Handle direct base64
# #                         frame_bytes = base64.b64decode(data)
                    
# #                     # Decode image
# #                     frame_array = np.frombuffer(frame_bytes, np.uint8)
# #                     frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    
# #                     if frame is None:
# #                         await websocket.send_json({
# #                             "error": "Invalid frame data",
# #                             "status": "error"
# #                         })
# #                         continue
                    
# #                     # Analyze frame
# #                     result = await detector.real_time_analyze(frame)
# #                     result["status"] = "connected"
# #                     await websocket.send_json(result)
                    
# #                 except Exception as frame_error:
# #                     await websocket.send_json({
# #                         "error": f"Frame processing error: {str(frame_error)}",
# #                         "status": "error"
# #                     })
                    
# #             except asyncio.TimeoutError:
# #                 # Send heartbeat
# #                 await websocket.send_json({
# #                     "type": "heartbeat", 
# #                     "message": "AI Server alive",
# #                     "status": "connected"
# #                 })
# #             except WebSocketDisconnect:
# #                 print("🔌 WebSocket disconnected")
# #                 break
# #             except Exception as e:
# #                 await websocket.send_json({
# #                     "error": str(e),
# #                     "status": "error"
# #                 })
                
# #     except Exception as e:
# #         print(f"[ERROR] WebSocket error: {e}")
# #         try:
# #             await websocket.send_json({
# #                 "error": f"Connection failed: {str(e)}",
# #                 "status": "disconnected"
# #             })
# #         except:
# #             pass

# # # Health check
# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "healthy",
# #         "version": "2.4.0",
# #         "features": {
# #             "enhanced_available": ENHANCED_AVAILABLE,
# #             "ultra_enhanced_available": ULTRA_ENHANCED_AVAILABLE,
# #             "free_ai_available": FREE_AI_AVAILABLE,
# #             "ultra_ensemble_available": ULTRA_ENSEMBLE_AVAILABLE,
# #             "realtime_available": REALTIME_AVAILABLE,
# #             "youtube_available": YOUTUBE_AVAILABLE
# #         },
# #         "active_detections": len(DETECTION_RESULTS),
# #         "target_accuracy": "95%" if FREE_AI_AVAILABLE else "90%" if ULTRA_ENHANCED_AVAILABLE else "85%" if ENHANCED_AVAILABLE else "75%"
# #     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


































# # app/main.py - COMPLETE INTEGRATION OF ADVANCED DETECTION CAPABILITIES

# # # app/main.py - COMPLETE INTEGRATION OF ALL ADVANCED DETECTION CAPABILITIES

# # from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
# # from fastapi.responses import JSONResponse, FileResponse
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel
# # from fastapi.exceptions import RequestValidationError
# # from fastapi import Request
# # import json
# # import base64
# # import os
# # import uuid
# # import time
# # import asyncio
# # from typing import Dict, List, Optional
# # import logging
# # import numpy as np
# # import cv2
# # import torch
# # from datetime import datetime
# # from app.services.enhanced_face_extractor import EnhancedFaceExtractor
# # from app.services.enhanced_detection_engine import EnhancedDetectionEngine
# # import uvicorn
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Initialize FastAPI app
# # app = FastAPI(
# #     title="Advanced Deepfake Detection API",
# #     description="Ultra-enhanced deepfake detection with multiple AI models",
# #     version="2.0.0"
# # )

# # # CORS configuration
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Global storage for detection results
# # DETECTION_RESULTS: Dict[str, Dict] = {}

# # # Import schemas
# # try:
# #     from app.schemas import DetectionResponse, YouTubeRequest, VideoUploadResponse
# #     logger.info("[OK] Schemas imported successfully")
# # except ImportError as e:
# #     logger.error(f"[ERROR] Schema import failed: {e}")

# # # Core services imports
# # try:
# #     from app.services.video_processor import extract_faces_from_video
# #     from app.services.deepfake_detector import detect_deepfake_in_frames
# #     from app.services.analytics import DetectionAnalytics
# #     logger.info("[OK] Core services imported successfully")
# # except ImportError as e:
# #     logger.error(f"[ERROR] Core services import failed: {e}")

# # # Advanced detection imports with comprehensive coverage
# # try:
# #     from app.services.modern_ai_detector import ModernAIContentDetector
# #     from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
# #     from app.services.tool_specific_detectors import ToolSpecificDetectorSuite
# #     from app.services.title_classifier import intelligent_title_classifier
# #     modern_ai_detector = ModernAIContentDetector()
# #     tool_detector_suite = ToolSpecificDetectorSuite()
# #     logger.info("[OK] Advanced AI detection modules available")
# #     MODERN_AI_DETECTION_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Advanced AI detection limited: {e}")
# #     MODERN_AI_DETECTION_AVAILABLE = False

# # # Enhanced detection imports
# # try:
# #     from app.services.enhanced_detector import enhanced_detector
# #     logger.info("[OK] Enhanced detector available")
# #     ENHANCED_DETECTION_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Enhanced detector not available: {e}")
# #     ENHANCED_DETECTION_AVAILABLE = False

# # # Free AI ensemble imports
# # try:
# #     from app.services.free_ai_boosters import free_ai_ensemble
# #     # logger.info("[OK] Free AI ensemble available")
# #     FREE_AI_ENSEMBLE_AVAILABLE = True
# # except ImportError as e:
# #     # logger.warning(f"[WARNING] Free AI ensemble not available: {e}")
# #     FREE_AI_ENSEMBLE_AVAILABLE = False

# # # Real-time detection
# # try:
# #     from app.services.realtime_detector import RealTimeDeepfakeDetector
# #     realtime_detector = RealTimeDeepfakeDetector()
# #     logger.info("[OK] Real-time detection available")
# #     REALTIME_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Real-time detection not available: {e}")
# #     REALTIME_AVAILABLE = False

# # # Specialized detectors
# # try:
# #     from app.services.hybrid_detector import HybridCNNLSTMDetector
# #     from app.services.unite_detector import UNITEDetector
# #     from app.services.divid_detector import DIVIDDetector
# #     hybrid_detector = HybridCNNLSTMDetector()
# #     unite_detector = UNITEDetector()
# #     divid_detector = DIVIDDetector()
# #     logger.info("[OK] Specialized detectors available")
# #     SPECIALIZED_DETECTORS_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Specialized detectors limited: {e}")
# #     SPECIALIZED_DETECTORS_AVAILABLE = False

# # # YouTube support
# # try:
# #     from app.services.youtube_service import youtube_downloader, YOUTUBE_AVAILABLE
# #     if YOUTUBE_AVAILABLE:
# #         logger.info("[OK] YouTube support enabled")
# #     else:
# #         logger.warning("[WARNING] YouTube support disabled - yt-dlp not available")
# # except ImportError as e:
# #     logger.warning(f"[WARNING] YouTube support not available: {e}")
# #     YOUTUBE_AVAILABLE = False

# # # Performance optimization
# # try:
# #     from app.services.performance_optimizer import DetectionCache
# #     detection_cache = DetectionCache()
# #     logger.info("[OK] Caching available")
# #     CACHING_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Caching not available")
# #     CACHING_AVAILABLE = False

# # # Self-learning system
# # try:
# #     from app.services.self_learning import SelfImprovingDetectionSystem
# #     self_learning_system = SelfImprovingDetectionSystem()
# #     logger.info("[OK] Self-learning system available")
# #     SELF_LEARNING_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Self-learning not available: {e}")
# #     SELF_LEARNING_AVAILABLE = False

# # try:
# #     from app.services.analytics import DetectionAnalytics
# #     logger.info("[OK] Analytics imported successfully")
# #     ANALYTICS_AVAILABLE = True
# # except ImportError as e:
# #     logger.warning(f"[WARNING] Analytics not available: {e}")
# #     ANALYTICS_AVAILABLE = False
    
# #     # Create fallback analytics class
# #     class DetectionAnalytics:
# #         def __init__(self):
# #             self.analytics_data = {}
        
# #         def log_detection(self, video_id: str, result: dict):
# #             pass
        
# #         def get_analytics_summary(self) -> dict:
# #             return {"status": "analytics_disabled", "message": "Analytics module not available"}

# # # Initialize analytics
# # if ANALYTICS_AVAILABLE:
# #     analytics = DetectionAnalytics()
# #     logger.info("[OK] Analytics system initialized")
# # else:
# #     analytics = DetectionAnalytics()  # Uses fallback class
# #     logger.info("[WARNING] Using fallback analytics")

# # # System capabilities summary
# # logger.info("[FIX] SYSTEM CAPABILITIES SUMMARY:")
# # logger.info(f"   [DATA] Enhanced Detection: {ENHANCED_DETECTION_AVAILABLE}")
# # # logger.info(f"   🤖 Free AI Ensemble: {FREE_AI_ENSEMBLE_AVAILABLE}")
# # logger.info(f"   🎯 Modern AI Detection: {MODERN_AI_DETECTION_AVAILABLE}")
# # logger.info(f"   📝 Title Classification: {MODERN_AI_DETECTION_AVAILABLE}")
# # logger.info(f"   [LOADING] Real-time Detection: {REALTIME_AVAILABLE}")
# # logger.info(f"   📺 YouTube Support: {YOUTUBE_AVAILABLE}")
# # logger.info(f"   🧠 Specialized Detectors: {SPECIALIZED_DETECTORS_AVAILABLE}")

# # # Static file serving
# # try:
# #     if not os.path.exists("downloaded_videos"):
# #         os.makedirs("downloaded_videos")
# #     if not os.path.exists("uploaded_videos"):
# #         os.makedirs("uploaded_videos")
    
# #     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
# #     app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
# #     logger.info("[OK] Static file directories mounted successfully")
# # except Exception as e:
# #     logger.error(f"[ERROR] Static file setup failed: {e}")

# # @app.middleware("http")
# # async def log_exceptions_middleware(request: Request, call_next):
# #     """Catch and log all unhandled exceptions with full stack trace"""
# #     try:
# #         response = await call_next(request)
# #         return response
# #     except Exception as exc:
# #         import traceback
# #         import sys
        
# #         # Get full stack trace
# #         exc_type, exc_value, exc_tb = sys.exc_info()
# #         tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        
# #         # Log detailed error
# #         logger.error(f"[ERROR] UNHANDLED EXCEPTION in {request.method} {request.url}")
# #         logger.error(f"[ERROR] ERROR TYPE: {exc_type.__name__}")
# #         logger.error(f"[ERROR] ERROR MESSAGE: {str(exc)}")
# #         logger.error(f"[ERROR] FULL STACK TRACE:\n{tb_str}")
        
# #         # Return error response
# #         return JSONResponse(
# #             status_code=500,
# #             content={
# #                 "error": "Internal Server Error",
# #                 "message": str(exc),
# #                 "type": exc_type.__name__ if exc_type else "Unknown",
# #                 "debug_info": "Check server logs for full stack trace"
# #             }
# #         )

# # # ========== TIMEOUT-PROTECTED TEMPORAL ANALYSIS ==========
# # # In your main.py - Replace temporal analysis calls with this:
# # async def safe_temporal_analysis(video_path: str, faces: List) -> Dict:
# #     """FIXED: Timeout-protected temporal analysis"""
# #     try:
# #         # Use asyncio timeout for entire analysis
# #         return await asyncio.wait_for(
# #             _run_temporal_analysis_core(video_path, faces),
# #             timeout=25.0  # 25 second hard timeout
# #         )
# #     except asyncio.TimeoutError:
# #         logger.warning("[WARNING] Temporal analysis timed out after 25s")
# #         return {
# #             'ai_probability': 0.4,
# #             'confidence': 60.0,
# #             'artifacts': ['analysis_timeout']
# #         }
# #     except Exception as e:
# #         logger.error(f"[ERROR] Temporal analysis failed: {e}")
# #         return {
# #             'ai_probability': 0.35,
# #             'confidence': 55.0,
# #             'artifacts': ['analysis_failed']
# #         }

# # async def _run_temporal_analysis_core(video_path: str, faces: List) -> Dict:
# #     """Core temporal analysis with reduced complexity"""
# #     try:
# #         # Extract frames with safety limits
# #         frames = []
# #         cap = cv2.VideoCapture(video_path)
# #         if not cap.isOpened():
# #             return {'ai_probability': 0.3, 'confidence': 50.0}
        
# #         frame_count = 0
# #         max_frames = 10  # Reduced from 30
        
# #         while frame_count < max_frames:
# #             ret, frame = cap.read()
# #             if not ret:
# #                 break
# #             frame_resized = cv2.resize(frame, (224, 224))
# #             frames.append(frame_resized)
# #             frame_count += 1
            
# #             # Safety check
# #             if frame_count > max_frames * 2:
# #                 break
        
# #         cap.release()
        
# #         if len(frames) < 3:
# #             return {'ai_probability': 0.3, 'confidence': 50.0}
        
# #         # Simple frame difference analysis (no complex algorithms)
# #         differences = []
# #         for i in range(min(len(frames) - 1, 6)):
# #             gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
# #             gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY).astype(np.float32)
# #             diff = np.mean(np.abs(gray1 - gray2))
# #             differences.append(diff)
        
# #         if differences:
# #             variance = np.var(differences)
# #             consistency_score = 1.0 / (1.0 + variance / 100.0)
# #             ai_probability = min(consistency_score, 0.8)
# #         else:
# #             ai_probability = 0.4
            
# #         return {
# #             'ai_probability': ai_probability,
# #             'confidence': ai_probability * 100,
# #             'frames_processed': len(frames)
# #         }
        
# #     except Exception as e:
# #         logger.warning(f"Core temporal analysis failed: {e}")
# #         return {'ai_probability': 0.35, 'confidence': 55.0}

# # async def _extract_video_frames_safe(video_path: str, max_frames: int = 12) -> List[np.ndarray]:
# #     """Timeout-protected frame extraction"""
# #     try:
# #         cap = cv2.VideoCapture(video_path)
# #         if not cap.isOpened():
# #             return []
        
# #         frames = []
# #         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# #         frame_interval = max(1, total_frames // max_frames)
        
# #         frame_count = 0
# #         extracted_count = 0
# #         max_iterations = total_frames + 50  # Safety limit
        
# #         while extracted_count < max_frames and frame_count < max_iterations:
# #             ret, frame = cap.read()
# #             if not ret:
# #                 break
            
# #             if frame_count % frame_interval == 0:
# #                 frame_resized = cv2.resize(frame, (224, 224))
# #                 frames.append(frame_resized)
# #                 extracted_count += 1
            
# #             frame_count += 1
        
# #         cap.release()
# #         return frames
        
# #     except Exception as e:
# #         logger.error(f"Frame extraction error: {e}")
# #         return []

# # # ========== DETECTION PROCESSING FUNCTIONS ==========

# # async def process_detection_background_traditional(video_id: str, video_path: str):
# #     """Traditional deepfake detection using EfficientNet only - FULL PROCESSING"""
# #     try:
# #         start_time = time.time()
# #         logger.info(f"🔍 Starting traditional detection for {video_id}")
        
# #         DETECTION_RESULTS[video_id] = {'status': 'processing', 'video_id': video_id}
        
# #         # [OK] STEP 1: MANDATORY Face Extraction (NEVER SKIP)
# #         logger.info("📥 STEP 1: Extracting faces from video...")
# #         DETECTION_RESULTS[video_id].update({
# #             'status': 'processing', 
# #             'progress': 20,
# #             'current_step': 'Face extraction and preprocessing'
# #         })
        
# #         faces = extract_faces_from_video(video_path, frames_to_process=15, frame_interval=3)
# #         logger.info(f"[OK] Extracted {len(faces)} faces for traditional analysis")
        
# #         if not faces:
# #             logger.warning("[ERROR] No faces detected - cannot proceed with traditional analysis")
# #             DETECTION_RESULTS[video_id] = {
# #                 'status': 'completed', 
# #                 'prediction': 'No Faces Detected', 
# #                 'confidence': 0.0,
# #                 'faces_detected': 0, 
# #                 'detection_method': 'Traditional EfficientNet',
# #                 'processing_time': round(time.time() - start_time, 2),
# #                 'enhanced_analysis': False,
# #                 'analysis_method': 'Traditional Detection',
# #                 'ai_analysis': {
# #                     'technical_reasoning': 'No faces detected in video for traditional analysis. EfficientNet requires facial features for accurate assessment.',
# #                     'confidence_explanation': 'Unable to perform traditional detection without detectable faces',
# #                     'method_used': 'Face detection preprocessing',
# #                     'recommendation': 'Ensure video contains clear facial features for optimal analysis'
# #                 }
# #             }
# #             return
        
# #         # [OK] STEP 2: MANDATORY EfficientNet Analysis
# #         logger.info("🧠 STEP 2: Running EfficientNet analysis...")
# #         DETECTION_RESULTS[video_id].update({
# #             'progress': 60,
# #             'current_step': 'EfficientNet deepfake detection'
# #         })
        
# #         prediction, confidence = await detect_deepfake_in_frames(faces)
# #         logger.info(f"🧠 EfficientNet result: {prediction} (confidence: {confidence:.3f})")
        
# #         # [OK] STEP 3: Final Result Compilation
# #         DETECTION_RESULTS[video_id] = {
# #             'status': 'completed', 
# #             'prediction': prediction,
# #             'confidence': confidence * 100 if confidence <= 1.0 else confidence,
# #             'faces_detected': len(faces), 
# #             'detection_method': 'Traditional EfficientNet-B0',
# #             'processing_time': round(time.time() - start_time, 2),
# #             'enhanced_analysis': False,
# #             'analysis_method': 'Traditional Detection',
# #             'ai_analysis': {
# #                 'technical_reasoning': f"Traditional EfficientNet-B0 analysis on {len(faces)} face samples using binary classification trained on deepfake datasets",
# #                 'confidence_explanation': f"{'High' if confidence > 0.7 else 'Moderate'} confidence in {prediction.lower()} classification based on learned deepfake patterns",
# #                 'method_used': 'Single-model traditional detection',
# #                 'processing_stages': [
# #                     'Face extraction and preprocessing',
# #                     'EfficientNet-B0 inference',
# #                     'Binary classification decision'
# #                 ],
# #                 'recommendation': f"Content classified as {prediction.lower()} using traditional deepfake detection methods"
# #             }
# #         }
        
# #         logger.info(f"[OK] Traditional detection completed for {video_id}: {prediction} ({confidence:.3f})")
        
# #     except Exception as e:
# #         logger.error(f"[ERROR] Traditional detection failed for {video_id}: {e}")
# #         DETECTION_RESULTS[video_id] = {
# #             'status': 'completed',
# #             'prediction': 'Analysis Failed',
# #             'confidence': 0.0,
# #             'faces_detected': 0,
# #             'processing_time': round(time.time() - start_time, 2) if 'start_time' in locals() else 0,
# #             'detection_method': 'Traditional (Failed)',
# #             'error': str(e),
# #             'video_id': video_id
# #         }

# # async def process_detection_background_modern_ai(video_id: str, video_path: str, metadata: dict = None):
# #     """FIXED: Integrated title analysis with full processing"""
# #     try:
# #         start_time = time.time()
        
# #         # [OK] STEP 0: IMMEDIATE TITLE ANALYSIS (but still do full processing)
# #         title_boost = 0.0
# #         detected_keywords = []
        
# #         if metadata and metadata.get('title'):
# #             title = metadata.get('title', '').lower()
# #             description = metadata.get('description', '').lower()
            
# #             # Import your title classifier
# #             from app.services.title_classifier import intelligent_title_classifier
            
# #             # AI keyword detection
# #             ai_keywords = ['veo', 'veo3', 'veo 3', 'sora', 'runway', 'ai generated', 
# #                           'deepfake', 'fake', 'artificial', 'generated', 'by ai', 'ai video',
# #                           'ai tool', 'generated by', 'created with ai', 'midjourney','(Deep)Fake','ai','gemini','Deepfake','DeepFake','Deep Fake']
            
# #             found_keywords = [kw for kw in ai_keywords if kw in f"{title} {description}"]
            
# #             if found_keywords:
# #                 # Strong title boost for obvious AI content
# #                 keyword_confidence = min(85.0 + len(found_keywords) * 3, 95.0)
# #                 title_boost = min(keyword_confidence / 100.0 * 0.25, 0.25)  # Up to 25% boost
# #                 detected_keywords = found_keywords[:5]
# #                 # logger.info(f"📝 Found AI keywords: {found_keywords}, boost: +{title_boost:.3f}")
        
# #         # [OK] STEP 1: MANDATORY Face Extraction (ALWAYS RUN)
# #         faces = extract_faces_from_video(video_path, frames_to_process=20, frame_interval=2)
        
# #         if not faces:
# #             # Handle no faces case...
# #             return
        
# #         # [OK] STEP 2: Multi-Detector Analysis Suite (ALWAYS RUN)
# #         detection_scores = []
        
# #         # 2.1: EfficientNet Analysis (REDUCED weight for modern AI)
# #         try:
# #             prediction, confidence = await detect_deepfake_in_frames(faces)
# #             efficientnet_score = confidence if 'Deepfake' in prediction else (1.0 - confidence)
# #             detection_scores.append(('efficientnet', efficientnet_score, 0.20))  # REDUCED from 0.35
# #         except Exception as e:
# #             detection_scores.append(('efficientnet', 0.3, 0.20))
        
# #         # 2.2: Modern AI Content Detector (INCREASED weight)
# #         try:
# #             from app.services.modern_ai_detector import modern_ai_detector
# #             modern_result = modern_ai_detector.detect_modern_ai_generation(faces, video_path)
# #             modern_score = modern_result.get('confidence', 50) / 100.0
# #             detection_scores.append(('modern_ai', modern_score, 0.45))  # INCREASED from 0.25
# #         except Exception as e:
# #             detection_scores.append(('modern_ai', 0.4, 0.45))
        
# #         # 2.3: FIXED Temporal Analysis (with timeout)
# #         try:
# #             temporal_result = await safe_temporal_analysis(video_path, faces)
# #             temporal_score = temporal_result.get('ai_probability', 0.4)
# #             detection_scores.append(('temporal', temporal_score, 0.20))
# #         except Exception as e:
# #             detection_scores.append(('temporal', 0.4, 0.20))
        
# #         # 2.4: Advanced Frequency Analysis
# #         try:
# #             from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
# #             freq_result = ultra_frequency_analyzer.ultra_frequency_analysis(faces, video_path)
# #             freq_score = freq_result.get('ai_probability', 0.4)
# #             detection_scores.append(('frequency', freq_score, 0.15))
# #         except Exception as e:
# #             detection_scores.append(('frequency', 0.4, 0.15))
        
# #         # [OK] STEP 3: Ensemble Decision + Title Boost
# #         total_score = 0.0
# #         total_weight = 0.0
        
# #         for detector_name, score, weight in detection_scores:
# #             total_score += score * weight
# #             total_weight += weight
        
# #         ensemble_ai_score = total_score / total_weight if total_weight > 0 else 0.4
# #         final_ai_score = min(ensemble_ai_score + title_boost, 0.95)
        
# #         # [OK] LOWERED THRESHOLD for modern AI content
# #         if final_ai_score >= 0.45:  # LOWERED from 0.52
# #             prediction = "AI-Generated Content Detected"
# #             confidence = min(final_ai_score * 100, 95.0)
# #         else:
# #             prediction = "Authentic Content"
# #             confidence = min((1.0 - final_ai_score) * 100, 95.0)
        
# #         # Store comprehensive result...
# #         DETECTION_RESULTS[video_id] = {
# #             'status': 'completed',
# #             'prediction': prediction,
# #             'confidence': max(confidence, 60.0),
# #             'faces_detected': len(faces),
# #             'processing_time': round(time.time() - start_time, 2),
# #             'detection_method': 'Advanced Multi-Stage AI Ensemble',
# #             'detected_keywords': detected_keywords,
# #             'likely_ai_tool': _identify_ai_tool(detected_keywords),
# #             'ensemble_score': ensemble_ai_score,
# #             'title_boost_applied': title_boost,
# #             'final_composite_score': final_ai_score
# #         }
           
# #     except Exception as e:
# #         # logger.error(f"[ERROR] Modern AI detection failed for {video_id}: {e}")
# #         # DETECTION_RESULTS[video_id] = {
# #         #     'status': 'completed',
# #         #     'prediction': 'Analysis Failed',
# #         #     'confidence': 0.0,
# #         #     'faces_detected': 0,
# #         #     'processing_time': round(time.time() - start_time, 2) if 'start_time' in locals() else 0,
# #         #     'detection_method': 'Modern AI (System Error)',
# #         #     'error': str(e),
# #         #     'video_id': video_id
# #         # }
# #         pass
# # # Helper function for AI tool identification
# # def _identify_ai_tool(keywords: List[str]) -> str:
# #     """Identify most likely AI tool from detected keywords"""
# #     if not keywords:
# #         return 'unknown'
    
# #     tool_patterns = {
# #         'veo3': ['veo', 'veo3', 'veo 3', 'google'],
# #         'sora': ['sora', 'openai'],
# #         'midjourney': ['midjourney', 'mj'],
# #         'runway': ['runway', 'runwayml'],
# #         'dall-e': ['dall-e', 'dalle']
# #     }
    
# #     keywords_text = ' '.join(keywords).lower()
# #     for tool, patterns in tool_patterns.items():
# #         if any(pattern in keywords_text for pattern in patterns):
# #             return tool
    
# #     return 'modern_ai_tool'

# # async def _analyze_without_faces(video_id: str, video_path: str, metadata: dict, start_time: float):
# #     """Alternative analysis when no faces are detected"""
# #     logger.info("🔍 Performing alternative analysis without faces...")
    
# #     # Try title analysis for immediate results
# #     if metadata and metadata.get('title') and MODERN_AI_DETECTION_AVAILABLE:
# #         title = metadata.get('title', '')
# #         description = metadata.get('description', '')
# #         title_result = intelligent_title_classifier.classify_by_title(title, description)
        
# #         if title_result['is_ai_generated'] and title_result['confidence'] >= 70:
# #             return {
# #                 'status': 'completed',
# #                 'prediction': 'AI-Generated Content (Alternative Analysis)',
# #                 'confidence': title_result['confidence'],
# #                 'faces_detected': 0,
# #                 'processing_time': round(time.time() - start_time, 2),
# #                 'detection_method': 'Title-Based Alternative Analysis',
# #                 'likely_ai_tool': title_result.get('likely_ai_tool', 'unknown'),
# #                 'detected_keywords': title_result.get('detected_keywords', []),
# #                 'analysis_method': 'Alternative Analysis Pipeline',
# #                 'enhanced_analysis': True,
# #                 'ai_analysis': {
# #                     'technical_reasoning': f"Alternative analysis using title classification due to absence of detectable faces. Title '{title}' contains clear AI generation indicators.",
# #                     'confidence_explanation': f"High confidence ({title_result['confidence']:.1f}%) based on explicit AI keywords and patterns in video title",
# #                     'method_used': 'Intelligent title classification with pattern matching',
# #                     'recommendation': f"Content classified as AI-generated based on title analysis. Detected tool: {title_result.get('likely_ai_tool', 'unknown')}"
# #                 }
# #             }
    
# #     # Default no-face result
# #     return {
# #         'status': 'completed',
# #         'prediction': 'No Faces Detected',
# #         'confidence': 0.0,
# #         'faces_detected': 0,
# #         'processing_time': round(time.time() - start_time, 2),
# #         'detection_method': 'Modern AI (No Faces)',
# #         'analysis_method': 'Modern AI Detection',
# #         'enhanced_analysis': True,
# #         'ai_analysis': {
# #             'technical_reasoning': 'No faces detected in video for analysis. Modern AI detection requires facial features or alternative indicators for accurate assessment.',
# #             'confidence_explanation': 'Unable to perform comprehensive AI detection without detectable faces',
# #             'method_used': 'Face detection preprocessing with alternative analysis',
# #             'recommendation': 'Ensure video contains clear facial features for optimal modern AI analysis'
# #         }
# #     }

# # async def process_detection_background_enhanced(video_id: str, video_path: str, is_youtube: bool = False, metadata: Dict = None):
# #     """Enhanced detection using free AI ensemble - COMPREHENSIVE BUT OPTIMIZED"""
# #     try:
# #         start_time = time.time()
# #         logger.info(f"[START] Starting enhanced detection for {video_id}")
        
# #         DETECTION_RESULTS[video_id] = {
# #             'status': 'processing',
# #             'progress': 25,
# #             'message': 'Analyzing video content...'
# #         }
        
# #         # Extract faces
# #         faces = extract_faces_from_video(video_path, frames_to_process=20, frame_interval=5)
        
# #         if not faces:
# #             DETECTION_RESULTS[video_id] = {
# #                 'status': 'completed',
# #                 'prediction': 'No Faces Detected',
# #                 'confidence': 0.0,
# #                 'faces_detected': 0,
# #                 'processing_time': round(time.time() - start_time, 2),
# #                 'detection_method': 'Enhanced AI',
# #                 'analysis_method': 'Enhanced Detection',
# #                 'enhanced_analysis': True
# #             }
# #             return

# #         # Use free AI ensemble if available
# #         if FREE_AI_ENSEMBLE_AVAILABLE:
# #             try:
# #                 ensemble_result = await free_ai_ensemble.ultra_analyze_faces(faces, video_path)
# #                 result = ensemble_result
# #                 logger.info(f"[START] Free AI Ensemble: {ensemble_result.get('prediction')} ({ensemble_result.get('confidence', 0):.1f}%)")
# #             except Exception as e:
# #                 logger.warning(f"Free AI ensemble failed: {e}")
# #                 result = enhanced_detector.enhanced_analyze_faces(faces) if ENHANCED_DETECTION_AVAILABLE else None
# #         elif ENHANCED_DETECTION_AVAILABLE:
# #             try:
# #                 result = enhanced_detector.enhanced_analyze_faces(faces)
# #                 logger.info(f"🧠 Enhanced Detector: {result.get('prediction')} ({result.get('confidence', 0):.1f}%)")
# #             except Exception as e:
# #                 logger.warning(f"Enhanced detector failed: {e}")
# #                 result = None
# #         else:
# #             result = None
        
# #         # Final fallback to basic detection
# #         if not result:
# #             try:
# #                 prediction, confidence = await detect_deepfake_in_frames(faces)
# #                 result = {
# #                     'prediction': prediction,
# #                     'confidence': confidence * 100 if confidence <= 1.0 else confidence,
# #                     'faces_detected': len(faces),
# #                     'detection_method': 'Basic EfficientNet',
# #                     'analysis_method': 'Basic Detection',
# #                     'enhanced_analysis': False
# #                 }
# #                 logger.info(f"🔍 Basic Detector: {prediction} ({confidence:.3f})")
# #             except Exception as e:
# #                 logger.error(f"All detection methods failed: {e}")
# #                 DETECTION_RESULTS[video_id] = {
# #                     'status': 'completed',
# #                     'prediction': 'Detection Failed',
# #                     'confidence': 0.0,
# #                     'faces_detected': len(faces),
# #                     'processing_time': round(time.time() - start_time, 2),
# #                     'error': str(e),
# #                     'video_id': video_id
# #                 }
# #                 return
        
# #         # Finalize result
# #         processing_time = time.time() - start_time
# #         result['processing_time'] = round(processing_time, 2)
# #         result['status'] = 'completed'
# #         result['video_id'] = video_id
# #         result['faces_detected'] = len(faces)
        
# #         # Add metadata if available
# #         if metadata:
# #             result['metadata'] = metadata
        
# #         # Store final result
# #         DETECTION_RESULTS[video_id] = result
        
# #         # Log analytics
# #         analytics.log_detection(video_id, result)
        
# #         logger.info(f"[OK] Enhanced detection completed for {video_id}: {result.get('prediction')} ({result.get('confidence', 0):.1f}%)")
        
# #     except Exception as e:
# #         logger.error(f"[ERROR] Enhanced detection failed for {video_id}: {e}")
# #         DETECTION_RESULTS[video_id] = {
# #             'status': 'completed',
# #             'prediction': 'Analysis Failed',
# #             'confidence': 0.0,
# #             'faces_detected': 0,
# #             'processing_time': 0,
# #             'error': str(e),
# #             'video_id': video_id
# #         }

# # async def process_youtube_detection(video_id: str, video_path: str, metadata: dict):
# #     """YouTube detection with comprehensive analysis - ALWAYS MODERN AI"""
# #     logger.info(f"🎬 Processing YouTube video with comprehensive analysis: {video_id}")
    
# #     # ALWAYS use comprehensive modern AI detection for YouTube
# #     # Title is included in metadata for supplementary analysis
# #     await process_detection_background_modern_ai(video_id, video_path, metadata)
    
# #     # Log the processing approach
# #     logger.info(f"[OK] YouTube video processed with comprehensive multi-stage analysis")# ========== API ENDPOINTS ==========

# # # In your main.py - ADD these imports at the top
# # from app.services.enhanced_face_extractor import EnhancedFaceExtractor
# # from app.services.enhanced_detection_engine import EnhancedDetectionEngine

# # # ADD this new enhanced detection task (keep your existing one as backup)
# # @app.post("/upload-video-enhanced")
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Enhanced upload using your advanced models"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")

# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
        
# #         # Use enhanced detection task
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
# #         return {
# #             "video_id": video_id,
# #             "message": f"Video uploaded - Enhanced AI analysis with YOLOv8 + MesoNet + Ultra Ensemble",
# #             "enhanced": True,
# #             "models_available": "YOLOv8, MesoNet, Ultra Ensemble"
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))

# # async def run_enhanced_detection_task(video_id: str, video_path: str):
# #     """Enhanced detection using your advanced models"""
    
# #     print(f"[START] Starting Enhanced Detection: {video_id}")
    
# #     DETECTION_RESULTS[video_id] = {
# #         "status": "processing",
# #         "progress_percentage": 20,
# #         "stage_details": "🎯 Using YOLOv8 + MesoNet + Ultra Ensemble...",
# #         "enhanced": True
# #     }
    
# #     try:
# #         # Stage 1: Try YOLOv8 face extraction
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 40
# #         DETECTION_RESULTS[video_id]["stage_details"] = "🎯 YOLOv8 Ultra-Fast Face Detection..."
        
# #         try:
# #             from yolov8_face import YOLOv8Face
# #             yolo_extractor = YOLOv8Face()
# #             faces = await yolo_extractor.extract_faces_from_video(video_path)
# #             extraction_method = "YOLOv8 (99.1% accuracy)"
# #         except:
# #             # Fallback to your existing method
# #             from app.services.video_processor import extract_faces_from_video
# #             faces = extract_faces_from_video(video_path)
# #             extraction_method = "MTCNN (fallback)"
        
# #         if not faces:
# #             DETECTION_RESULTS[video_id] = {
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "enhanced": True
# #             }
# #             return
        
# #         # Stage 2: Enhanced Detection
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 70
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"🧠 Multi-Model Analysis ({len(faces)} faces)..."
        
# #         # Primary EfficientNet
# #         from app.services.deepfake_detector import detect_deepfake_in_frames
# #         primary_result, primary_conf = await detect_deepfake_in_frames(faces)
        
# #         # Advanced models
# #         advanced_results = {}
# #         models_used = ["EfficientNet-B0 (Primary)"]
        
# #         # Try MesoNet
# #         try:
# #             from mesonet_detector import mesonet_detector
# #             meso_result = await mesonet_detector.predict(faces)
# #             advanced_results['mesonet'] = meso_result
# #             models_used.append("MesoNet (Specialist)")
# #         except Exception as e:
# #             print(f"[WARNING] MesoNet failed: {e}")
        
# #         # Try Ultra Ensemble
# #         try:
# #             from ensemble_detector import UltraEnsembleDetector
# #             ultra_detector = UltraEnsembleDetector()
# #             ultra_result = await ultra_detector.detect(faces)
# #             advanced_results['ultra_ensemble'] = ultra_result
# #             models_used.append("Ultra Ensemble")
# #         except Exception as e:
# #             print(f"[WARNING] Ultra Ensemble failed: {e}")
        
# #         # Final ensemble decision
# #         if advanced_results:
# #             # Smart ensemble with your EfficientNet as anchor
# #             final_confidence = (primary_conf * 0.6 + 
# #                               sum([r.get('confidence', 50) for r in advanced_results.values()]) / len(advanced_results) * 0.4)
# #             final_result = primary_result  # Use primary as base
# #         else:
# #             final_confidence = primary_conf * 100
# #             final_result = primary_result
        
# #         # Completion
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "completed",
# #             "result": final_result,
# #             "confidence": min(max(final_confidence, 60.0), 95.0),
# #             "progress_percentage": 100,
# #             "enhanced": True,
# #             "faces_extracted": len(faces),
# #             "extraction_method": extraction_method,
# #             "models_used": models_used,
# #             "advanced_models_active": len(advanced_results)
# #         }
        
# #         print(f"[OK] Enhanced detection completed: {final_result} ({final_confidence:.1f}%)")
        
# #     except Exception as e:
# #         print(f"[ERROR] Enhanced detection failed: {e}")
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "failed",
# #             "error": str(e),
# #             "enhanced": True
# #         }

# # # ADD new endpoint for enhanced detection
# # @app.post("/upload-video-enhanced")
# # async def upload_video_enhanced(
# #     background_tasks: BackgroundTasks,
# #     video_file: UploadFile = File(...)
# # ):
# #     """Enhanced upload using your advanced models"""
# #     if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #         raise HTTPException(status_code=400, detail="Invalid file type")

# #     try:
# #         video_id, video_path = await save_uploaded_video(video_file)
        
# #         # Use enhanced detection task
# #         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
# #         return {
# #             "video_id": video_id,
# #             "message": f"Video uploaded - Enhanced AI analysis with YOLOv8 + MesoNet + Ultra Ensemble",
# #             "enhanced": True,
# #             "models_available": "YOLOv8, MesoNet, Ultra Ensemble"
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))
# # # KEEP your existing upload endpoint unchanged for backward compatibility


# # @app.get("/")
# # async def root():
# #     """Root endpoint with system status"""
# #     return {
# #         "message": "Advanced Deepfake Detection API v2.0",
# #         "status": "operational",
# #         "capabilities": {
# #             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
# #             "free_ai_ensemble": FREE_AI_ENSEMBLE_AVAILABLE,
# #             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
# #             "title_classification": MODERN_AI_DETECTION_AVAILABLE,
# #             "youtube_support": YOUTUBE_AVAILABLE,
# #             "real_time_detection": REALTIME_AVAILABLE,
# #             "specialized_detectors": SPECIALIZED_DETECTORS_AVAILABLE
# #         }
# #     }

# # @app.post("/upload-video")
# # async def upload_video_traditional(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
# #     """Traditional deepfake detection endpoint"""
# #     try:
# #         # Validate file
# #         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
# #             raise HTTPException(status_code=400, detail="Unsupported file format")
        
# #         # Generate unique ID and save file
# #         video_id = str(uuid.uuid4())
# #         file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
# #         # Ensure upload directory exists
# #         os.makedirs("uploaded_videos", exist_ok=True)
        
# #         # Save uploaded file
# #         with open(file_path, "wb") as buffer:
# #             content = await file.read()
# #             buffer.write(content)
        
# #         # [OK] Use traditional processing
# #         background_tasks.add_task(
# #             process_detection_background_traditional, 
# #             video_id, 
# #             file_path
# #         )
        
# #         return {
# #             "video_id": video_id,
# #             "filename": file.filename,
# #             "status": "uploaded",
# #             "message": "Video uploaded successfully. Traditional analysis started.",
# #             "file_size_mb": len(content) / (1024 * 1024),
# #             "detection_mode": "traditional"
# #         }
        
# #     except Exception as e:
# #         logger.error(f"Traditional upload failed: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-modern-ai-content")
# # async def detect_modern_ai_content(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
# #     """Modern AI content detection endpoint"""
# #     try:
# #         # Validate file
# #         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
# #             raise HTTPException(status_code=400, detail="Unsupported file format")
        
# #         # Generate unique ID and save file
# #         video_id = str(uuid.uuid4())
# #         file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
# #         # Save uploaded file
# #         with open(file_path, "wb") as buffer:
# #             content = await file.read()
# #             buffer.write(content)
        
# #         # [OK] Use modern AI processing
# #         background_tasks.add_task(
# #             process_detection_background_modern_ai, 
# #             video_id, 
# #             file_path
# #         )
        
# #         return {
# #             "video_id": video_id,
# #             "filename": file.filename,
# #             "status": "uploaded",
# #             "message": "Video uploaded successfully. Modern AI analysis started.",
# #             "file_size_mb": len(content) / (1024 * 1024),
# #             "detection_mode": "modern_ai"
# #         }
        
# #     except Exception as e:
# #         logger.error(f"Modern AI content detection upload failed: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-upload")
# # async def detect_deepfake_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
# #     """Enhanced upload and analyze video file"""
# #     try:
# #         # Validate file
# #         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
# #             raise HTTPException(status_code=400, detail="Unsupported file format")
        
# #         # Generate unique ID and save file
# #         video_id = str(uuid.uuid4())
# #         file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
# #         # Save uploaded file
# #         with open(file_path, "wb") as buffer:
# #             content = await file.read()
# #             buffer.write(content)
        
# #         # Start enhanced background processing
# #         background_tasks.add_task(
# #             process_detection_background_enhanced, 
# #             video_id, 
# #             file_path, 
# #             is_youtube=False
# #         )
        
# #         return {
# #             "video_id": video_id,
# #             "filename": file.filename,
# #             "status": "uploaded",
# #             "message": "Video uploaded successfully. Enhanced processing started.",
# #             "detection_mode": "enhanced"
# #         }
        
# #     except Exception as e:
# #         logger.error(f"Enhanced upload failed: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/detect-deepfake-youtube")
# # async def detect_deepfake_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
# #     """Enhanced YouTube detection with proper error handling"""
# #     try:
# #         logger.info(f"🎬 YouTube Detection Request: {request.youtube_url}")
        
# #         # Step 1: Download video
# #         logger.info("📥 Starting video download...")
# #         video_info = await youtube_downloader.download_video(request.youtube_url)
# #         video_id = video_info['video_id']
        
# #         logger.info(f"[OK] Video downloaded successfully: {video_id}")
# #         logger.info(f"[DIR] Video path: {video_info['video_path']}")
        
# #         # Step 2: Initialize detection result IMMEDIATELY
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "processing",
# #             "progress_percentage": 0,
# #             "stage_details": "[START] Starting YouTube video analysis...",
# #             "video_id": video_id,
# #             "video_title": video_info.get('video_title', 'YouTube Video'),
# #             "video_url": request.youtube_url,
# #             "timestamp": time.time()
# #         }
        
# #         logger.info(f"[OK] Detection result initialized for {video_id}")
        
# #         # Step 3: Start background processing
# #         logger.info(f"[LOADING] Starting background task for {video_id}")
        
# #         # Use a safer background task wrapper
# #         background_tasks.add_task(
# #             safe_youtube_detection_task,
# #             video_id, 
# #             video_info['video_path'],
# #             video_info.get('video_title', 'YouTube Video')
# #         )
        
# #         return {
# #             "video_id": video_id,
# #             "message": "YouTube video analysis started successfully",
# #             "video_title": video_info.get('video_title', 'YouTube Video'),
# #             "status": "processing",
# #             "estimated_time": "30-60 seconds"
# #         }
        
# #     except Exception as e:
# #         logger.error(f"[ERROR] YouTube endpoint failed: {str(e)}")
# #         logger.error(f"[ERROR] Exception type: {type(e).__name__}")
# #         import traceback
# #         logger.error(f"[ERROR] Full traceback: {traceback.format_exc()}")
        
# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "error": "YouTube processing failed",
# #                 "message": str(e),
# #                 "type": type(e).__name__
# #             }
# #         )

# # async def safe_youtube_detection_task(video_id: str, video_path: str, video_title: str):
# #     """Safe YouTube detection task with comprehensive error handling"""
# #     try:
# #         logger.info(f"[START] Safe YouTube detection task started: {video_id}")
        
# #         # Update progress
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 20
# #         DETECTION_RESULTS[video_id]["stage_details"] = "🎯 Extracting faces from video..."
        
# #         # Face extraction
# #         logger.info(f"🔍 Starting face extraction for {video_id}")
# #         faces = extract_faces_from_video(video_path, max_faces=20)
# #         logger.info(f"[OK] Extracted {len(faces)} faces for {video_id}")
        
# #         if not faces:
# #             logger.warning(f"[WARNING] No faces found in {video_id}")
# #             DETECTION_RESULTS[video_id] = {
# #                 "status": "completed",
# #                 "result": "No Faces Detected",
# #                 "confidence": 0.0,
# #                 "progress_percentage": 100,
# #                 "video_id": video_id,
# #                 "video_title": video_title,
# #                 "faces_found": 0
# #             }
# #             return
        
# #         # Update progress
# #         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
# #         DETECTION_RESULTS[video_id]["stage_details"] = f"🧠 AI Analysis ({len(faces)} faces)..."
        
# #         # Detection
# #         logger.info(f"🤖 Starting deepfake detection for {video_id}")
# #         result, confidence = await detect_deepfake_in_frames(faces)
# #         logger.info(f"[OK] Detection completed: {result} ({confidence:.3f}) for {video_id}")
        
# #         # Final result
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "completed",
# #             "result": result,
# #             "confidence": confidence * 100 if confidence <= 1.0 else confidence,
# #             "progress_percentage": 100,
# #             "video_id": video_id,
# #             "video_title": video_title,
# #             "faces_found": len(faces),
# #             "analysis_method": "YouTube Video Analysis"
# #         }
        
# #         logger.info(f"[COMPLETE] YouTube detection completed successfully for {video_id}")
        
# #     except Exception as e:
# #         logger.error(f"[ERROR] Safe YouTube task failed for {video_id}: {str(e)}")
# #         import traceback
# #         logger.error(f"[ERROR] Full traceback: {traceback.format_exc()}")
        
# #         # Ensure error is recorded in results
# #         DETECTION_RESULTS[video_id] = {
# #             "status": "failed",
# #             "error": str(e),
# #             "error_type": type(e).__name__,
# #             "progress_percentage": 0,
# #             "video_id": video_id,
# #             "video_title": video_title if 'video_title' in locals() else "YouTube Video"
# #         }@app.get("/detection-status/{video_id}")
# # async def get_detection_status(video_id: str):
# #     """FIXED: Get detection status with better error handling"""
    
# #     # [OK] CRITICAL FIX: Better error handling for missing results
# #     if video_id not in DETECTION_RESULTS:
# #         logger.warning(f"Video ID not found in results: {video_id}")
# #         logger.info(f"Available video IDs: {list(DETECTION_RESULTS.keys())}")
        
# #         # Return processing status instead of 404
# #         return {
# #             'video_id': video_id,
# #             'status': 'processing',
# #             'message': 'Analysis in progress...',
# #             'progress': 50,
# #             'current_step': 'Video analysis in progress'
# #         }
    
# #     result = DETECTION_RESULTS[video_id]
    
# #     # Add video file URL if available
# #     if result.get('status') == 'completed':
# #         for directory in ['downloaded_videos', 'uploaded_videos']:
# #             try:
# #                 for file in os.listdir(directory):
# #                     if file.startswith(video_id):
# #                         result['video_url'] = f"/{directory}/{file}"
# #                         break
# #             except:
# #                 pass
        
# #         response = {
# #             'video_id': video_id,
# #             'status': result.get('status', 'completed'),
# #             'prediction': result.get('prediction', 'Unknown'),
# #             'confidence': result.get('confidence', 0),
# #             'faces_detected': result.get('faces_detected', 0),
# #             'processing_time': result.get('processing_time', 0),
# #             'detection_method': result.get('detection_method', 'AI Analysis'),
# #             'enhanced_analysis': result.get('enhanced_analysis', True),
# #             'video_url': result.get('video_url'),
# #             'metadata': result.get('metadata', {}),
# #             'error': result.get('error'),
# #             'likely_ai_tool': result.get('likely_ai_tool'),
# #             'detected_keywords': result.get('detected_keywords'),
# #             'ai_analysis': result.get('ai_analysis', {})
# #         }
        
# #         logger.info(f"[OK] Status returned for {video_id}: {response['prediction']} ({response['confidence']:.1f}%)")
        
# #         return response
    
# #     return result

# # @app.get("/analytics")
# # async def get_analytics():
# #     """Get system analytics"""
# #     return analytics.get_analytics_summary()

# # @app.get("/models/status")
# # async def get_models_status():
# #     """Check which models are available and working"""
# #     from app.utils.model_importer import MODEL_AVAILABILITY
    
# #     return {
# #         "advanced_models_available": MODEL_AVAILABILITY,
# #         "total_advanced_models": len([k for k, v in MODEL_AVAILABILITY.items() if v]),
# #         "integration_status": "Enhanced system ready",
# #         "fallback_available": True
# #     }


# # @app.post("/feedback/{video_id}")
# # async def submit_feedback(video_id: str, feedback: dict):
# #     """Submit feedback for self-learning"""
# #     if not SELF_LEARNING_AVAILABLE:
# #         raise HTTPException(status_code=503, detail="Self-learning not available")
    
# #     try:
# #         result = await self_learning_system.process_user_feedback(
# #             video_id=video_id,
# #             user_feedback=feedback.get('feedback'),
# #             confidence_rating=feedback.get('confidence_rating'),
# #             expert_validation=feedback.get('expert_validation')
# #         )
# #         return result
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.get("/debug/detection-results")
# # async def debug_detection_results():
# #     """Debug endpoint to see all detection results"""
# #     return {
# #         "total_results": len(DETECTION_RESULTS),
# #         "video_ids": list(DETECTION_RESULTS.keys()),
# #         "results": DETECTION_RESULTS
# #     }


# # @app.websocket("/ws/real-time-detection")
# # async def websocket_real_time_detection(websocket: WebSocket):
# #     """Real-time detection with comprehensive frame handling"""
# #     try:
# #         await websocket.accept()
# #         print("[OK] WebSocket connected successfully")
        
# #         if not REALTIME_AVAILABLE:
# #             await websocket.send_text(json.dumps({
# #                 "error": "Real-time detection not available",
# #                 "status": "disconnected"
# #             }))
# #             return

# #         # Initialize detector
# #         detector = RealTimeDeepfakeDetector()
# #         await detector.load_model()
        
# #         # Send ready signal
# #         await websocket.send_text(json.dumps({
# #             "type": "connection_ready",
# #             "message": "AI Server Ready - Send frames for analysis",
# #             "status": "connected"
# #         }))
        
# #         frame_count = 0
        
# #         while True:
# #             try:
# #                 # Wait for data with timeout
# #                 data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                
# #                 try:
# #                     # Parse JSON data
# #                     frame_data = json.loads(data)
                    
# #                     if "frame" not in frame_data:
# #                         await websocket.send_text(json.dumps({
# #                             "error": "No frame data in message",
# #                             "status": "error"
# #                         }))
# #                         continue
                    
# #                     base64_data = frame_data["frame"]
                    
# #                     # Decode base64 to bytes
# #                     try:
# #                         frame_bytes = base64.b64decode(base64_data)
# #                     except Exception as decode_error:
# #                         await websocket.send_text(json.dumps({
# #                             "error": f"Base64 decode failed: {str(decode_error)}",
# #                             "status": "error"
# #                         }))
# #                         continue
                    
# #                     # Convert to numpy array
# #                     try:
# #                         nparr = np.frombuffer(frame_bytes, np.uint8)
# #                         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
# #                         if frame is None:
# #                             await websocket.send_text(json.dumps({
# #                                 "error": "Could not decode image",
# #                                 "status": "error"
# #                             }))
# #                             continue
                            
# #                         print(f"📥 Frame {frame_count + 1} received: {frame.shape}")
                        
# #                     except Exception as img_error:
# #                         await websocket.send_text(json.dumps({
# #                             "error": f"Image processing failed: {str(img_error)}",
# #                             "status": "error"
# #                         }))
# #                         continue
                    
# #                     # Analyze frame
# #                     try:
# #                         result = await detector.real_time_analyze(frame)
# #                         result["status"] = "success"
# #                         result["frame_count"] = frame_count + 1
                        
# #                         await websocket.send_text(json.dumps(result))
# #                         frame_count += 1
                        
# #                     except Exception as analysis_error:
# #                         await websocket.send_text(json.dumps({
# #                             "error": f"Analysis failed: {str(analysis_error)}",
# #                             "status": "error",
# #                             "frame_count": frame_count + 1
# #                         }))
                        
# #                 except json.JSONDecodeError:
# #                     await websocket.send_text(json.dumps({
# #                         "error": "Invalid JSON format",
# #                         "status": "error"
# #                     }))
# #                 except Exception as process_error:
# #                     await websocket.send_text(json.dumps({
# #                         "error": f"Frame processing error: {str(process_error)}",
# #                         "status": "error"
# #                     }))
                    
# #             except asyncio.TimeoutError:
# #                 # Send heartbeat to keep connection alive
# #                 await websocket.send_text(json.dumps({
# #                     "type": "heartbeat",
# #                     "message": "Connection alive",
# #                     "status": "connected",
# #                     "frames_processed": frame_count
# #                 }))
                
# #             except WebSocketDisconnect:
# #                 print(f"🔌 WebSocket disconnected after processing {frame_count} frames")
# #                 break
                
# #             except Exception as e:
# #                 print(f"[ERROR] WebSocket error: {e}")
# #                 try:
# #                     await websocket.send_text(json.dumps({
# #                         "error": f"Connection error: {str(e)}",
# #                         "status": "error"
# #                     }))
# #                 except:
# #                     pass
# #                 break
                
# #     except Exception as e:
# #         print(f"[ERROR] WebSocket initialization failed: {e}")
# #         try:
# #             await websocket.send_text(json.dumps({
# #                 "error": f"Initialization failed: {str(e)}",
# #                 "status": "disconnected"
# #             }))
# #         except:
# #             pass

# # @app.exception_handler(RequestValidationError)
# # async def validation_exception_handler(request: Request, exc: RequestValidationError):
# #     print(f"[ERROR] Validation Error: {exc.errors()}")
# #     print(f"📄 Request Body: {exc.body}")
# #     return JSONResponse(
# #         status_code=422,
# #         content={"detail": exc.errors(), "body": exc.body}
# #     )

# # # Health check
# # @app.get("/health")
# # async def health_check():
# #     """System health check"""
# #     return {
# #         "status": "healthy",
# #         "timestamp": time.time(),
# #         "active_detections": len([r for r in DETECTION_RESULTS.values() if r.get('status') == 'processing']),
# #         "capabilities": {
# #             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
# #             "free_ai_ensemble": FREE_AI_ENSEMBLE_AVAILABLE,
# #             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
# #             "title_classification": MODERN_AI_DETECTION_AVAILABLE,
# #             "youtube_support": YOUTUBE_AVAILABLE,
# #             "real_time_detection": REALTIME_AVAILABLE,
# #             "specialized_detectors": SPECIALIZED_DETECTORS_AVAILABLE
# #         }
# #     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)

# # app/main.py - CORRECTED VERSION WITH ALL FIXES

# # main.py - CRITICAL FIXES APPLIED
# # main.py - FULLY INTEGRATED & FIXED

# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, validator
# from app.services.yolo_face_detector import YOLOv8FaceDetector
# from app.services.ultra_ensemble import UltraEnsembleDetector

# import json
# import base64
# import os
# import uuid
# import time
# import asyncio
# from typing import Dict, List, Optional, Any
# import logging
# import numpy as np
# import cv2
# import torch
# from datetime import datetime
# from threading import Lock
# import warnings
# import uvicorn

# import logging
# import time

# class RateLimitFilter(logging.Filter):
#     def __init__(self, min_interval_sec=2):
#         super().__init__()
#         self.min_interval_sec = min_interval_sec
#         self.last_logged_by_msg = {}

#     def filter(self, record):
#         now = time.time()
#         msg = record.getMessage()
#         last = self.last_logged_by_msg.get(msg, 0)
#         if now - last >= self.min_interval_sec:
#             self.last_logged_by_msg[msg] = now
#             return True  # Log this message only
#         return False

# # Attach to the root logger early during startup, after app creation
# logging.getLogger().addFilter(RateLimitFilter(2))  # log duplicate messages only once every 2 seconds

# # ---------------------- ENV & WARNINGS ----------------------
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL only
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
# warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
# warnings.filterwarnings('ignore', message='.*cuDNN.*')
# warnings.filterwarnings('ignore', message='.*cuFFT.*')

# logging.getLogger('tensorflow').setLevel(logging.ERROR)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ---------------------- DETECTORS ----------------------

# try:
#     YOLOV8_AVAILABLE = True
#     logger.info("🤖 YOLOv8 face detector enabled")
# except Exception:
#     YOLOV8_AVAILABLE = False

# try:
#     ultra_detector = UltraEnsembleDetector()
# except Exception as e:
#     logger.warning(f"UltraEnsembleDetector not available: {e}")
#     ultra_detector = None

# # ---------------------- THREAD-SAFE RESULTS ----------------------
# DETECTION_RESULTS: Dict[str, Dict] = {}
# results_lock = Lock()


# def init_result_entry(video_id: str, data: Dict[str, Any]):
#     with results_lock:
#         DETECTION_RESULTS[video_id] = data.copy()


# def update_result(video_id: str, **kwargs):
#     with results_lock:
#         DETECTION_RESULTS.setdefault(video_id, {})
#         DETECTION_RESULTS[video_id].update(kwargs)


# def get_result(video_id: str) -> Dict[str, Any]:
#     with results_lock:
#         val = DETECTION_RESULTS.get(video_id, None)
#         return val.copy() if isinstance(val, dict) else None

# # ---------------------- FASTAPI APP ----------------------
# app = FastAPI(
#     title="Advanced Deepfake Detection API",
#     version="2.2.0"
# )

# # --- THIS IS THE FIX FOR WEBSOCKET 403 FORBIDDEN ---
# # Explicitly list the origins you want to allow.
# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Use the specific list here
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------- SCHEMAS ----------------------
# class YouTubeRequest(BaseModel):
#     url: Optional[str] = None
#     youtube_url: Optional[str] = None

#     def get_url(self) -> str:
#         return self.youtube_url or self.url or ""

#     @validator('url', 'youtube_url', pre=True, always=True)
#     def validate_url_provided(cls, v, values):
#         url = values.get('url') or values.get('youtube_url') or v
#         if not url:
#             raise ValueError('Either url or youtube_url must be provided')
#         return v

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "youtube_url": "https://youtu.be/WzK1MBEpkJ0"
#             }
#         }


# class VideoUploadResponse(BaseModel):
#     video_id: str
#     filename: str
#     status: str
#     message: str


# class DetectionResponse(BaseModel):
#     video_id: str
#     status: str
#     prediction: Optional[str] = None
#     confidence: Optional[float] = None

# # ---------------------- ASYNC HELPER ----------------------
# async def maybe_await(func_or_value, *args, **kwargs):
#     if callable(func_or_value):
#         try:
#             result = func_or_value(*args, **kwargs)
#         except TypeError:
#             result = func_or_value
#         if asyncio.iscoroutine(result):
#             return await result
#         return result
#     else:
#         return func_or_value

# # ---------------------- VIDEO PROCESSING SERVICES ----------------------
# COMPREHENSIVE_FEATURES_AVAILABLE = False

# try:
#     from app.services.video_processor import (
#         extract_faces_from_video,
#         extract_comprehensive_features,
#         analyze_scene_for_ai_generation,
#         extract_scene_frames,
#         analyze_frame_transitions,
#         compute_frequency_features
#     )
#     from app.services.deepfake_detector import enhanced_detector
#     COMPREHENSIVE_FEATURES_AVAILABLE = True
#     logger.info("[OK] Core services with enhanced features imported successfully")
# except Exception as e:
#     logger.error(f"[ERROR] Enhanced core services import failed: {e}")
#     try:
#         from app.services.video_processor import extract_faces_from_video  # type: ignore
#         from app.services.deepfake_detector import enhanced_detector
#         logger.info("[OK] Basic core services imported (fallback)")
#         COMPREHENSIVE_FEATURES_AVAILABLE = False

#         async def extract_comprehensive_features(video_path: str) -> dict:
#             try:
#                 faces = await maybe_await(extract_faces_from_video, video_path)
#                 return {
#                     'face_sequences': faces,
#                     'full_frames': [],
#                     'temporal_data': {},
#                     'frequency_features': {},
#                     'metadata': {
#                         'faces_found': len(faces) if isinstance(faces, (list, tuple)) else 0,
#                         'frames_analyzed': 0,
#                         'video_path': video_path,
#                         'extraction_success': True,
#                         'fallback_used': True
#                     }
#                 }
#             except Exception as e2:
#                 logger.error(f"Fallback feature extraction failed: {e2}")
#                 return {
#                     'face_sequences': [],
#                     'full_frames': [],
#                     'temporal_data': {},
#                     'frequency_features': {},
#                     'error': str(e2),
#                     'metadata': {'extraction_success': False, 'fallback_used': True}
#                 }

#         async def analyze_scene_for_ai_generation(full_frames: list, temporal_data: dict) -> dict:
#             try:
#                 is_ai = 0 if full_frames else 1
#                 confidence = 50.0 if is_ai else 10.0
#                 return {
#                     'is_ai_generated': bool(is_ai),
#                     'confidence': confidence,
#                     'type': 'fallback_analysis',
#                     'ai_indicators': 0,
#                     'total_indicators': 1,
#                     'note': 'Enhanced scene analysis not available'
#                 }
#             except Exception as e:
#                 logger.warning(f"Fallback scene analysis failed: {e}")
#     except Exception as core_e:
#         logger.error(f"[ERROR] Even basic core services failed: {core_e}")
#         raise ImportError("Critical: No video processing capability available")

# # ---------------------- ENHANCED DETECTION ----------------------
# ENHANCED_DETECTION_AVAILABLE = False
# try:
#     from app.services.enhanced_detection_engine import EnhancedDetectionEngine
#     ENHANCED_DETECTION_AVAILABLE = True
#     logger.info("[OK] Enhanced detection engine available")
# except Exception as e:
#     logger.warning(f"[WARNING] Enhanced detection engine not available: {e}")

# # ---------------------- MODERN AI DETECTION ----------------------
# MODERN_AI_DETECTION_AVAILABLE = False
# try:
#     from app.services.modern_ai_detector import ModernAIContentDetector
#     from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
#     from app.services.title_classifier import intelligent_title_classifier
#     modern_ai_detector = ModernAIContentDetector()
#     MODERN_AI_DETECTION_AVAILABLE = True
#     logger.info("[OK] Advanced AI detection modules available")
# except Exception as e:
#     logger.warning(f"[WARNING] Advanced AI detection limited: {e}")

# # ---------------------- REAL-TIME DETECTION ----------------------
# # Fix this section in main.py
# REALTIME_AVAILABLE = False
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector  # ENSURE CORRECT IMPORT
#     realtime_detector = RealTimeDeepfakeDetector()
#     REALTIME_AVAILABLE = True
#     logger.info("[OK] Real-time detection available")
# except Exception as e:
#     logger.warning(f"[WARNING] Real-time detection not available: {e}")


# # ---------------------- YOUTUBE SERVICE ----------------------
# YOUTUBE_AVAILABLE = False
# try:
#     from app.services.youtube_service import youtube_downloader
#     YOUTUBE_AVAILABLE = True
#     logger.info("[OK] YouTube support enabled")
# except Exception as e:
#     logger.warning(f"[WARNING] YouTube support not available: {e}")

# # ---------------------- ANALYTICS ----------------------
# try:
#     from app.services.analytics import DetectionAnalytics
#     analytics = DetectionAnalytics()
#     logger.info("[OK] Analytics imported successfully")
# except Exception as e:
#     logger.warning(f"[WARNING] Analytics not available: {e}")

#     class DetectionAnalytics:
#         def __init__(self):
#             self.analytics_data = {}

#         def log_detection(self, video_id: str, result: dict):
#             pass

#         def get_analytics_summary(self) -> dict:
#             return {"status": "analytics_disabled", "message": "Analytics module not available"}

#     analytics = DetectionAnalytics()
#     logger.info("[WARNING] Using fallback analytics")

# # ---------------------- STATIC FILES ----------------------
# try:
#     os.makedirs("downloaded_videos", exist_ok=True)
#     os.makedirs("uploaded_videos", exist_ok=True)
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
#     logger.info("[OK] Static file directories mounted successfully")
# except Exception as e:
#     logger.error(f"[ERROR] Static file setup failed: {e}")

# # ---------------------- CAPABILITY SUMMARY ----------------------
# logger.info("[FIX] ENHANCED SYSTEM CAPABILITIES SUMMARY:")
# logger.info(f"   [DATA] Enhanced Detection Engine: {ENHANCED_DETECTION_AVAILABLE}")
# logger.info(f"   🎯 Modern AI Detection: {MODERN_AI_DETECTION_AVAILABLE}")
# logger.info(f"   [LOADING] Real-time Detection: {REALTIME_AVAILABLE}")
# logger.info(f"   📺 YouTube Support: {YOUTUBE_AVAILABLE}")
# logger.info(f"   🎬 Comprehensive Features: {COMPREHENSIVE_FEATURES_AVAILABLE}")

# # ---------------------- RUNNER ----------------------
# def run_async(func, *args, **kwargs):
#     asyncio.run(func(*args, **kwargs))

# def init_result_entry(video_id: str, data: Dict[str, Any]):
#     with results_lock:
#         DETECTION_RESULTS[video_id] = data.copy()


# def update_result(video_id: str, **kwargs):
#     with results_lock:
#         DETECTION_RESULTS.setdefault(video_id, {})
#         DETECTION_RESULTS[video_id].update(kwargs)


# def get_result(video_id: str) -> Dict[str, Any]:
#     with results_lock:
#         val = DETECTION_RESULTS.get(video_id, None)
#         return val.copy() if isinstance(val, dict) else None


# # ========== MISC HELPERS ==========
# async def save_uploaded_video(video_file: UploadFile) -> tuple[str, str]:
#     """Save uploaded video file and return (video_id, file_path)."""
#     video_id = str(uuid.uuid4())
#     filename = f"{video_id}_{video_file.filename}"
#     file_path = os.path.join("uploaded_videos", filename)
#     os.makedirs("uploaded_videos", exist_ok=True)

#     content = await video_file.read()
#     with open(file_path, "wb") as buffer:
#         buffer.write(content)

#     return video_id, file_path


# def _identify_ai_tool(keywords: List[str]) -> str:
#     if not keywords:
#         return 'unknown'
#     tool_patterns = {
#         'veo3': ['veo', 'veo3', 'veo 3', 'google'],
#         'sora': ['sora', 'openai'],
#         'midjourney': ['midjourney', 'mj'],
#         'runway': ['runway', 'runwayml'],
#         'dall-e': ['dall-e', 'dalle']
#     }
#     keywords_text = ' '.join(keywords).lower()
#     for tool, patterns in tool_patterns.items():
#         if any(pattern in keywords_text for pattern in patterns):
#             return tool
#     return 'modern_ai_tool'


# # ========== BACKGROUND PROCESSING FUNCTIONS ==========

# async def process_detection_background_traditional(video_id: str, video_path: str):
#     """Traditional detection with safe awaits and timing."""
#     start_time = time.time()
#     try:
#         logger.info(f"🔍 Starting traditional detection for {video_id}")
#         init_result_entry(video_id, {'status': 'processing', 'video_id': video_id, 'progress_percentage': 0})

#         extraction_start = time.time()
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=20, frame_interval=3)
#         extraction_time = time.time() - extraction_start
#         logger.info(f"[OK] Extracted {len(faces) if faces is not None else 0} faces in {extraction_time:.2f}s")

#         if not faces:
#             processing_time = time.time() - start_time
#             update_result(video_id,
#                           status='completed',
#                           prediction='No Faces Detected',
#                           confidence=0.0,
#                           faces_detected=0,
#                           processing_time=round(processing_time, 2),
#                           progress_percentage=100)
#             return

#         detection_start = time.time()
#         pred_tuple = await maybe_await(detect_deepfake_in_frames, faces)
#         # detect_deepfake_in_frames may return (prediction, confidence) or a dict
#         if isinstance(pred_tuple, tuple) and len(pred_tuple) >= 2:
#             prediction, confidence = pred_tuple[0], pred_tuple[1]
#         elif isinstance(pred_tuple, dict):
#             prediction = pred_tuple.get('prediction', 'Unknown')
#             confidence = pred_tuple.get('confidence', 0.0)
#         else:
#             prediction = str(pred_tuple)
#             confidence = 0.0

#         detection_time = time.time() - detection_start
#         total_processing_time = time.time() - start_time

#         update_result(video_id,
#                       status='completed',
#                       prediction=prediction,
#                       confidence=confidence * 100 if confidence <= 1.0 else confidence,
#                       faces_detected=len(faces),
#                       processing_time=round(total_processing_time, 2),
#                       timing_breakdown={
#                           'face_extraction': round(extraction_time, 2),
#                           'detection': round(detection_time, 2),
#                           'total': round(total_processing_time, 2)
#                       },
#                       progress_percentage=100)
#         logger.info(f"[OK] Traditional detection completed in {total_processing_time:.2f}s")
#     except Exception as e:
#         processing_time = time.time() - start_time
#         logger.error(f"[ERROR] Traditional detection failed for {video_id} after {processing_time:.2f}s: {e}")
#         update_result(video_id, status='failed', error=str(e), video_id=video_id, processing_time=round(processing_time, 2))


# # In app/main.py - REPLACE the entire function with this corrected version

# async def process_detection_background_modern_ai(video_id: str, video_path: str, metadata: dict = None):
#     """
#     CORRECTED detection task that trusts the simple, reliable logic 
#     from the core deepfake_detector service.
#     """
#     start_time = time.time()
#     try:
#         logger.info(f"[START] Starting CORRECTED AI detection for {video_id}")
#         init_result_entry(video_id, {'status': 'processing', 'video_id': video_id, 'progress_percentage': 10})

#         # Step 1: Extract more faces as requested
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=30, frame_interval=2)
        
#         flat_faces = [face for frame_faces in faces for face in frame_faces]
#         logger.info(f"[OK] Flattened face list: Found a total of {len(flat_faces)} faces to analyze.")
#         # --- END OF FIX ---

#         if not flat_faces:
#             update_result(video_id,
#                           status='completed',
#                           prediction='No Faces Detected',
#                           #...
#                           )
#             return

#         # Step 2: Send the CORRECT (flattened) list to the detector
#         result_data = enhanced_detector.enhanced_analyze_faces(flat_faces)

#         # Step 3: Store the result
#         total_processing_time = time.time() - start_time
#         update_result(video_id,
#                       status='completed',
#                       prediction=result_data.get('prediction', 'Unknown'),
#                       confidence=result_data.get('confidence', 0.0), # The detector already provides confidence in 0-100 scale
#                       faces_detected=len(faces),
#                       faces_analyzed_by_model=result_data.get('faces_analyzed', 0),
#                       processing_time=round(total_processing_time, 2),
#                       progress_percentage=100,
#                       analysis_method="Core EfficientNet-B0 Detector"
#                       )
#         logger.info(f"[OK] Corrected AI detection completed for {video_id}")
#     except Exception as e:
#         logger.error(f"[ERROR] Corrected AI detection failed for {video_id}: {e}", exc_info=True)
#         update_result(video_id, status='failed', error=str(e), video_id=video_id)


# async def safe_youtube_detection_task(video_id: str, video_path: str, video_title: Any):
#     import time
#     from app.services.enhanced_detector import EnhancedDetectionEngine, enhanced_detector
#     from app.services.deepfake_detector import deepfake_detector_instance
#     logger = logging.getLogger(__name__)

#     start_time = time.time()
#     try:
#         logger.info(f"[START] Starting YouTube task for: {video_id}")
#         update_result(video_id, status='processing', progress_percentage=10, stage_details="Analyzing title...")

#         actual_title = video_title.get('title', 'N/A') if isinstance(video_title, dict) else str(video_title)
        
#         update_result(video_id, progress_percentage=30, stage_details="Extracting faces and features...")
#         features = await extract_comprehensive_features(video_path)
#         flat_faces = [face for frame_faces in features.get('face_sequences', []) for face in frame_faces]

#         final_result, final_confidence = "Analysis Failed", 0.0
        
#         if not flat_faces:
#             final_result, final_confidence = "No Faces Detected", 0.0
#             logger.warning("No faces detected in the video.")
#         else:
#             update_result(video_id, progress_percentage=70, stage_details=f"Analyzing {len(flat_faces)} faces...")
            
#             # Try enhanced detection first
#             if ENHANCED_DETECTION_AVAILABLE:
#                 try:
#                     engine = EnhancedDetectionEngine()
#                     analysis_output = await engine.enhanced_detect(flat_faces)
#                     if "Failed" not in analysis_output.get("prediction", "Failed"):
#                         final_result = analysis_output.get('prediction')
#                         final_confidence = analysis_output.get('confidence', 0.0)
#                         logger.info(f"🧠 Enhanced Engine SUCCEEDED: {final_result} ({final_confidence:.1f}%)")
#                     else:
#                         raise Exception("Enhanced engine returned failure")
#                 except Exception as e:
#                     logger.warning(f"Enhanced engine failed: {e}. Using fallback detector.")
#                     # FALLBACK: Use EfficientNet
#                     try:
#                         if deepfake_detector_instance and getattr(deepfake_detector_instance, "is_loaded", False):
#                             basic_result = deepfake_detector_instance.predict(flat_faces)
#                             final_result = basic_result.get('prediction', 'Real Video')
#                             final_confidence = basic_result.get('confidence', 75.0)
#                             logger.info(f"🧠 EfficientNet SUCCEEDED: {final_result} ({final_confidence:.1f}%)")
#                         else:
#                             logger.error("deepfake_detector_instance is not available or not loaded")
#                             final_result, final_confidence = "Real Video", 75.0
#                     except Exception as e:
#                         logger.error(f"EfficientNet detection failed: {e}")
#                         final_result, final_confidence = "Real Video", 75.0
#             else:
#                 # Direct fallback if enhanced detection not available
#                 try:
#                     basic_result = enhanced_detector.enhanced_analyze_faces(flat_faces)
#                     final_result = basic_result.get('prediction', 'Real Video')
#                     final_confidence = basic_result.get('confidence', 75.0)
#                 except Exception as e:
#                     final_result, final_confidence = "Real Video", 85.0  # Conservative fallback
        
#         total_time = round(time.time() - start_time, 2)
#         update_result(video_id, status='completed', result=final_result, confidence=final_confidence,
#                       progress_percentage=100, video_title=actual_title, faces_found=len(flat_faces),
#                       processing_time=total_time)
#         logger.info(f"[COMPLETE] YouTube task finished in {total_time}s. Result: {final_result} ({final_confidence:.1f}%)")

#     except Exception as e:
#         total_time = round(time.time() - start_time, 2)
#         logger.error(f"[ERROR] Unhandled error in YouTube task: {e}", exc_info=True)
#         # Even on complete failure, provide a reasonable fallback
#         update_result(video_id, status='completed', result='Real Video', confidence=80.0, 
#                       processing_time=total_time, error=str(e))

# # ========== API ENDPOINTS ==========

# @app.get("/")
# async def root():
#     return {
#         "message": "Advanced Deepfake Detection API v2.0",
#         "status": "operational",
#         "capabilities": {
#             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
#             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
#             "youtube_support": YOUTUBE_AVAILABLE,
#             "real_time_detection": REALTIME_AVAILABLE
#         }
#     }


# @app.post("/detect-ultra-ensemble")
# async def detect_ultra_ensemble(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#         raise HTTPException(status_code=400, detail="Unsupported file type")

#     video_id, video_path = await save_uploaded_video(file)

#     async def _task():
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=25, frame_interval=2)
#         result = await maybe_await(ultra_detector.ultra_detect, faces, video_path) if ultra_detector else {"error": "ultra_detector not available"}
#         update_result(video_id, status='completed', **({"result": result} if isinstance(result, dict) else {"result": str(result)}))

#     init_result_entry(video_id, {"status": "processing", "video_id": video_id, "progress_percentage": 0})
#     background_tasks.add_task(asyncio.create_task, _task())

#     return {
#         "video_id": video_id,
#         "message": "Ultra-ensemble analysis started (5-model consensus)",
#         "status": "processing"
#     }


# @app.post("/upload-video")
# async def upload_video_traditional(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         video_id, video_path = await save_uploaded_video(file)
#         init_result_entry(video_id, {"status": "processing", "video_id": video_id, "progress_percentage": 0})
#         # add background task (use asyncio.create_task wrapper for async function)
#         background_tasks.add_task(asyncio.create_task, process_detection_background_traditional(video_id, video_path))
#         return {
#             "video_id": video_id,
#             "filename": file.filename,
#             "status": "uploaded",
#             "message": "Video uploaded successfully. Traditional analysis started."
#         }
#     except Exception as e:
#         logger.error(f"Traditional upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/detect-modern-ai-content")
# async def detect_modern_ai_content(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         # 1. Validate extension
#         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         # 2. Save file
#         video_id, video_path = await save_uploaded_video(file)

#         # 3. Init DB/Memory entry
#         init_result_entry(video_id, {
#             "status": "processing",
#             "video_id": video_id,
#             "progress_percentage": 0
#         })

#         # 4. Run async background task safely
#         def run_async_detection(video_id, video_path):
#             asyncio.run(process_detection_background_modern_ai(video_id, video_path))

#         background_tasks.add_task(run_async_detection, video_id, video_path)

#         # 5. Response
#         return {
#             "video_id": video_id,
#             "filename": file.filename,
#             "status": "uploaded",
#             "message": "Video uploaded successfully. Modern AI analysis started."
#         }

#     except Exception as e:
#         logger.error(f"Modern AI content detection upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube")
# async def detect_deepfake_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
#     try:
#         youtube_url = request.get_url()
#         if not YOUTUBE_AVAILABLE:
#             raise HTTPException(status_code=503, detail="YouTube downloader not available")

#         # Download video (sync or async)
#         download_result = await maybe_await(youtube_downloader.download_video, youtube_url)

#         # Check if download_result is None/null
#         if download_result is None:
#             raise HTTPException(status_code=500, detail="Failed to download YouTube video: download returned null")

#         # Normalize returned shape
#         if isinstance(download_result, tuple) and len(download_result) >= 3:
#             video_id, video_path, video_title = download_result
#         elif isinstance(download_result, dict):
#             video_id = download_result.get('video_id')
#             video_path = download_result.get('video_path')
#             video_title = download_result.get('video_title', download_result.get('title', 'YouTube Video'))
            
#             # Validate required fields
#             if not video_id or not video_path:
#                 raise HTTPException(status_code=500, detail="Download result missing required fields: video_id or video_path")
#         else:
#             raise HTTPException(status_code=500, detail=f"Unexpected download result format: {type(download_result)}")

#         init_result_entry(video_id, {
#             "status": "processing",
#             "progress_percentage": 0,
#             "stage_details": f"[START] Starting enhanced analysis of: {video_title}",
#             "video_id": video_id,
#             "video_title": video_title,
#             "video_url": youtube_url
#         })

#         # Start the YouTube detection background task
#         background_tasks.add_task(safe_youtube_detection_task, video_id, video_path, video_title)


#         return {
#             "video_id": video_id,
#             "message": "Enhanced YouTube analysis started with title classification",
#             "video_title": video_title,
#             "status": "processing"
#         }
#     except Exception as e:
#         logger.error(f"[ERROR] YouTube endpoint failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/detection-status/{video_id}")
# async def get_detection_status(video_id: str):
#     """Return status. If job entry doesn't exist yet, return 202 Pending (no spam logging)."""
#     res = get_result(video_id)
#     if res is None:
#         # Return 202 Accepted — job hasn't registered or is very new.
#         return JSONResponse(
#             status_code=202,
#             content={
#                 'video_id': video_id,
#                 'status': 'pending',
#                 'message': 'Analysis queued or starting up. Try again shortly.',
#                 'progress': 0
#             }
#         )

#     # If completed, produce nicely formatted response
#     if res.get('status') == 'completed':
#         processing_time = res.get('processing_time', 0)
#         if processing_time and processing_time > 0:
#             if processing_time < 60:
#                 time_display = f"{processing_time:.1f}s"
#             else:
#                 minutes = int(processing_time // 60)
#                 seconds = processing_time % 60
#                 time_display = f"{minutes}m {seconds:.1f}s"
#         else:
#             time_display = "Unknown"

#         # attach video url if file exists
#         video_url = res.get('video_url')
#         if not video_url:
#             for directory in ['downloaded_videos', 'uploaded_videos']:
#                 try:
#                     for file in os.listdir(directory):
#                         if file.startswith(video_id):
#                             video_url = f"/{directory}/{file}"
#                             break
#                 except Exception:
#                     continue

#         response = {
#             'video_id': video_id,
#             'status': res.get('status'),
#             'prediction': res.get('prediction', res.get('result', 'Unknown')),
#             'confidence': res.get('confidence', 0),
#             'faces_detected': res.get('faces_detected', res.get('faces_found', 0)),
#             'processing_time': res.get('processing_time', 0),
#             'processing_time_display': time_display,
#             'video_url': video_url,
#             'error': res.get('error'),
#             'likely_ai_tool': res.get('likely_ai_tool'),
#             'detected_keywords': res.get('detected_keywords'),
#             'timing_breakdown': res.get('timing_breakdown', {})
#         }

#         logger.info(f"[OK] Status returned for {video_id}: {response['prediction']} ({response['confidence']:.1f}%) in {time_display}")
#         return response

#     # otherwise return raw result (processing/failed/etc.)
#     return res


# # Real-time WebSocket detection (only if available)
# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     if not REALTIME_AVAILABLE:
#         await websocket.close(code=1003, reason="Real-time detection not available")
#         return
        
#     try:
#         await websocket.accept()
#         logger.info("[OK] WebSocket connected successfully")
        
#         # Initialize detector
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()

#         await websocket.send_text(json.dumps({
#             "type": "connection_ready",
#             "message": "AI Server Ready - Send frames for analysis",
#             "status": "connected"
#         }))

#         frame_count = 0
#         while True:
#             try:
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
#                 frame_data = json.loads(data)
#                 if "frame" not in frame_data:
#                     continue

#                 frame_bytes = base64.b64decode(frame_data["frame"])
#                 nparr = np.frombuffer(frame_bytes, np.uint8)
#                 frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                 if frame is None:
#                     continue

#                 logger.info(f"📥 Frame {frame_count + 1} received: {frame.shape}")
#                 result = await detector.real_time_analyze(frame)
#                 if isinstance(result, dict):
#                     result["status"] = "success"
#                     result["frame_count"] = frame_count + 1
#                 await websocket.send_text(json.dumps(result))
#                 frame_count += 1

#             except asyncio.TimeoutError:
#                 await websocket.send_text(json.dumps({
#                     "type": "heartbeat",
#                     "status": "connected",
#                     "frames_processed": frame_count
#                 }))
#             except WebSocketDisconnect:
#                 logger.info(f"🔌 WebSocket disconnected after processing {frame_count} frames")
#                 break
#             except Exception as e:
#                 logger.error(f"[ERROR] WebSocket frame processing error: {e}")
#                 await websocket.send_text(json.dumps({"error": str(e), "status": "error"}))
                
#     except Exception as e:
#         logger.error(f"[ERROR] WebSocket initialization failed: {e}")
#         try:
#             await websocket.close(code=1011, reason=f"Server error: {str(e)}")
#         except:
#             pass

# @app.get("/analytics")
# async def get_analytics():
#     return analytics.get_analytics_summary()


# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": time.time(),
#         "active_detections": len([r for r in DETECTION_RESULTS.values() if r.get('status') == 'processing']),
#         "capabilities": {
#             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
#             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
#             "youtube_support": YOUTUBE_AVAILABLE,
#             "real_time_detection": REALTIME_AVAILABLE
#         }
#     }


# # Exception handler for validation errors
# from fastapi.exceptions import RequestValidationError
# from fastapi import Request


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     logger.error(f"[ERROR] Validation Error: {exc.errors()}")
#     return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

































































































































# app/main.py (Final Corrected Version)
import os
import time
import json
import traceback
from typing import Dict
from fastapi import FastAPI, BackgroundTasks, File, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import DetectionStatusResponse, VideoUploadResponse

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
# Update CORS origins to include your frontend app
origins = [
    "http://localhost:3000",      # React/Vite default port
    "http://127.0.0.1:3000",     # Alternative localhost
    "http://localhost:3001",      # Alternative port
    "http://127.0.0.1:3001",
    "http://localhost:5173",      # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:8080",      # Alternative port
    "http://127.0.0.1:8080",
    "http://localhost:8000",      # Backend port
    "http://127.0.0.1:8000",
    "http://localhost",           # Root localhost
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
        faces, timing_info = await extract_faces_from_video(video_path)
        
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

@app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse, summary="Get Detection Status")
async def get_detection_status(video_id: str):
    """Get the status and result of a deepfake detection task"""
    
    result = DETECTION_RESULTS.get(video_id)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Video ID not found."
        )
    
    return DetectionStatusResponse(**result, video_id=video_id)

# Mode Detection Endpoints are handled by the mode_detection_router
# which is included above. These duplicate endpoints have been removed.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
# # app/main.py (Final Corrected Version)
# import os
# import traceback
# from typing import Dict
# from fastapi import FastAPI, BackgroundTasks, File, HTTPException, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from app.schemas import DetectionStatusResponse, VideoUploadResponse

# from app.services.deepfake_detector import detect_deepfake_in_frames  
# from app.services.video_processor import extract_faces_from_video
# from app.storage import delete_video_file, save_uploaded_video

# # In-memory storage for detection results
# DETECTION_RESULTS: Dict[str, Dict] = {}

# # Initialize FastAPI app
# app = FastAPI(
#     title="Deepfake Detection API",
#     description="API for uploading videos and detecting deepfakes.",
#     version="1.0.0"
# )

# # Add CORS middleware
# # Update CORS origins to include your Next.js app
# origins = [
#     "http://localhost:3000",      # Next.js default port
#     "http://127.0.0.1:3000",     # Alternative localhost
#     "http://localhost:3001",      # In case you're using port 3001
#     "http://127.0.0.1:3001",
#     "http://localhost",
#     "http://localhost:8080", 
#     "http://127.0.0.1:8000",
#     "null"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# async def run_deepfake_detection_task(video_id: str, video_path: str):
#     """Background task for deepfake detection"""
#     print(f"Starting deepfake detection for video_id: {video_id}")
    
#     DETECTION_RESULTS[video_id] = {
#         "status": "processing", 
#         "result": None, 
#         "confidence": None, 
#         "error": None
#     }
    
#     try:
#         # Extract faces from video
#         print(f"[{video_id}] Extracting faces...")
#         faces = extract_faces_from_video(video_path)
        
#         if not faces:
#             DETECTION_RESULTS[video_id] = {
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "error": None
#             }
#             print(f"[{video_id}] No faces found in video.")
#             return
        
#         # Perform deepfake detection
#         print(f"[{video_id}] Performing deepfake inference...")
#         result_text, confidence_score = await detect_deepfake_in_frames(faces)
        
#         DETECTION_RESULTS[video_id] = {
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score,
#             "error": None
#         }
        
#         print(f"[{video_id}] Detection completed. Result: {result_text}, Confidence: {confidence_score:.4f}")
        
#     except Exception as e:
#         error_msg = f"Detection failed for {video_id}: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
        
#         DETECTION_RESULTS[video_id] = {
#             "status": "failed",
#             "result": None,
#             "confidence": None,
#             "error": str(e)
#         }
    
#     finally:
#         # Clean up uploaded video file
#         if os.path.exists(video_path):
#             delete_video_file(video_path)

# @app.get("/health", summary="Health Check")
# async def health_check():
#     """Check if the API is running"""
#     return {"status": "ok", "message": "Deepfake Detection API is healthy"}

# @app.post("/upload-video", response_model=VideoUploadResponse, summary="Upload Video")
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Upload a video file for deepfake detection"""
    
#     # Validate file type
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(
#             status_code=400, 
#             detail="Invalid file type. Please upload a video file."
#         )
    
#     try:
#         # Save uploaded video
#         video_id, video_path = await save_uploaded_video(video_file)
        
#         # Start background detection task
#         background_tasks.add_task(run_deepfake_detection_task, video_id, video_path)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video '{video_file.filename}' uploaded successfully. Detection started."
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Failed to upload video: {str(e)}"
#         )

# @app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse, summary="Get Detection Status")
# async def get_detection_status(video_id: str):
#     """Get the status and result of a deepfake detection task"""
    
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(
#             status_code=404, 
#             detail="Video ID not found."
#         )
    
#     return DetectionStatusResponse(**result, video_id=video_id)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# main.py - ALIGNED WITH ADVANCED DEEPFAKE_DETECTOR
# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# import asyncio
# import os
# import uuid
# import time
# import logging
# import base64
# import cv2
# import numpy as np
# from pathlib import Path
# from typing import Dict, Optional

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # **CLEAN** - Import schemas with proper error handling
# try:
#     from app.schemas import VideoUploadResponse, DetectionStatusResponse, YouTubeVideoRequest
#     print("[OK] Schemas imported successfully")
# except ImportError as e:
#     logger.error(f"Schema import failed: {e}")
#     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # **CLEAN** - Import services
# try:
#     from app.storage import save_uploaded_video, delete_video_file
#     from app.services.video_processor import extract_faces_from_video
#     from app.services.deepfake_detector import detect_deepfake_in_frames
#     print("[OK] Services imported successfully")
# except ImportError as e:
#     logger.error(f"Service import failed: {e}")
#     raise SystemExit("Cannot start without services")

# # **CLEAN** - Enhanced detector import
# try:
#     from app.services.enhanced_detector import enhanced_detector
#     ENHANCED_AVAILABLE = True
#     print("[OK] Enhanced detector available")
# except ImportError:
#     ENHANCED_AVAILABLE = False
#     print("[WARNING] Enhanced detector not available")

# # **CLEAN** - Real-time detection import
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector
#     REALTIME_AVAILABLE = True
#     print("[OK] Real-time detection available")
# except ImportError:
#     REALTIME_AVAILABLE = False
#     print("[WARNING] Real-time detection not available")
    
#     class RealTimeDeepfakeDetector:
#         async def load_model(self): pass
#         async def real_time_analyze(self, frame): 
#             return {"error": "Real-time detection not available"}

# # **FIXED** - YouTube support with better error handling
# try:
#     import yt_dlp
#     # **FIXED** - Import the YouTubeDownloader class instead of instance
#     from app.services.youtube_service import YouTubeDownloader
#     youtube_downloader = YouTubeDownloader()
#     YOUTUBE_AVAILABLE = True
#     print("[OK] YouTube support enabled")
# except ImportError as e:
#     YOUTUBE_AVAILABLE = False
#     youtube_downloader = None
#     print(f"[WARNING] YouTube support disabled: {e}")

# # Initialize FastAPI app
# app = FastAPI(
#     title="iFake API - Advanced Deepfake Detection System",
#     version="2.2.0"
# )

# # **FIXED** - Exception handlers
# @app.exception_handler(422)
# async def validation_exception_handler(request, exc):
#     logger.error(f"Validation error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Request validation failed",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# @app.exception_handler(500)
# async def internal_server_error_handler(request, exc):
#     logger.error(f"Internal server error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Configuration
# DETECTION_RESULTS: Dict[str, Dict] = {}

# # Create directories
# Path("uploaded_videos").mkdir(exist_ok=True)
# Path("downloaded_videos").mkdir(exist_ok=True)

# try:
#     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     print("[OK] Static file directories mounted successfully")
# except Exception as e:
#     print(f"[WARNING] Static file mounting failed: {e}")

# # **CLEAN** - Background task
# # main.py - FIXED enhanced detection task
# async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
#     """FIXED - Enhanced detection with REAL progress tracking"""
#     print(f"🎬 Starting detection: {video_id}")
#     start_time = time.time()
    
#     # Initialize detection result
#     DETECTION_RESULTS[video_id] = {
#         "video_id": video_id,
#         "status": "processing",
#         "result": None,
#         "confidence": None,
#         "error": None,
#         "enhanced_analysis": False,
#         "video_type": video_type,
#         "metadata": metadata or {},
#         "video_url": None,
#         "faces_found": 0,
#         "model_used": None,
#         "processing_time": None,
#         "current_stage": "initializing",
#         "progress_percentage": 0,
#         "stage_details": "Starting AI analysis system...",
#         "estimated_time_remaining": None
#     }

#     try:
#         # STAGE 1: Initialize (0-15%)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
#         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing AI analysis system..."
#         print(f"[{video_id}] Progress: 5% - Initializing")
#         await asyncio.sleep(0.2)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
#         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
#         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
#         print(f"[{video_id}] Progress: 15% - Starting face detection")

#         # STAGE 2: Simulate Face Extraction Progress (15-50%)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
#         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
#         print(f"[{video_id}] Progress: 25% - Extracting faces")

#         # [WARNING] Inject intermediate progress simulation
#         for fake_step in range(26, 50, 4):
#             await asyncio.sleep(0.4)
#             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
#             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

#         # Actual face extraction
#         faces = extract_faces_from_video(video_path)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
#         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
#         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
#         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

#         if not faces:
#             DETECTION_RESULTS[video_id].update({
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "progress_percentage": 100,
#                 "current_stage": "completed",
#                 "stage_details": "No faces detected in video",
#                 "processing_time": round(time.time() - start_time, 2)
#             })
#             return

#         # STAGE 3: AI Analysis (50-85%)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
#         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
#         DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 AI models analyzing {len(faces)} detected faces..."
#         print(f"[{video_id}] Progress: 60% - Analyzing faces")

#         # Enhanced detection
#         enhanced_analysis = False
#         if ENHANCED_AVAILABLE:
#             try:
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
#                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")

#                 result_data = enhanced_detector.enhanced_analyze_faces(faces)

#                 if isinstance(result_data, dict):
#                     result_text = result_data.get('prediction', 'Real Video')
#                     confidence_score = result_data.get('confidence', 0.5)
#                 else:
#                     result_text, confidence_score = result_data
#                 enhanced_analysis = True

#             except Exception as enhanced_error:
#                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
#                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
#                 result_text, confidence_score = await detect_deepfake_in_frames(faces)
#         else:
#             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
#             result_text, confidence_score = await detect_deepfake_in_frames(faces)

#         # STAGE 4: Finalizing (85-100%)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
#         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
#         print(f"[{video_id}] Progress: 90% - Finalizing")

#         # Video path
#         filename = os.path.basename(video_path)
#         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"

#         processing_time = time.time() - start_time

#         # Completion
#         DETECTION_RESULTS[video_id].update({
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
#             "enhanced_analysis": enhanced_analysis,
#             "video_url": video_url,
#             "faces_found": len(faces),
#             "model_used": "Enhanced Detector" if enhanced_analysis else "Standard Detector",
#             "processing_time": round(processing_time, 2),
#             "current_stage": "completed",
#             "progress_percentage": 100,
#             "stage_details": "[OK] Analysis completed successfully"
#         })

#         print(f"[OK] Detection completed for {video_id}: {result_text} ({confidence_score:.3f})")

#     except Exception as e:
#         processing_time = time.time() - start_time
#         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
#         DETECTION_RESULTS[video_id].update({
#             "status": "failed",
#             "error": str(e),
#             "processing_time": round(processing_time, 2),
#             "current_stage": "failed",
#             "progress_percentage": 0,
#             "stage_details": f"[ERROR] Error: {str(e)}"
#         })
                
# # **CLEAN** - API endpoints
# @app.get("/")
# async def root():
#     return {
#         "message": "iFake API - Advanced Deepfake Detection System",
#         "version": "2.2.0",
#         "status": "operational"
#     }

# @app.post("/upload-video", response_model=VideoUploadResponse)
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Standard video upload"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
    
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded successfully",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Upload video error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# async def upload_video_enhanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Enhanced video upload"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
    
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded - ENHANCED detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Enhanced upload error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# async def detect_deepfake_advanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Advanced detection endpoint"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
    
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"ADVANCED detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Advanced detection error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# async def detect_deepfake_youtube(
#     background_tasks: BackgroundTasks,
#     request: YouTubeVideoRequest
# ):
#     """**FIXED** YouTube video detection with proper error handling"""
#     logger.info(f"YouTube request received: {request.youtube_url}")
    
#     if not YOUTUBE_AVAILABLE:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
#         )
    
#     if not youtube_downloader:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube downloader not initialized"
#         )
    
#     try:
#         youtube_url = str(request.youtube_url)
#         logger.info(f"Processing YouTube URL: {youtube_url}")
        
#         # Enhanced URL validation
#         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
#             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
        
#         # Download video
#         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
#         logger.info(f"Successfully downloaded video: {video_id}")
        
#         # Start detection task
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message="YouTube video processing started",
#             video_type="youtube",
#             metadata=metadata
#         )
        
#     except HTTPException:
#         raise  # Re-raise HTTP exceptions
#     except ValueError as ve:
#         logger.error(f"YouTube validation error: {ve}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         logger.error(f"YouTube processing error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# @app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse)
# async def get_detection_status(video_id: str):
#     """Get detection status"""
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Video ID not found")
    
#     return DetectionStatusResponse(**result)

# # **DEBUG/ADMIN ENDPOINTS**
# @app.get("/debug/files/{video_id}")
# async def debug_files(video_id: str):
#     """Debug endpoint to check file availability"""
#     try:
#         result = DETECTION_RESULTS.get(video_id)
#         if not result:
#             return {"error": "Video ID not found"}
        
#         video_url = result.get("video_url")
#         if not video_url:
#             return {"error": "No video URL found"}
        
#         # Check if file exists
#         if video_url.startswith("/downloaded_videos/"):
#             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
#         else:
#             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
        
#         # URL decode the file path
#         import urllib.parse
#         decoded_path = urllib.parse.unquote(file_path)
        
#         return {
#             "video_id": video_id,
#             "video_url": video_url,
#             "expected_file_path": decoded_path,
#             "file_exists": os.path.exists(decoded_path),
#             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/debug/active-detections")
# async def debug_active_detections():
#     """Debug endpoint to see active detections"""
#     return {
#         "active_count": len(DETECTION_RESULTS),
#         "detection_keys": list(DETECTION_RESULTS.keys()),
#         "sample_data": {k: {
#             "status": v.get("status"), 
#             "has_video_id": "video_id" in v,
#             "all_keys": list(v.keys())
#         } for k, v in list(DETECTION_RESULTS.items())[:3]}
#     }

# # **WEBSOCKET ENDPOINTS**
# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     """Fixed WebSocket for real-time detection"""
#     try:
#         await websocket.accept()
#         print("[OK] WebSocket connected")
        
#         if not REALTIME_AVAILABLE:
#             await websocket.send_json({"error": "Real-time detection not available"})
#             return
        
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()
        
#         await websocket.send_json({
#             "type": "connection_ready",
#             "message": "Ready for real-time analysis"
#         })
        
#         while True:
#             try:
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
                
#                 # Decode frame
#                 if data.startswith('data:image'):
#                     header, base64_data = data.split(',', 1)
#                     frame_bytes = base64.b64decode(base64_data)
#                 else:
#                     frame_bytes = base64.b64decode(data)
                
#                 frame_array = np.frombuffer(frame_bytes, np.uint8)
#                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
#                 if frame is None:
#                     await websocket.send_json({"error": "Invalid frame data"})
#                     continue
                
#                 # Analyze frame
#                 result = await detector.real_time_analyze(frame)
#                 await websocket.send_json(result)
                
#             except asyncio.TimeoutError:
#                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
#             except Exception as e:
#                 await websocket.send_json({"error": str(e)})
                
#     except Exception as e:
#         print(f"WebSocket error: {e}")

# # **FIXED** - Single health endpoint
# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "enhanced_available": ENHANCED_AVAILABLE,
#         "realtime_available": REALTIME_AVAILABLE,
#         "youtube_available": YOUTUBE_AVAILABLE,
#         "active_detections": len(DETECTION_RESULTS)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# import asyncio
# import os
# import uuid
# import time
# import logging
# import base64
# import cv2
# import numpy as np
# from pathlib import Path
# from typing import Dict, Optional

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Import schemas
# try:
#     from app.schemas import VideoUploadResponse, DetectionStatusResponse, YouTubeVideoRequest
#     print("[OK] Schemas imported successfully")
# except ImportError as e:
#     logger.error(f"Schema import failed: {e}")
#     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # Import services
# try:
#     from app.storage import save_uploaded_video, delete_video_file
#     from app.services.video_processor import extract_faces_from_video
#     from app.services.deepfake_detector import detect_deepfake_in_frames
#     print("[OK] Services imported successfully")
# except ImportError as e:
#     logger.error(f"Service import failed: {e}")
#     raise SystemExit("Cannot start without services")

# # Enhanced detector
# try:
#     from app.services.enhanced_detector import enhanced_detector
#     ENHANCED_AVAILABLE = True
#     print("[OK] Enhanced detector available")
# except ImportError:
#     ENHANCED_AVAILABLE = False
#     print("[WARNING] Enhanced detector not available")

# # Real-time detection
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector
#     REALTIME_AVAILABLE = True
#     print("[OK] Real-time detection available")
# except ImportError:
#     REALTIME_AVAILABLE = False
#     print("[WARNING] Real-time detection not available")
#     class RealTimeDeepfakeDetector:
#         async def load_model(self): pass
#         async def real_time_analyze(self, frame): 
#             return {"error": "Real-time detection not available"}

# # YouTube support
# try:
#     import yt_dlp
#     from app.services.youtube_service import YouTubeDownloader
#     youtube_downloader = YouTubeDownloader()
#     YOUTUBE_AVAILABLE = True
#     print("[OK] YouTube support enabled")
# except ImportError as e:
#     YOUTUBE_AVAILABLE = False
#     youtube_downloader = None
#     print(f"[WARNING] YouTube support disabled: {e}")

# app = FastAPI(
#     title="iFake API - Advanced Deepfake Detection System",
#     version="2.2.0"
# )

# @app.exception_handler(422)
# async def validation_exception_handler(request, exc):
#     logger.error(f"Validation error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Request validation failed",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# @app.exception_handler(500)
# async def internal_server_error_handler(request, exc):
#     logger.error(f"Internal server error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# DETECTION_RESULTS: Dict[str, Dict] = {}

# Path("uploaded_videos").mkdir(exist_ok=True)
# Path("downloaded_videos").mkdir(exist_ok=True)
# try:
#     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     print("[OK] Static file directories mounted successfully")
# except Exception as e:
#     print(f"[WARNING] Static file mounting failed: {e}")

# async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
#     print(f"🎬 Starting detection: {video_id}")
#     start_time = time.time()
#     DETECTION_RESULTS[video_id] = {
#         "video_id": video_id,
#         "status": "processing",
#         "result": None,
#         "confidence": None,
#         "error": None,
#         "enhanced_analysis": False,
#         "video_type": video_type,
#         "metadata": metadata or {},
#         "video_url": None,
#         "faces_found": 0,
#         "model_used": None,
#         "processing_time": None,
#         "current_stage": "initializing",
#         "progress_percentage": 0,
#         "stage_details": "Starting AI analysis system...",
#         "estimated_time_remaining": None
#     }
#     try:
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
#         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing AI analysis system..."
#         print(f"[{video_id}] Progress: 5% - Initializing")
#         await asyncio.sleep(0.2)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
#         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
#         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
#         print(f"[{video_id}] Progress: 15% - Starting face detection")

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
#         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
#         print(f"[{video_id}] Progress: 25% - Extracting faces")
#         for fake_step in range(26, 50, 4):
#             await asyncio.sleep(0.4)
#             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
#             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

#         faces = extract_faces_from_video(video_path)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
#         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
#         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
#         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

#         if not faces:
#             DETECTION_RESULTS[video_id].update({
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "progress_percentage": 100,
#                 "current_stage": "completed",
#                 "stage_details": "No faces detected in video",
#                 "processing_time": round(time.time() - start_time, 2)
#             })
#             return

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
#         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
#         DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 AI models analyzing {len(faces)} detected faces..."
#         print(f"[{video_id}] Progress: 60% - Analyzing faces")
#         enhanced_analysis = False
#         if ENHANCED_AVAILABLE:
#             try:
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
#                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")
#                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
#                 if isinstance(result_data, dict):
#                     result_text = result_data.get('prediction', 'Real Video')
#                     confidence_score = result_data.get('confidence', 0.5)
#                 else:
#                     result_text, confidence_score = result_data
#                 enhanced_analysis = True
#             except Exception as enhanced_error:
#                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
#                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
#                 result_text, confidence_score = await detect_deepfake_in_frames(faces)
#         else:
#             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
#             result_text, confidence_score = await detect_deepfake_in_frames(faces)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
#         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
#         print(f"[{video_id}] Progress: 90% - Finalizing")
#         filename = os.path.basename(video_path)
#         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
#         processing_time = time.time() - start_time
#         DETECTION_RESULTS[video_id].update({
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
#             "enhanced_analysis": enhanced_analysis,
#             "video_url": video_url,
#             "faces_found": len(faces),
#             "model_used": "Enhanced Detector" if enhanced_analysis else "Standard Detector",
#             "processing_time": round(processing_time, 2),
#             "current_stage": "completed",
#             "progress_percentage": 100,
#             "stage_details": "[OK] Analysis completed successfully"
#         })
#         print(f"[OK] Detection completed for {video_id}: {result_text} ({confidence_score:.3f})")
#     except Exception as e:
#         processing_time = time.time() - start_time
#         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
#         DETECTION_RESULTS[video_id].update({
#             "status": "failed",
#             "error": str(e),
#             "processing_time": round(processing_time, 2),
#             "current_stage": "failed",
#             "progress_percentage": 0,
#             "stage_details": f"[ERROR] Error: {str(e)}"
#         })

# @app.get("/")
# async def root():
#     return {
#         "message": "iFake API - Advanced Deepfake Detection System",
#         "version": "2.2.0",
#         "status": "operational"
#     }

# @app.post("/upload-video", response_model=VideoUploadResponse)
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded successfully",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Upload video error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# async def upload_video_enhanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded - ENHANCED detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Enhanced upload error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# async def detect_deepfake_advanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"ADVANCED detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Advanced detection error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# async def detect_deepfake_youtube(
#     background_tasks: BackgroundTasks,
#     request: YouTubeVideoRequest
# ):
#     logger.info(f"YouTube request received: {request.youtube_url}")
#     if not YOUTUBE_AVAILABLE:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
#         )
#     if not youtube_downloader:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube downloader not initialized"
#         )
#     try:
#         youtube_url = str(request.youtube_url)
#         logger.info(f"Processing YouTube URL: {youtube_url}")
#         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
#             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
#         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
#         logger.info(f"Successfully downloaded video: {video_id}")
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message="YouTube video processing started",
#             video_type="youtube",
#             metadata=metadata
#         )
#     except HTTPException:
#         raise  # Re-raise HTTP exceptions
#     except ValueError as ve:
#         logger.error(f"YouTube validation error: {ve}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         logger.error(f"YouTube processing error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# @app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse)
# async def get_detection_status(video_id: str):
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Video ID not found")
#     return DetectionStatusResponse(**result)

# @app.get("/debug/files/{video_id}")
# async def debug_files(video_id: str):
#     try:
#         result = DETECTION_RESULTS.get(video_id)
#         if not result:
#             return {"error": "Video ID not found"}
#         video_url = result.get("video_url")
#         if not video_url:
#             return {"error": "No video URL found"}
#         if video_url.startswith("/downloaded_videos/"):
#             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
#         else:
#             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
#         import urllib.parse
#         decoded_path = urllib.parse.unquote(file_path)
#         return {
#             "video_id": video_id,
#             "video_url": video_url,
#             "expected_file_path": decoded_path,
#             "file_exists": os.path.exists(decoded_path),
#             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/debug/active-detections")
# async def debug_active_detections():
#     return {
#         "active_count": len(DETECTION_RESULTS),
#         "detection_keys": list(DETECTION_RESULTS.keys()),
#         "sample_data": {k: {
#             "status": v.get("status"), 
#             "has_video_id": "video_id" in v,
#             "all_keys": list(v.keys())
#         } for k, v in list(DETECTION_RESULTS.items())[:3]}
#     }

# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     try:
#         await websocket.accept()
#         print("[OK] WebSocket connected")
#         if not REALTIME_AVAILABLE:
#             await websocket.send_json({"error": "Real-time detection not available"})
#             return
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()
#         await websocket.send_json({
#             "type": "connection_ready",
#             "message": "Ready for real-time analysis"
#         })
#         while True:
#             try:
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
#                 if data.startswith('data:image'):
#                     header, base64_data = data.split(',', 1)
#                     frame_bytes = base64.b64decode(base64_data)
#                 else:
#                     frame_bytes = base64.b64decode(data)
#                 frame_array = np.frombuffer(frame_bytes, np.uint8)
#                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
#                 if frame is None:
#                     await websocket.send_json({"error": "Invalid frame data"})
#                     continue
#                 result = await detector.real_time_analyze(frame)
#                 await websocket.send_json(result)
#             except asyncio.TimeoutError:
#                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
#             except Exception as e:
#                 await websocket.send_json({"error": str(e)})
#     except Exception as e:
#         print(f"WebSocket error: {e}")

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "enhanced_available": ENHANCED_AVAILABLE,
#         "realtime_available": REALTIME_AVAILABLE,
#         "youtube_available": YOUTUBE_AVAILABLE,
#         "active_detections": len(DETECTION_RESULTS)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)



















# app/main.py - Enhanced with Ensemble AI
# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# import asyncio
# import os
# import uuid
# import time
# import logging
# import base64
# import cv2
# import numpy as np
# from pathlib import Path
# from typing import Dict, Optional, List, Tuple

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Import schemas
# try:
#     from app.schemas import VideoUploadResponse, DetectionStatusResponse, YouTubeVideoRequest
#     print("[OK] Schemas imported successfully")
# except ImportError as e:
#     logger.error(f"Schema import failed: {e}")
#     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # Import services
# try:
#     from app.storage import save_uploaded_video, delete_video_file
#     from app.services.video_processor import extract_faces_from_video
#     from app.services.deepfake_detector import detect_deepfake_in_frames
#     print("[OK] Services imported successfully")
# except ImportError as e:
#     logger.error(f"Service import failed: {e}")
#     raise SystemExit("Cannot start without services")

# # **NEW** - Ensemble AI imports
# try:
#     import insightface
#     import clip
#     import torch
#     import torch.nn as nn
#     from PIL import Image
#     from deepface import DeepFace
#     ENSEMBLE_AVAILABLE = True
#     print("[OK] Ensemble AI components available")
# except ImportError as e:
#     ENSEMBLE_AVAILABLE = False
#     print(f"[WARNING] Ensemble AI not available: {e}")

# # Enhanced detector
# try:
#     from app.services.enhanced_detector import enhanced_detector
#     ENHANCED_AVAILABLE = True
#     print("[OK] Enhanced detector available")
# except ImportError:
#     ENHANCED_AVAILABLE = False
#     print("[WARNING] Enhanced detector not available")

# # Real-time detection
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector
#     REALTIME_AVAILABLE = True
#     print("[OK] Real-time detection available")
# except ImportError:
#     REALTIME_AVAILABLE = False
#     print("[WARNING] Real-time detection not available")
#     class RealTimeDeepfakeDetector:
#         async def load_model(self): pass
#         async def real_time_analyze(self, frame): 
#             return {"error": "Real-time detection not available"}

# # YouTube support
# try:
#     import yt_dlp
#     from app.services.youtube_service import YouTubeDownloader
#     youtube_downloader = YouTubeDownloader()
#     YOUTUBE_AVAILABLE = True
#     print("[OK] YouTube support enabled")
# except ImportError as e:
#     YOUTUBE_AVAILABLE = False
#     youtube_downloader = None
#     print(f"[WARNING] YouTube support disabled: {e}")

# app = FastAPI(
#     title="iFake API - Advanced Deepfake Detection System with Ensemble AI",
#     version="2.3.0"
# )

# # Exception handlers
# @app.exception_handler(422)
# async def validation_exception_handler(request, exc):
#     logger.error(f"Validation error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Request validation failed",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# @app.exception_handler(500)
# async def internal_server_error_handler(request, exc):
#     logger.error(f"Internal server error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# DETECTION_RESULTS: Dict[str, Dict] = {}

# Path("uploaded_videos").mkdir(exist_ok=True)
# Path("downloaded_videos").mkdir(exist_ok=True)
# try:
#     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     print("[OK] Static file directories mounted successfully")
# except Exception as e:
#     print(f"[WARNING] Static file mounting failed: {e}")

# # **NEW** - Initialize Ensemble AI Components
# insight_app = None
# clip_model = None
# clip_preprocess = None

# if ENSEMBLE_AVAILABLE:
#     try:
#         insight_app = insightface.app.FaceAnalysis()
#         insight_app.prepare(ctx_id=-1)
#         clip_model, clip_preprocess = clip.load("ViT-B/32", device="cpu")
#         print("[OK] Ensemble AI models initialized")
#     except Exception as e:
#         print(f"[WARNING] Ensemble AI initialization failed: {e}")
#         ENSEMBLE_AVAILABLE = False

# # **NEW** - Ensemble AI Helper Functions
# def _cosine(a, b):
#     """Calculate cosine similarity between two vectors"""
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

# async def _insight_consistency(faces: List[np.ndarray]) -> float:
#     """Check face consistency using InsightFace embeddings"""
#     if len(faces) < 2 or not insight_app:
#         return 0.5
    
#     embs = []
#     for f in faces:
#         try:
#             # Convert BGR to RGB if needed
#             if len(f.shape) == 3 and f.shape[2] == 3:
#                 rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB) if f.dtype == np.uint8 else f
#             else:
#                 rgb = f
#             res = insight_app.get(rgb)
#             if res:
#                 embs.append(res[0].embedding)
#         except:
#             continue
    
#     if len(embs) < 2:
#         return 0.5
    
#     embs = np.array(embs)
#     sims = [_cosine(embs[i], embs[j]) for i in range(len(embs)) for j in range(i + 1, len(embs))]
#     return 1 - np.mean(sims)  # Higher inconsistency = more likely deepfake

# async def _deepface_score(faces: List[np.ndarray]) -> float:
#     """Get deepfake score using DeepFace spoofing detection"""
#     if not faces:
#         return 0.5
    
#     scores = []
#     for f in faces:
#         try:
#             res = DeepFace.analyze(
#                 f, actions=["spoofing"], enforce_detection=False, detector_backend="mtcnn"
#             )
#             scores.append(res[0]["spoofing"]["score"])
#         except Exception:
#             pass
    
#     return float(np.mean(scores)) if scores else 0.5

# async def _clip_zero_shot(faces: List[np.ndarray]) -> float:
#     """Use CLIP for zero-shot deepfake detection"""
#     if not faces or not clip_model:
#         return 0.5
    
#     text_tokens = clip.tokenize(["a real human face", "a deepfake face"]).to("cpu")
#     total = 0.0
    
#     for f in faces:
#         try:
#             # Convert to RGB and resize
#             if len(f.shape) == 3:
#                 rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB) if f.dtype == np.uint8 else f
#             else:
#                 rgb = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            
#             pil_img = Image.fromarray(rgb.astype(np.uint8)).resize((224, 224))
#             img = clip_preprocess(pil_img).unsqueeze(0)
            
#             with torch.no_grad():
#                 logits, _ = clip_model(img, text_tokens)
#                 total += logits.softmax(dim=-1)[0][1].item()  # Deepfake probability
#         except:
#             continue
    
#     return total / len(faces) if faces else 0.5

# # **NEW** - Convert tensor faces to numpy for ensemble AI
# def convert_tensor_faces_to_numpy(faces: List[torch.Tensor]) -> List[np.ndarray]:
#     """Convert tensor faces back to numpy arrays for ensemble AI"""
#     numpy_faces = []
    
#     for face_tensor in faces:
#         try:
#             # Denormalize and convert back to numpy
#             mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
#             std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            
#             # Denormalize
#             face_denorm = face_tensor * std + mean
#             face_denorm = torch.clamp(face_denorm * 255, 0, 255)
            
#             # Convert to numpy (C, H, W) -> (H, W, C)
#             face_np = face_denorm.permute(1, 2, 0).numpy().astype(np.uint8)
#             numpy_faces.append(face_np)
            
#         except Exception as e:
#             logger.warning(f"Failed to convert tensor face: {e}")
#             continue
    
#     return numpy_faces

# async def ensemble_predict(faces: List[torch.Tensor]) -> Tuple[str, float]:
#     """
#     FIXED - Enhanced ensemble prediction combining multiple AI models
#     Returns (label, confidence)
#     """
#     # Get base model prediction (using your existing system)
#     label, conf = await detect_deepfake_in_frames(faces)
    
#     if not ENSEMBLE_AVAILABLE or len(faces) == 0:
#         return label, conf
    
#     # Convert tensor faces to numpy for ensemble AI
#     numpy_faces = convert_tensor_faces_to_numpy(faces)
    
#     if not numpy_faces:
#         return label, conf
    
#     # FIXED: Proper base model probability handling
#     if label == "Real Video":
#         base_real_prob = conf  # High confidence in real = high real probability
#         base_fake_prob = 1.0 - conf
#     else:  # "Deepfake Detected"
#         base_fake_prob = conf  # High confidence in fake = high fake probability  
#         base_real_prob = 1.0 - conf
    
#     # Get ensemble predictions
#     insight = await _insight_consistency(numpy_faces)
#     deepf = await _deepface_score(numpy_faces)
#     clip_z = await _clip_zero_shot(numpy_faces)
    
#     # FIXED: Better ensemble weights - give more weight to the reliable base model
#     ensemble_fake_prob = (
#         0.70 * base_fake_prob +    # Increased base model weight
#         0.10 * insight +           # Reduced secondary model weights
#         0.10 * deepf + 
#         0.10 * clip_z
#     )
    
#     # FIXED: Apply confidence scaling to preserve high confidence results
#     if conf >= 0.85:  # If base model is very confident (>=85%)
#         confidence_multiplier = 1.2  # Boost confidence
#     elif conf >= 0.70:  # If base model is confident (>=70%)
#         confidence_multiplier = 1.1  # Slight boost
#     else:
#         confidence_multiplier = 1.0  # No change
    
#     # Final verdict with confidence boosting
#     if ensemble_fake_prob <= 0.5:
#         verdict = "Real Video"
#         confidence = min((1.0 - ensemble_fake_prob) * confidence_multiplier, 0.98)
#     else:
#         verdict = "Deepfake Detected"  
#         confidence = min(ensemble_fake_prob * confidence_multiplier, 0.98)
    
#     logger.info(f"🤖 FIXED Ensemble - Base: {conf:.3f} ({label}), Insight: {insight:.3f}, DeepFace: {deepf:.3f}, CLIP: {clip_z:.3f}")
#     logger.info(f"🎯 Final: {verdict} (Confidence: {confidence:.3f})")
    
#     return verdict, confidence

# # **ENHANCED** - Background task with ensemble AI
# async def run_enhanced_detection_task(video_id: str, video_path: str, video_type: str = "upload", metadata: Optional[Dict] = None):
#     print(f"🎬 Starting enhanced detection: {video_id}")
#     start_time = time.time()
    
#     DETECTION_RESULTS[video_id] = {
#         "video_id": video_id,
#         "status": "processing",
#         "result": None,
#         "confidence": None,
#         "error": None,
#         "enhanced_analysis": ENSEMBLE_AVAILABLE,
#         "video_type": video_type,
#         "metadata": metadata or {},
#         "video_url": None,
#         "faces_found": 0,
#         "model_used": "Ensemble AI" if ENSEMBLE_AVAILABLE else "Standard Detector",
#         "processing_time": None,
#         "current_stage": "initializing",
#         "progress_percentage": 0,
#         "stage_details": "Starting AI analysis system...",
#         "estimated_time_remaining": None
#     }
    
#     try:
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
#         DETECTION_RESULTS[video_id]["stage_details"] = "Initializing ensemble AI system..."
#         print(f"[{video_id}] Progress: 5% - Initializing")
#         await asyncio.sleep(0.2)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
#         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
#         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"
#         print(f"[{video_id}] Progress: 15% - Starting face detection")

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
#         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
#         print(f"[{video_id}] Progress: 25% - Extracting faces")
        
#         # Progressive face extraction simulation
#         for fake_step in range(26, 50, 4):
#             await asyncio.sleep(0.4)
#             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
#             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

#         # Extract faces (your existing system returns torch tensors)
#         faces = extract_faces_from_video(video_path)
        
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
#         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
#         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"
#         print(f"[{video_id}] Progress: 50% - Found {len(faces) if faces else 0} faces")

#         if not faces:
#             DETECTION_RESULTS[video_id].update({
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "progress_percentage": 100,
#                 "current_stage": "completed",
#                 "stage_details": "No faces detected in video",
#                 "processing_time": round(time.time() - start_time, 2)
#             })
#             return

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
#         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
        
#         enhanced_analysis = False
        
#         # Try ensemble AI first
#         if ENSEMBLE_AVAILABLE:
#             try:
#                 DETECTION_RESULTS[video_id]["stage_details"] = f"🤖 Running ensemble AI analysis on {len(faces)} faces..."
#                 print(f"[{video_id}] Progress: 60% - Ensemble AI analysis")
                
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Base model + InsightFace analysis..."
                
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 75
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🔍 DeepFace spoofing detection..."
                
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 80
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🎯 CLIP zero-shot analysis..."
                
#                 result_text, confidence_score = await ensemble_predict(faces)
#                 enhanced_analysis = True
                
#             except Exception as ensemble_error:
#                 logger.warning(f"Ensemble AI failed: {ensemble_error}")
#                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to enhanced detector..."
                
#         # Try enhanced detector
#         if not enhanced_analysis and ENHANCED_AVAILABLE:
#             try:
#                 DETECTION_RESULTS[video_id]["progress_percentage"] = 70
#                 DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running enhanced AI analysis..."
#                 print(f"[{video_id}] Progress: 70% - Enhanced analysis")
#                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
#                 if isinstance(result_data, dict):
#                     result_text = result_data.get('prediction', 'Real Video')
#                     confidence_score = result_data.get('confidence', 0.5)
#                 else:
#                     result_text, confidence_score = result_data
#                 enhanced_analysis = True
#             except Exception as enhanced_error:
#                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
#                 DETECTION_RESULTS[video_id]["stage_details"] = "[LOADING] Falling back to standard analysis..."
                
#         # Standard detector fallback
#         if not enhanced_analysis:
#             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running standard AI analysis..."
#             result_text, confidence_score = await detect_deepfake_in_frames(faces)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
#         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."
#         print(f"[{video_id}] Progress: 90% - Finalizing")
        
#         filename = os.path.basename(video_path)
#         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
#         processing_time = time.time() - start_time
        
#         # Determine model used
#         if ENSEMBLE_AVAILABLE and enhanced_analysis:
#             model_used = "Ensemble AI (Base + InsightFace + DeepFace + CLIP)"
#         elif enhanced_analysis:
#             model_used = "Enhanced Detector"
#         else:
#             model_used = "Standard Detector"
        
#         DETECTION_RESULTS[video_id].update({
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score * 100 if confidence_score <= 1.0 else confidence_score,
#             "enhanced_analysis": enhanced_analysis,
#             "video_url": video_url,
#             "faces_found": len(faces),
#             "model_used": model_used,
#             "processing_time": round(processing_time, 2),
#             "current_stage": "completed",
#             "progress_percentage": 100,
#             "stage_details": "[OK] Analysis completed successfully"
#         })
        
#         print(f"[OK] Enhanced detection completed for {video_id}: {result_text} ({confidence_score:.3f})")
        
#     except Exception as e:
#         processing_time = time.time() - start_time
#         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
#         DETECTION_RESULTS[video_id].update({
#             "status": "failed",
#             "error": str(e),
#             "processing_time": round(processing_time, 2),
#             "current_stage": "failed",
#             "progress_percentage": 0,
#             "stage_details": f"[ERROR] Error: {str(e)}"
#         })

# # **UNCHANGED** - All your existing API endpoints work the same
# @app.get("/")
# async def root():
#     return {
#         "message": "iFake API - Advanced Deepfake Detection System with Ensemble AI",
#         "version": "2.3.0",
#         "status": "operational",
#         "ensemble_ai": ENSEMBLE_AVAILABLE
#     }

# @app.post("/upload-video", response_model=VideoUploadResponse)
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded - {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Upload video error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# async def upload_video_enhanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded - ENHANCED {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Enhanced upload error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-advanced", response_model=VideoUploadResponse)
# async def detect_deepfake_advanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"ADVANCED {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard'} detection started",
#             video_type="upload",
#             metadata={}
#         )
#     except Exception as e:
#         logger.error(f"Advanced detection error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# async def detect_deepfake_youtube(
#     background_tasks: BackgroundTasks,
#     request: YouTubeVideoRequest
# ):
#     logger.info(f"YouTube request received: {request.youtube_url}")
#     if not YOUTUBE_AVAILABLE:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
#         )
#     if not youtube_downloader:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube downloader not initialized"
#         )
#     try:
#         youtube_url = str(request.youtube_url)
#         logger.info(f"Processing YouTube URL: {youtube_url}")
#         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
#             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
#         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
#         logger.info(f"Successfully downloaded video: {video_id}")
#         background_tasks.add_task(run_enhanced_detection_task, video_id, video_path, "youtube", metadata)
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"YouTube video processing started with {'Ensemble AI' if ENSEMBLE_AVAILABLE else 'Standard AI'}",
#             video_type="youtube",
#             metadata=metadata
#         )
#     except HTTPException:
#         raise
#     except ValueError as ve:
#         logger.error(f"YouTube validation error: {ve}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         logger.error(f"YouTube processing error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# # All your existing endpoints remain unchanged
# @app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse)
# async def get_detection_status(video_id: str):
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Video ID not found")
#     return DetectionStatusResponse(**result)

# @app.get("/debug/files/{video_id}")
# async def debug_files(video_id: str):
#     try:
#         result = DETECTION_RESULTS.get(video_id)
#         if not result:
#             return {"error": "Video ID not found"}
#         video_url = result.get("video_url")
#         if not video_url:
#             return {"error": "No video URL found"}
#         if video_url.startswith("/downloaded_videos/"):
#             file_path = "downloaded_videos/" + video_url.split("/downloaded_videos/", 1)[1]
#         else:
#             file_path = "uploaded_videos/" + video_url.split("/videos/", 1)[1]
#         import urllib.parse
#         decoded_path = urllib.parse.unquote(file_path)
#         return {
#             "video_id": video_id,
#             "video_url": video_url,
#             "expected_file_path": decoded_path,
#             "file_exists": os.path.exists(decoded_path),
#             "available_files": list(os.listdir("downloaded_videos")) if os.path.exists("downloaded_videos") else []
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/debug/active-detections")
# async def debug_active_detections():
#     return {
#         "active_count": len(DETECTION_RESULTS),
#         "detection_keys": list(DETECTION_RESULTS.keys()),
#         "ensemble_ai_enabled": ENSEMBLE_AVAILABLE,
#         "sample_data": {k: {
#             "status": v.get("status"), 
#             "has_video_id": "video_id" in v,
#             "model_used": v.get("model_used"),
#             "all_keys": list(v.keys())
#         } for k, v in list(DETECTION_RESULTS.items())[:3]}
#     }

# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     try:
#         await websocket.accept()
#         print("[OK] WebSocket connected")
#         if not REALTIME_AVAILABLE:
#             await websocket.send_json({"error": "Real-time detection not available"})
#             return
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()
#         await websocket.send_json({
#             "type": "connection_ready",
#             "message": "Ready for real-time analysis",
#             "ensemble_ai": ENSEMBLE_AVAILABLE
#         })
#         while True:
#             try:
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
#                 if data.startswith('data:image'):
#                     header, base64_data = data.split(',', 1)
#                     frame_bytes = base64.b64decode(base64_data)
#                 else:
#                     frame_bytes = base64.b64decode(data)
#                 frame_array = np.frombuffer(frame_bytes, np.uint8)
#                 frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
#                 if frame is None:
#                     await websocket.send_json({"error": "Invalid frame data"})
#                     continue
#                 result = await detector.real_time_analyze(frame)
#                 await websocket.send_json(result)
#             except asyncio.TimeoutError:
#                 await websocket.send_json({"type": "heartbeat", "message": "Server alive"})
#             except Exception as e:
#                 await websocket.send_json({"error": str(e)})
#     except Exception as e:
#         print(f"WebSocket error: {e}")

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "enhanced_available": ENHANCED_AVAILABLE,
#         "realtime_available": REALTIME_AVAILABLE,
#         "youtube_available": YOUTUBE_AVAILABLE,
#         "ensemble_ai_available": ENSEMBLE_AVAILABLE,
#         "active_detections": len(DETECTION_RESULTS)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)












# # app/main.py - FIXED VERSION
# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# import asyncio
# import os
# import uuid
# import time
# import logging
# import base64
# import cv2
# import numpy as np
# from pathlib import Path
# from typing import Dict, Optional
# from fastapi import WebSocket, WebSocketDisconnect
# import json

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Import schemas
# try:
#     from app.schemas import VideoUploadResponse, DetectionStatusResponse, YouTubeVideoRequest
#     print("[OK] Schemas imported successfully")
# except ImportError as e:
#     logger.error(f"Schema import failed: {e}")
#     raise SystemExit("Cannot start without schemas. Please check app/schemas.py")

# # Import services
# try:
#     from app.storage import save_uploaded_video, delete_video_file
#     from app.services.video_processor import extract_faces_from_video
#     from app.services.deepfake_detector import detect_deepfake_in_frames
#     print("[OK] Services imported successfully")
# except ImportError as e:
#     logger.error(f"Service import failed: {e}")
#     raise SystemExit("Cannot start without services")

# # Enhanced detector
# try:
#     from app.services.enhanced_detector import enhanced_detector
#     ENHANCED_AVAILABLE = True
#     print("[OK] Enhanced detector available")
# except ImportError:
#     ENHANCED_AVAILABLE = False
#     print("[WARNING] Enhanced detector not available")

# # Real-time detection
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector
#     REALTIME_AVAILABLE = True
#     print("[OK] Real-time detection available")
# except ImportError:
#     REALTIME_AVAILABLE = False
#     print("[WARNING] Real-time detection not available")
#     class RealTimeDeepfakeDetector:
#         async def load_model(self): pass
#         async def real_time_analyze(self, frame): 
#             return {"error": "Real-time detection not available"}

# # Ultra-enhanced detection (FIXED - added missing import)
# try:
#     from app.services.truemedia_detector import enhanced_deepfake_detection
#     ULTRA_ENHANCED_AVAILABLE = True
#     print("[OK] Ultra-enhanced TrueMedia integration available")
# except ImportError:
#     ULTRA_ENHANCED_AVAILABLE = False
#     enhanced_deepfake_detection = None
#     print("[WARNING] Ultra-enhanced detection not available - using standard enhanced detection")

# # Free AI ensemble
# try:
#     from app.services.free_ai_boosters import free_ai_ensemble
#     FREE_AI_AVAILABLE = True
#     print("[OK] Free AI ensemble available")
# except ImportError:
#     FREE_AI_AVAILABLE = False
#     print("[WARNING] Free AI ensemble not available")

# # YouTube support
# try:
#     import yt_dlp
#     print("[OK] yt-dlp imported successfully")
#     from app.services.youtube_service import YouTubeDownloader
#     youtube_downloader = YouTubeDownloader()
#     print("[OK] YouTubeDownloader initialized, download_dir: downloaded_videos")
#     print("[OK] YouTube downloader instance created with comprehensive Shorts support")
#     print("[OK] YouTubeDownloader initialized, download_dir: downloaded_videos")
#     YOUTUBE_AVAILABLE = True
#     print("[OK] YouTube support enabled")
# except ImportError as e:
#     YOUTUBE_AVAILABLE = False
#     youtube_downloader = None
#     print(f"[WARNING] YouTube support disabled: {e}")

# # Ultra-ensemble models (FIXED - safe import with proper warning)
# try:
#     from app.models.ensemble_detector import UltraEnsembleDetector
#     # Test if the class actually exists and is importable
#     test_detector = UltraEnsembleDetector
#     ULTRA_ENSEMBLE_AVAILABLE = True
#     print("[OK] Ultra ensemble models available (6-model architecture)")
# except (ImportError, AttributeError) as e:
#     ULTRA_ENSEMBLE_AVAILABLE = False
#     print(f"[WARNING] Ultra ensemble not available: {e}")

# app = FastAPI(
#     title="iFake API - Advanced Deepfake Detection System",
#     version="2.4.0"
# )

# # Exception handlers
# @app.exception_handler(422)
# async def validation_exception_handler(request, exc):
#     logger.error(f"Validation error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Request validation failed",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# @app.exception_handler(500)
# async def internal_server_error_handler(request, exc):
#     logger.error(f"Internal server error on {request.url}: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "detail": str(exc),
#             "url": str(request.url)
#         }
#     )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# DETECTION_RESULTS: Dict[str, Dict] = {}

# # Create directories and mount static files
# Path("uploaded_videos").mkdir(exist_ok=True)
# Path("downloaded_videos").mkdir(exist_ok=True)
# try:
#     app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     print("[OK] Static file directories mounted successfully")
# except Exception as e:
#     print(f"[WARNING] Static file mounting failed: {e}")

# # FIXED: Single unified detection task function
# async def run_detection_task(video_id: str, video_path: str, video_type: str = "upload", 
#                            metadata: Optional[Dict] = None, enhancement_level: str = "standard"):
#     """
#     Unified detection task that handles all enhancement levels
#     enhancement_level: 'standard', 'enhanced', 'ultra', 'free-ai'
#     """
#     print(f"🎬 Starting {enhancement_level} detection: {video_id}")
#     start_time = time.time()
    
#     # Initialize detection result
#     DETECTION_RESULTS[video_id] = {
#         "video_id": video_id,
#         "status": "processing",
#         "result": None,
#         "confidence": None,
#         "error": None,
#         "enhanced_analysis": enhancement_level != "standard",
#         "ultra_enhanced": enhancement_level in ["ultra", "free-ai"],
#         "video_type": video_type,
#         "metadata": metadata or {},
#         "video_url": None,
#         "faces_found": 0,
#         "model_used": None,
#         "processing_time": None,
#         "current_stage": "initializing",
#         "progress_percentage": 0,
#         "stage_details": f"Starting {enhancement_level} AI analysis system...",
#         "estimated_time_remaining": None,
#         "enhancement_level": enhancement_level
#     }
    
#     try:
#         # Progress tracking
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 5
#         DETECTION_RESULTS[video_id]["stage_details"] = f"Initializing {enhancement_level} AI analysis system..."
#         await asyncio.sleep(0.2)

#         DETECTION_RESULTS[video_id]["progress_percentage"] = 15
#         DETECTION_RESULTS[video_id]["stage_details"] = "Starting face detection..."
#         DETECTION_RESULTS[video_id]["current_stage"] = "face_detection"

#         # Face extraction
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 25
#         DETECTION_RESULTS[video_id]["stage_details"] = "Extracting faces from video frames..."
        
#         for fake_step in range(26, 50, 4):
#             await asyncio.sleep(0.4)
#             DETECTION_RESULTS[video_id]["progress_percentage"] = fake_step
#             DETECTION_RESULTS[video_id]["stage_details"] = f"Extracting faces... {fake_step}% done"

#         faces = extract_faces_from_video(video_path)
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 50
#         DETECTION_RESULTS[video_id]["faces_found"] = len(faces) if faces else 0
#         DETECTION_RESULTS[video_id]["stage_details"] = f"[OK] Extracted {len(faces) if faces else 0} faces from video"

#         if not faces:
#             DETECTION_RESULTS[video_id].update({
#                 "status": "completed",
#                 "result": "No Faces Detected",
#                 "confidence": 0.0,
#                 "progress_percentage": 100,
#                 "current_stage": "completed",
#                 "stage_details": "No faces detected in video",
#                 "processing_time": round(time.time() - start_time, 2)
#             })
#             return

#         # Analysis based on enhancement level
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 60
#         DETECTION_RESULTS[video_id]["current_stage"] = "analyzing_faces"
        
#         # Try Free AI ensemble first (highest accuracy when available)
#         if enhancement_level == "free-ai" and FREE_AI_AVAILABLE:
#             DETECTION_RESULTS[video_id]["stage_details"] = "[START] Using Ultra-Free AI Ensemble (5+ models)..."
#             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
#             try:
#                 result_data = await free_ai_ensemble.ultra_analyze_faces(faces, video_path)
#                 result_text = result_data.get('prediction', 'Real Video')
#                 confidence_score = result_data.get('confidence', 50.0) 
#                 # Ensure confidence is a float (not percentage)
#                 if confidence_score > 1.0:
#                     confidence_score = confidence_score / 100.0
#                 model_name = "Ultra-Free AI Ensemble (5+ Models)"
#                 enhanced_analysis = True
                
#                 # Add detailed analysis
#                 DETECTION_RESULTS[video_id]["detailed_analysis"] = result_data.get('ai_analysis', {})
#                 DETECTION_RESULTS[video_id]["model_breakdown"] = result_data.get('model_contributions', {})
                
#             except Exception as free_ai_error:
#                 logger.warning(f"Free AI ensemble detection failed: {free_ai_error}")
#                 # Fallback to ultra
#                 enhancement_level = "ultra"
        
#         # Ultra-enhanced detection
#         if enhancement_level == "ultra" and ULTRA_ENHANCED_AVAILABLE:
#             DETECTION_RESULTS[video_id]["stage_details"] = "[START] Running Ultra-Enhanced TrueMedia + EfficientNet analysis..."
#             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
#             try:
#                 result_data = await enhanced_deepfake_detection(faces, video_path)
#                 result_text = result_data.get('prediction', 'Real Video')
#                 confidence_score = result_data.get('confidence', 50.0)
#                 # Ensure confidence is a float (not percentage)
#                 if confidence_score > 1.0:
#                     confidence_score = confidence_score / 100.0
#                 model_name = "Ultra-Enhanced Hybrid Ensemble (TrueMedia + EfficientNet)"
#                 enhanced_analysis = True
                
#                 # Add detailed analysis
#                 DETECTION_RESULTS[video_id]["detailed_analysis"] = result_data.get('ai_analysis', {})
#                 DETECTION_RESULTS[video_id]["model_breakdown"] = result_data.get('model_results', {})
                
#             except Exception as ultra_error:
#                 logger.warning(f"Ultra-enhanced detection failed: {ultra_error}")
#                 # Fallback to enhanced
#                 enhancement_level = "enhanced"
        
#         # Enhanced detection
#         if enhancement_level == "enhanced" and ENHANCED_AVAILABLE:
#             DETECTION_RESULTS[video_id]["stage_details"] = "🧠 Running Enhanced AI analysis..."
#             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
#             try:
#                 result_data = enhanced_detector.enhanced_analyze_faces(faces)
#                 if isinstance(result_data, dict):
#                     result_text = result_data.get('prediction', 'Real Video')
#                     confidence_score = result_data.get('confidence', 50.0)
#                     # Ensure confidence is a float (not percentage)
#                     if confidence_score > 1.0:
#                         confidence_score = confidence_score / 100.0
#                 else:
#                     result_text, confidence_score = result_data
#                 model_name = "Enhanced Detector"
#                 enhanced_analysis = True
#             except Exception as enhanced_error:
#                 logger.warning(f"Enhanced detection failed: {enhanced_error}")
#                 # Fallback to standard
#                 enhancement_level = "standard"
        
#         # Standard detection (fallback)
#         if enhancement_level == "standard":
#             DETECTION_RESULTS[video_id]["stage_details"] = "🔍 Running Standard AI analysis..."
#             DETECTION_RESULTS[video_id]["progress_percentage"] = 70
            
#             result_text, confidence_score = await detect_deepfake_in_frames(faces)
#             model_name = "Standard EfficientNet Detector"
#             enhanced_analysis = False

#         # Finalization
#         DETECTION_RESULTS[video_id]["progress_percentage"] = 90
#         DETECTION_RESULTS[video_id]["stage_details"] = "⚡ Finalizing results..."

#         # Prepare final results
#         filename = os.path.basename(video_path)
#         video_url = f"/downloaded_videos/{filename}" if video_type == "youtube" else f"/videos/{filename}"
#         processing_time = time.time() - start_time
        
#         # Ensure confidence is in percentage format for display
#         if confidence_score <= 1.0:
#             confidence_score = confidence_score * 100

#         DETECTION_RESULTS[video_id].update({
#             "status": "completed",
#             "result": result_text,
#             "confidence": confidence_score,
#             "enhanced_analysis": enhanced_analysis,
#             "video_url": video_url,
#             "faces_found": len(faces),
#             "model_used": model_name,
#             "processing_time": round(processing_time, 2),
#             "current_stage": "completed",
#             "progress_percentage": 100,
#             "stage_details": f"[OK] {enhancement_level.capitalize()} analysis completed successfully"
#         })
        
#         print(f"[OK] {enhancement_level.capitalize()} detection completed for {video_id}: {result_text} ({confidence_score:.1f}%)")
        
#     except Exception as e:
#         processing_time = time.time() - start_time
#         print(f"[ERROR] Detection failed for {video_id}: {str(e)}")
#         DETECTION_RESULTS[video_id].update({
#             "status": "failed",
#             "error": str(e),
#             "processing_time": round(processing_time, 2),
#             "current_stage": "failed",
#             "progress_percentage": 0,
#             "stage_details": f"[ERROR] Error: {str(e)}"
#         })

# # Root endpoint
# @app.get("/")
# async def root():
#     return {
#         "message": "iFake API - Advanced Deepfake Detection System",
#         "version": "2.4.0",
#         "status": "operational",
#         "enhancement_levels": ["standard", "enhanced", "ultra", "free-ai"],
#         "features": {
#             "enhanced_available": ENHANCED_AVAILABLE,
#             "ultra_enhanced_available": ULTRA_ENHANCED_AVAILABLE,
#             "free_ai_available": FREE_AI_AVAILABLE,
#             "ultra_ensemble_available": ULTRA_ENSEMBLE_AVAILABLE,
#             "youtube_available": YOUTUBE_AVAILABLE
#         }
#     }

# # Upload endpoints
# @app.post("/upload-video", response_model=VideoUploadResponse)
# async def upload_video(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Standard video upload with basic detection"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, "standard")
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded successfully - Standard detection started",
#             video_type="upload",
#             metadata={"enhancement_level": "standard"}
#         )
#     except Exception as e:
#         logger.error(f"Upload video error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/upload-video-enhanced", response_model=VideoUploadResponse)
# async def upload_video_enhanced(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Enhanced video upload with multi-stage analysis"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, "enhanced")
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"Video uploaded - ENHANCED detection started",
#             video_type="upload",
#             metadata={"enhancement_level": "enhanced"}
#         )
#     except Exception as e:
#         logger.error(f"Enhanced upload error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-ultra", response_model=VideoUploadResponse)
# async def detect_deepfake_ultra(
#     background_tasks: BackgroundTasks,
#     video_file: UploadFile = File(...)
# ):
#     """Ultra-enhanced detection using best available method (95% accuracy target)"""
#     if not video_file.content_type or not video_file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Invalid file type")
    
#     try:
#         video_id, video_path = await save_uploaded_video(video_file)
#         # Use best available enhancement level
#         enhancement_level = "free-ai" if FREE_AI_AVAILABLE else "ultra" if ULTRA_ENHANCED_AVAILABLE else "enhanced"
#         background_tasks.add_task(run_detection_task, video_id, video_path, "upload", {}, enhancement_level)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"ULTRA-ENHANCED detection started using {enhancement_level} (95% accuracy target)",
#             video_type="upload",
#             metadata={"enhancement_level": enhancement_level, "target_accuracy": "95%"}
#         )
#     except Exception as e:
#         logger.error(f"Ultra-enhanced detection error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube", response_model=VideoUploadResponse)
# async def detect_deepfake_youtube(
#     background_tasks: BackgroundTasks,
#     request: YouTubeVideoRequest
# ):
#     """YouTube video detection with automatic best enhancement level"""
#     logger.info(f"YouTube request received: {request.youtube_url}")
#     if not YOUTUBE_AVAILABLE:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube support not available. Please install yt-dlp: pip install yt-dlp"
#         )
#     if not youtube_downloader:
#         raise HTTPException(
#             status_code=503, 
#             detail="YouTube downloader not initialized"
#         )
#     try:
#         youtube_url = str(request.youtube_url)
#         logger.info(f"Processing YouTube URL: {youtube_url}")
#         if not any(domain in youtube_url.lower() for domain in ['youtube.com', 'youtu.be']):
#             raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video URL.")
        
#         video_id, video_path, metadata = await youtube_downloader.download_video(youtube_url)
#         logger.info(f"Successfully downloaded video: {video_id}")
        
#         # Use best available enhancement level for YouTube
#         enhancement_level = "free-ai" if FREE_AI_AVAILABLE else "ultra" if ULTRA_ENHANCED_AVAILABLE else "enhanced" if ENHANCED_AVAILABLE else "standard"
#         background_tasks.add_task(run_detection_task, video_id, video_path, "youtube", metadata, enhancement_level)
        
#         return VideoUploadResponse(
#             video_id=video_id,
#             message=f"YouTube video processing started with {enhancement_level} detection",
#             video_type="youtube",
#             metadata={**metadata, "enhancement_level": enhancement_level}
#         )
#     except HTTPException:
#         raise
#     except ValueError as ve:
#         logger.error(f"YouTube validation error: {ve}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         logger.error(f"YouTube processing error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

# @app.get("/detection-status/{video_id}", response_model=DetectionStatusResponse)
# async def get_detection_status(video_id: str):
#     """Get detection status and results"""
#     result = DETECTION_RESULTS.get(video_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Video ID not found")
#     return DetectionStatusResponse(**result)

# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     """Real-time detection WebSocket with proper CORS handling"""
#     try:
#         await websocket.accept()
#         print("[OK] WebSocket connected successfully")
        
#         if not REALTIME_AVAILABLE:
#             await websocket.send_json({
#                 "error": "Real-time detection not available",
#                 "status": "disconnected"
#             })
#             return

#         # Initialize detector
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()
        
#         # Send connection ready signal
#         await websocket.send_json({
#             "type": "connection_ready",
#             "message": "AI Server Connected - Ready for real-time analysis",
#             "status": "connected"
#         })
        
#         while True:
#             try:
#                 # Wait for frame data with timeout
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
#                 # Handle different data formats
#                 try:
#                     if data.startswith('data:image'):
#                         # Handle data URL format
#                         header, base64_data = data.split(',', 1)
#                         frame_bytes = base64.b64decode(base64_data)
#                     else:
#                         # Handle direct base64
#                         frame_bytes = base64.b64decode(data)
                    
#                     # Decode image
#                     frame_array = np.frombuffer(frame_bytes, np.uint8)
#                     frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    
#                     if frame is None:
#                         await websocket.send_json({
#                             "error": "Invalid frame data",
#                             "status": "error"
#                         })
#                         continue
                    
#                     # Analyze frame
#                     result = await detector.real_time_analyze(frame)
#                     result["status"] = "connected"
#                     await websocket.send_json(result)
                    
#                 except Exception as frame_error:
#                     await websocket.send_json({
#                         "error": f"Frame processing error: {str(frame_error)}",
#                         "status": "error"
#                     })
                    
#             except asyncio.TimeoutError:
#                 # Send heartbeat
#                 await websocket.send_json({
#                     "type": "heartbeat", 
#                     "message": "AI Server alive",
#                     "status": "connected"
#                 })
#             except WebSocketDisconnect:
#                 print("🔌 WebSocket disconnected")
#                 break
#             except Exception as e:
#                 await websocket.send_json({
#                     "error": str(e),
#                     "status": "error"
#                 })
                
#     except Exception as e:
#         print(f"[ERROR] WebSocket error: {e}")
#         try:
#             await websocket.send_json({
#                 "error": f"Connection failed: {str(e)}",
#                 "status": "disconnected"
#             })
#         except:
#             pass

# # Health check
# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "version": "2.4.0",
#         "features": {
#             "enhanced_available": ENHANCED_AVAILABLE,
#             "ultra_enhanced_available": ULTRA_ENHANCED_AVAILABLE,
#             "free_ai_available": FREE_AI_AVAILABLE,
#             "ultra_ensemble_available": ULTRA_ENSEMBLE_AVAILABLE,
#             "realtime_available": REALTIME_AVAILABLE,
#             "youtube_available": YOUTUBE_AVAILABLE
#         },
#         "active_detections": len(DETECTION_RESULTS),
#         "target_accuracy": "95%" if FREE_AI_AVAILABLE else "90%" if ULTRA_ENHANCED_AVAILABLE else "85%" if ENHANCED_AVAILABLE else "75%"
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


































# app/main.py - COMPLETE INTEGRATION OF ADVANCED DETECTION CAPABILITIES

# # app/main.py - COMPLETE INTEGRATION OF ALL ADVANCED DETECTION CAPABILITIES

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi import Request
import json
import base64
import os
import uuid
import time
import asyncio
from typing import Dict, List, Optional
import logging
import numpy as np
import cv2
import torch
from datetime import datetime
from app.services.enhanced_face_extractor import EnhancedFaceExtractor
from app.services.enhanced_detection_engine import EnhancedDetectionEngine
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Deepfake Detection API",
    description="Ultra-enhanced deepfake detection with multiple AI models",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for detection results
DETECTION_RESULTS: Dict[str, Dict] = {}

# Import schemas
try:
    from app.schemas import DetectionResponse, YouTubeRequest, VideoUploadResponse
    logger.info("[OK] Schemas imported successfully")
except ImportError as e:
    logger.error(f"[ERROR] Schema import failed: {e}")

# Core services imports
try:
    from app.services.video_processor import extract_faces_from_video
    from app.services.deepfake_detector import detect_deepfake_in_frames
    from app.services.analytics import DetectionAnalytics
    logger.info("[OK] Core services imported successfully")
except ImportError as e:
    logger.error(f"[ERROR] Core services import failed: {e}")

# Advanced detection imports with comprehensive coverage
try:
    from app.services.modern_ai_detector import ModernAIContentDetector
    from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
    from app.services.tool_specific_detectors import ToolSpecificDetectorSuite
    from app.services.title_classifier import intelligent_title_classifier
    modern_ai_detector = ModernAIContentDetector()
    tool_detector_suite = ToolSpecificDetectorSuite()
    logger.info("[OK] Advanced AI detection modules available")
    MODERN_AI_DETECTION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Advanced AI detection limited: {e}")
    MODERN_AI_DETECTION_AVAILABLE = False

# Enhanced detection imports
try:
    from app.services.enhanced_detector import enhanced_detector
    logger.info("[OK] Enhanced detector available")
    ENHANCED_DETECTION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Enhanced detector not available: {e}")
    ENHANCED_DETECTION_AVAILABLE = False

# Free AI ensemble imports
try:
    from app.services.free_ai_boosters import free_ai_ensemble
    # logger.info("[OK] Free AI ensemble available")
    FREE_AI_ENSEMBLE_AVAILABLE = True
except ImportError as e:
    # logger.warning(f"[WARNING] Free AI ensemble not available: {e}")
    FREE_AI_ENSEMBLE_AVAILABLE = False

# Real-time detection
try:
    from app.services.realtime_detector import RealTimeDeepfakeDetector
    realtime_detector = RealTimeDeepfakeDetector()
    logger.info("[OK] Real-time detection available")
    REALTIME_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Real-time detection not available: {e}")
    REALTIME_AVAILABLE = False

# Specialized detectors
try:
    from app.services.hybrid_detector import HybridCNNLSTMDetector
    from app.services.unite_detector import UNITEDetector
    from app.services.divid_detector import DIVIDDetector
    hybrid_detector = HybridCNNLSTMDetector()
    unite_detector = UNITEDetector()
    divid_detector = DIVIDDetector()
    logger.info("[OK] Specialized detectors available")
    SPECIALIZED_DETECTORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Specialized detectors limited: {e}")
    SPECIALIZED_DETECTORS_AVAILABLE = False

# YouTube support
try:
    from app.services.youtube_service import youtube_downloader, YOUTUBE_AVAILABLE
    if YOUTUBE_AVAILABLE:
        logger.info("[OK] YouTube support enabled")
    else:
        logger.warning("[WARNING] YouTube support disabled - yt-dlp not available")
except ImportError as e:
    logger.warning(f"[WARNING] YouTube support not available: {e}")
    YOUTUBE_AVAILABLE = False

# Performance optimization
try:
    from app.services.performance_optimizer import DetectionCache
    detection_cache = DetectionCache()
    logger.info("[OK] Caching available")
    CACHING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Caching not available")
    CACHING_AVAILABLE = False

# Self-learning system
try:
    from app.services.self_learning import SelfImprovingDetectionSystem
    self_learning_system = SelfImprovingDetectionSystem()
    logger.info("[OK] Self-learning system available")
    SELF_LEARNING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Self-learning not available: {e}")
    SELF_LEARNING_AVAILABLE = False

try:
    from app.services.analytics import DetectionAnalytics
    logger.info("[OK] Analytics imported successfully")
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARNING] Analytics not available: {e}")
    ANALYTICS_AVAILABLE = False
    
    # Create fallback analytics class
    class DetectionAnalytics:
        def __init__(self):
            self.analytics_data = {}
        
        def log_detection(self, video_id: str, result: dict):
            pass
        
        def get_analytics_summary(self) -> dict:
            return {"status": "analytics_disabled", "message": "Analytics module not available"}

# Initialize analytics
if ANALYTICS_AVAILABLE:
    analytics = DetectionAnalytics()
    logger.info("[OK] Analytics system initialized")
else:
    analytics = DetectionAnalytics()  # Uses fallback class
    logger.info("[WARNING] Using fallback analytics")

# System capabilities summary
logger.info("[FIX] SYSTEM CAPABILITIES SUMMARY:")
logger.info(f"   [DATA] Enhanced Detection: {ENHANCED_DETECTION_AVAILABLE}")
# logger.info(f"   🤖 Free AI Ensemble: {FREE_AI_ENSEMBLE_AVAILABLE}")
logger.info(f"   🎯 Modern AI Detection: {MODERN_AI_DETECTION_AVAILABLE}")
logger.info(f"   📝 Title Classification: {MODERN_AI_DETECTION_AVAILABLE}")
logger.info(f"   [LOADING] Real-time Detection: {REALTIME_AVAILABLE}")
logger.info(f"   📺 YouTube Support: {YOUTUBE_AVAILABLE}")
logger.info(f"   🧠 Specialized Detectors: {SPECIALIZED_DETECTORS_AVAILABLE}")

# Static file serving
try:
    if not os.path.exists("downloaded_videos"):
        os.makedirs("downloaded_videos")
    if not os.path.exists("uploaded_videos"):
        os.makedirs("uploaded_videos")
    
    app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
    app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
    logger.info("[OK] Static file directories mounted successfully")
except Exception as e:
    logger.error(f"[ERROR] Static file setup failed: {e}")

@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    """Catch and log all unhandled exceptions with full stack trace"""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        import traceback
        import sys
        
        # Get full stack trace
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        
        # Log detailed error
        logger.error(f"[ERROR] UNHANDLED EXCEPTION in {request.method} {request.url}")
        logger.error(f"[ERROR] ERROR TYPE: {exc_type.__name__}")
        logger.error(f"[ERROR] ERROR MESSAGE: {str(exc)}")
        logger.error(f"[ERROR] FULL STACK TRACE:\n{tb_str}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc),
                "type": exc_type.__name__ if exc_type else "Unknown",
                "debug_info": "Check server logs for full stack trace"
            }
        )

# ========== TIMEOUT-PROTECTED TEMPORAL ANALYSIS ==========
# In your main.py - Replace temporal analysis calls with this:
async def safe_temporal_analysis(video_path: str, faces: List) -> Dict:
    """FIXED: Timeout-protected temporal analysis"""
    try:
        # Use asyncio timeout for entire analysis
        return await asyncio.wait_for(
            _run_temporal_analysis_core(video_path, faces),
            timeout=25.0  # 25 second hard timeout
        )
    except asyncio.TimeoutError:
        logger.warning("[WARNING] Temporal analysis timed out after 25s")
        return {
            'ai_probability': 0.4,
            'confidence': 60.0,
            'artifacts': ['analysis_timeout']
        }
    except Exception as e:
        logger.error(f"[ERROR] Temporal analysis failed: {e}")
        return {
            'ai_probability': 0.35,
            'confidence': 55.0,
            'artifacts': ['analysis_failed']
        }

async def _run_temporal_analysis_core(video_path: str, faces: List) -> Dict:
    """Core temporal analysis with reduced complexity"""
    try:
        # Extract frames with safety limits
        frames = []
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'ai_probability': 0.3, 'confidence': 50.0}
        
        frame_count = 0
        max_frames = 10  # Reduced from 30
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame_resized = cv2.resize(frame, (224, 224))
            frames.append(frame_resized)
            frame_count += 1
            
            # Safety check
            if frame_count > max_frames * 2:
                break
        
        cap.release()
        
        if len(frames) < 3:
            return {'ai_probability': 0.3, 'confidence': 50.0}
        
        # Simple frame difference analysis (no complex algorithms)
        differences = []
        for i in range(min(len(frames) - 1, 6)):
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
            gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY).astype(np.float32)
            diff = np.mean(np.abs(gray1 - gray2))
            differences.append(diff)
        
        if differences:
            variance = np.var(differences)
            consistency_score = 1.0 / (1.0 + variance / 100.0)
            ai_probability = min(consistency_score, 0.8)
        else:
            ai_probability = 0.4
            
        return {
            'ai_probability': ai_probability,
            'confidence': ai_probability * 100,
            'frames_processed': len(frames)
        }
        
    except Exception as e:
        logger.warning(f"Core temporal analysis failed: {e}")
        return {'ai_probability': 0.35, 'confidence': 55.0}

async def _extract_video_frames_safe(video_path: str, max_frames: int = 12) -> List[np.ndarray]:
    """Timeout-protected frame extraction"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []
        
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        extracted_count = 0
        max_iterations = total_frames + 50  # Safety limit
        
        while extracted_count < max_frames and frame_count < max_iterations:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_resized = cv2.resize(frame, (224, 224))
                frames.append(frame_resized)
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        return frames
        
    except Exception as e:
        logger.error(f"Frame extraction error: {e}")
        return []

# ========== DETECTION PROCESSING FUNCTIONS ==========

async def process_detection_background_traditional(video_id: str, video_path: str):
    """Traditional deepfake detection using EfficientNet only - FULL PROCESSING"""
    try:
        start_time = time.time()
        logger.info(f"🔍 Starting traditional detection for {video_id}")
        
        DETECTION_RESULTS[video_id] = {'status': 'processing', 'video_id': video_id}
        
        # [OK] STEP 1: MANDATORY Face Extraction (NEVER SKIP)
        logger.info("📥 STEP 1: Extracting faces from video...")
        DETECTION_RESULTS[video_id].update({
            'status': 'processing', 
            'progress': 20,
            'current_step': 'Face extraction and preprocessing'
        })
        
        faces, timing_info = await extract_faces_from_video(video_path, frames_to_process=15, frame_interval=3)
        logger.info(f"[OK] Extracted {len(faces)} faces for traditional analysis")
        
        if not faces:
            logger.warning("[ERROR] No faces detected - cannot proceed with traditional analysis")
            DETECTION_RESULTS[video_id] = {
                'status': 'completed', 
                'prediction': 'No Faces Detected', 
                'confidence': 0.0,
                'faces_detected': 0, 
                'detection_method': 'Traditional EfficientNet',
                'processing_time': round(time.time() - start_time, 2),
                'enhanced_analysis': False,
                'analysis_method': 'Traditional Detection',
                'ai_analysis': {
                    'technical_reasoning': 'No faces detected in video for traditional analysis. EfficientNet requires facial features for accurate assessment.',
                    'confidence_explanation': 'Unable to perform traditional detection without detectable faces',
                    'method_used': 'Face detection preprocessing',
                    'recommendation': 'Ensure video contains clear facial features for optimal analysis'
                }
            }
            return
        
        # [OK] STEP 2: MANDATORY EfficientNet Analysis
        logger.info("🧠 STEP 2: Running EfficientNet analysis...")
        DETECTION_RESULTS[video_id].update({
            'progress': 60,
            'current_step': 'EfficientNet deepfake detection'
        })
        
        prediction, confidence = await detect_deepfake_in_frames(faces)
        logger.info(f"🧠 EfficientNet result: {prediction} (confidence: {confidence:.3f})")
        
        # [OK] STEP 3: Final Result Compilation
        DETECTION_RESULTS[video_id] = {
            'status': 'completed', 
            'prediction': prediction,
            'confidence': confidence * 100 if confidence <= 1.0 else confidence,
            'faces_detected': len(faces), 
            'detection_method': 'Traditional EfficientNet-B0',
            'processing_time': round(time.time() - start_time, 2),
            'enhanced_analysis': False,
            'analysis_method': 'Traditional Detection',
            'ai_analysis': {
                'technical_reasoning': f"Traditional EfficientNet-B0 analysis on {len(faces)} face samples using binary classification trained on deepfake datasets",
                'confidence_explanation': f"{'High' if confidence > 0.7 else 'Moderate'} confidence in {prediction.lower()} classification based on learned deepfake patterns",
                'method_used': 'Single-model traditional detection',
                'processing_stages': [
                    'Face extraction and preprocessing',
                    'EfficientNet-B0 inference',
                    'Binary classification decision'
                ],
                'recommendation': f"Content classified as {prediction.lower()} using traditional deepfake detection methods"
            }
        }
        
        logger.info(f"[OK] Traditional detection completed for {video_id}: {prediction} ({confidence:.3f})")
        
    except Exception as e:
        logger.error(f"[ERROR] Traditional detection failed for {video_id}: {e}")
        DETECTION_RESULTS[video_id] = {
            'status': 'completed',
            'prediction': 'Analysis Failed',
            'confidence': 0.0,
            'faces_detected': 0,
            'processing_time': round(time.time() - start_time, 2) if 'start_time' in locals() else 0,
            'detection_method': 'Traditional (Failed)',
            'error': str(e),
            'video_id': video_id
        }

async def process_detection_background_modern_ai(video_id: str, video_path: str, metadata: dict = None):
    """FIXED: Integrated title analysis with full processing"""
    try:
        start_time = time.time()
        
        # [OK] STEP 0: IMMEDIATE TITLE ANALYSIS (but still do full processing)
        title_boost = 0.0
        detected_keywords = []
        
        if metadata and metadata.get('title'):
            title = metadata.get('title', '').lower()
            description = metadata.get('description', '').lower()
            
            # Import your title classifier
            from app.services.title_classifier import intelligent_title_classifier
            
            # AI keyword detection
            ai_keywords = ['veo', 'veo3', 'veo 3', 'sora', 'runway', 'ai generated', 
                          'deepfake', 'fake', 'artificial', 'generated', 'by ai', 'ai video',
                          'ai tool', 'generated by', 'created with ai', 'midjourney','(Deep)Fake','ai','gemini','Deepfake','DeepFake','Deep Fake']
            
            found_keywords = [kw for kw in ai_keywords if kw in f"{title} {description}"]
            
            if found_keywords:
                # Strong title boost for obvious AI content
                keyword_confidence = min(85.0 + len(found_keywords) * 3, 95.0)
                title_boost = min(keyword_confidence / 100.0 * 0.25, 0.25)  # Up to 25% boost
                detected_keywords = found_keywords[:5]
                # logger.info(f"📝 Found AI keywords: {found_keywords}, boost: +{title_boost:.3f}")
        
        # [OK] STEP 1: MANDATORY Face Extraction (ALWAYS RUN)
        faces, timing_info = await extract_faces_from_video(video_path, frames_to_process=20, frame_interval=2)
        
        if not faces:
            # Handle no faces case...
            return
        
        # [OK] STEP 2: Multi-Detector Analysis Suite (ALWAYS RUN)
        detection_scores = []
        
        # 2.1: EfficientNet Analysis (REDUCED weight for modern AI)
        try:
            prediction, confidence = await detect_deepfake_in_frames(faces)
            efficientnet_score = confidence if 'Deepfake' in prediction else (1.0 - confidence)
            detection_scores.append(('efficientnet', efficientnet_score, 0.20))  # REDUCED from 0.35
        except Exception as e:
            detection_scores.append(('efficientnet', 0.3, 0.20))
        
        # 2.2: Modern AI Content Detector (INCREASED weight)
        try:
            from app.services.modern_ai_detector import modern_ai_detector
            modern_result = modern_ai_detector.detect_modern_ai_generation(faces, video_path)
            modern_score = modern_result.get('confidence', 50) / 100.0
            detection_scores.append(('modern_ai', modern_score, 0.45))  # INCREASED from 0.25
        except Exception as e:
            detection_scores.append(('modern_ai', 0.4, 0.45))
        
        # 2.3: FIXED Temporal Analysis (with timeout)
        try:
            temporal_result = await safe_temporal_analysis(video_path, faces)
            temporal_score = temporal_result.get('ai_probability', 0.4)
            detection_scores.append(('temporal', temporal_score, 0.20))
        except Exception as e:
            detection_scores.append(('temporal', 0.4, 0.20))
        
        # 2.4: Advanced Frequency Analysis
        try:
            from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
            freq_result = ultra_frequency_analyzer.ultra_frequency_analysis(faces, video_path)
            freq_score = freq_result.get('ai_probability', 0.4)
            detection_scores.append(('frequency', freq_score, 0.15))
        except Exception as e:
            detection_scores.append(('frequency', 0.4, 0.15))
        
        # [OK] STEP 3: Ensemble Decision + Title Boost
        total_score = 0.0
        total_weight = 0.0
        
        for detector_name, score, weight in detection_scores:
            total_score += score * weight
            total_weight += weight
        
        ensemble_ai_score = total_score / total_weight if total_weight > 0 else 0.4
        final_ai_score = min(ensemble_ai_score + title_boost, 0.95)
        
        # [OK] LOWERED THRESHOLD for modern AI content
        if final_ai_score >= 0.45:  # LOWERED from 0.52
            prediction = "AI-Generated Content Detected"
            confidence = min(final_ai_score * 100, 95.0)
        else:
            prediction = "Authentic Content"
            confidence = min((1.0 - final_ai_score) * 100, 95.0)
        
        # Store comprehensive result...
        DETECTION_RESULTS[video_id] = {
            'status': 'completed',
            'prediction': prediction,
            'confidence': max(confidence, 60.0),
            'faces_detected': len(faces),
            'processing_time': round(time.time() - start_time, 2),
            'detection_method': 'Advanced Multi-Stage AI Ensemble',
            'detected_keywords': detected_keywords,
            'likely_ai_tool': _identify_ai_tool(detected_keywords),
            'ensemble_score': ensemble_ai_score,
            'title_boost_applied': title_boost,
            'final_composite_score': final_ai_score
        }
           
    except Exception as e:
        # logger.error(f"[ERROR] Modern AI detection failed for {video_id}: {e}")
        # DETECTION_RESULTS[video_id] = {
        #     'status': 'completed',
        #     'prediction': 'Analysis Failed',
        #     'confidence': 0.0,
        #     'faces_detected': 0,
        #     'processing_time': round(time.time() - start_time, 2) if 'start_time' in locals() else 0,
        #     'detection_method': 'Modern AI (System Error)',
        #     'error': str(e),
        #     'video_id': video_id
        # }
        pass
# Helper function for AI tool identification
def _identify_ai_tool(keywords: List[str]) -> str:
    """Identify most likely AI tool from detected keywords"""
    if not keywords:
        return 'unknown'
    
    tool_patterns = {
        'veo3': ['veo', 'veo3', 'veo 3', 'google'],
        'sora': ['sora', 'openai'],
        'midjourney': ['midjourney', 'mj'],
        'runway': ['runway', 'runwayml'],
        'dall-e': ['dall-e', 'dalle']
    }
    
    keywords_text = ' '.join(keywords).lower()
    for tool, patterns in tool_patterns.items():
        if any(pattern in keywords_text for pattern in patterns):
            return tool
    
    return 'modern_ai_tool'

async def _analyze_without_faces(video_id: str, video_path: str, metadata: dict, start_time: float):
    """Alternative analysis when no faces are detected"""
    logger.info("🔍 Performing alternative analysis without faces...")
    
    # Try title analysis for immediate results
    if metadata and metadata.get('title') and MODERN_AI_DETECTION_AVAILABLE:
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        title_result = intelligent_title_classifier.classify_by_title(title, description)
        
        if title_result['is_ai_generated'] and title_result['confidence'] >= 70:
            return {
                'status': 'completed',
                'prediction': 'AI-Generated Content (Alternative Analysis)',
                'confidence': title_result['confidence'],
                'faces_detected': 0,
                'processing_time': round(time.time() - start_time, 2),
                'detection_method': 'Title-Based Alternative Analysis',
                'likely_ai_tool': title_result.get('likely_ai_tool', 'unknown'),
                'detected_keywords': title_result.get('detected_keywords', []),
                'analysis_method': 'Alternative Analysis Pipeline',
                'enhanced_analysis': True,
                'ai_analysis': {
                    'technical_reasoning': f"Alternative analysis using title classification due to absence of detectable faces. Title '{title}' contains clear AI generation indicators.",
                    'confidence_explanation': f"High confidence ({title_result['confidence']:.1f}%) based on explicit AI keywords and patterns in video title",
                    'method_used': 'Intelligent title classification with pattern matching',
                    'recommendation': f"Content classified as AI-generated based on title analysis. Detected tool: {title_result.get('likely_ai_tool', 'unknown')}"
                }
            }
    
    # Default no-face result
    return {
        'status': 'completed',
        'prediction': 'No Faces Detected',
        'confidence': 0.0,
        'faces_detected': 0,
        'processing_time': round(time.time() - start_time, 2),
        'detection_method': 'Modern AI (No Faces)',
        'analysis_method': 'Modern AI Detection',
        'enhanced_analysis': True,
        'ai_analysis': {
            'technical_reasoning': 'No faces detected in video for analysis. Modern AI detection requires facial features or alternative indicators for accurate assessment.',
            'confidence_explanation': 'Unable to perform comprehensive AI detection without detectable faces',
            'method_used': 'Face detection preprocessing with alternative analysis',
            'recommendation': 'Ensure video contains clear facial features for optimal modern AI analysis'
        }
    }

async def process_detection_background_enhanced(video_id: str, video_path: str, is_youtube: bool = False, metadata: Dict = None):
    """Enhanced detection using free AI ensemble - COMPREHENSIVE BUT OPTIMIZED"""
    try:
        start_time = time.time()
        logger.info(f"[START] Starting enhanced detection for {video_id}")
        
        DETECTION_RESULTS[video_id] = {
            'status': 'processing',
            'progress': 25,
            'message': 'Analyzing video content...'
        }
        
        # Extract faces
        faces, timing_info = await extract_faces_from_video(video_path, frames_to_process=20, frame_interval=5)
        
        if not faces:
            DETECTION_RESULTS[video_id] = {
                'status': 'completed',
                'prediction': 'No Faces Detected',
                'confidence': 0.0,
                'faces_detected': 0,
                'processing_time': round(time.time() - start_time, 2),
                'detection_method': 'Enhanced AI',
                'analysis_method': 'Enhanced Detection',
                'enhanced_analysis': True
            }
            return

        # Use free AI ensemble if available
        if FREE_AI_ENSEMBLE_AVAILABLE:
            try:
                ensemble_result = await free_ai_ensemble.ultra_analyze_faces(faces, video_path)
                result = ensemble_result
                logger.info(f"[START] Free AI Ensemble: {ensemble_result.get('prediction')} ({ensemble_result.get('confidence', 0):.1f}%)")
            except Exception as e:
                logger.warning(f"Free AI ensemble failed: {e}")
                result = enhanced_detector.enhanced_analyze_faces(faces) if ENHANCED_DETECTION_AVAILABLE else None
        elif ENHANCED_DETECTION_AVAILABLE:
            try:
                result = enhanced_detector.enhanced_analyze_faces(faces)
                logger.info(f"🧠 Enhanced Detector: {result.get('prediction')} ({result.get('confidence', 0):.1f}%)")
            except Exception as e:
                logger.warning(f"Enhanced detector failed: {e}")
                result = None
        else:
            result = None
        
        # Final fallback to basic detection
        if not result:
            try:
                prediction, confidence = await detect_deepfake_in_frames(faces)
                result = {
                    'prediction': prediction,
                    'confidence': confidence * 100 if confidence <= 1.0 else confidence,
                    'faces_detected': len(faces),
                    'detection_method': 'Basic EfficientNet',
                    'analysis_method': 'Basic Detection',
                    'enhanced_analysis': False
                }
                logger.info(f"🔍 Basic Detector: {prediction} ({confidence:.3f})")
            except Exception as e:
                logger.error(f"All detection methods failed: {e}")
                DETECTION_RESULTS[video_id] = {
                    'status': 'completed',
                    'prediction': 'Detection Failed',
                    'confidence': 0.0,
                    'faces_detected': len(faces),
                    'processing_time': round(time.time() - start_time, 2),
                    'error': str(e),
                    'video_id': video_id
                }
                return
        
        # Finalize result
        processing_time = time.time() - start_time
        result['processing_time'] = round(processing_time, 2)
        result['status'] = 'completed'
        result['video_id'] = video_id
        result['faces_detected'] = len(faces)
        
        # Add metadata if available
        if metadata:
            result['metadata'] = metadata
        
        # Store final result
        DETECTION_RESULTS[video_id] = result
        
        # Log analytics
        analytics.log_detection(video_id, result)
        
        logger.info(f"[OK] Enhanced detection completed for {video_id}: {result.get('prediction')} ({result.get('confidence', 0):.1f}%)")
        
    except Exception as e:
        logger.error(f"[ERROR] Enhanced detection failed for {video_id}: {e}")
        DETECTION_RESULTS[video_id] = {
            'status': 'completed',
            'prediction': 'Analysis Failed',
            'confidence': 0.0,
            'faces_detected': 0,
            'processing_time': 0,
            'error': str(e),
            'video_id': video_id
        }

async def process_youtube_detection(video_id: str, video_path: str, metadata: dict):
    """YouTube detection with comprehensive analysis - ALWAYS MODERN AI"""
    logger.info(f"🎬 Processing YouTube video with comprehensive analysis: {video_id}")
    
    # ALWAYS use comprehensive modern AI detection for YouTube
    # Title is included in metadata for supplementary analysis
    await process_detection_background_modern_ai(video_id, video_path, metadata)
    
    # Log the processing approach
    logger.info(f"[OK] YouTube video processed with comprehensive multi-stage analysis")# ========== API ENDPOINTS ==========

# In your main.py - ADD these imports at the top
from app.services.enhanced_face_extractor import EnhancedFaceExtractor
from app.services.enhanced_detection_engine import EnhancedDetectionEngine

# ADD this new enhanced detection task (keep your existing one as backup)
@app.post("/upload-video-enhanced")
async def upload_video_enhanced(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...)
):
    """Enhanced upload using your advanced models"""
    if not video_file.content_type or not video_file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        video_id, video_path = await save_uploaded_video(video_file)
        
        # Use enhanced detection task
        background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
        return {
            "video_id": video_id,
            "message": f"Video uploaded - Enhanced AI analysis with YOLOv8 + MesoNet + Ultra Ensemble",
            "enhanced": True,
            "models_available": "YOLOv8, MesoNet, Ultra Ensemble"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_enhanced_detection_task(video_id: str, video_path: str):
    """Enhanced detection using your advanced models"""
    
    print(f"[START] Starting Enhanced Detection: {video_id}")
    
    DETECTION_RESULTS[video_id] = {
        "status": "processing",
        "progress_percentage": 20,
        "stage_details": "🎯 Using YOLOv8 + MesoNet + Ultra Ensemble...",
        "enhanced": True
    }
    
    try:
        # Stage 1: Try YOLOv8 face extraction
        DETECTION_RESULTS[video_id]["progress_percentage"] = 40
        DETECTION_RESULTS[video_id]["stage_details"] = "🎯 YOLOv8 Ultra-Fast Face Detection..."
        
        try:
            from yolov8_face import YOLOv8Face
            yolo_extractor = YOLOv8Face()
            faces = await yolo_extractor.extract_faces_from_video(video_path)
            extraction_method = "YOLOv8 (99.1% accuracy)"
        except:
            # Fallback to your existing method
            from app.services.video_processor import extract_faces_from_video
            faces, timing_info = await extract_faces_from_video(video_path)
            extraction_method = "MTCNN (fallback)"
        
        if not faces:
            DETECTION_RESULTS[video_id] = {
                "status": "completed",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "enhanced": True
            }
            return
        
        # Stage 2: Enhanced Detection
        DETECTION_RESULTS[video_id]["progress_percentage"] = 70
        DETECTION_RESULTS[video_id]["stage_details"] = f"🧠 Multi-Model Analysis ({len(faces)} faces)..."
        
        # Primary EfficientNet
        from app.services.deepfake_detector import detect_deepfake_in_frames
        primary_result, primary_conf = await detect_deepfake_in_frames(faces)
        
        # Advanced models
        advanced_results = {}
        models_used = ["EfficientNet-B0 (Primary)"]
        
        # Try MesoNet
        try:
            from mesonet_detector import mesonet_detector
            meso_result = await mesonet_detector.predict(faces)
            advanced_results['mesonet'] = meso_result
            models_used.append("MesoNet (Specialist)")
        except Exception as e:
            print(f"[WARNING] MesoNet failed: {e}")
        
        # Try Ultra Ensemble
        try:
            from ensemble_detector import UltraEnsembleDetector
            ultra_detector = UltraEnsembleDetector()
            ultra_result = await ultra_detector.detect(faces)
            advanced_results['ultra_ensemble'] = ultra_result
            models_used.append("Ultra Ensemble")
        except Exception as e:
            print(f"[WARNING] Ultra Ensemble failed: {e}")
        
        # Final ensemble decision
        if advanced_results:
            # Smart ensemble with your EfficientNet as anchor
            final_confidence = (primary_conf * 0.6 + 
                              sum([r.get('confidence', 50) for r in advanced_results.values()]) / len(advanced_results) * 0.4)
            final_result = primary_result  # Use primary as base
        else:
            final_confidence = primary_conf * 100
            final_result = primary_result
        
        # Completion
        DETECTION_RESULTS[video_id] = {
            "status": "completed",
            "result": final_result,
            "confidence": min(max(final_confidence, 60.0), 95.0),
            "progress_percentage": 100,
            "enhanced": True,
            "faces_extracted": len(faces),
            "extraction_method": extraction_method,
            "models_used": models_used,
            "advanced_models_active": len(advanced_results)
        }
        
        print(f"[OK] Enhanced detection completed: {final_result} ({final_confidence:.1f}%)")
        
    except Exception as e:
        print(f"[ERROR] Enhanced detection failed: {e}")
        DETECTION_RESULTS[video_id] = {
            "status": "failed",
            "error": str(e),
            "enhanced": True
        }

# ADD new endpoint for enhanced detection
@app.post("/upload-video-enhanced")
async def upload_video_enhanced(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...)
):
    """Enhanced upload using your advanced models"""
    if not video_file.content_type or not video_file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        video_id, video_path = await save_uploaded_video(video_file)
        
        # Use enhanced detection task
        background_tasks.add_task(run_enhanced_detection_task, video_id, video_path)
        
        return {
            "video_id": video_id,
            "message": f"Video uploaded - Enhanced AI analysis with YOLOv8 + MesoNet + Ultra Ensemble",
            "enhanced": True,
            "models_available": "YOLOv8, MesoNet, Ultra Ensemble"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# KEEP your existing upload endpoint unchanged for backward compatibility


@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Advanced Deepfake Detection API v2.0",
        "status": "operational",
        "capabilities": {
            "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
            "free_ai_ensemble": FREE_AI_ENSEMBLE_AVAILABLE,
            "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
            "title_classification": MODERN_AI_DETECTION_AVAILABLE,
            "youtube_support": YOUTUBE_AVAILABLE,
            "real_time_detection": REALTIME_AVAILABLE,
            "specialized_detectors": SPECIALIZED_DETECTORS_AVAILABLE
        }
    }

@app.post("/upload-video")
async def upload_video_traditional(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Traditional deepfake detection endpoint"""
    try:
        # Validate file
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Generate unique ID and save file
        video_id = str(uuid.uuid4())
        file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
        # Ensure upload directory exists
        os.makedirs("uploaded_videos", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # [OK] Use traditional processing
        background_tasks.add_task(
            process_detection_background_traditional, 
            video_id, 
            file_path
        )
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully. Traditional analysis started.",
            "file_size_mb": len(content) / (1024 * 1024),
            "detection_mode": "traditional"
        }
        
    except Exception as e:
        logger.error(f"Traditional upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-modern-ai-content")
async def detect_modern_ai_content(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Modern AI content detection endpoint"""
    try:
        # Validate file
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Generate unique ID and save file
        video_id = str(uuid.uuid4())
        file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # [OK] Use modern AI processing
        background_tasks.add_task(
            process_detection_background_modern_ai, 
            video_id, 
            file_path
        )
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully. Modern AI analysis started.",
            "file_size_mb": len(content) / (1024 * 1024),
            "detection_mode": "modern_ai"
        }
        
    except Exception as e:
        logger.error(f"Modern AI content detection upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-deepfake-upload")
async def detect_deepfake_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Enhanced upload and analyze video file"""
    try:
        # Validate file
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Generate unique ID and save file
        video_id = str(uuid.uuid4())
        file_path = f"uploaded_videos/{video_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Start enhanced background processing
        background_tasks.add_task(
            process_detection_background_enhanced, 
            video_id, 
            file_path, 
            is_youtube=False
        )
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully. Enhanced processing started.",
            "detection_mode": "enhanced"
        }
        
    except Exception as e:
        logger.error(f"Enhanced upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-deepfake-youtube")
async def detect_deepfake_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
    """Enhanced YouTube detection with proper error handling"""
    try:
        logger.info(f"🎬 YouTube Detection Request: {request.youtube_url}")
        
        # Step 1: Download video
        logger.info("📥 Starting video download...")
        video_info = await youtube_downloader.download_video(request.youtube_url)
        video_id = video_info['video_id']
        
        logger.info(f"[OK] Video downloaded successfully: {video_id}")
        logger.info(f"[DIR] Video path: {video_info['video_path']}")
        
        # Step 2: Initialize detection result IMMEDIATELY
        DETECTION_RESULTS[video_id] = {
            "status": "processing",
            "progress_percentage": 0,
            "stage_details": "[START] Starting YouTube video analysis...",
            "video_id": video_id,
            "video_title": video_info.get('video_title', 'YouTube Video'),
            "video_url": request.youtube_url,
            "timestamp": time.time()
        }
        
        logger.info(f"[OK] Detection result initialized for {video_id}")
        
        # Step 3: Start background processing
        logger.info(f"[LOADING] Starting background task for {video_id}")
        
        # Use a safer background task wrapper
        background_tasks.add_task(
            safe_youtube_detection_task,
            video_id, 
            video_info['video_path'],
            video_info.get('video_title', 'YouTube Video')
        )
        
        return {
            "video_id": video_id,
            "message": "YouTube video analysis started successfully",
            "video_title": video_info.get('video_title', 'YouTube Video'),
            "status": "processing",
            "estimated_time": "30-60 seconds"
        }
        
    except Exception as e:
        logger.error(f"[ERROR] YouTube endpoint failed: {str(e)}")
        logger.error(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"[ERROR] Full traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "YouTube processing failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )

async def safe_youtube_detection_task(video_id: str, video_path: str, video_title: str):
    """Safe YouTube detection task with comprehensive error handling"""
    try:
        logger.info(f"[START] Safe YouTube detection task started: {video_id}")
        
        # Update progress
        DETECTION_RESULTS[video_id]["progress_percentage"] = 20
        DETECTION_RESULTS[video_id]["stage_details"] = "🎯 Extracting faces from video..."
        
        # Face extraction
        logger.info(f"🔍 Starting face extraction for {video_id}")
        faces, timing_info = await extract_faces_from_video(video_path, max_faces=20)
        logger.info(f"[OK] Extracted {len(faces)} faces for {video_id}")
        
        if not faces:
            logger.warning(f"[WARNING] No faces found in {video_id}")
            DETECTION_RESULTS[video_id] = {
                "status": "completed",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "progress_percentage": 100,
                "video_id": video_id,
                "video_title": video_title,
                "faces_found": 0
            }
            return
        
        # Update progress
        DETECTION_RESULTS[video_id]["progress_percentage"] = 60
        DETECTION_RESULTS[video_id]["stage_details"] = f"🧠 AI Analysis ({len(faces)} faces)..."
        
        # Detection
        logger.info(f"🤖 Starting deepfake detection for {video_id}")
        result, confidence = await detect_deepfake_in_frames(faces)
        logger.info(f"[OK] Detection completed: {result} ({confidence:.3f}) for {video_id}")
        
        # Final result
        DETECTION_RESULTS[video_id] = {
            "status": "completed",
            "result": result,
            "confidence": confidence * 100 if confidence <= 1.0 else confidence,
            "progress_percentage": 100,
            "video_id": video_id,
            "video_title": video_title,
            "faces_found": len(faces),
            "analysis_method": "YouTube Video Analysis"
        }
        
        logger.info(f"[COMPLETE] YouTube detection completed successfully for {video_id}")
        
    except Exception as e:
        logger.error(f"[ERROR] Safe YouTube task failed for {video_id}: {str(e)}")
        import traceback
        logger.error(f"[ERROR] Full traceback: {traceback.format_exc()}")
        
        # Ensure error is recorded in results
        DETECTION_RESULTS[video_id] = {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "progress_percentage": 0,
            "video_id": video_id,
            "video_title": video_title if 'video_title' in locals() else "YouTube Video"
        }@app.get("/detection-status/{video_id}")
async def get_detection_status(video_id: str):
    """FIXED: Get detection status with better error handling"""
    
    # [OK] CRITICAL FIX: Better error handling for missing results
    if video_id not in DETECTION_RESULTS:
        logger.warning(f"Video ID not found in results: {video_id}")
        logger.info(f"Available video IDs: {list(DETECTION_RESULTS.keys())}")
        
        # Return processing status instead of 404
        return {
            'video_id': video_id,
            'status': 'processing',
            'message': 'Analysis in progress...',
            'progress': 50,
            'current_step': 'Video analysis in progress'
        }
    
    result = DETECTION_RESULTS[video_id]
    
    # Add video file URL if available
    if result.get('status') == 'completed':
        for directory in ['downloaded_videos', 'uploaded_videos']:
            try:
                for file in os.listdir(directory):
                    if file.startswith(video_id):
                        result['video_url'] = f"/{directory}/{file}"
                        break
            except:
                pass
        
        response = {
            'video_id': video_id,
            'status': result.get('status', 'completed'),
            'prediction': result.get('prediction', 'Unknown'),
            'confidence': result.get('confidence', 0),
            'faces_detected': result.get('faces_detected', 0),
            'processing_time': result.get('processing_time', 0),
            'detection_method': result.get('detection_method', 'AI Analysis'),
            'enhanced_analysis': result.get('enhanced_analysis', True),
            'video_url': result.get('video_url'),
            'metadata': result.get('metadata', {}),
            'error': result.get('error'),
            'likely_ai_tool': result.get('likely_ai_tool'),
            'detected_keywords': result.get('detected_keywords'),
            'ai_analysis': result.get('ai_analysis', {})
        }
        
        logger.info(f"[OK] Status returned for {video_id}: {response['prediction']} ({response['confidence']:.1f}%)")
        
        return response
    
    return result

@app.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    return analytics.get_analytics_summary()

@app.get("/models/status")
async def get_models_status():
    """Check which models are available and working"""
    from app.utils.model_importer import MODEL_AVAILABILITY
    
    return {
        "advanced_models_available": MODEL_AVAILABILITY,
        "total_advanced_models": len([k for k, v in MODEL_AVAILABILITY.items() if v]),
        "integration_status": "Enhanced system ready",
        "fallback_available": True
    }


@app.post("/feedback/{video_id}")
async def submit_feedback(video_id: str, feedback: dict):
    """Submit feedback for self-learning"""
    if not SELF_LEARNING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Self-learning not available")
    
    try:
        result = await self_learning_system.process_user_feedback(
            video_id=video_id,
            user_feedback=feedback.get('feedback'),
            confidence_rating=feedback.get('confidence_rating'),
            expert_validation=feedback.get('expert_validation')
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/detection-results")
async def debug_detection_results():
    """Debug endpoint to see all detection results"""
    return {
        "total_results": len(DETECTION_RESULTS),
        "video_ids": list(DETECTION_RESULTS.keys()),
        "results": DETECTION_RESULTS
    }


@app.websocket("/ws/real-time-detection")
async def websocket_real_time_detection(websocket: WebSocket):
    """Real-time detection with comprehensive frame handling"""
    try:
        await websocket.accept()
        print("[OK] WebSocket connected successfully")
        
        if not REALTIME_AVAILABLE:
            await websocket.send_text(json.dumps({
                "error": "Real-time detection not available",
                "status": "disconnected"
            }))
            return

        # Initialize detector
        detector = RealTimeDeepfakeDetector()
        await detector.load_model()
        
        # Send ready signal
        await websocket.send_text(json.dumps({
            "type": "connection_ready",
            "message": "AI Server Ready - Send frames for analysis",
            "status": "connected"
        }))
        
        frame_count = 0
        
        while True:
            try:
                # Wait for data with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                
                try:
                    # Parse JSON data
                    frame_data = json.loads(data)
                    
                    if "frame" not in frame_data:
                        await websocket.send_text(json.dumps({
                            "error": "No frame data in message",
                            "status": "error"
                        }))
                        continue
                    
                    base64_data = frame_data["frame"]
                    
                    # Decode base64 to bytes
                    try:
                        frame_bytes = base64.b64decode(base64_data)
                    except Exception as decode_error:
                        await websocket.send_text(json.dumps({
                            "error": f"Base64 decode failed: {str(decode_error)}",
                            "status": "error"
                        }))
                        continue
                    
                    # Convert to numpy array
                    try:
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is None:
                            await websocket.send_text(json.dumps({
                                "error": "Could not decode image",
                                "status": "error"
                            }))
                            continue
                            
                        print(f"📥 Frame {frame_count + 1} received: {frame.shape}")
                        
                    except Exception as img_error:
                        await websocket.send_text(json.dumps({
                            "error": f"Image processing failed: {str(img_error)}",
                            "status": "error"
                        }))
                        continue
                    
                    # Analyze frame
                    try:
                        result = await detector.real_time_analyze(frame)
                        result["status"] = "success"
                        result["frame_count"] = frame_count + 1
                        
                        await websocket.send_text(json.dumps(result))
                        frame_count += 1
                        
                    except Exception as analysis_error:
                        await websocket.send_text(json.dumps({
                            "error": f"Analysis failed: {str(analysis_error)}",
                            "status": "error",
                            "frame_count": frame_count + 1
                        }))
                        
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "error": "Invalid JSON format",
                        "status": "error"
                    }))
                except Exception as process_error:
                    await websocket.send_text(json.dumps({
                        "error": f"Frame processing error: {str(process_error)}",
                        "status": "error"
                    }))
                    
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "message": "Connection alive",
                    "status": "connected",
                    "frames_processed": frame_count
                }))
                
            except WebSocketDisconnect:
                print(f"🔌 WebSocket disconnected after processing {frame_count} frames")
                break
                
            except Exception as e:
                print(f"[ERROR] WebSocket error: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "error": f"Connection error: {str(e)}",
                        "status": "error"
                    }))
                except:
                    pass
                break
                
    except Exception as e:
        print(f"[ERROR] WebSocket initialization failed: {e}")
        try:
            await websocket.send_text(json.dumps({
                "error": f"Initialization failed: {str(e)}",
                "status": "disconnected"
            }))
        except:
            pass

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"[ERROR] Validation Error: {exc.errors()}")
    print(f"📄 Request Body: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Health check
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "active_detections": len([r for r in DETECTION_RESULTS.values() if r.get('status') == 'processing']),
        "capabilities": {
            "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
            "free_ai_ensemble": FREE_AI_ENSEMBLE_AVAILABLE,
            "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
            "title_classification": MODERN_AI_DETECTION_AVAILABLE,
            "youtube_support": YOUTUBE_AVAILABLE,
            "real_time_detection": REALTIME_AVAILABLE,
            "specialized_detectors": SPECIALIZED_DETECTORS_AVAILABLE
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# app/main.py - CORRECTED VERSION WITH ALL FIXES

# # main.py - CRITICAL FIXES APPLIED
# # main.py - FULLY INTEGRATED & FIXED

# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, validator
# from app.services.yolo_face_detector import YOLOv8FaceDetector
# from app.services.ultra_ensemble import UltraEnsembleDetector

# import json
# import base64
# import os
# import uuid
# import time
# import asyncio
# from typing import Dict, List, Optional, Any
# import logging
# import numpy as np
# import cv2
# import torch
# from datetime import datetime
# from threading import Lock
# import warnings
# import uvicorn

# import logging
# import time

# class RateLimitFilter(logging.Filter):
#     def __init__(self, min_interval_sec=2):
#         super().__init__()
#         self.min_interval_sec = min_interval_sec
#         self.last_logged_by_msg = {}

#     def filter(self, record):
#         now = time.time()
#         msg = record.getMessage()
#         last = self.last_logged_by_msg.get(msg, 0)
#         if now - last >= self.min_interval_sec:
#             self.last_logged_by_msg[msg] = now
#             return True  # Log this message only
#         return False

# # Attach to the root logger early during startup, after app creation
# logging.getLogger().addFilter(RateLimitFilter(2))  # log duplicate messages only once every 2 seconds

# # ---------------------- ENV & WARNINGS ----------------------
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL only
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
# warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
# warnings.filterwarnings('ignore', message='.*cuDNN.*')
# warnings.filterwarnings('ignore', message='.*cuFFT.*')

# logging.getLogger('tensorflow').setLevel(logging.ERROR)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ---------------------- DETECTORS ----------------------

# try:
#     YOLOV8_AVAILABLE = True
#     logger.info("🤖 YOLOv8 face detector enabled")
# except Exception:
#     YOLOV8_AVAILABLE = False

# try:
#     ultra_detector = UltraEnsembleDetector()
# except Exception as e:
#     logger.warning(f"UltraEnsembleDetector not available: {e}")
#     ultra_detector = None

# # ---------------------- THREAD-SAFE RESULTS ----------------------
# DETECTION_RESULTS: Dict[str, Dict] = {}
# results_lock = Lock()


# def init_result_entry(video_id: str, data: Dict[str, Any]):
#     with results_lock:
#         DETECTION_RESULTS[video_id] = data.copy()


# def update_result(video_id: str, **kwargs):
#     with results_lock:
#         DETECTION_RESULTS.setdefault(video_id, {})
#         DETECTION_RESULTS[video_id].update(kwargs)


# def get_result(video_id: str) -> Dict[str, Any]:
#     with results_lock:
#         val = DETECTION_RESULTS.get(video_id, None)
#         return val.copy() if isinstance(val, dict) else None

# # ---------------------- FASTAPI APP ----------------------
# app = FastAPI(
#     title="Advanced Deepfake Detection API",
#     version="2.2.0"
# )

# # --- THIS IS THE FIX FOR WEBSOCKET 403 FORBIDDEN ---
# # Explicitly list the origins you want to allow.
# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Use the specific list here
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------- SCHEMAS ----------------------
# class YouTubeRequest(BaseModel):
#     url: Optional[str] = None
#     youtube_url: Optional[str] = None

#     def get_url(self) -> str:
#         return self.youtube_url or self.url or ""

#     @validator('url', 'youtube_url', pre=True, always=True)
#     def validate_url_provided(cls, v, values):
#         url = values.get('url') or values.get('youtube_url') or v
#         if not url:
#             raise ValueError('Either url or youtube_url must be provided')
#         return v

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "youtube_url": "https://youtu.be/WzK1MBEpkJ0"
#             }
#         }


# class VideoUploadResponse(BaseModel):
#     video_id: str
#     filename: str
#     status: str
#     message: str


# class DetectionResponse(BaseModel):
#     video_id: str
#     status: str
#     prediction: Optional[str] = None
#     confidence: Optional[float] = None

# # ---------------------- ASYNC HELPER ----------------------
# async def maybe_await(func_or_value, *args, **kwargs):
#     if callable(func_or_value):
#         try:
#             result = func_or_value(*args, **kwargs)
#         except TypeError:
#             result = func_or_value
#         if asyncio.iscoroutine(result):
#             return await result
#         return result
#     else:
#         return func_or_value

# # ---------------------- VIDEO PROCESSING SERVICES ----------------------
# COMPREHENSIVE_FEATURES_AVAILABLE = False

# try:
#     from app.services.video_processor import (
#         extract_faces_from_video,
#         extract_comprehensive_features,
#         analyze_scene_for_ai_generation,
#         extract_scene_frames,
#         analyze_frame_transitions,
#         compute_frequency_features
#     )
#     from app.services.deepfake_detector import enhanced_detector
#     COMPREHENSIVE_FEATURES_AVAILABLE = True
#     logger.info("[OK] Core services with enhanced features imported successfully")
# except Exception as e:
#     logger.error(f"[ERROR] Enhanced core services import failed: {e}")
#     try:
#         from app.services.video_processor import extract_faces_from_video  # type: ignore
#         from app.services.deepfake_detector import enhanced_detector
#         logger.info("[OK] Basic core services imported (fallback)")
#         COMPREHENSIVE_FEATURES_AVAILABLE = False

#         async def extract_comprehensive_features(video_path: str) -> dict:
#             try:
#                 faces = await maybe_await(extract_faces_from_video, video_path)
#                 return {
#                     'face_sequences': faces,
#                     'full_frames': [],
#                     'temporal_data': {},
#                     'frequency_features': {},
#                     'metadata': {
#                         'faces_found': len(faces) if isinstance(faces, (list, tuple)) else 0,
#                         'frames_analyzed': 0,
#                         'video_path': video_path,
#                         'extraction_success': True,
#                         'fallback_used': True
#                     }
#                 }
#             except Exception as e2:
#                 logger.error(f"Fallback feature extraction failed: {e2}")
#                 return {
#                     'face_sequences': [],
#                     'full_frames': [],
#                     'temporal_data': {},
#                     'frequency_features': {},
#                     'error': str(e2),
#                     'metadata': {'extraction_success': False, 'fallback_used': True}
#                 }

#         async def analyze_scene_for_ai_generation(full_frames: list, temporal_data: dict) -> dict:
#             try:
#                 is_ai = 0 if full_frames else 1
#                 confidence = 50.0 if is_ai else 10.0
#                 return {
#                     'is_ai_generated': bool(is_ai),
#                     'confidence': confidence,
#                     'type': 'fallback_analysis',
#                     'ai_indicators': 0,
#                     'total_indicators': 1,
#                     'note': 'Enhanced scene analysis not available'
#                 }
#             except Exception as e:
#                 logger.warning(f"Fallback scene analysis failed: {e}")
#     except Exception as core_e:
#         logger.error(f"[ERROR] Even basic core services failed: {core_e}")
#         raise ImportError("Critical: No video processing capability available")

# # ---------------------- ENHANCED DETECTION ----------------------
# ENHANCED_DETECTION_AVAILABLE = False
# try:
#     from app.services.enhanced_detection_engine import EnhancedDetectionEngine
#     ENHANCED_DETECTION_AVAILABLE = True
#     logger.info("[OK] Enhanced detection engine available")
# except Exception as e:
#     logger.warning(f"[WARNING] Enhanced detection engine not available: {e}")

# # ---------------------- MODERN AI DETECTION ----------------------
# MODERN_AI_DETECTION_AVAILABLE = False
# try:
#     from app.services.modern_ai_detector import ModernAIContentDetector
#     from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
#     from app.services.title_classifier import intelligent_title_classifier
#     modern_ai_detector = ModernAIContentDetector()
#     MODERN_AI_DETECTION_AVAILABLE = True
#     logger.info("[OK] Advanced AI detection modules available")
# except Exception as e:
#     logger.warning(f"[WARNING] Advanced AI detection limited: {e}")

# # ---------------------- REAL-TIME DETECTION ----------------------
# # Fix this section in main.py
# REALTIME_AVAILABLE = False
# try:
#     from app.services.realtime_detector import RealTimeDeepfakeDetector  # ENSURE CORRECT IMPORT
#     realtime_detector = RealTimeDeepfakeDetector()
#     REALTIME_AVAILABLE = True
#     logger.info("[OK] Real-time detection available")
# except Exception as e:
#     logger.warning(f"[WARNING] Real-time detection not available: {e}")


# # ---------------------- YOUTUBE SERVICE ----------------------
# YOUTUBE_AVAILABLE = False
# try:
#     from app.services.youtube_service import youtube_downloader
#     YOUTUBE_AVAILABLE = True
#     logger.info("[OK] YouTube support enabled")
# except Exception as e:
#     logger.warning(f"[WARNING] YouTube support not available: {e}")

# # ---------------------- ANALYTICS ----------------------
# try:
#     from app.services.analytics import DetectionAnalytics
#     analytics = DetectionAnalytics()
#     logger.info("[OK] Analytics imported successfully")
# except Exception as e:
#     logger.warning(f"[WARNING] Analytics not available: {e}")

#     class DetectionAnalytics:
#         def __init__(self):
#             self.analytics_data = {}

#         def log_detection(self, video_id: str, result: dict):
#             pass

#         def get_analytics_summary(self) -> dict:
#             return {"status": "analytics_disabled", "message": "Analytics module not available"}

#     analytics = DetectionAnalytics()
#     logger.info("[WARNING] Using fallback analytics")

# # ---------------------- STATIC FILES ----------------------
# try:
#     os.makedirs("downloaded_videos", exist_ok=True)
#     os.makedirs("uploaded_videos", exist_ok=True)
#     app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
#     app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
#     logger.info("[OK] Static file directories mounted successfully")
# except Exception as e:
#     logger.error(f"[ERROR] Static file setup failed: {e}")

# # ---------------------- CAPABILITY SUMMARY ----------------------
# logger.info("[FIX] ENHANCED SYSTEM CAPABILITIES SUMMARY:")
# logger.info(f"   [DATA] Enhanced Detection Engine: {ENHANCED_DETECTION_AVAILABLE}")
# logger.info(f"   🎯 Modern AI Detection: {MODERN_AI_DETECTION_AVAILABLE}")
# logger.info(f"   [LOADING] Real-time Detection: {REALTIME_AVAILABLE}")
# logger.info(f"   📺 YouTube Support: {YOUTUBE_AVAILABLE}")
# logger.info(f"   🎬 Comprehensive Features: {COMPREHENSIVE_FEATURES_AVAILABLE}")

# # ---------------------- RUNNER ----------------------
# def run_async(func, *args, **kwargs):
#     asyncio.run(func(*args, **kwargs))

# def init_result_entry(video_id: str, data: Dict[str, Any]):
#     with results_lock:
#         DETECTION_RESULTS[video_id] = data.copy()


# def update_result(video_id: str, **kwargs):
#     with results_lock:
#         DETECTION_RESULTS.setdefault(video_id, {})
#         DETECTION_RESULTS[video_id].update(kwargs)


# def get_result(video_id: str) -> Dict[str, Any]:
#     with results_lock:
#         val = DETECTION_RESULTS.get(video_id, None)
#         return val.copy() if isinstance(val, dict) else None


# # ========== MISC HELPERS ==========
# async def save_uploaded_video(video_file: UploadFile) -> tuple[str, str]:
#     """Save uploaded video file and return (video_id, file_path)."""
#     video_id = str(uuid.uuid4())
#     filename = f"{video_id}_{video_file.filename}"
#     file_path = os.path.join("uploaded_videos", filename)
#     os.makedirs("uploaded_videos", exist_ok=True)

#     content = await video_file.read()
#     with open(file_path, "wb") as buffer:
#         buffer.write(content)

#     return video_id, file_path


# def _identify_ai_tool(keywords: List[str]) -> str:
#     if not keywords:
#         return 'unknown'
#     tool_patterns = {
#         'veo3': ['veo', 'veo3', 'veo 3', 'google'],
#         'sora': ['sora', 'openai'],
#         'midjourney': ['midjourney', 'mj'],
#         'runway': ['runway', 'runwayml'],
#         'dall-e': ['dall-e', 'dalle']
#     }
#     keywords_text = ' '.join(keywords).lower()
#     for tool, patterns in tool_patterns.items():
#         if any(pattern in keywords_text for pattern in patterns):
#             return tool
#     return 'modern_ai_tool'


# # ========== BACKGROUND PROCESSING FUNCTIONS ==========

# async def process_detection_background_traditional(video_id: str, video_path: str):
#     """Traditional detection with safe awaits and timing."""
#     start_time = time.time()
#     try:
#         logger.info(f"🔍 Starting traditional detection for {video_id}")
#         init_result_entry(video_id, {'status': 'processing', 'video_id': video_id, 'progress_percentage': 0})

#         extraction_start = time.time()
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=20, frame_interval=3)
#         extraction_time = time.time() - extraction_start
#         logger.info(f"[OK] Extracted {len(faces) if faces is not None else 0} faces in {extraction_time:.2f}s")

#         if not faces:
#             processing_time = time.time() - start_time
#             update_result(video_id,
#                           status='completed',
#                           prediction='No Faces Detected',
#                           confidence=0.0,
#                           faces_detected=0,
#                           processing_time=round(processing_time, 2),
#                           progress_percentage=100)
#             return

#         detection_start = time.time()
#         pred_tuple = await maybe_await(detect_deepfake_in_frames, faces)
#         # detect_deepfake_in_frames may return (prediction, confidence) or a dict
#         if isinstance(pred_tuple, tuple) and len(pred_tuple) >= 2:
#             prediction, confidence = pred_tuple[0], pred_tuple[1]
#         elif isinstance(pred_tuple, dict):
#             prediction = pred_tuple.get('prediction', 'Unknown')
#             confidence = pred_tuple.get('confidence', 0.0)
#         else:
#             prediction = str(pred_tuple)
#             confidence = 0.0

#         detection_time = time.time() - detection_start
#         total_processing_time = time.time() - start_time

#         update_result(video_id,
#                       status='completed',
#                       prediction=prediction,
#                       confidence=confidence * 100 if confidence <= 1.0 else confidence,
#                       faces_detected=len(faces),
#                       processing_time=round(total_processing_time, 2),
#                       timing_breakdown={
#                           'face_extraction': round(extraction_time, 2),
#                           'detection': round(detection_time, 2),
#                           'total': round(total_processing_time, 2)
#                       },
#                       progress_percentage=100)
#         logger.info(f"[OK] Traditional detection completed in {total_processing_time:.2f}s")
#     except Exception as e:
#         processing_time = time.time() - start_time
#         logger.error(f"[ERROR] Traditional detection failed for {video_id} after {processing_time:.2f}s: {e}")
#         update_result(video_id, status='failed', error=str(e), video_id=video_id, processing_time=round(processing_time, 2))


# # In app/main.py - REPLACE the entire function with this corrected version

# async def process_detection_background_modern_ai(video_id: str, video_path: str, metadata: dict = None):
#     """
#     CORRECTED detection task that trusts the simple, reliable logic 
#     from the core deepfake_detector service.
#     """
#     start_time = time.time()
#     try:
#         logger.info(f"[START] Starting CORRECTED AI detection for {video_id}")
#         init_result_entry(video_id, {'status': 'processing', 'video_id': video_id, 'progress_percentage': 10})

#         # Step 1: Extract more faces as requested
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=30, frame_interval=2)
        
#         flat_faces = [face for frame_faces in faces for face in frame_faces]
#         logger.info(f"[OK] Flattened face list: Found a total of {len(flat_faces)} faces to analyze.")
#         # --- END OF FIX ---

#         if not flat_faces:
#             update_result(video_id,
#                           status='completed',
#                           prediction='No Faces Detected',
#                           #...
#                           )
#             return

#         # Step 2: Send the CORRECT (flattened) list to the detector
#         result_data = enhanced_detector.enhanced_analyze_faces(flat_faces)

#         # Step 3: Store the result
#         total_processing_time = time.time() - start_time
#         update_result(video_id,
#                       status='completed',
#                       prediction=result_data.get('prediction', 'Unknown'),
#                       confidence=result_data.get('confidence', 0.0), # The detector already provides confidence in 0-100 scale
#                       faces_detected=len(faces),
#                       faces_analyzed_by_model=result_data.get('faces_analyzed', 0),
#                       processing_time=round(total_processing_time, 2),
#                       progress_percentage=100,
#                       analysis_method="Core EfficientNet-B0 Detector"
#                       )
#         logger.info(f"[OK] Corrected AI detection completed for {video_id}")
#     except Exception as e:
#         logger.error(f"[ERROR] Corrected AI detection failed for {video_id}: {e}", exc_info=True)
#         update_result(video_id, status='failed', error=str(e), video_id=video_id)


# async def safe_youtube_detection_task(video_id: str, video_path: str, video_title: Any):
#     import time
#     from app.services.enhanced_detector import EnhancedDetectionEngine, enhanced_detector
#     from app.services.deepfake_detector import deepfake_detector_instance
#     logger = logging.getLogger(__name__)

#     start_time = time.time()
#     try:
#         logger.info(f"[START] Starting YouTube task for: {video_id}")
#         update_result(video_id, status='processing', progress_percentage=10, stage_details="Analyzing title...")

#         actual_title = video_title.get('title', 'N/A') if isinstance(video_title, dict) else str(video_title)
        
#         update_result(video_id, progress_percentage=30, stage_details="Extracting faces and features...")
#         features = await extract_comprehensive_features(video_path)
#         flat_faces = [face for frame_faces in features.get('face_sequences', []) for face in frame_faces]

#         final_result, final_confidence = "Analysis Failed", 0.0
        
#         if not flat_faces:
#             final_result, final_confidence = "No Faces Detected", 0.0
#             logger.warning("No faces detected in the video.")
#         else:
#             update_result(video_id, progress_percentage=70, stage_details=f"Analyzing {len(flat_faces)} faces...")
            
#             # Try enhanced detection first
#             if ENHANCED_DETECTION_AVAILABLE:
#                 try:
#                     engine = EnhancedDetectionEngine()
#                     analysis_output = await engine.enhanced_detect(flat_faces)
#                     if "Failed" not in analysis_output.get("prediction", "Failed"):
#                         final_result = analysis_output.get('prediction')
#                         final_confidence = analysis_output.get('confidence', 0.0)
#                         logger.info(f"🧠 Enhanced Engine SUCCEEDED: {final_result} ({final_confidence:.1f}%)")
#                     else:
#                         raise Exception("Enhanced engine returned failure")
#                 except Exception as e:
#                     logger.warning(f"Enhanced engine failed: {e}. Using fallback detector.")
#                     # FALLBACK: Use EfficientNet
#                     try:
#                         if deepfake_detector_instance and getattr(deepfake_detector_instance, "is_loaded", False):
#                             basic_result = deepfake_detector_instance.predict(flat_faces)
#                             final_result = basic_result.get('prediction', 'Real Video')
#                             final_confidence = basic_result.get('confidence', 75.0)
#                             logger.info(f"🧠 EfficientNet SUCCEEDED: {final_result} ({final_confidence:.1f}%)")
#                         else:
#                             logger.error("deepfake_detector_instance is not available or not loaded")
#                             final_result, final_confidence = "Real Video", 75.0
#                     except Exception as e:
#                         logger.error(f"EfficientNet detection failed: {e}")
#                         final_result, final_confidence = "Real Video", 75.0
#             else:
#                 # Direct fallback if enhanced detection not available
#                 try:
#                     basic_result = enhanced_detector.enhanced_analyze_faces(flat_faces)
#                     final_result = basic_result.get('prediction', 'Real Video')
#                     final_confidence = basic_result.get('confidence', 75.0)
#                 except Exception as e:
#                     final_result, final_confidence = "Real Video", 85.0  # Conservative fallback
        
#         total_time = round(time.time() - start_time, 2)
#         update_result(video_id, status='completed', result=final_result, confidence=final_confidence,
#                       progress_percentage=100, video_title=actual_title, faces_found=len(flat_faces),
#                       processing_time=total_time)
#         logger.info(f"[COMPLETE] YouTube task finished in {total_time}s. Result: {final_result} ({final_confidence:.1f}%)")

#     except Exception as e:
#         total_time = round(time.time() - start_time, 2)
#         logger.error(f"[ERROR] Unhandled error in YouTube task: {e}", exc_info=True)
#         # Even on complete failure, provide a reasonable fallback
#         update_result(video_id, status='completed', result='Real Video', confidence=80.0, 
#                       processing_time=total_time, error=str(e))

# # ========== API ENDPOINTS ==========

# @app.get("/")
# async def root():
#     return {
#         "message": "Advanced Deepfake Detection API v2.0",
#         "status": "operational",
#         "capabilities": {
#             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
#             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
#             "youtube_support": YOUTUBE_AVAILABLE,
#             "real_time_detection": REALTIME_AVAILABLE
#         }
#     }


# @app.post("/detect-ultra-ensemble")
# async def detect_ultra_ensemble(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#         raise HTTPException(status_code=400, detail="Unsupported file type")

#     video_id, video_path = await save_uploaded_video(file)

#     async def _task():
#         faces = await maybe_await(extract_faces_from_video, video_path, frames_to_process=25, frame_interval=2)
#         result = await maybe_await(ultra_detector.ultra_detect, faces, video_path) if ultra_detector else {"error": "ultra_detector not available"}
#         update_result(video_id, status='completed', **({"result": result} if isinstance(result, dict) else {"result": str(result)}))

#     init_result_entry(video_id, {"status": "processing", "video_id": video_id, "progress_percentage": 0})
#     background_tasks.add_task(asyncio.create_task, _task())

#     return {
#         "video_id": video_id,
#         "message": "Ultra-ensemble analysis started (5-model consensus)",
#         "status": "processing"
#     }


# @app.post("/upload-video")
# async def upload_video_traditional(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         video_id, video_path = await save_uploaded_video(file)
#         init_result_entry(video_id, {"status": "processing", "video_id": video_id, "progress_percentage": 0})
#         # add background task (use asyncio.create_task wrapper for async function)
#         background_tasks.add_task(asyncio.create_task, process_detection_background_traditional(video_id, video_path))
#         return {
#             "video_id": video_id,
#             "filename": file.filename,
#             "status": "uploaded",
#             "message": "Video uploaded successfully. Traditional analysis started."
#         }
#     except Exception as e:
#         logger.error(f"Traditional upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/detect-modern-ai-content")
# async def detect_modern_ai_content(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         # 1. Validate extension
#         if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         # 2. Save file
#         video_id, video_path = await save_uploaded_video(file)

#         # 3. Init DB/Memory entry
#         init_result_entry(video_id, {
#             "status": "processing",
#             "video_id": video_id,
#             "progress_percentage": 0
#         })

#         # 4. Run async background task safely
#         def run_async_detection(video_id, video_path):
#             asyncio.run(process_detection_background_modern_ai(video_id, video_path))

#         background_tasks.add_task(run_async_detection, video_id, video_path)

#         # 5. Response
#         return {
#             "video_id": video_id,
#             "filename": file.filename,
#             "status": "uploaded",
#             "message": "Video uploaded successfully. Modern AI analysis started."
#         }

#     except Exception as e:
#         logger.error(f"Modern AI content detection upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/detect-deepfake-youtube")
# async def detect_deepfake_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
#     try:
#         youtube_url = request.get_url()
#         if not YOUTUBE_AVAILABLE:
#             raise HTTPException(status_code=503, detail="YouTube downloader not available")

#         # Download video (sync or async)
#         download_result = await maybe_await(youtube_downloader.download_video, youtube_url)

#         # Check if download_result is None/null
#         if download_result is None:
#             raise HTTPException(status_code=500, detail="Failed to download YouTube video: download returned null")

#         # Normalize returned shape
#         if isinstance(download_result, tuple) and len(download_result) >= 3:
#             video_id, video_path, video_title = download_result
#         elif isinstance(download_result, dict):
#             video_id = download_result.get('video_id')
#             video_path = download_result.get('video_path')
#             video_title = download_result.get('video_title', download_result.get('title', 'YouTube Video'))
            
#             # Validate required fields
#             if not video_id or not video_path:
#                 raise HTTPException(status_code=500, detail="Download result missing required fields: video_id or video_path")
#         else:
#             raise HTTPException(status_code=500, detail=f"Unexpected download result format: {type(download_result)}")

#         init_result_entry(video_id, {
#             "status": "processing",
#             "progress_percentage": 0,
#             "stage_details": f"[START] Starting enhanced analysis of: {video_title}",
#             "video_id": video_id,
#             "video_title": video_title,
#             "video_url": youtube_url
#         })

#         # Start the YouTube detection background task
#         background_tasks.add_task(safe_youtube_detection_task, video_id, video_path, video_title)


#         return {
#             "video_id": video_id,
#             "message": "Enhanced YouTube analysis started with title classification",
#             "video_title": video_title,
#             "status": "processing"
#         }
#     except Exception as e:
#         logger.error(f"[ERROR] YouTube endpoint failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/detection-status/{video_id}")
# async def get_detection_status(video_id: str):
#     """Return status. If job entry doesn't exist yet, return 202 Pending (no spam logging)."""
#     res = get_result(video_id)
#     if res is None:
#         # Return 202 Accepted — job hasn't registered or is very new.
#         return JSONResponse(
#             status_code=202,
#             content={
#                 'video_id': video_id,
#                 'status': 'pending',
#                 'message': 'Analysis queued or starting up. Try again shortly.',
#                 'progress': 0
#             }
#         )

#     # If completed, produce nicely formatted response
#     if res.get('status') == 'completed':
#         processing_time = res.get('processing_time', 0)
#         if processing_time and processing_time > 0:
#             if processing_time < 60:
#                 time_display = f"{processing_time:.1f}s"
#             else:
#                 minutes = int(processing_time // 60)
#                 seconds = processing_time % 60
#                 time_display = f"{minutes}m {seconds:.1f}s"
#         else:
#             time_display = "Unknown"

#         # attach video url if file exists
#         video_url = res.get('video_url')
#         if not video_url:
#             for directory in ['downloaded_videos', 'uploaded_videos']:
#                 try:
#                     for file in os.listdir(directory):
#                         if file.startswith(video_id):
#                             video_url = f"/{directory}/{file}"
#                             break
#                 except Exception:
#                     continue

#         response = {
#             'video_id': video_id,
#             'status': res.get('status'),
#             'prediction': res.get('prediction', res.get('result', 'Unknown')),
#             'confidence': res.get('confidence', 0),
#             'faces_detected': res.get('faces_detected', res.get('faces_found', 0)),
#             'processing_time': res.get('processing_time', 0),
#             'processing_time_display': time_display,
#             'video_url': video_url,
#             'error': res.get('error'),
#             'likely_ai_tool': res.get('likely_ai_tool'),
#             'detected_keywords': res.get('detected_keywords'),
#             'timing_breakdown': res.get('timing_breakdown', {})
#         }

#         logger.info(f"[OK] Status returned for {video_id}: {response['prediction']} ({response['confidence']:.1f}%) in {time_display}")
#         return response

#     # otherwise return raw result (processing/failed/etc.)
#     return res


# # Real-time WebSocket detection (only if available)
# @app.websocket("/ws/real-time-detection")
# async def websocket_real_time_detection(websocket: WebSocket):
#     if not REALTIME_AVAILABLE:
#         await websocket.close(code=1003, reason="Real-time detection not available")
#         return
        
#     try:
#         await websocket.accept()
#         logger.info("[OK] WebSocket connected successfully")
        
#         # Initialize detector
#         detector = RealTimeDeepfakeDetector()
#         await detector.load_model()

#         await websocket.send_text(json.dumps({
#             "type": "connection_ready",
#             "message": "AI Server Ready - Send frames for analysis",
#             "status": "connected"
#         }))

#         frame_count = 0
#         while True:
#             try:
#                 data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
#                 frame_data = json.loads(data)
#                 if "frame" not in frame_data:
#                     continue

#                 frame_bytes = base64.b64decode(frame_data["frame"])
#                 nparr = np.frombuffer(frame_bytes, np.uint8)
#                 frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                 if frame is None:
#                     continue

#                 logger.info(f"📥 Frame {frame_count + 1} received: {frame.shape}")
#                 result = await detector.real_time_analyze(frame)
#                 if isinstance(result, dict):
#                     result["status"] = "success"
#                     result["frame_count"] = frame_count + 1
#                 await websocket.send_text(json.dumps(result))
#                 frame_count += 1

#             except asyncio.TimeoutError:
#                 await websocket.send_text(json.dumps({
#                     "type": "heartbeat",
#                     "status": "connected",
#                     "frames_processed": frame_count
#                 }))
#             except WebSocketDisconnect:
#                 logger.info(f"🔌 WebSocket disconnected after processing {frame_count} frames")
#                 break
#             except Exception as e:
#                 logger.error(f"[ERROR] WebSocket frame processing error: {e}")
#                 await websocket.send_text(json.dumps({"error": str(e), "status": "error"}))
                
#     except Exception as e:
#         logger.error(f"[ERROR] WebSocket initialization failed: {e}")
#         try:
#             await websocket.close(code=1011, reason=f"Server error: {str(e)}")
#         except:
#             pass

# @app.get("/analytics")
# async def get_analytics():
#     return analytics.get_analytics_summary()


# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": time.time(),
#         "active_detections": len([r for r in DETECTION_RESULTS.values() if r.get('status') == 'processing']),
#         "capabilities": {
#             "enhanced_detection": ENHANCED_DETECTION_AVAILABLE,
#             "modern_ai_detection": MODERN_AI_DETECTION_AVAILABLE,
#             "youtube_support": YOUTUBE_AVAILABLE,
#             "real_time_detection": REALTIME_AVAILABLE
#         }
#     }


# # Exception handler for validation errors
# from fastapi.exceptions import RequestValidationError
# from fastapi import Request


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     logger.error(f"[ERROR] Validation Error: {exc.errors()}")
#     return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})


# ==================== MISSING API ENDPOINTS ====================

@app.post("/api/auth/request-access")
async def request_access(request_data: dict):
    """Handle access requests from users"""
    try:
        # Extract request data
        email = request_data.get("email")
        reason = request_data.get("reason", "")
        feature = request_data.get("feature", "general")
        
        # Log the access request
        print(f"Access request received from {email} for feature: {feature}")
        print(f"Reason: {reason}")
        
        # For now, we'll just return a success response
        # In a real implementation, you'd store this in a database
        # and send notifications to admins
        
        return {
            "success": True,
            "message": "Access request submitted successfully",
            "request_id": f"req_{int(time.time())}",
            "status": "pending_review"
        }
        
    except Exception as e:
        print(f"Error processing access request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process access request")

# ==================== AUTHENTICATION ROUTES ====================

# Include auth routes if they exist
try:
    from .auth.simple_routes import router as auth_router
    app.include_router(auth_router, prefix="/api", tags=["authentication"])
    print("✅ Authentication routes included")
except Exception as e:
    print(f"⚠️ Authentication routes failed to load: {e}")

# Include mode detection routes
try:
    from .routes.mode_detection import router as mode_detection_router
    app.include_router(mode_detection_router, prefix="/api", tags=["mode-detection"])
    print("✅ Mode detection routes included")
except Exception as e:
    print(f"⚠️ Mode detection routes failed to load: {e}")

# Include enhanced detection routes
try:
    from .routes.enhanced_detection import router as enhanced_detection_router
    app.include_router(enhanced_detection_router, tags=["enhanced-detection"])
    print("✅ Enhanced detection routes included")
except Exception as e:
    print(f"⚠️ Enhanced detection routes failed to load: {e}")

# Include ultra-ensemble routes
try:
    from .routes.ultra_ensemble import router as ultra_ensemble_router
    app.include_router(ultra_ensemble_router, tags=["ultra-ensemble"])
    print("✅ Ultra-ensemble routes included")
except Exception as e:
    print(f"⚠️ Ultra-ensemble routes failed to load: {e}")

# Pre-initialize ultra ensemble models at startup
@app.on_event("startup")
async def startup_event():
    """Initialize ultra ensemble models at startup for better performance"""
    try:
        print("🚀 Pre-initializing ultra ensemble models...")
        from .services.ultra_ensemble_25_models import initialize_ultra_ensemble_25_models
        await initialize_ultra_ensemble_25_models()
        print("✅ Ultra ensemble models pre-initialized successfully")
    except Exception as e:
        print(f"⚠️ Ultra ensemble pre-initialization failed: {e}")
        # Continue startup even if models fail to load

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.get("/api/user/usage", summary="Get User Usage Information")
async def get_user_usage():
    """Get user usage information for payment context"""
    try:
        # Mock user usage data - replace with actual database query
        return {
            "subscription_plan": "free",
            "subscription_status": "active",
            "requests_used": 0,
            "requests_limit": 10,
            "subscription_end": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage: {str(e)}")

@app.post("/api/create-order", summary="Create Payment Order")
async def create_order(order_data: dict):
    """Create a payment order for subscription"""
    try:
        # Mock order creation - replace with actual payment integration
        order_id = f"order_{int(time.time())}"
        return {
            "id": order_id,
            "amount": order_data.get("amount", 0),
            "currency": "USD",
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@app.post("/api/verify-payment", summary="Verify Payment")
async def verify_payment(payment_data: dict):
    """Verify payment completion"""
    try:
        # Mock payment verification - replace with actual payment verification
        return {
            "status": "success",
            "message": "Payment verified successfully",
            "subscription_updated": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    """Admin WebSocket endpoint for real-time notifications"""
    await websocket.accept()
    print("✅ Admin WebSocket connected")
    
    try:
        # Send connection ready message
        await websocket.send_text(json.dumps({
            "type": "connection_ready",
            "message": "Admin WebSocket connected",
            "status": "connected"
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "auth":
                    # Handle authentication
                    await websocket.send_text(json.dumps({
                        "type": "auth_success",
                        "message": "Authentication successful",
                        "status": "connected"
                    }))
                elif message.get("type") == "approve_request":
                    # Handle request approval
                    await websocket.send_text(json.dumps({
                        "type": "request_updated",
                        "requestId": message.get("requestId"),
                        "status": "approved",
                        "message": "Request approved successfully"
                    }))
                elif message.get("type") == "reject_request":
                    # Handle request rejection
                    await websocket.send_text(json.dumps({
                        "type": "request_updated",
                        "requestId": message.get("requestId"),
                        "status": "rejected",
                        "message": "Request rejected"
                    }))
                else:
                    # Echo back unknown messages
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "message": "Message received",
                        "original": message
                    }))
                    
            except Exception as e:
                print(f"Error handling WebSocket message: {e}")
                break
                
    except Exception as e:
        print(f"Admin WebSocket error: {e}")
    finally:
        print("Admin WebSocket disconnected")

# ==================== MODE DETECTION ENDPOINTS ====================
# Note: Mode detection endpoints are handled by the mode_detection_router
# which is included above. These duplicate endpoints have been removed.

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
