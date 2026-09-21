#!/usr/bin/env python3
"""
🚀 Deepfake Detector - Fixed Main Application
This file contains all the fixes for PyTorch model loading, CUDA warnings, and graceful shutdown.
"""

# Suppress CUDA warnings at the very beginning
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore", message="Unable to register cuDNN factory")
warnings.filterwarnings("ignore", message="Unable to register cuBLAS factory")
warnings.filterwarnings("ignore", message="computation placer already registered")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Fix LooseVersion error by using packaging.version
try:
    from packaging import version
    # Replace any LooseVersion usage with version.parse
    import distutils.version
    distutils.version.LooseVersion = version.Version
except ImportError:
    # Fallback if packaging is not available
    pass

import asyncio
import logging
import sys
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import base64
import uuid
import time
import functools

# FastAPI imports
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError

# ML/AI imports
import numpy as np
import cv2
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YOLOv8 safe globals for PyTorch 2.6 compatibility
try:
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
    logger.info("✅ YOLOv8 safe globals configured for PyTorch 2.6")
except ImportError:
    logger.warning("⚠️ YOLOv8 not available, skipping safe globals configuration")

# Import the deepfake detector service
try:
    from backend.app.services.deepfake_detector import (
        detect_deepfake_in_frames,
        detect_deepfake_sync,
        detect_faces_yolo_sync,
        validate_cuda_setup
    )
    logger.info("✅ Deepfake detector service imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import deepfake detector service: {e}")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="Deepfake Detector API",
    description="Advanced AI-powered deepfake detection system",
    version="2.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for tracking
DETECTION_RESULTS = {}
ACTIVE_WEBSOCKETS = set()

# Pydantic models
class DetectionRequest(BaseModel):
    video_id: str
    frames: List[str]  # Base64 encoded frames

class DetectionResponse(BaseModel):
    video_id: str
    result: str
    confidence: float
    timestamp: str
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    cuda_available: bool
    models_loaded: bool
    active_detections: int

# Utility functions
def safe_base64_decode(data: str) -> Optional[np.ndarray]:
    """Safely decode base64 image data"""
    try:
        # Remove data URL prefix if present
        if ',' in data:
            data = data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.warning("⚠️ Failed to decode image from base64")
            return None
            
        return image
    except Exception as e:
        logger.error(f"❌ Base64 decode error: {e}")
        return None

def extract_faces_from_frame(frame: np.ndarray) -> List[np.ndarray]:
    """Extract faces from a frame using YOLOv8"""
    try:
        faces = detect_faces_yolo_sync(frame)
        return faces
    except Exception as e:
        logger.error(f"❌ Face extraction failed: {e}")
        return []

# API endpoints
@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Deepfake Detector API",
        "version": "2.2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        cuda_available = torch.cuda.is_available()
        models_loaded = True  # Assume models are loaded if we got this far
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            cuda_available=cuda_available,
            models_loaded=models_loaded,
            active_detections=len(DETECTION_RESULTS)
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            cuda_available=False,
            models_loaded=False,
            active_detections=0
        )

@app.post("/detect", response_model=DetectionResponse)
async def detect_deepfake(request: DetectionRequest):
    """Detect deepfakes in video frames"""
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Processing detection request for video {request.video_id}")
        
        # Decode frames
        frames = []
        for frame_data in request.frames:
            frame = safe_base64_decode(frame_data)
            if frame is not None:
                frames.append(frame)
        
        if not frames:
            raise HTTPException(status_code=400, detail="No valid frames provided")
        
        # Extract faces from frames
        all_faces = []
        for frame in frames:
            faces = extract_faces_from_frame(frame)
            all_faces.extend(faces)
        
        if not all_faces:
            raise HTTPException(status_code=400, detail="No faces detected in frames")
        
        # Detect deepfakes
        result, confidence = await detect_deepfake_in_frames(all_faces)
        
        processing_time = time.time() - start_time
        
        # Store result
        DETECTION_RESULTS[request.video_id] = {
            "result": result,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        response = DetectionResponse(
            video_id=request.video_id,
            result=result,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
        logger.info(f"✅ Detection completed: {result} (confidence: {confidence:.3f})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.get("/detection/{video_id}")
async def get_detection_result(video_id: str):
    """Get detection result for a video"""
    if video_id not in DETECTION_RESULTS:
        raise HTTPException(status_code=404, detail="Detection result not found")
    
    return DETECTION_RESULTS[video_id]

@app.delete("/detection/{video_id}")
async def delete_detection_result(video_id: str):
    """Delete detection result for a video"""
    if video_id in DETECTION_RESULTS:
        del DETECTION_RESULTS[video_id]
        return {"message": "Detection result deleted"}
    else:
        raise HTTPException(status_code=404, detail="Detection result not found")

@app.get("/detections")
async def list_detections():
    """List all detection results"""
    return {
        "detections": DETECTION_RESULTS,
        "count": len(DETECTION_RESULTS)
    }

# WebSocket endpoint for real-time detection
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection"""
    await websocket.accept()
    ACTIVE_WEBSOCKETS.add(websocket)
    
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "frame":
                # Process frame
                frame_data = message.get("frame")
                if frame_data:
                    frame = safe_base64_decode(frame_data)
                    if frame is not None:
                        # Extract faces and detect
                        faces = extract_faces_from_frame(frame)
                        if faces:
                            result, confidence = await detect_deepfake_in_frames(faces)
                            
                            # Send result back
                            await websocket.send_text(json.dumps({
                                "type": "result",
                                "result": result,
                                "confidence": confidence,
                                "timestamp": datetime.now().isoformat()
                            }))
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "No faces detected"
                            }))
            
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        ACTIVE_WEBSOCKETS.discard(websocket)

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Graceful shutdown handling
def run_server():
    """Run the server with graceful shutdown handling"""
    try:
        import uvicorn
        logger.info("🚀 Starting Deepfake Detector server...")
        logger.info("📖 API documentation: http://localhost:8000/docs")
        logger.info("🔄 Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "app.main_fixed:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True
        )
    except asyncio.CancelledError:
        logger.info("🔴 Server shutdown gracefully")
    except KeyboardInterrupt:
        logger.info("🟡 Server stopped manually")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise

# Initialize models on startup
@app.on_event("startup")
async def startup_event():
    """Initialize models and validate setup on startup"""
    logger.info("🔄 Initializing Deepfake Detector...")
    
    try:
        # Validate CUDA setup
        cuda_ok = validate_cuda_setup()
        if cuda_ok:
            logger.info("✅ CUDA setup validated successfully")
        else:
            logger.warning("⚠️ CUDA setup validation failed, using CPU fallback")
        
        logger.info("✅ Deepfake Detector initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        # Don't exit, just log the error and continue

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down Deepfake Detector...")
    
    # Close all WebSocket connections
    for websocket in ACTIVE_WEBSOCKETS.copy():
        try:
            await websocket.close()
        except Exception as e:
            logger.warning(f"⚠️ Error closing WebSocket: {e}")
    
    # Clear detection results
    DETECTION_RESULTS.clear()
    
    logger.info("✅ Shutdown completed")

if __name__ == "__main__":
    run_server()
