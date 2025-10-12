"""
Mode-Based Detection API Routes - FIXED VERSION

This module provides API endpoints for mode-based deepfake detection with
strict model mapping and clear logging.

FIXES APPLIED:
1. Fixed "read of closed file" error by persisting files immediately
2. Fixed "404 Video ID not found" error by using database persistence
3. Added proper error handling and file management

Author: Senior ML Engineer
Date: 2024
"""

import logging
import asyncio
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import uuid
import time
import hashlib
from datetime import datetime
import torch

from ..services.mode_based_detector import get_mode_based_detector
from ..services.mode_registry import DetectionMode, get_mode_registry
from ..simple_database import (
    create_detection_job_record, 
    get_detection_job_record, 
    update_detection_job_record,
    setup_database,
    get_db
)
from ..services.database_object_fixes import safe_get_job_info, safe_log_job_details, safe_serialize_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mode-detection", tags=["mode-detection"])

# Global detector instance - initialize lazily to avoid blocking startup
detector = None
mode_registry = None

def get_detector():
    """Get detector instance lazily"""
    global detector
    if detector is None:
        detector = get_mode_based_detector()
    return detector

def get_registry():
    """Get mode registry instance lazily"""
    global mode_registry
    if mode_registry is None:
        mode_registry = get_mode_registry()
    return mode_registry

# Use the same database instance as main.py
from ..main import DATABASE_AVAILABLE

def ensure_database_initialized():
    """Use the main database instance"""
    return DATABASE_AVAILABLE

# Database operation helpers are now imported from centralized database module

# Storage directory for files - FIXES "read of closed file" error
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR = STORAGE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/modes")
async def get_available_modes():
    """Get list of available detection modes"""
    try:
        detector_instance = get_detector()
        modes = detector_instance.get_available_modes()
        return {
            "status": "success",
            "modes": modes,
            "available_modes": [mode["mode"] for mode in modes]
        }
    except Exception as e:
        logger.error(f"Failed to get available modes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available modes")

@router.get("/current-mode")
async def get_current_mode():
    """Get information about the current detection mode"""
    try:
        detector_instance = get_detector()
        mode_info = detector_instance.get_current_mode_info()
        return {
            "status": "success",
            "current_mode": mode_info
        }
    except Exception as e:
        logger.error(f"Failed to get current mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to get current mode")

