"""
Ultra Ensemble Mode Routes
=========================

API endpoints for Ultra Ensemble Mode - 25+ AI Models Integration
Provides maximum accuracy and comprehensive analysis.
"""

# Apply comprehensive warning suppression at the very beginning
try:
    import warnings
    warnings.filterwarnings("ignore")
    import os
    os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
    os.environ.setdefault("TORCH_WARN_LEVEL", "0")
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
except:
    pass

# Apply ultra aggressive warning suppression
try:
    from ..services.ultra_aggressive_warning_suppression import ultra_aggressive_suppression
    ultra_aggressive_suppression()
except ImportError:
    # Fallback to basic warning suppression
    import warnings
    warnings.simplefilter("ignore")
    pass

import asyncio
import logging
import time
import hashlib
import os
from typing import Dict, List, Optional, Tuple
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import numpy as np
from pathlib import Path

from ..services.ultra_ensemble_25_models import get_ultra_ensemble, UltraEnsemble25Models
from ..services.video_processor import extract_faces_from_video
from ..services.rag_agent import get_rag_agent, analyze_with_rag
from ..services.generative_ai_models import get_generative_ai_models, analyze_with_generative_ai
from ..storage import save_uploaded_video, delete_video_file

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ultra-ensemble", tags=["Ultra Ensemble Mode"])

# Global shared storage for detection results
_ULTRA_ENSEMBLE_RESULTS: Dict[str, Dict] = {}
# Separate store for explainer-only outputs (RAG/GenAI); never used as final authority
_EXPLAINER_RESULTS: Dict[str, Dict] = {}

# Video hash cache to prevent duplicate processing
_VIDEO_HASH_CACHE: Dict[str, str] = {}

def get_ultra_ensemble_result_sync(video_id: str) -> Optional[Dict]:
    """Get ultra-ensemble detection result by video ID (synchronous version)"""
    logger.info(f"get_ultra_ensemble_result_sync called for video_id: {video_id}")
    logger.info(f"get_ultra_ensemble_result_sync - _ULTRA_ENSEMBLE_RESULTS keys: {list(_ULTRA_ENSEMBLE_RESULTS.keys())}")
    logger.info(f"get_ultra_ensemble_result_sync - Video ID in results: {video_id in _ULTRA_ENSEMBLE_RESULTS}")
    result = _ULTRA_ENSEMBLE_RESULTS.get(video_id)
    logger.info(f"get_ultra_ensemble_result_sync - Result found: {result is not None}")
    if result:
        logger.info(f"get_ultra_ensemble_result_sync - Result status: {result.get('status', 'unknown')}")
    return result

def store_ultra_ensemble_result(video_id: str, result: Dict):
    """Store ultra-ensemble detection result"""
    _ULTRA_ENSEMBLE_RESULTS[video_id] = result
    logger.info(f"store_ultra_ensemble_result - Stored result for video_id: {video_id}")
    logger.info(f"store_ultra_ensemble_result - Total results: {len(_ULTRA_ENSEMBLE_RESULTS)}")

def generate_video_hash(video_path: str) -> str:
    """Generate deterministic hash for video file to detect duplicates"""
    try:
        if not os.path.exists(video_path):
            return ""
        
        # Get file size and modification time for hash
        stat = os.stat(video_path)
        file_size = stat.st_size
        mtime = stat.st_mtime
        
        # Read first and last 1KB of file for content hash
        with open(video_path, 'rb') as f:
            # First 1KB
            first_chunk = f.read(1024)
            # Last 1KB
            f.seek(max(0, file_size - 1024))
            last_chunk = f.read(1024)
        
        # Create hash from file characteristics
        hash_input = f"{file_size}_{mtime}_{first_chunk.hex()}_{last_chunk.hex()}"
        return hashlib.md5(hash_input.encode()).hexdigest()
        
    except Exception as e:
        logger.warning(f"Video hash generation failed: {e}")
        return ""

