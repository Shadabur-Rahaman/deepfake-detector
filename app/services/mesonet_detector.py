# app/models/mesonet_detector.py
import torch, torch.nn as nn
import logging, pathlib

logger = logging.getLogger(__name__)
WEIGHTS = pathlib.Path(__file__).parent / "mesonet_weights.pth"

# Try to import timm with error handling for Python 3.13 compatibility
TIMM_AVAILABLE = False
try:
    import timm
    TIMM_AVAILABLE = True
    logger.info("✅ timm imported successfully")
except Exception as e:
    logger.warning(f"⚠️ timm import failed (possibly Python 3.13 compatibility issue): {e}")
    TIMM_AVAILABLE = False

class _MesoNet(nn.Module):
    """Very small CNN – 55 k params."""
    def __init__(self):
        super().__init__()
        if TIMM_AVAILABLE:
            try:
                self.backbone = timm.create_model('mobilenetv3_small_050', pretrained=False, num_classes=1)
            except Exception as e:
                logger.warning(f"⚠️ timm model creation failed: {e}, using fallback")
                TIMM_AVAILABLE = False
                raise
        else:
            # Fallback implementation without timm
            raise ImportError("timm not available - cannot create MesoNet model")
            
        self.act = nn.Sigmoid()

    def forward(self, x):
        return self.act(self.backbone(x)).squeeze(1)

class MesoNetDetector:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        if not TIMM_AVAILABLE:
            logger.error("❌ MesoNet detector not available - timm dependency missing")
            self.model = None
            return
            
        try:
            self.model = _MesoNet().to(device)
            if WEIGHTS.exists():
                self.model.load_state_dict(torch.load(WEIGHTS, map_location=device))
            self.model.eval()
            logger.info("✅ MesoNet detector initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MesoNet detector: {e}")
            self.model = None

    @torch.no_grad()
    async def predict(self, faces):
        """faces = list[Tensor (3,224,224)]  -> {'prediction', 'confidence'}"""
        if not faces:
            return {'prediction': 'No Faces', 'confidence': 0.0}
        
        if self.model is None:
            return {'prediction': 'Error', 'confidence': 0.0, 'error': 'MesoNet model not available'}
            
        try:
            batch = torch.stack(faces).to(self.device)
            prob = self.model(batch).mean().item()     # avg over faces
            if prob >= 0.5:
                return {'prediction': 'Deepfake', 'confidence': prob}
            return {'prediction': 'Real', 'confidence': 1 - prob}
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {'prediction': 'Error', 'confidence': 0.0, 'error': str(e)}