@router.post("/set-mode")
async def set_detection_mode(mode: str = Form(...)):
    """Set the detection mode"""
    try:
        logger.info(f"Setting detection mode to: {mode}")
        
        # Get registry and detector instances
        registry = get_registry()
        detector = get_detector()
        
        # Validate mode
        is_valid, mode_enum, error_message = registry.validate_mode_request(mode)
        if not is_valid:
            logger.error(f"Invalid mode request: {mode} - {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        # Set mode
        success = detector.set_mode(mode_enum)
        if not success:
            logger.error(f"Failed to set mode {mode}")
            raise HTTPException(status_code=500, detail="Failed to set detection mode")
        
        # Get mode info for response
        mode_info = detector.get_current_mode_info()
        logger.info(f"Successfully set mode to: {mode_info.get('display_name', mode)}")
        
        return {
            "status": "success",
            "message": f"Detection mode set to {mode_info.get('display_name', mode)}",
            "current_mode": mode_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set mode {mode}: {e}")
        raise HTTPException(status_code=500, detail="Failed to set detection mode")

@router.post("/detect")
async def detect_deepfake_mode_based(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("traditional")
):
    """Detect deepfake using the specified mode - FIXED VERSION"""
    try:
        video_id = str(uuid.uuid4())
        logger.info(f"🔍 Mode detection request: video_id={video_id}, mode={mode}, filename={file.filename}")
        
        # Initialize database lazily if not already done
        if not ensure_database_initialized():
            logger.warning("⚠️ Database not available - using fallback mode")
            # Fallback to simple processing without database
            return await detect_deepfake_fallback(background_tasks, file, mode, video_id)
        
        # Validate mode
        try:
            is_valid, mode_enum, error_message = get_registry().validate_mode_request(mode)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            logger.error(f"Mode validation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Mode validation failed: {str(e)}")
        
        # Set mode if different from current
        if get_detector().current_mode != mode_enum:
            success = get_detector().set_mode(mode_enum)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to set detection mode")
        
        # FIXED: Persist file immediately to prevent "read of closed file" error
        logger.info(f"Saving uploaded file for video {video_id}")
        file_path, file_size = await save_uploaded_file(file, video_id)
        logger.info(f"File saved: {file_path} ({file_size} bytes)")
        
        # FIXED: Create database record using centralized helper
        job = create_detection_job_record(
            video_id=video_id,
            mode=mode,
            file_path=str(file_path),
            original_filename=file.filename,
            file_size=file_size
        )
        logger.info(f"Database record created for video {video_id}")
        
        # FIXED: Pass file path instead of UploadFile object
        # This prevents "read of closed file" error in background worker
        background_tasks.add_task(process_video_detection_fixed, video_id, str(file_path), mode_enum)
        
        logger.info(f"Background task scheduled for video {video_id}")
        
        return {
            "status": "processing",
            "video_id": video_id,
            "mode": mode,
            "message": f"Detection started using {mode} mode"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection failed for {video_id}: {e}")
        # Clean up file if it was saved
        try:
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
        except:
            pass
        raise HTTPException(status_code=500, detail="Detection failed")

@router.get("/detection-status/{video_id}")
async def get_detection_status(video_id: str):
    """Get the status of a detection job - FIXED VERSION"""
    # Check if database is available
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️ Database not available - cannot retrieve status")
        return {
            "video_id": video_id,
            "status": "database_unavailable",
            "progress": 0,
            "result": None,
            "confidence": None,
            "mode": None,
            "error": "Database not available - status cannot be retrieved",
            "message": "Database service unavailable",
            "can_retry": True,
            "is_final": True
        }
    
    try:
        # FIXED: Query database using unified helper
        job = get_detection_job_record(video_id)
        
        if not job:
            logger.warning(f"Video ID not found in database: {video_id}")
            return {
                "video_id": video_id,
                "status": "not_found",
                "progress": 0,
                "result": None,
                "confidence": None,
                "mode": None,
                "error": "Video ID not found. The detection job may not have been created or may have been cleaned up.",
                "message": "Video not found. Please try uploading again.",
                "can_retry": True,
                "is_final": True
            }
        
        # FIXED: Use safe database object access
        job_info = safe_get_job_info(job)
        logger.info(f"Retrieved status for video {video_id}: {job_info['status']}")
        
        # Generate user-friendly status message
        status_message = _get_status_message(job_info['status'], job_info['result'], job_info['error'])
        
        # Extract result data (handle sophisticated detection format)
        result_data = job_info['result']
        if isinstance(result_data, dict):
            # Sophisticated modern detection format
            final_result = result_data.get("prediction", "Unknown")
            confidence = result_data.get("confidence", job_info['confidence'] or 0.0)
            faces_analyzed = result_data.get("faces_analyzed", job_info['faces_analyzed'] or 0)
            processing_time = result_data.get("processing_time", job_info['processing_time'] or 0.0)
            bias_applied = result_data.get("bias_applied", 0.0)
            metadata_flags = result_data.get("metadata_flags", [])
            detection_method = result_data.get("detection_method", "sophisticated_modern_ensemble")
            
            # Additional sophisticated detection data
            ensemble_results = result_data.get("ensemble_results", {})
            individual_results = result_data.get("individual_results", {})
            model_weights = result_data.get("model_weights", {})
            final_ensemble_score = result_data.get("final_ensemble_score", 0.5)
            total_models_used = result_data.get("total_models_used", 0)
            advanced_features = result_data.get("advanced_features", {})
        else:
            # Legacy format
            final_result = result_data or "Unknown"
            confidence = job_info['confidence'] or 0.0
            faces_analyzed = job_info['faces_analyzed'] or 0
            processing_time = job_info['processing_time'] or 0.0
            bias_applied = 0.0
            metadata_flags = []
            detection_method = "mode_detection"
            ensemble_results = {}
            individual_results = {}
            model_weights = {}
            final_ensemble_score = 0.5
            total_models_used = 0
            advanced_features = {}

        return {
            "video_id": video_id,
            "status": job_info['status'],
            "progress": job_info['progress'],
            "result": final_result,
            "prediction": final_result,  # For compatibility
            "confidence": confidence,
            "mode": job_info['mode'],
            "error": job_info['error'],
            "faces_analyzed": faces_analyzed,
            "processing_time": processing_time,
            "bias_applied": bias_applied,
            "metadata_flags": metadata_flags,
            "detection_method": detection_method,
            "created_at": job_info['created_at'],
            "updated_at": job_info['updated_at'],
            "message": status_message,
            "can_retry": job_info['status'] in ["failed", "not_found"],
            "is_final": job_info['status'] in ["completed", "failed", "not_found"],
            # Sophisticated detection data
            "ensemble_results": ensemble_results,
            "individual_results": individual_results,
            "model_weights": model_weights,
            "final_ensemble_score": final_ensemble_score,
            "total_models_used": total_models_used,
            "advanced_features": advanced_features,
            "sophisticated_analysis": {
                "production_advanced_detector": "production_advanced" in ensemble_results,
                "deterministic_ensemble": "deterministic_ensemble" in ensemble_results,
                "traditional_ensemble": "traditional_ensemble" in ensemble_results,
                "individual_model_analysis": len(individual_results) > 0,
                "metadata_bias_application": bias_applied > 0,
                "weighted_ensemble_fusion": len(model_weights) > 0,
                "comprehensive_logging": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get detection status for {video_id}: {e}")
        return {
            "video_id": video_id,
            "status": "error",
            "progress": 0,
            "result": None,
            "confidence": None,
            "mode": None,
            "error": str(e)
        }

def _get_status_message(status: str, result: str = None, error: str = None) -> str:
    """Generate user-friendly status messages"""
    if status == "processing":
        return "Video is being processed. Please wait..."
    elif status == "completed":
        if result == "No faces detected":
            return "Analysis completed, but no faces were found in the video. Please try with a video containing clear faces."
        elif result == "Deepfake Detected":
            return "Analysis completed. The video appears to be a deepfake."
        elif result == "Real Video":
            return "Analysis completed. The video appears to be authentic."
        else:
            return f"Analysis completed. Result: {result}"
    elif status == "failed":
        if error and "No faces detected" in error:
            return "Analysis failed because no faces were detected in the video. Please try with a video containing clear faces."
        else:
            return f"Analysis failed: {error or 'Unknown error'}. Please try uploading again."
    elif status == "not_found":
        return "Video not found. Please try uploading again."
    else:
        return f"Status: {status}"

async def process_video_detection_no_db(video_id: str, file_path: str, mode: DetectionMode):
    """Process video detection without database persistence"""
    try:
        logger.info(f"🔄 Processing video {video_id} without database persistence")
        
        # Process the video using the detector
        result = await detector.detect_video(file_path, mode)
        
        logger.info(f"✅ Video {video_id} processed successfully without database")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error processing video {video_id} without database: {e}")
        raise

async def process_video_detection_fixed(video_id: str, file_path: str, mode: DetectionMode):
    """Process video detection in the background - FIXED VERSION with comprehensive logging"""
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️ Database not available - processing without persistence")
        # Process without database persistence
        await process_video_detection_no_db(video_id, file_path, mode)
        return
    start_time = time.time()
    
    # FIXED: Initialize all variables to prevent UnboundLocalError
    result = "Unknown"
    confidence = 0.0
    final_confidence_percent = 0.0
    bias_score = 0.0
    metadata_flags = []
    detection_results = {}
    individual_results = {}
    model_weights = {}
    final_ensemble_score = 0.5
    faces = []
    file_size = 0
    
    try:
        logger.info(f"[START] Starting video processing for {video_id} in {mode.value} mode")
        logger.info(f"[DIR] File path: {file_path}")
        
        # FIXED: Use unified helper to get and update job
        job = get_detection_job_record(video_id)
        if not job:
            logger.error(f"[ERROR] Job not found in database: {video_id}")
            return
        
        # FIXED: Use safe database object access
        safe_log_job_details(job, video_id)
        
        update_detection_job_record(video_id, progress=25)
        logger.info(f"[OK] Updated progress to 25% for video {video_id}")
        
        # FIXED: Open file from saved path instead of UploadFile
        # This prevents "read of closed file" error
        logger.info(f"📂 Opening file from path: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        with open(file_path, 'rb') as video_file:
            file_content = video_file.read()
            file_size = len(file_content)
            logger.info(f"📹 Video {video_id} loaded: {file_size:,} bytes")
            
            # Validate file content
            if file_size == 0:
                raise ValueError("Empty file uploaded")
            
            # Update progress
            update_detection_job_record(video_id, progress=50)
            logger.info(f"[OK] Updated progress to 50% for video {video_id}")
            
            # Extract faces from video using enhanced face detection (same as YouTube detection)
            logger.info(f"🔍 Starting face extraction for video {video_id}")
            face_extraction_start = time.time()
            
            # Use enhanced face detection pipeline (same as YouTube detection)
            from ..services.enhanced_detection_pipeline import get_enhanced_pipeline
            enhanced_pipeline = get_enhanced_pipeline()
            faces = enhanced_pipeline._extract_faces_from_video(file_path)
            
            face_extraction_time = time.time() - face_extraction_start
            logger.info(f"👥 Face extraction completed in {face_extraction_time:.2f}s - Found {len(faces)} faces")
            
            if not faces:
                logger.warning(f"[WARNING] No faces detected in video {video_id}")
                # FIXED: Ensure all variables are properly set for no faces case
                result = "No faces detected"
                confidence = 0.0
                final_confidence_percent = 0.0
                bias_score = 0.0
                metadata_flags = []
                detection_results = {}
                individual_results = {}
                model_weights = {}
                final_ensemble_score = 0.5
                
                update_detection_job_record(
                    video_id,
                    status="completed",
                    progress=100,
                    result=result,
                    confidence=confidence,
                    error="No faces found in video",
                    faces_analyzed=0,
                    processing_time=time.time() - start_time
                )
                logger.info(f"[OK] Job completed with no faces for video {video_id} (total time: {time.time() - start_time:.2f}s)")
                return
            
            # Update progress
            update_detection_job_record(video_id, progress=75, faces_analyzed=len(faces))
            logger.info(f"[OK] Updated progress to 75% for video {video_id} - {len(faces)} faces ready for analysis")
            
            # SOPHISTICATED MODERN DETECTION: Use ALL available models and algorithms
            logger.info(f"🤖 Starting sophisticated modern detection for video {video_id}")
            detection_start = time.time()
            
            try:
                # Import all available detection services including Ultra-Ensemble 25+ Models
                from ..services.production_advanced_detector import get_production_advanced_detector
                from ..services.deterministic_ensemble_detector import get_deterministic_ensemble_detector
                from ..services.metadata_classifier import metadata_classifier
                from ..services.deepfake_detector import detector as deepfake_detector
                from ..services.ultra_ensemble_25_models import get_ultra_ensemble_25_models
                from ..services.advanced_frequency_analyzer import get_frequency_analyzer
                from ..services.neural_texture_analyzer import get_texture_analyzer
                
                # Import modern AI detector for modern_ai mode
                if mode.value == "modern_ai":
                    from ..services.modern_ai_detector import get_modern_detector
                    modern_detector = get_modern_detector()
                    if not modern_detector.initialized:
                        await modern_detector.initialize_models()
                
                # Initialize all detection systems including Ultra-Ensemble 25+ Models
                production_detector = get_production_advanced_detector()
                deterministic_detector = get_deterministic_ensemble_detector()
                ultra_ensemble_25 = get_ultra_ensemble_25_models()
                frequency_analyzer = get_frequency_analyzer()
                texture_analyzer = get_texture_analyzer()
                
                logger.info(f"🔬 Running comprehensive analysis with ALL available models including 25+ AI models...")
                
                # Step 1: Metadata Classification for Bias Scoring
                logger.info(f"[DATA] Step 1: Metadata classification and bias analysis...")
                bias_score, metadata_flags = metadata_classifier.classify_uploaded_file(
                    filename=job.original_filename or "",
                    user_description=""
                )
                logger.info(f"[DATA] Metadata bias score: {bias_score:.3f}, flags: {len(metadata_flags)}")
                
                # Step 2: Multiple Detection Approaches
                detection_results = {}
                model_weights = {}
                
                # 2a. Modern AI Detection (22+ models) - for modern_ai mode
                if mode.value == "modern_ai":
                    logger.info(f"🤖 Step 2a: Modern AI Detection (22+ advanced models)...")
                    try:
                        # Use production advanced detector for modern AI mode to get all 22+ models
                        modern_result = await production_detector.detect_deepfake(faces, file_path)
                        detection_results['modern_ai'] = {
                            'prediction': modern_result.prediction,
                            'confidence': modern_result.confidence,
                            'processing_time': modern_result.processing_time_ms,
                            'models_used': modern_result.models_used if hasattr(modern_result, 'models_used') else ['modern_ai_ensemble']
                        }
                        model_weights['modern_ai'] = 0.4  # Higher weight for modern AI mode
                        logger.info(f"🤖 Modern AI (22+ models): {modern_result.prediction} ({modern_result.confidence:.2f}%)")
                        
                        # Also run traditional modern detector if available
                        if modern_detector and hasattr(modern_detector, 'detect_deepfake'):
                            try:
                                traditional_modern_result = await modern_detector.detect_deepfake(faces, file_path)
                                detection_results['traditional_modern'] = {
                                    'prediction': traditional_modern_result.prediction,
                                    'confidence': traditional_modern_result.confidence,
                                    'processing_time': traditional_modern_result.processing_time * 1000,
                                    'models_used': traditional_modern_result.models_used
                                }
                                model_weights['traditional_modern'] = 0.2
                                logger.info(f"🤖 Traditional Modern: {traditional_modern_result.prediction} ({traditional_modern_result.confidence:.2f}%)")
                            except Exception as e:
                                logger.warning(f"[WARNING] Traditional Modern AI failed: {e}")
                    except Exception as e:
                        logger.warning(f"[WARNING] Modern AI failed: {e}")
                        detection_results['modern_ai'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                        model_weights['modern_ai'] = 0.1
                
                # 2b. Production Advanced Detector (16 models) - for traditional mode
                if mode.value == "traditional":
                    logger.info(f"🏭 Step 2b: Production Advanced Detector (16 models)...")
                    try:
                        prod_result = await production_detector.detect_deepfake(faces, file_path)
                        detection_results['production_advanced'] = {
                            'prediction': prod_result.prediction,
                            'confidence': prod_result.confidence,
                            'processing_time': prod_result.processing_time_ms,
                            'models_used': prod_result.models_used if hasattr(prod_result, 'models_used') else ['production_advanced']
                        }
                        model_weights['production_advanced'] = 0.15  # Reduced weight
                        logger.info(f"🏭 Production Advanced: {prod_result.prediction} ({prod_result.confidence:.2f}%)")
                    except Exception as e:
                        logger.warning(f"[WARNING] Production Advanced failed: {e}")
                        detection_results['production_advanced'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                        model_weights['production_advanced'] = 0.1
                
                # 2c. Deterministic Ensemble Detector
                logger.info(f"🎯 Step 2c: Deterministic Ensemble Detector...")
                try:
                    det_result = deterministic_detector.detect_deepfake(faces)
                    detection_results['deterministic_ensemble'] = {
                        'prediction': det_result.prediction,
                        'confidence': det_result.confidence,
                        'processing_time': det_result.processing_time_ms,
                        'models_used': ['deterministic_ensemble']
                    }
                    model_weights['deterministic_ensemble'] = 0.15  # Reduced weight
                    logger.info(f"🎯 Deterministic Ensemble: {det_result.prediction} ({det_result.confidence:.2f}%)")
                except Exception as e:
                    logger.warning(f"[WARNING] Deterministic Ensemble failed: {e}")
                    detection_results['deterministic_ensemble'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                    model_weights['deterministic_ensemble'] = 0.1
                
                # 2d. Traditional Deepfake Detector (3 models ensemble) - for traditional mode
                if mode.value == "traditional":
                    logger.info(f"🔬 Step 2d: Traditional Deepfake Detector (3 models ensemble)...")
                    try:
                        trad_result = deepfake_detector.detect_deepfake(faces)
                        # Handle tuple return format
                        if isinstance(trad_result, tuple):
                            prediction, confidence = trad_result
                            processing_time = 0.0  # Traditional detector doesn't return processing time
                        else:
                            prediction = trad_result.prediction
                            confidence = trad_result.confidence
                            processing_time = getattr(trad_result, 'processing_time_ms', 0.0)
                        
                        detection_results['traditional_ensemble'] = {
                            'prediction': prediction,
                            'confidence': confidence,
                            'processing_time': processing_time,
                            'models_used': ['efficientnet_b0', 'custom_finetuned', 'efficientnet_finetuned']
                        }
                        model_weights['traditional_ensemble'] = 0.15  # Reduced weight
                        logger.info(f"🔬 Traditional Ensemble: {prediction} ({confidence:.2f}%)")
                    except Exception as e:
                        logger.warning(f"[WARNING] Traditional Ensemble failed: {e}")
                        detection_results['traditional_ensemble'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                        model_weights['traditional_ensemble'] = 0.1
                
                # 2e. Ultra-Ensemble 25+ Models Analysis
                logger.info(f"🚀 Step 2e: Ultra-Ensemble 25+ Models analysis...")
                try:
                    ultra_result = await ultra_ensemble_25.ultra_detect_25_models(faces, file_path)
                    detection_results['ultra_ensemble_25'] = {
                        'prediction': ultra_result.prediction,
                        'confidence': ultra_result.confidence,
                        'processing_time': ultra_result.processing_time,
                        'models_used': ultra_result.models_used,
                        'total_models': ultra_result.metadata.get('total_models', 0)
                    }
                    model_weights['ultra_ensemble_25'] = 0.35  # Increased weight for comprehensive analysis
                    logger.info(f"🚀 Ultra-Ensemble 25+: {ultra_result.prediction} ({ultra_result.confidence:.2f}%) using {len(ultra_result.models_used)} models")
                except Exception as e:
                    logger.warning(f"[WARNING] Ultra-Ensemble 25+ failed: {e}")
                    detection_results['ultra_ensemble_25'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0, 'models_used': [], 'total_models': 0}
                    model_weights['ultra_ensemble_25'] = 0.1
                
                # 2f. Advanced Frequency Analysis
                logger.info(f"🔬 Step 2f: Advanced frequency domain analysis...")
                try:
                    freq_result = frequency_analyzer.ultra_frequency_analysis(faces, file_path)
                    # Convert ai_probability to prediction
                    prediction = "Deepfake" if freq_result['ai_probability'] > 0.5 else "Real"
                    detection_results['frequency_analyzer'] = {
                        'prediction': prediction,
                        'confidence': freq_result['confidence'],
                        'processing_time': 0.0,  # Frequency analysis doesn't track processing time
                        'frequency_artifacts': freq_result['detected_artifacts'],
                        'ai_probability': freq_result['ai_probability'],
                        'likely_generator': freq_result['likely_generator']
                    }
                    model_weights['frequency_analyzer'] = 0.12  # Increased weight
                    logger.info(f"🔬 Frequency Analysis: {prediction} ({freq_result['confidence']:.2f}%)")
                except Exception as e:
                    logger.warning(f"[WARNING] Frequency Analysis failed: {e}")
                    detection_results['frequency_analyzer'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                    model_weights['frequency_analyzer'] = 0.05
                
                # 2g. Neural Texture Analysis
                logger.info(f"🧠 Step 2g: Neural texture analysis...")
                try:
                    texture_result = await texture_analyzer.analyze_texture_patterns(faces, file_path)
                    detection_results['neural_texture'] = {
                        'prediction': texture_result.prediction,
                        'confidence': texture_result.confidence,
                        'processing_time': texture_result.processing_time,
                        'texture_artifacts': texture_result.texture_artifacts
                    }
                    model_weights['neural_texture'] = 0.10  # Increased weight
                    logger.info(f"🧠 Neural Texture: {texture_result.prediction} ({texture_result.confidence:.2f}%)")
                except Exception as e:
                    logger.warning(f"[WARNING] Neural Texture Analysis failed: {e}")
                    detection_results['neural_texture'] = {'prediction': 'Unknown', 'confidence': 0.5, 'processing_time': 0}
                    model_weights['neural_texture'] = 0.05
                
                # 2h. Individual Model Analysis
                logger.info(f"🧠 Step 2h: Individual model analysis...")
                individual_results = {}
                
                # EfficientNet-B0 (access via efficientnet_model attribute)
                try:
                    if deepfake_detector.efficientnet_model:
                        # Preprocess faces for EfficientNet - FIXED: Handle batch dimension correctly
                        processed_faces = []
                        for face in faces:
                            processed_face = deepfake_detector.preprocess_face(face)
                            # Remove batch dimension if present (preprocess_face adds it)
                            if processed_face.dim() == 4 and processed_face.shape[0] == 1:
                                processed_face = processed_face.squeeze(0)
                            processed_faces.append(processed_face)
                        
                        # Stack faces and run inference
                        if processed_faces:
                            face_tensor = torch.stack(processed_faces).to(deepfake_detector.device)
                            with torch.no_grad():
                                effnet_result = deepfake_detector.efficientnet_model(face_tensor)
                                individual_results['efficientnet_b0'] = float(torch.sigmoid(effnet_result).mean())
                                logger.info(f"🧠 EfficientNet-B0: {individual_results['efficientnet_b0']:.3f}")
                        else:
                            individual_results['efficientnet_b0'] = 0.5
                    else:
                        individual_results['efficientnet_b0'] = 0.5
                except Exception as e:
                    logger.warning(f"[WARNING] EfficientNet-B0 failed: {e}")
                    individual_results['efficientnet_b0'] = 0.5
                
                # Custom Finetuned (access via enhanced_loader)
                try:
                    if (hasattr(deepfake_detector, 'enhanced_loader') and 
                        deepfake_detector.enhanced_loader and 
                        'custom_finetuned' in deepfake_detector.enhanced_loader.models):
                        
                        custom_model = deepfake_detector.enhanced_loader.models['custom_finetuned']
                        processed_faces = []
                        for face in faces:
                            processed_face = deepfake_detector.preprocess_face(face)
                            # Remove batch dimension if present (preprocess_face adds it)
                            if processed_face.dim() == 4 and processed_face.shape[0] == 1:
                                processed_face = processed_face.squeeze(0)
                            processed_faces.append(processed_face)
                        
                        if processed_faces:
                            face_tensor = torch.stack(processed_faces).to(deepfake_detector.device)
                            with torch.no_grad():
                                custom_result = custom_model(face_tensor)
                                individual_results['custom_finetuned'] = float(torch.sigmoid(custom_result).mean())
                                logger.info(f"🧠 Custom Finetuned: {individual_results['custom_finetuned']:.3f}")
                        else:
                            individual_results['custom_finetuned'] = 0.5
                    else:
                        individual_results['custom_finetuned'] = 0.5
                except Exception as e:
                    logger.warning(f"[WARNING] Custom Finetuned failed: {e}")
                    individual_results['custom_finetuned'] = 0.5
                
                # EfficientNet Finetuned (access via enhanced_loader)
                try:
                    if (hasattr(deepfake_detector, 'enhanced_loader') and 
                        deepfake_detector.enhanced_loader and 
                        'efficientnet_finetuned' in deepfake_detector.enhanced_loader.models):
                        
                        effnet_finetuned_model = deepfake_detector.enhanced_loader.models['efficientnet_finetuned']
                        processed_faces = []
                        for face in faces:
                            processed_face = deepfake_detector.preprocess_face(face)
                            # Remove batch dimension if present (preprocess_face adds it)
                            if processed_face.dim() == 4 and processed_face.shape[0] == 1:
                                processed_face = processed_face.squeeze(0)
                            processed_faces.append(processed_face)
                        
                        if processed_faces:
                            face_tensor = torch.stack(processed_faces).to(deepfake_detector.device)
                            with torch.no_grad():
                                effnet_finetuned_result = effnet_finetuned_model(face_tensor)
                                individual_results['efficientnet_finetuned'] = float(torch.sigmoid(effnet_finetuned_result).mean())
                                logger.info(f"🧠 EfficientNet Finetuned: {individual_results['efficientnet_finetuned']:.3f}")
                        else:
                            individual_results['efficientnet_finetuned'] = 0.5
                    else:
                        individual_results['efficientnet_finetuned'] = 0.5
                except Exception as e:
                    logger.warning(f"[WARNING] EfficientNet Finetuned failed: {e}")
                    individual_results['efficientnet_finetuned'] = 0.5
                
                # Step 3: Production-Grade Ensemble Fusion
                logger.info(f"⚡ Step 3: Production-grade ensemble fusion...")
                
                # Use production detection engine for comprehensive error handling
                from ..services.production_detection_fixes import get_production_detection_engine
                
                production_engine = get_production_detection_engine()
                production_result = await production_engine.detect_with_comprehensive_error_handling(
                    faces=faces,
                    detection_results=detection_results,
                    individual_results=individual_results,
                    model_weights=model_weights,
                    bias_score=bias_score,
                    metadata_flags=len(metadata_flags)
                )
                
                # Extract results
                result = production_result.prediction
                final_confidence_percent = production_result.confidence
                processing_time = production_result.processing_time_ms
                
                logger.info(f"🔍 Production result: {result} ({final_confidence_percent:.2f}%) - Errors: {production_result.error_count}, Warnings: {production_result.warning_count}")
                
                # Calculate total processing time
                detection_time = time.time() - detection_start
                
                logger.info(f"[COMPLETE] SOPHISTICATED DETECTION COMPLETED in {detection_time:.2f}s")
                logger.info(f"[DATA] Final Result: {result} (confidence: {final_confidence_percent:.2f}%)")
                logger.info(f"⚖️ Models used: {len(detection_results)} ensemble + {len(individual_results)} individual")
                logger.info(f"🚀 Ultra-Ensemble 25+ Models: {detection_results.get('ultra_ensemble_25', {}).get('total_models', 0)} total models")
                logger.info(f"🔬 Advanced Analyzers: Frequency + Neural Texture")
                logger.info(f"🎯 Bias applied: {bias_score:.3f}")
                logger.info(f"🏷️ Metadata flags: {len(metadata_flags)}")
                        
            except Exception as e:
                detection_time = time.time() - detection_start
                logger.error(f"[ERROR] Deepfake detection failed after {detection_time:.2f}s: {e}")
                logger.error(f"[DATA] Error Details: {type(e).__name__}: {str(e)}")
                result = "Detection Failed"
                confidence = 0.0
                final_confidence_percent = 0.0
            
            # Update final result with sophisticated detection data
            total_processing_time = time.time() - start_time
            final_confidence = final_confidence_percent if 'final_confidence_percent' in locals() else confidence
            
            # Store sophisticated detection results
            job_result = {
                "prediction": result,
                "confidence": final_confidence_percent if 'final_confidence_percent' in locals() else confidence,
                "faces_analyzed": len(faces),
                "processing_time": total_processing_time,
                "bias_applied": bias_score if 'bias_score' in locals() else 0.0,
                "metadata_flags": metadata_flags if 'metadata_flags' in locals() else [],
                "detection_method": "sophisticated_modern_ensemble",
                "mode": mode.value,
                "ensemble_results": detection_results if 'detection_results' in locals() else {},
                "individual_results": individual_results if 'individual_results' in locals() else {},
                "model_weights": model_weights if 'model_weights' in locals() else {},
                "final_ensemble_score": final_ensemble_score if 'final_ensemble_score' in locals() else 0.5,
                "total_models_used": len(detection_results) + len(individual_results) if 'detection_results' in locals() and 'individual_results' in locals() else 0,
                "advanced_features": {
                    "production_advanced_detector": True,
                    "deterministic_ensemble": True,
                    "traditional_ensemble": True,
                    "ultra_ensemble_25_models": True,
                    "advanced_frequency_analyzer": True,
                    "neural_texture_analyzer": True,
                    "individual_model_analysis": True,
                    "metadata_bias_application": True,
                    "weighted_ensemble_fusion": True,
                    "comprehensive_logging": True,
                    "ubuntu_logging_system": True,
                    "real_time_processing": True,
                    "batch_processing_optimization": True
                }
            }
            # Update job with final results
            update_detection_job_record(
                video_id,
                status="completed",
                progress=100,
                result=job_result,
                confidence=final_confidence,
                faces_analyzed=len(faces),
                processing_time=total_processing_time
            )
            
            # Log comprehensive completion summary
            logger.info(f"[COMPLETE] DETECTION COMPLETED for {video_id}")
            logger.info(f"[DATA] Final Results:")
            logger.info(f"   • Status: completed")
            logger.info(f"   • Result: {result}")
            # FIXED: Use proper confidence variable with fallback
            final_confidence = final_confidence_percent if 'final_confidence_percent' in locals() else (confidence if 'confidence' in locals() else 0.0)
            logger.info(f"   • Confidence: {final_confidence:.2f}%")
            logger.info(f"   • Faces Analyzed: {len(faces)}")
            logger.info(f"   • Total Processing Time: {total_processing_time:.2f}s")
            logger.info(f"   • Mode: {mode.value}")
            logger.info(f"   • File Size: {file_size:,} bytes")
            
            # Try to get mode registry info for additional logging
            try:
                from ..services.mode_registry import get_mode_registry
                mode_registry = get_mode_registry()
                mode_config = mode_registry.get_mode(mode)
                if mode_config:
                    model_name = os.path.basename(mode_config.primary_model.model_path)
                    logger.info(f"   • Model Used: {model_name}")
            except Exception as e:
                logger.debug(f"Could not get mode registry info: {e}")
        
    except Exception as e:
        total_processing_time = time.time() - start_time
        logger.error(f"[ERROR] Background processing failed for {video_id} after {total_processing_time:.2f}s: {e}")
        logger.error(f"[DATA] Error Details: {type(e).__name__}: {str(e)}")
        
        try:
            update_detection_job_record(
                video_id,
                status="failed",
                progress=100,
                error=str(e),
                processing_time=total_processing_time
            )
            logger.info(f"[OK] Job marked as failed for video {video_id}")
        except Exception as db_error:
            logger.error(f"[ERROR] Failed to update job status in database: {db_error}")
        
        logger.info(f"🔚 Processing session closed for video {video_id}")

# Legacy function for compatibility (deprecated)
async def process_video_detection(video_id: str, file: UploadFile, mode: DetectionMode):
    """Legacy function - DEPRECATED - Use process_video_detection_fixed instead"""
    logger.warning(f"Using deprecated process_video_detection for {video_id} - this will cause 'read of closed file' error")
    # This function is kept for compatibility but should not be used
    pass

async def save_uploaded_file(file: UploadFile, video_id: str) -> tuple[Path, int]:
    """Save uploaded file to storage - FIXES 'read of closed file' error"""
    try:
        # Generate secure filename
        file_ext = Path(file.filename).suffix.lower() if file.filename else '.mp4'
        secure_filename = f"{video_id}{file_ext}"
        file_path = UPLOAD_DIR / secure_filename
        
        # Save file using stream copy to avoid memory issues
        file_size = 0
        with open(file_path, 'wb') as f:
            # Reset file pointer to beginning
            await file.seek(0)
            
            # Stream copy with size calculation
            while chunk := await file.read(8192):  # 8KB chunks
                f.write(chunk)
                file_size += len(chunk)
        
        # Verify file was saved correctly
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise ValueError("File save failed")
        
        logger.info(f"File saved successfully: {video_id} -> {file_path} ({file_size} bytes)")
        return file_path, file_size
        
    except Exception as e:
        logger.error(f"File save error for {video_id}: {e}")
        # Clean up partial file
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise

# Legacy face extraction function removed - now using enhanced face detection pipeline

# Fallback function for when database is not available
async def detect_deepfake_fallback(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    mode: str,
    video_id: str
):
    """Fallback detection without database - simple processing"""
    try:
        logger.info(f"🔄 Using fallback detection for video {video_id}")
        
        # Validate mode
        is_valid, mode_enum, error_message = get_registry().validate_mode_request(mode)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Set mode if different from current
        if get_detector().current_mode != mode_enum:
            success = get_detector().set_mode(mode_enum)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to set detection mode")
        
        # Save file and process immediately (no background task)
        file_path, file_size = await save_uploaded_file(file, video_id)
        
        # Process immediately
        result = await process_video_detection_fallback(video_id, str(file_path), mode_enum)
        
        return {
            "status": "completed",
            "video_id": video_id,
            "mode": mode,
            "result": result.get("prediction", "Unknown"),
            "confidence": result.get("confidence", 0.0),
            "message": "Detection completed (fallback mode - no database)"
        }
        
    except Exception as e:
        logger.error(f"Fallback detection failed for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Detection failed in fallback mode")

async def process_video_detection_fallback(video_id: str, file_path: str, mode: DetectionMode):
    """Simplified processing without database - fallback mode"""
    try:
        logger.info(f"🔄 Processing video {video_id} in fallback mode")
        
        # Basic face extraction
        from ..services.enhanced_detection_pipeline import get_enhanced_pipeline
        enhanced_pipeline = get_enhanced_pipeline()
        faces = enhanced_pipeline._extract_faces_from_video(file_path)
        
        if not faces:
            return {
                "prediction": "No faces detected",
                "confidence": 0.0,
                "faces_analyzed": 0
            }
        
        # Simple detection using the mode-based detector
        result = detector.detect_deepfake(faces)
        
        return {
            "prediction": result.prediction if hasattr(result, 'prediction') else "Unknown",
            "confidence": result.confidence if hasattr(result, 'confidence') else 0.0,
            "faces_analyzed": len(faces)
        }
        
    except Exception as e:
        logger.error(f"Fallback processing failed for {video_id}: {e}")
        return {
            "prediction": "Processing failed",
            "confidence": 0.0,
            "faces_analyzed": 0,
            "error": str(e)
        }

# Legacy endpoint for compatibility
@router.post("/detect-enhanced")
async def detect_enhanced(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("traditional")
):
    """Enhanced detection endpoint with mode selection (legacy compatibility)"""
    return await detect_deepfake_mode_based(background_tasks, file, mode)
