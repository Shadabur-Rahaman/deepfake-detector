# backend/app/routes/optimal_detection.py
# Optimal Production-Grade Detection API Routes

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import time
import logging
from typing import Optional, Dict, Any
import asyncio

from ..services.optimal_production_detector import get_optimal_detector, DetectionTier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimal", tags=["Optimal Detection"])

@router.post("/detect")
async def detect_deepfake_optimal(
    file: UploadFile = File(...),
    tier: Optional[str] = Form("auto"),
    video_id: Optional[str] = Form(None)
):
    """
    Optimal Production-Grade Deepfake Detection
    
    Features:
    - Adaptive resource management
    - Multi-tier detection (ultra_fast, balanced, maximum_accuracy, production)
    - Optimized face extraction (15-25 faces based on tier)
    - Production-grade error handling
    - Real-time performance monitoring
    """
    try:
        # Generate video ID if not provided
        if not video_id:
            video_id = str(uuid.uuid4())
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file
        video_path = f"temp_uploads/{video_id}_{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        
        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize detection result (will be handled by the detector)
        logger.info(f"🎯 Starting optimal detection for {video_id} with tier: {tier}")
        
        # Start background detection
        asyncio.create_task(process_optimal_detection(video_id, video_path, tier))
        
        return JSONResponse({
            "video_id": video_id,
            "status": "processing",
            "message": "Optimal detection started",
            "tier": tier,
            "estimated_time": get_estimated_time(tier)
        })
        
    except Exception as e:
        logger.error(f"Optimal detection initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection initialization failed: {str(e)}")

@router.get("/status/{video_id}")
async def get_optimal_detection_status(video_id: str):
    """Get status of optimal detection"""
    try:
        # For now, return a simple status - this will be enhanced later
        return JSONResponse({
            "video_id": video_id,
            "status": "processing",
            "progress": 50,
            "message": "Optimal detection in progress...",
            "tier": "balanced",
            "processing_time": 0,
            "result": None
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """Get system information and capabilities"""
    try:
        detector = await get_optimal_detector()
        system_info = detector.get_system_info()
        
        return JSONResponse({
            "system_info": system_info,
            "available_tiers": [tier.value for tier in DetectionTier],
            "recommended_tier": get_recommended_tier(system_info)
        })
        
    except Exception as e:
        logger.error(f"System info retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"System info retrieval failed: {str(e)}")

@router.get("/performance-stats")
async def get_performance_stats():
    """Get performance statistics"""
    try:
        detector = await get_optimal_detector()
        stats = detector.performance_stats
        
        return JSONResponse({
            "performance_stats": stats,
            "recommendations": get_performance_recommendations(stats)
        })
        
    except Exception as e:
        logger.error(f"Performance stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance stats retrieval failed: {str(e)}")

async def process_optimal_detection(video_id: str, video_path: str, tier: str):
    """Process optimal detection in background"""
    try:
        logger.info(f"🎯 Starting optimal detection for {video_id} with tier: {tier}")
        
        # Get optimal detector
        detector = await get_optimal_detector()
        
        # Override tier if specified
        if tier != "auto":
            try:
                detector.tier = DetectionTier(tier)
                logger.info(f"🎯 Using specified tier: {tier}")
            except ValueError:
                logger.warning(f"Invalid tier '{tier}', using auto-detected tier")
        
        # Run optimal detection
        result = await detector.detect_deepfake_optimal(video_path, video_id)
        
        logger.info(f"✅ Optimal detection completed for {video_id}: {result['prediction']} ({result['confidence']:.2f})")
        
        # Cleanup temporary file
        try:
            os.remove(video_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Optimal detection processing failed: {e}")

def get_estimated_time(tier: str) -> str:
    """Get estimated processing time for tier"""
    estimates = {
        "ultra_fast": "5-8 seconds",
        "balanced": "10-15 seconds", 
        "maximum_accuracy": "20-30 seconds",
        "production": "10-20 seconds",
        "auto": "10-20 seconds"
    }
    return estimates.get(tier, "10-20 seconds")

def get_recommended_tier(system_info: Dict[str, Any]) -> str:
    """Get recommended tier based on system info"""
    device = system_info.get('device', 'cpu')
    tier = system_info.get('tier', 'production')
    
    if 'cuda' in device:
        if 'maximum' in tier:
            return "maximum_accuracy"
        else:
            return "balanced"
    else:
        return "ultra_fast"

def get_performance_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Get performance recommendations based on stats"""
    recommendations = []
    
    avg_time = stats.get('avg_processing_time', 0)
    success_rate = stats.get('success_rate', 0)
    
    if avg_time > 20:
        recommendations.append("Consider using 'ultra_fast' tier for better performance")
    
    if success_rate < 0.9:
        recommendations.append("System may be under resource pressure, consider 'balanced' tier")
    
    if avg_time < 5 and success_rate > 0.95:
        recommendations.append("System performing optimally, 'maximum_accuracy' tier recommended")
    
    return recommendations

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for optimal detection system"""
    try:
        detector = await get_optimal_detector()
        system_info = detector.get_system_info()
        
        return JSONResponse({
            "status": "healthy",
            "system_info": system_info,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }, status_code=500)
