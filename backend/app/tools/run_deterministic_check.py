#!/usr/bin/env python3
"""
Deterministic Regression Check Tool
===================================

This script runs deterministic regression tests to verify that the same inputs
produce identical outputs across multiple runs.

Usage:
    python run_deterministic_check.py [--test-image PATH] [--runs N] [--verbose]

Examples:
    python run_deterministic_check.py
    python run_deterministic_check.py --test-image test_face.jpg --runs 5
    python run_deterministic_check.py --verbose
"""

import asyncio
import argparse
import sys
import os
import time
import json
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.deterministic_config import setup_deterministic_inference, get_deterministic_config
from services.deterministic_ensemble_detector import DeterministicEnsembleDetector
from services.deterministic_face_detector import detect_faces_deterministic
from services.deterministic_deepfake_detector import DeterministicDeepfakeDetector

class DeterministicRegressionChecker:
    """Comprehensive deterministic regression checker"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        self.config = None
        self.detector = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{timestamp}] {level}: {message}")
    
    async def initialize(self):
        """Initialize deterministic environment and detector"""
        try:
            self.log("Initializing deterministic environment...")
            setup_deterministic_inference(seed=42, enable=True)
            self.config = get_deterministic_config()
            
            self.log("Initializing ensemble detector...")
            self.detector = DeterministicEnsembleDetector()
            await self.detector.initialize_models()
            
            self.log("[OK] Initialization complete")
            return True
            
        except Exception as e:
            self.log(f"[ERROR] Initialization failed: {e}", "ERROR")
            return False
    
    def create_test_image(self, size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Create a deterministic test image"""
        # Create a simple test image with known patterns
        image = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        
        # Add deterministic patterns
        image[50:150, 50:150] = [128, 128, 128]  # Gray square
        image[100:120, 100:120] = [255, 255, 255]  # White square
        image[30:50, 30:50] = [64, 64, 64]  # Dark gray square
        
        return image
    
    def load_test_image(self, image_path: str) -> np.ndarray:
        """Load test image from file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Test image not found: {image_path}")
            
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            self.log(f"Loaded test image: {image_path} (shape: {image.shape})")
            return image
            
        except Exception as e:
            self.log(f"Failed to load test image: {e}", "ERROR")
            raise
    
    def run_preprocessing_test(self, image: np.ndarray, runs: int = 5) -> Dict[str, Any]:
        """Test preprocessing consistency"""
        self.log(f"Running preprocessing test ({runs} runs)...")
        
        results = {
            "test_name": "preprocessing_consistency",
            "runs": runs,
            "hashes": [],
            "tensor_shapes": [],
            "tensor_ranges": [],
            "consistent": True,
            "errors": []
        }
        
        try:
            detector = DeterministicDeepfakeDetector()
            
            for i in range(runs):
                # Preprocess image
                tensor = detector.preprocess_face_deterministic(image)
                
                # Generate hash
                hash_val = self.config.generate_preprocessing_hash(image)
                
                # Store results
                results["hashes"].append(hash_val)
                results["tensor_shapes"].append(list(tensor.shape))
                results["tensor_ranges"].append({
                    "min": float(tensor.min().item()),
                    "max": float(tensor.max().item()),
                    "mean": float(tensor.mean().item())
                })
            
            # Check consistency
            unique_hashes = set(results["hashes"])
            if len(unique_hashes) != 1:
                results["consistent"] = False
                results["errors"].append(f"Hash inconsistency: {len(unique_hashes)} unique hashes")
            
            # Check tensor consistency
            for i in range(1, len(results["tensor_ranges"])):
                prev_range = results["tensor_ranges"][i-1]
                curr_range = results["tensor_ranges"][i]
                
                for key in ["min", "max", "mean"]:
                    diff = abs(prev_range[key] - curr_range[key])
                    if diff > 1e-6:
                        results["consistent"] = False
                        results["errors"].append(f"Tensor {key} inconsistency: {diff}")
            
            if results["consistent"]:
                self.log("[OK] Preprocessing test passed")
            else:
                self.log("[ERROR] Preprocessing test failed", "ERROR")
            
            return results
            
        except Exception as e:
            results["consistent"] = False
            results["errors"].append(f"Preprocessing test failed: {e}")
            self.log(f"[ERROR] Preprocessing test failed: {e}", "ERROR")
            return results
    
    def run_face_detection_test(self, image: np.ndarray, runs: int = 5) -> Dict[str, Any]:
        """Test face detection consistency"""
        self.log(f"Running face detection test ({runs} runs)...")
        
        results = {
            "test_name": "face_detection_consistency",
            "runs": runs,
            "face_counts": [],
            "face_shapes": [],
            "coordinates": [],
            "consistent": True,
            "errors": []
        }
        
        try:
            for i in range(runs):
                faces, coords = detect_faces_deterministic(image)
                
                results["face_counts"].append(len(faces))
                results["face_shapes"].append([list(face.shape) for face in faces])
                results["coordinates"].append(coords)
            
            # Check consistency
            unique_counts = set(results["face_counts"])
            if len(unique_counts) != 1:
                results["consistent"] = False
                results["errors"].append(f"Face count inconsistency: {unique_counts}")
            
            # Check face shapes consistency
            for i in range(1, len(results["face_shapes"])):
                if results["face_shapes"][i-1] != results["face_shapes"][i]:
                    results["consistent"] = False
                    results["errors"].append(f"Face shapes inconsistency at run {i}")
            
            if results["consistent"]:
                self.log("[OK] Face detection test passed")
            else:
                self.log("[ERROR] Face detection test failed", "ERROR")
            
            return results
            
        except Exception as e:
            results["consistent"] = False
            results["errors"].append(f"Face detection test failed: {e}")
            self.log(f"[ERROR] Face detection test failed: {e}", "ERROR")
            return results
    
    async def run_ensemble_detection_test(self, image: np.ndarray, runs: int = 5) -> Dict[str, Any]:
        """Test ensemble detection consistency"""
        self.log(f"Running ensemble detection test ({runs} runs)...")
        
        results = {
            "test_name": "ensemble_detection_consistency",
            "runs": runs,
            "preproc_hashes": [],
            "model_results": {},
            "fusion_raws": [],
            "fusion_smootheds": [],
            "final_predictions": [],
            "final_confidences": [],
            "consistent": True,
            "errors": []
        }
        
        try:
            # Detect faces first
            faces, _ = detect_faces_deterministic(image)
            
            if not faces:
                # Create a dummy face if none detected
                faces = [image[50:150, 50:150] if image.shape[0] > 150 and image.shape[1] > 150 else image]
            
            # Initialize model results structure
            for model_name in self.detector.models.keys():
                results["model_results"][model_name] = {
                    "predictions": [],
                    "confidences": [],
                    "raw_outputs": []
                }
            
            for i in range(runs):
                # Run ensemble detection
                ensemble_result = await self.detector.detect_ensemble(faces, frame_id=i)
                
                # Store results
                results["preproc_hashes"].append(ensemble_result.preproc_hash)
                results["fusion_raws"].append(ensemble_result.fusion_raw)
                results["fusion_smootheds"].append(ensemble_result.fusion_smoothed)
                results["final_predictions"].append(ensemble_result.final_prediction)
                results["final_confidences"].append(ensemble_result.final_confidence)
                
                # Store model results
                for model_name, model_result in ensemble_result.model_results.items():
                    if model_name in results["model_results"]:
                        results["model_results"][model_name]["predictions"].append(model_result.prediction)
                        results["model_results"][model_name]["confidences"].append(model_result.confidence)
                        results["model_results"][model_name]["raw_outputs"].append(model_result.raw_output)
            
            # Check consistency
            unique_hashes = set(results["preproc_hashes"])
            if len(unique_hashes) != 1:
                results["consistent"] = False
                results["errors"].append(f"Preprocessing hash inconsistency: {len(unique_hashes)} unique hashes")
            
            # Check fusion results consistency
            for i in range(1, len(results["fusion_raws"])):
                if abs(results["fusion_raws"][i-1] - results["fusion_raws"][i]) > 1e-5:
                    results["consistent"] = False
                    results["errors"].append(f"Fusion raw inconsistency at run {i}")
                
                if results["final_predictions"][i-1] != results["final_predictions"][i]:
                    results["consistent"] = False
                    results["errors"].append(f"Final prediction inconsistency at run {i}")
                
                if abs(results["final_confidences"][i-1] - results["final_confidences"][i]) > 1e-5:
                    results["consistent"] = False
                    results["errors"].append(f"Final confidence inconsistency at run {i}")
            
            # Check model results consistency
            for model_name, model_data in results["model_results"].items():
                if model_data["predictions"]:
                    unique_predictions = set(model_data["predictions"])
                    if len(unique_predictions) != 1:
                        results["consistent"] = False
                        results["errors"].append(f"Model {model_name} prediction inconsistency")
                    
                    for i in range(1, len(model_data["confidences"])):
                        if abs(model_data["confidences"][i-1] - model_data["confidences"][i]) > 1e-5:
                            results["consistent"] = False
                            results["errors"].append(f"Model {model_name} confidence inconsistency at run {i}")
            
            if results["consistent"]:
                self.log("[OK] Ensemble detection test passed")
            else:
                self.log("[ERROR] Ensemble detection test failed", "ERROR")
            
            return results
            
        except Exception as e:
            results["consistent"] = False
            results["errors"].append(f"Ensemble detection test failed: {e}")
            self.log(f"[ERROR] Ensemble detection test failed: {e}", "ERROR")
            return results
    
    def run_configuration_test(self) -> Dict[str, Any]:
        """Test configuration consistency"""
        self.log("Running configuration test...")
        
        results = {
            "test_name": "configuration_consistency",
            "consistent": True,
            "errors": [],
            "config_info": {}
        }
        
        try:
            # Get configuration info
            config_info = self.config.get_deterministic_info()
            results["config_info"] = config_info
            
            # Check required fields
            required_fields = [
                "seed", "enable_deterministic", "initialized",
                "pytorch_deterministic", "pytorch_benchmark"
            ]
            
            for field in required_fields:
                if field not in config_info:
                    results["consistent"] = False
                    results["errors"].append(f"Missing configuration field: {field}")
            
            # Check deterministic settings
            if not config_info.get("enable_deterministic", False):
                results["consistent"] = False
                results["errors"].append("Deterministic mode not enabled")
            
            if not config_info.get("pytorch_deterministic", False):
                results["consistent"] = False
                results["errors"].append("PyTorch deterministic not enabled")
            
            if config_info.get("pytorch_benchmark", True):
                results["consistent"] = False
                results["errors"].append("PyTorch benchmark should be disabled")
            
            if results["consistent"]:
                self.log("[OK] Configuration test passed")
            else:
                self.log("[ERROR] Configuration test failed", "ERROR")
            
            return results
            
        except Exception as e:
            results["consistent"] = False
            results["errors"].append(f"Configuration test failed: {e}")
            self.log(f"[ERROR] Configuration test failed: {e}", "ERROR")
            return results
    
    async def run_all_tests(self, test_image_path: str = None, runs: int = 5) -> Dict[str, Any]:
        """Run all deterministic regression tests"""
        self.log("[START] Starting deterministic regression check...")
        
        # Initialize
        if not await self.initialize():
            return {"success": False, "error": "Initialization failed"}
        
        # Load or create test image
        if test_image_path and os.path.exists(test_image_path):
            image = self.load_test_image(test_image_path)
        else:
            image = self.create_test_image()
            self.log("Using generated test image")
        
        # Run tests
        test_results = []
        
        # Configuration test
        config_result = self.run_configuration_test()
        test_results.append(config_result)
        
        # Preprocessing test
        preproc_result = self.run_preprocessing_test(image, runs)
        test_results.append(preproc_result)
        
        # Face detection test
        face_result = self.run_face_detection_test(image, runs)
        test_results.append(face_result)
        
        # Ensemble detection test
        ensemble_result = await self.run_ensemble_detection_test(image, runs)
        test_results.append(ensemble_result)
        
        # Summary
        all_passed = all(result["consistent"] for result in test_results)
        
        summary = {
            "success": all_passed,
            "timestamp": datetime.now().isoformat(),
            "runs": runs,
            "test_image_shape": list(image.shape),
            "tests": test_results,
            "summary": {
                "total_tests": len(test_results),
                "passed_tests": sum(1 for r in test_results if r["consistent"]),
                "failed_tests": sum(1 for r in test_results if not r["consistent"]),
                "all_passed": all_passed
            }
        }
        
        # Log summary
        if all_passed:
            self.log("[COMPLETE] All deterministic regression tests passed!")
        else:
            self.log("[ERROR] Some deterministic regression tests failed", "ERROR")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], output_path: str = None):
        """Save test results to file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"deterministic_test_results_{timestamp}.json"
        
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            self.log(f"Results saved to: {output_path}")
        except Exception as e:
            self.log(f"Failed to save results: {e}", "ERROR")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Deterministic Regression Check Tool")
    parser.add_argument("--test-image", type=str, help="Path to test image")
    parser.add_argument("--runs", type=int, default=5, help="Number of runs per test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    # Create checker
    checker = DeterministicRegressionChecker(verbose=args.verbose)
    
    # Run tests
    results = await checker.run_all_tests(
        test_image_path=args.test_image,
        runs=args.runs
    )
    
    # Save results
    checker.save_results(results, args.output)
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
