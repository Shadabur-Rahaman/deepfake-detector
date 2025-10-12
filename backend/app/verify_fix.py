#!/usr/bin/env python3
"""
Quick verification script for the frame processing fix
"""

import asyncio
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def verify_frame_processing_fix():
    """Verify that the frame processing fix works"""
    try:
        logger.info("🔍 Verifying frame processing fix...")
        
        from services.enhanced_async_detector import EnhancedAsyncDeepfakeDetector, DetectionConfig
        
        # Create detector with test configuration
        config = DetectionConfig(
            batch_size=4,
            enable_batching=True,
            max_processing_time_ms=200.0,
            enable_temporal_smoothing=True
        )
        
        detector = EnhancedAsyncDeepfakeDetector(config)
        
        # Initialize and start
        await detector.initialize()
        await detector.start_detection()
        
        logger.info("[OK] Detector initialized and started")
        
        # Test frame processing
        import numpy as np
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Process multiple frames quickly
        results = []
        for i in range(5):
            logger.info(f"Processing test frame {i+1}...")
            result = await detector.process_frame(test_frame)
            
            if result:
                logger.info(f"[OK] Frame {i+1} processed: {result.prediction}")
                results.append(result)
            else:
                logger.warning(f"[ERROR] Frame {i+1} returned None")
            
            # Small delay
            await asyncio.sleep(0.1)
        
        # Check results
        success_rate = len(results) / 5
        logger.info(f"[DATA] Success rate: {success_rate:.1%} ({len(results)}/5 frames processed)")
        
        if success_rate >= 0.8:  # At least 80% success
            logger.info("[COMPLETE] Frame processing fix VERIFIED - working correctly!")
            return True
        else:
            logger.error("[ERROR] Frame processing fix FAILED - too many frames skipped")
            return False
        
    except Exception as e:
        logger.error(f"[ERROR] Verification failed: {e}")
        return False
    finally:
        try:
            await detector.stop_detection()
            await detector.cleanup()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(verify_frame_processing_fix())
    exit(0 if success else 1)