def check_duplicate_video(video_path: str) -> Optional[str]:
    """Check if video has been processed before and return existing video_id"""
    try:
        video_hash = generate_video_hash(video_path)
        if not video_hash:
            return None
        
        # Check if we've seen this video before
        if video_hash in _VIDEO_HASH_CACHE:
            existing_video_id = _VIDEO_HASH_CACHE[video_hash]
            # Check if result still exists
            if existing_video_id in _ULTRA_ENSEMBLE_RESULTS:
                logger.info(f"🎯 Found duplicate video with existing result: {existing_video_id}")
                return existing_video_id
            else:
                # Clean up stale hash entry
                del _VIDEO_HASH_CACHE[video_hash]
        
        return None
        
    except Exception as e:
        logger.warning(f"Duplicate check failed: {e}")
        return None

def register_video_hash(video_id: str, video_path: str):
    """Register video hash to prevent duplicate processing"""
    try:
        video_hash = generate_video_hash(video_path)
        if video_hash:
            _VIDEO_HASH_CACHE[video_hash] = video_id
            logger.info(f"📝 Registered video hash for {video_id}")
    except Exception as e:
        logger.warning(f"Video hash registration failed: {e}")

def _integrate_enhanced_results(standard_prediction: str, standard_confidence: float, 
                              rag_result, generative_results: Dict) -> Tuple[str, float]:
    """Compute analysis-only merge of RAG/GenAI with standard ensemble.
    NOTE: Ultra Ensemble remains the final authority; this function must NOT override it.
    Returns a synthesized enhanced view for logging/analysis, but callers must not replace the final decision with it.
    """
    try:
        # Collect all predictions and confidences
        predictions = []
        confidences = []
        weights = []
        
        # Standard ensemble results
        predictions.append(standard_prediction)
        confidences.append(standard_confidence)
        weights.append(0.4)  # 40% weight for standard ensemble
        
        # RAG Agent results
        if rag_result and hasattr(rag_result, 'is_deepfake'):
            rag_prediction = "Deepfake Detected" if rag_result.is_deepfake else "Real Video"
            predictions.append(rag_prediction)
            confidences.append(rag_result.confidence)
            weights.append(0.3)  # 30% weight for RAG analysis
        
        # Generative AI ensemble results
        if generative_results and "ensemble" in generative_results:
            gen_result = generative_results["ensemble"]
            if hasattr(gen_result, 'prediction'):
                predictions.append(gen_result.prediction)
                confidences.append(gen_result.confidence)
                weights.append(0.3)  # 30% weight for generative AI
        
        # Weighted analysis voting (for context only)
        deepfake_votes = 0.0
        real_votes = 0.0
        total_weight = 0.0
        
        for pred, conf, weight in zip(predictions, confidences, weights):
            weighted_conf = conf * weight
            total_weight += weighted_conf
            
            if "Deepfake" in pred:
                deepfake_votes += weighted_conf
            else:
                real_votes += weighted_conf
        
        # Determine analysis-only synthesized outcome
        if total_weight == 0:
            return standard_prediction, standard_confidence
        
        if deepfake_votes > real_votes:
            final_prediction = "Deepfake Detected"
            final_confidence = deepfake_votes / total_weight
        else:
            final_prediction = "Real Video"
            final_confidence = real_votes / total_weight
        
        return final_prediction, final_confidence
        
    except Exception as e:
        logger.warning(f"Enhanced results integration failed: {e}")
        return standard_prediction, standard_confidence

# Backward compatibility
DETECTION_RESULTS = _ULTRA_ENSEMBLE_RESULTS

