import time
from typing import Dict, List

class DetectionAnalytics:
    def __init__(self):
        self.analytics_data = {
            'total_detections': 0,
            'detections_by_type': {},
            'processing_times': [],
            'start_time': time.time()
        }

    def log_detection(self, video_id: str, result: dict):
        """Log detection result for analytics"""
        try:
            self.analytics_data['total_detections'] += 1
            
            prediction = result.get('prediction', 'Unknown')
            if prediction not in self.analytics_data['detections_by_type']:
                self.analytics_data['detections_by_type'][prediction] = 0
            self.analytics_data['detections_by_type'][prediction] += 1
            
            processing_time = result.get('processing_time', 0)
            if processing_time > 0:
                self.analytics_data['processing_times'].append(processing_time)
                
        except Exception as e:
            print(f"Analytics logging failed: {e}")

    def get_analytics_summary(self) -> dict:
        """Get analytics summary"""
        uptime = time.time() - self.analytics_data['start_time']
        avg_processing_time = (
            sum(self.analytics_data['processing_times']) / len(self.analytics_data['processing_times'])
            if self.analytics_data['processing_times'] else 0
        )
        
        return {
            "status": "operational",
            "total_detections": self.analytics_data['total_detections'],
            "uptime_seconds": round(uptime, 2),
            "detection_breakdown": self.analytics_data['detections_by_type'],
            "average_processing_time": round(avg_processing_time, 2)
        }
