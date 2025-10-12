# app/services/analytics.py
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DetectionAnalytics:
    """Simple analytics tracking for detections"""
    
    def __init__(self):
        self.analytics_data = {
            "total_detections": 0,
            "detection_history": [],
            "processing_times": [],
            "model_usage": {}
        }
    
    def log_detection(self, video_id: str, result: dict):
        """Log a detection result"""
        try:
            self.analytics_data["total_detections"] += 1
            
            # Log detection event
            detection_event = {
                "video_id": video_id,
                "timestamp": datetime.now().isoformat(),
                "prediction": result.get("prediction", "Unknown"),
                "confidence": result.get("confidence", 0),
                "processing_time": result.get("processing_time", 0),
                "detection_method": result.get("detection_method", "Unknown")
            }
            
            self.analytics_data["detection_history"].append(detection_event)
            
            # Keep only last 1000 entries
            if len(self.analytics_data["detection_history"]) > 1000:
                self.analytics_data["detection_history"] = self.analytics_data["detection_history"][-1000:]
            
            # Track processing times
            if result.get("processing_time"):
                self.analytics_data["processing_times"].append(result["processing_time"])
                if len(self.analytics_data["processing_times"]) > 1000:
                    self.analytics_data["processing_times"] = self.analytics_data["processing_times"][-1000:]
            
            # Track model usage
            method = result.get("detection_method", "Unknown")
            self.analytics_data["model_usage"][method] = self.analytics_data["model_usage"].get(method, 0) + 1
            
        except Exception as e:
            logger.error(f"Analytics logging error: {e}")
    
    def get_analytics_summary(self) -> dict:
        """Get analytics summary"""
        try:
            # Calculate average processing time
            avg_processing_time = 0
            if self.analytics_data["processing_times"]:
                avg_processing_time = sum(self.analytics_data["processing_times"]) / len(self.analytics_data["processing_times"])
            
            # Get recent detections (last 24h)
            now = datetime.now()
            yesterday = now - timedelta(hours=24)
            recent_detections = [
                d for d in self.analytics_data["detection_history"] 
                if datetime.fromisoformat(d["timestamp"]) > yesterday
            ]
            
            # Content distribution
            content_distribution = {}
            for detection in recent_detections:
                pred = detection["prediction"]
                content_distribution[pred] = content_distribution.get(pred, 0) + 1
            
            return {
                "status": "active",
                "total_detections_24h": len(recent_detections),
                "avg_processing_time": round(avg_processing_time, 2),
                "content_distribution": content_distribution,
                "model_performance": self.analytics_data["model_usage"],
                "total_all_time": self.analytics_data["total_detections"]
            }
            
        except Exception as e:
            logger.error(f"Analytics summary error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "total_detections_24h": 0,
                "avg_processing_time": 0,
                "content_distribution": {},
                "model_performance": {}
            }