@router.get("/status", summary="Get Ultra Ensemble Status")
async def get_ultra_ensemble_status():
    """Get the status of Ultra Ensemble models"""
    try:
        ensemble = await get_ultra_ensemble()
        status = await ensemble.get_model_status()
        
        return {
            "status": "success",
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            "initialized": status["initialized"],
            "model_count": status["model_count"],
            "models_loaded": len([m for m in status["models"].values() if m["loaded"]]),
            "total_models": len(status["models"]),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get Ultra Ensemble status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/detection-status/{video_id}", summary="Get Ultra Ensemble Detection Status")
async def get_ultra_ensemble_detection_status(video_id: str):
    """Get the status of a specific Ultra Ensemble detection job"""
    try:
        logger.info(f"Checking status for video_id: {video_id}")
        logger.info(f"DETECTION_RESULTS keys: {list(DETECTION_RESULTS.keys())}")
        logger.info(f"Video ID in DETECTION_RESULTS: {video_id in DETECTION_RESULTS}")
        
        if video_id not in _ULTRA_ENSEMBLE_RESULTS:
            logger.warning(f"Video ID not found in results: {video_id}")
            logger.info(f"Available video IDs: {list(_ULTRA_ENSEMBLE_RESULTS.keys())}")
            return {
                "video_id": video_id,
                "status": "not_found",
                "progress": 0,
                "result": None,
                "confidence": None,
                "detailed_analysis": None,
                "error": "Video ID not found. The detection job may not have been created or may have been cleaned up.",
                "message": "Video not found. Please try uploading again.",
                "can_retry": True,
                "is_final": True,
                "mode": "Ultra Ensemble Mode",
                "description": "25+ AI Models Integration – Maximum Accuracy & Analysis"
            }
        
        result = _ULTRA_ENSEMBLE_RESULTS[video_id]
        logger.info(f"Retrieved Ultra Ensemble status for video {video_id}: {result.get('status', 'unknown')}")
        logger.info(f"Status check - _ULTRA_ENSEMBLE_RESULTS keys: {list(_ULTRA_ENSEMBLE_RESULTS.keys())}")
        logger.info(f"Status check - Video ID in results: {video_id in _ULTRA_ENSEMBLE_RESULTS}")
        
        # Format confidence as percentage for UI display
        confidence_value = result.get("confidence", 0.0)
        if confidence_value is not None:
            confidence_percentage = round(confidence_value * 100, 1)
        else:
            confidence_percentage = 0.0
        
        # Get detailed analysis for UI display
        detailed_analysis = result.get("detailed_analysis", {})
        faces_analyzed = detailed_analysis.get("faces_analyzed", 0)
        model_count = detailed_analysis.get("model_count", 0)
        
        # Get processing time from result
        processing_time = result.get("processing_time", "0.0s")
        
        # Use standardized response format
        from ..main import standardize_detection_response
        response = standardize_detection_response(video_id, result, "Ultra Ensemble")
        
        # Add ultra ensemble specific fields
        response.update({
            "progress": 100 if result.get("status") == "completed" else 50,
            "result": result.get("result"),
            "confidence_decimal": confidence_value,  # Keep decimal for backend
            "model_count": model_count,
            "analysis_type": "Ultra Ensemble",
            "detailed_analysis": detailed_analysis,
            "description": result.get("description", "25+ AI Models Integration – Maximum Accuracy & Analysis")
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get Ultra Ensemble detection status: {e}")
        error_result = {
            "status": "error",
            "prediction": "Error",
            "confidence": 0.0,
            "faces_detected": 0,
            "processing_time": 0.0,
            "detection_method": "Ultra Ensemble (Error)",
            "error": str(e)
        }
        return standardize_detection_response(video_id, error_result, "Ultra Ensemble")

@router.post("/detect", summary="Ultra Ensemble Detection")
async def ultra_ensemble_detection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Perform Ultra Ensemble detection using 25+ AI models with duplicate detection
    
    This endpoint provides the most comprehensive deepfake detection available,
    integrating 25+ specialized AI models for maximum accuracy.
    """
    try:
        # Save uploaded video (function generates its own video_id)
        video_id, video_path = await save_uploaded_video(file)
        
        # Check for duplicate video processing
        existing_video_id = check_duplicate_video(video_path)
        if existing_video_id:
            logger.info(f"🎯 Duplicate video detected, returning existing result: {existing_video_id}")
            return {
                "status": "completed",
                "video_id": existing_video_id,
                "mode": "Ultra Ensemble Mode",
                "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
                "message": "Video already processed. Returning cached result.",
                "duplicate_detected": True,
                "original_video_id": existing_video_id
            }
        
        # Register video hash to prevent future duplicates
        register_video_hash(video_id, video_path)
        
        # Start background detection task
        logger.info(f"Adding background task for video_id: {video_id}")
        # Immediately register a processing record so status calls don't return empty or zeros
        try:
            store_ultra_ensemble_result(video_id, {
                "status": "processing",
                "result": None,
                "confidence": None,
                "detailed_analysis": {"faces_analyzed": 0, "model_count": 0},
                "error": None,
                "mode": "Ultra Ensemble Mode",
                "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
                "processing_time": None,
                "start_time": time.time()
            })
        except Exception as e:
            logger.debug(f"Could not store initial processing record: {e}")
        background_tasks.add_task(
            run_ultra_ensemble_detection_task, 
            video_id, 
            video_path
        )
        logger.info(f"Background task added for video_id: {video_id}")
        
        return {
            "status": "processing",
            "video_id": video_id,
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            "message": "Ultra Ensemble detection started. This may take longer due to comprehensive analysis.",
            "estimated_time": "30-60 seconds",
            "duplicate_detected": False
        }
        
    except Exception as e:
        logger.error(f"Failed to start Ultra Ensemble detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.get("/result/{video_id}", summary="Get Ultra Ensemble Detection Result")
async def get_ultra_ensemble_result(video_id: str):
    """Get the result of Ultra Ensemble detection"""
    try:
        if video_id not in _ULTRA_ENSEMBLE_RESULTS:
            raise HTTPException(status_code=404, detail="Video ID not found")
        
        result = _ULTRA_ENSEMBLE_RESULTS[video_id]
        
        return {
            "video_id": video_id,
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Ultra Ensemble result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")

@router.post("/analyze-faces", summary="Ultra Ensemble Face Analysis")
async def ultra_ensemble_face_analysis(faces_data: dict):
    """
    Perform Ultra Ensemble analysis on provided face data
    
    This endpoint analyzes face arrays directly using all 25+ models
    for maximum accuracy detection.
    """
    try:
        faces = faces_data.get("faces", [])
        if not faces:
            raise HTTPException(status_code=400, detail="No faces provided")
        
        # Get Ultra Ensemble instance
        ensemble = await get_ultra_ensemble()
        
        # Convert faces to numpy arrays if needed
        face_arrays = []
        for face in faces:
            if isinstance(face, list):
                face_arrays.append(np.array(face))
            else:
                face_arrays.append(face)
        
        # Run Ultra Ensemble prediction
        prediction, confidence, detailed_results = await ensemble.predict_ensemble(
            face_arrays, 
            video_path=None
        )
        
        return {
            "status": "success",
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            "prediction": prediction,
            "confidence": confidence,
            "detailed_analysis": detailed_results,
            "faces_analyzed": len(face_arrays),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Ultra Ensemble face analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/models", summary="Get Ultra Ensemble Models Info")
async def get_ultra_ensemble_models():
    """Get detailed information about all models in the Ultra Ensemble"""
    try:
        ensemble = await get_ultra_ensemble()
        status = await ensemble.get_model_status()
        
        return {
            "status": "success",
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            "model_count": status["model_count"],
            "models": status["models"],
            "weights": status["weights"],
            "initialized": status["initialized"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get Ultra Ensemble models info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models info: {str(e)}")

@router.post("/initialize", summary="Initialize Ultra Ensemble Models")
async def initialize_ultra_ensemble():
    """Manually initialize Ultra Ensemble models"""
    try:
        ensemble = await get_ultra_ensemble()
        await ensemble.initialize_models()
        
        return {
            "status": "success",
            "message": "Ultra Ensemble models initialized successfully",
            "model_count": ensemble.model_count,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize Ultra Ensemble: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

async def run_ultra_ensemble_detection_task(video_id: str, video_path: str):
    """Background task for Ultra Ensemble detection"""
    start_time = time.time()
    logger.info(f"🚀 BACKGROUND TASK STARTED for video_id: {video_id}")
    logger.info(f"🚀 Video path: {video_path}")
    logger.info(f"🚀 DETECTION_RESULTS before task: {list(DETECTION_RESULTS.keys())}")
    logger.info(f"Starting Ultra Ensemble detection for video_id: {video_id}")
    
    store_ultra_ensemble_result(video_id, {
        "status": "processing",
        "result": None,
        "confidence": None,
        "detailed_analysis": None,
        "error": None,
        "mode": "Ultra Ensemble Mode",
        "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
        "start_time": start_time
    })
    
    try:
        # Extract faces from video
        logger.info(f"[{video_id}] Extracting faces from video...")
        faces, timing_info = await extract_faces_from_video(video_path)
        logger.info(f"[{video_id}] Face extraction completed: {len(faces)} faces found")
        
        if not faces:
            store_ultra_ensemble_result(video_id, {
                "status": "completed",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "detailed_analysis": {"faces_analyzed": 0, "error": "No faces found"},
                "error": None,
                "mode": "Ultra Ensemble Mode",
                "description": "25+ AI Models Integration – Maximum Accuracy & Analysis"
            })
            logger.info(f"[{video_id}] No faces found in video.")
            return
        
        # Get Ultra Ensemble instance
        ensemble = await get_ultra_ensemble()
        
        # Perform Ultra Ensemble detection
        logger.info(f"[{video_id}] Running Ultra Ensemble analysis on {len(faces)} faces...")
        try:
            prediction, confidence, detailed_results = await ensemble.predict_ensemble(
                faces, 
                video_path
            )
            logger.info(f"[{video_id}] Ultra Ensemble prediction completed: {prediction} (confidence: {confidence:.4f})")
        except Exception as e:
            logger.error(f"[{video_id}] Ultra Ensemble prediction failed: {e}")
            prediction = "Analysis Failed"
            confidence = 0.0
            detailed_results = {"error": str(e)}
        
        # Enhanced Analysis with RAG Agent and Generative AI
        logger.info(f"[{video_id}] Running enhanced RAG and Generative AI analysis...")
        try:
            # RAG Agent Analysis
            rag_agent = await get_rag_agent()
            additional_context = {
                "video_quality": "high" if len(faces) > 5 else "medium",
                "has_audio": False,  # Could be enhanced with audio analysis
                "has_expressions": True
            }
            rag_result = await rag_agent.analyze_video(video_path, faces, additional_context)
            
            # Generative AI Analysis
            generative_ai_models = await get_generative_ai_models()
            generative_results = await generative_ai_models.analyze_with_all_models(faces)
            
            # Integrate results
            enhanced_prediction, enhanced_confidence = _integrate_enhanced_results(
                prediction, confidence, rag_result, generative_results
            )
            
            # Update detailed results with enhanced analysis (context only)
            detailed_results.update({
                "rag_analysis": {
                    "is_deepfake": rag_result.is_deepfake,
                    "confidence": rag_result.confidence,
                    "deepfake_type": rag_result.deepfake_type.value,
                    "reasoning": rag_result.reasoning,
                    "detected_patterns": [p.name for p in rag_result.detected_patterns],
                    "recommendations": rag_result.recommendations,
                    "uncertainty_factors": rag_result.uncertainty_factors
                },
                "generative_ai_analysis": {
                    "transformer": {
                        "prediction": getattr(generative_results.get("transformer", {}), 'prediction', 'Unknown'),
                        "confidence": getattr(generative_results.get("transformer", {}), 'confidence', 0.0),
                        "attention_weights": getattr(generative_results.get("transformer", {}), 'attention_weights', {})
                    },
                    "gan": {
                        "prediction": getattr(generative_results.get("gan", {}), 'prediction', 'Unknown'),
                        "confidence": getattr(generative_results.get("gan", {}), 'confidence', 0.0),
                        "features": getattr(generative_results.get("gan", {}), 'features', {})
                    },
                    "ensemble": {
                        "prediction": getattr(generative_results.get("ensemble", {}), 'prediction', 'Unknown'),
                        "confidence": getattr(generative_results.get("ensemble", {}), 'confidence', 0.0)
                    }
                },
                "enhanced_prediction": enhanced_prediction,
                "enhanced_confidence": enhanced_confidence
            })
            
            # Do NOT override Ultra Ensemble final decision
            if enhanced_prediction != prediction:
                logger.info(f"[{video_id}] Enhanced analysis differs, keeping Ultra Ensemble decision: {prediction} (ensemble_conf: {confidence:.4f}, enhanced_conf: {enhanced_confidence:.4f})")
            
        except Exception as e:
            logger.warning(f"[{video_id}] Enhanced analysis failed: {e}, using standard results")
        
        # Calculate total processing time
        end_time = time.time()
        total_processing_time = round(end_time - start_time, 2)
        
        store_ultra_ensemble_result(video_id, {
            "status": "completed",
            "result": prediction,
            "confidence": confidence,
            "detailed_analysis": detailed_results,
            "error": None,
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis",
            "processing_time": f"{total_processing_time}s",
            "start_time": start_time,
            "end_time": end_time
        })
        
        logger.info(f"[{video_id}] Ultra Ensemble detection completed.")
        logger.info(f"[{video_id}] Result: {prediction}, Confidence: {confidence:.4f}")
        logger.info(f"[{video_id}] Models used: {detailed_results.get('model_count', 0)}")
        logger.info(f"[{video_id}] Result stored in DETECTION_RESULTS: {video_id in DETECTION_RESULTS}")
        logger.info(f"[{video_id}] Available video IDs: {list(DETECTION_RESULTS.keys())}")
        logger.info(f"[{video_id}] Stored result: {DETECTION_RESULTS[video_id]}")
        
    except Exception as e:
        error_msg = f"Ultra Ensemble detection failed for {video_id}: {str(e)}"
        logger.error(error_msg)
        
        store_ultra_ensemble_result(video_id, {
            "status": "failed",
            "result": None,
            "confidence": None,
            "detailed_analysis": None,
            "error": str(e),
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis"
        })
    
    finally:
        # Clean up uploaded video file
        try:
            if Path(video_path).exists():
                delete_video_file(video_path)
                logger.info(f"[{video_id}] Cleaned up video file")
        except Exception as e:
            logger.warning(f"[{video_id}] Failed to clean up video file: {e}")
        
        # Clean up detection results after some time to prevent memory leaks
        try:
            # Keep results for 1 hour, then clean up
            import threading
            def cleanup_results():
                import time
                time.sleep(3600)  # Wait 1 hour
                if video_id in _ULTRA_ENSEMBLE_RESULTS:
                    del _ULTRA_ENSEMBLE_RESULTS[video_id]
                    logger.info(f"[{video_id}] Cleaned up detection results")
            
            cleanup_thread = threading.Thread(target=cleanup_results, daemon=True)
            cleanup_thread.start()
            logger.info(f"[{video_id}] Cleanup thread scheduled for 1 hour from now")
        except Exception as e:
            logger.warning(f"[{video_id}] Failed to schedule cleanup: {e}")
        
        # Add debugging to track when results are accessed
        logger.info(f"[{video_id}] Final _ULTRA_ENSEMBLE_RESULTS state: {list(_ULTRA_ENSEMBLE_RESULTS.keys())}")
        logger.info(f"[{video_id}] Video ID still in results: {video_id in _ULTRA_ENSEMBLE_RESULTS}")

@router.delete("/result/{video_id}", summary="Delete Ultra Ensemble Detection Result")
async def delete_ultra_ensemble_result(video_id: str):
    """Delete a specific Ultra Ensemble detection result"""
    try:
        if video_id in _ULTRA_ENSEMBLE_RESULTS:
            del _ULTRA_ENSEMBLE_RESULTS[video_id]
            return {"status": "success", "message": f"Result for {video_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Video ID not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete Ultra Ensemble result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete result: {str(e)}")

@router.get("/results", summary="Get All Ultra Ensemble Results")
async def get_all_ultra_ensemble_results():
    """Get all Ultra Ensemble detection results"""
    try:
        return {
            "status": "success",
            "results": _ULTRA_ENSEMBLE_RESULTS,
            "count": len(_ULTRA_ENSEMBLE_RESULTS),
            "mode": "Ultra Ensemble Mode",
            "description": "25+ AI Models Integration – Maximum Accuracy & Analysis"
        }
        
    except Exception as e:
        logger.error(f"Failed to get Ultra Ensemble results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.post("/analyze-with-rag", summary="RAG Agent Analysis")
async def analyze_with_rag_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Perform deepfake detection using RAG (Retrieval-Augmented Generation) Agent
    
    This endpoint uses advanced RAG techniques with:
    - Knowledge retrieval from deepfake detection patterns
    - Generative AI for intelligent analysis
    - Context-aware decision making
    - Adaptive learning capabilities
    """
    try:
        # Save uploaded video
        video_id, video_path = await save_uploaded_video(file)
        
        # Start background RAG analysis task
        logger.info(f"Adding RAG analysis task for video_id: {video_id}")
        background_tasks.add_task(
            run_rag_analysis_task, 
            video_id, 
            video_path
        )
        
        return {
            "status": "processing",
            "video_id": video_id,
            "mode": "RAG Agent Analysis",
            "description": "Retrieval-Augmented Generation with Knowledge Base",
            "message": "RAG Agent analysis started with advanced pattern recognition.",
            "estimated_time": "45-90 seconds",
            "features": [
                "Knowledge retrieval from deepfake patterns",
                "Generative AI analysis",
                "Context-aware decision making",
                "Adaptive learning"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to start RAG analysis: {e}")
        raise HTTPException(status_code=500, detail=f"RAG analysis failed: {str(e)}")

@router.post("/analyze-with-generative-ai", summary="Generative AI Analysis")
async def analyze_with_generative_ai_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Perform deepfake detection using advanced Generative AI models
    
    This endpoint uses cutting-edge generative AI techniques:
    - Transformer-based sequence analysis
    - GAN-based pattern recognition
    - Multi-modal ensemble learning
    - Attention mechanisms
    """
    try:
        # Save uploaded video
        video_id, video_path = await save_uploaded_video(file)
        
        # Start background Generative AI analysis task
        logger.info(f"Adding Generative AI analysis task for video_id: {video_id}")
        background_tasks.add_task(
            run_generative_ai_analysis_task, 
            video_id, 
            video_path
        )
        
        return {
            "status": "processing",
            "video_id": video_id,
            "mode": "Generative AI Analysis",
            "description": "Advanced Generative AI Models Integration",
            "message": "Generative AI analysis started with transformer and GAN models.",
            "estimated_time": "60-120 seconds",
            "features": [
                "Transformer-based sequence analysis",
                "GAN-based pattern recognition",
                "Multi-modal ensemble learning",
                "Attention mechanisms",
                "Uncertainty quantification"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to start Generative AI analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Generative AI analysis failed: {str(e)}")

async def run_rag_analysis_task(video_id: str, video_path: str):
    """Background task for RAG Agent analysis"""
    start_time = time.time()
    logger.info(f"🤖 RAG Agent analysis started for video_id: {video_id}")
    
    # Explainer-only: keep internal status separate, do not mark main result as processing
    _EXPLAINER_RESULTS[video_id] = {
        "status": "processing",
        "module": "rag",
        "start_time": start_time
    }
    
    try:
        # Extract faces from video
        logger.info(f"[{video_id}] Extracting faces for RAG analysis...")
        faces, timing_info = await extract_faces_from_video(video_path)
        logger.info(f"[{video_id}] Face extraction completed: {len(faces)} faces found")
        
        if not faces:
            _EXPLAINER_RESULTS[video_id] = {
                "status": "completed",
                "module": "rag",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "detailed_analysis": {"faces_analyzed": 0, "error": "No faces found"},
            }
            return
        
        # RAG Agent Analysis
        logger.info(f"[{video_id}] Running RAG Agent analysis on {len(faces)} faces...")
        rag_agent = await get_rag_agent()
        additional_context = {
            "video_quality": "high" if len(faces) > 5 else "medium",
            "has_audio": False,
            "has_expressions": True
        }
        
        rag_result = await rag_agent.analyze_video(video_path, faces, additional_context)
        
        # Calculate processing time
        end_time = time.time()
        total_processing_time = round(end_time - start_time, 2)
        
        # Store explainer results only
        _EXPLAINER_RESULTS[video_id] = {
            "status": "completed",
            "module": "rag",
            "result": "Deepfake Detected" if rag_result.is_deepfake else "Real Video",
            "confidence": rag_result.confidence,
            "detailed_analysis": {
                "rag_analysis": {
                    "is_deepfake": rag_result.is_deepfake,
                    "confidence": rag_result.confidence,
                    "deepfake_type": rag_result.deepfake_type.value,
                    "reasoning": rag_result.reasoning,
                    "detected_patterns": [p.name for p in rag_result.detected_patterns],
                    "recommendations": rag_result.recommendations,
                    "uncertainty_factors": rag_result.uncertainty_factors
                },
                "faces_analyzed": len(faces),
                "processing_time": f"{total_processing_time}s"
            },
            "processing_time": f"{total_processing_time}s",
            "start_time": start_time,
            "end_time": end_time
        }
        
        logger.info(f"[{video_id}] RAG Agent analysis completed: {rag_result.is_deepfake} (confidence: {rag_result.confidence:.4f})")
        
    except Exception as e:
        error_msg = f"RAG Agent analysis failed for {video_id}: {str(e)}"
        logger.error(error_msg)
        
        _EXPLAINER_RESULTS[video_id] = {
            "status": "failed",
            "module": "rag",
            "error": str(e)
        }
    
    finally:
        # Clean up video file
        try:
            if Path(video_path).exists():
                delete_video_file(video_path)
                logger.info(f"[{video_id}] Cleaned up video file")
        except Exception as e:
            logger.warning(f"[{video_id}] Failed to clean up video file: {e}")

async def run_generative_ai_analysis_task(video_id: str, video_path: str):
    """Background task for Generative AI analysis"""
    start_time = time.time()
    logger.info(f"🤖 Generative AI analysis started for video_id: {video_id}")
    
    # Explainer-only: keep separate store
    _EXPLAINER_RESULTS[video_id] = {
        "status": "processing",
        "module": "genai",
        "start_time": start_time
    }
    
    try:
        # Extract faces from video
        logger.info(f"[{video_id}] Extracting faces for Generative AI analysis...")
        faces, timing_info = await extract_faces_from_video(video_path)
        logger.info(f"[{video_id}] Face extraction completed: {len(faces)} faces found")
        
        if not faces:
            _EXPLAINER_RESULTS[video_id] = {
                "status": "completed",
                "module": "genai",
                "result": "No Faces Detected",
                "confidence": 0.0,
                "detailed_analysis": {"faces_analyzed": 0, "error": "No faces found"}
            }
            return
        
        # Generative AI Analysis
        logger.info(f"[{video_id}] Running Generative AI analysis on {len(faces)} faces...")
        generative_ai_models = await get_generative_ai_models()
        generative_results = await generative_ai_models.analyze_with_all_models(faces)
        
        # Get ensemble result
        ensemble_result = generative_results.get("ensemble", {})
        prediction = getattr(ensemble_result, 'prediction', 'Unknown')
        confidence = getattr(ensemble_result, 'confidence', 0.0)
        
        # Calculate processing time
        end_time = time.time()
        total_processing_time = round(end_time - start_time, 2)
        
        _EXPLAINER_RESULTS[video_id] = {
            "status": "completed",
            "module": "genai",
            "result": prediction,
            "confidence": confidence,
            "detailed_analysis": {
                "generative_ai_analysis": {
                    "transformer": {
                        "prediction": getattr(generative_results.get("transformer", {}), 'prediction', 'Unknown'),
                        "confidence": getattr(generative_results.get("transformer", {}), 'confidence', 0.0),
                        "attention_weights": getattr(generative_results.get("transformer", {}), 'attention_weights', {})
                    },
                    "gan": {
                        "prediction": getattr(generative_results.get("gan", {}), 'prediction', 'Unknown'),
                        "confidence": getattr(generative_results.get("gan", {}), 'confidence', 0.0),
                        "features": getattr(generative_results.get("gan", {}), 'features', {})
                    },
                    "ensemble": {
                        "prediction": prediction,
                        "confidence": confidence
                    }
                },
                "faces_analyzed": len(faces),
                "processing_time": f"{total_processing_time}s"
            },
            "processing_time": f"{total_processing_time}s",
            "start_time": start_time,
            "end_time": end_time
        }
        
        logger.info(f"[{video_id}] Generative AI analysis completed: {prediction} (confidence: {confidence:.4f})")
        
    except Exception as e:
        error_msg = f"Generative AI analysis failed for {video_id}: {str(e)}"
        logger.error(error_msg)
        
        _EXPLAINER_RESULTS[video_id] = {
            "status": "failed",
            "module": "genai",
            "error": str(e)
        }
    
    finally:
        # Clean up video file
        try:
            if Path(video_path).exists():
                delete_video_file(video_path)
                logger.info(f"[{video_id}] Cleaned up video file")
        except Exception as e:
            logger.warning(f"[{video_id}] Failed to clean up video file: {e}")
