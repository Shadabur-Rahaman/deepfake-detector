# app/services/enhanced_detection_engine.py - FINAL STABLE VERSION
import torch
from typing import Dict, List
import logging
from backend.app.services.deepfake_detector import enhanced_detector
from backend.app.utils.model_importer import MODEL_AVAILABILITY

logger = logging.getLogger(__name__)

# This flag will be imported by main.py
ENHANCED_DETECTION_AVAILABLE = False

class EnhancedDetectionEngine:
    def __init__(self):
        self.advanced_models = {}
        self._load_available_models()

    def _load_available_models(self):
        global ENHANCED_DETECTION_AVAILABLE
        if MODEL_AVAILABILITY.get('mesonet'):
            try:
                from app.models.mesonet_detector import MesoNetDetector
                self.advanced_models['mesonet'] = MesoNetDetector()
                logger.info("✅ MesoNet loaded (deepfake specialist)")
                ENHANCED_DETECTION_AVAILABLE = True
            except Exception as e:
                logger.warning(f"⚠️ MesoNet loading failed: {e}")
        logger.info(f"🚀 Enhanced engine loaded with {len(self.advanced_models)} advanced models.")

    async def enhanced_detect(self, faces: List[torch.Tensor]) -> Dict:
        if not faces: return {"prediction": "No Faces Detected", "confidence": 0.0}

        primary_data = enhanced_detector.enhanced_analyze_faces(faces)
        if "error" in primary_data: return primary_data

        primary_conf = primary_data.get('confidence', 0.0)
        final_predictions = [primary_conf]

        if 'mesonet' in self.advanced_models:
            try:
                meso_result = await self.advanced_models['mesonet'].predict(faces)
                if "error" not in meso_result:
                    final_predictions.append(meso_result.get('confidence', 0.0))
            except Exception as e:
                logger.warning(f"⚠️ MesoNet prediction failed during runtime: {e}")

        final_confidence = sum(final_predictions) / len(final_predictions)
        final_prediction = "Deepfake Detected" if final_confidence > 50.0 else "Real Video"
        
        return {"prediction": final_prediction, "confidence": final_confidence}