#!/usr/bin/env python3
# backend/app/tools/check_startup_models.py - Model Loading Startup Check Tool

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.model_availability import initialize_model_availability, get_availability_status, get_installation_hints
from services.model_loader import load_all_models, get_startup_summary

def setup_logging():
    """Setup logging for the startup check"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_model_status(status: dict, title: str):
    """Print model status in a formatted way"""
    print(f"\n{title}:")
    for model, available in status.items():
        status_icon = "[OK]" if available else "[ERROR]"
        print(f"  {status_icon} {model}: {'Available' if available else 'Not Available'}")

def print_installation_hints(hints: dict):
    """Print installation hints for unavailable models"""
    if hints:
        print("\n💡 Installation Hints:")
        for model, hint in hints.items():
            print(f"  {model}: {hint}")
    else:
        print("\n[OK] All models are available!")

def print_startup_summary(summary: dict):
    """Print comprehensive startup summary"""
    print_separator("STARTUP SUMMARY")
    
    print(f"Device: {summary['device']}")
    print(f"Total models attempted: {summary['total_models_attempted']}")
    
    print(f"\n[OK] Successfully loaded models ({len(summary['successful_models'])}):")
    for model in summary['successful_models']:
        print(f"  - {model}")
    
    if summary['failed_models']:
        print(f"\n[ERROR] Failed to load models ({len(summary['failed_models'])}):")
        for model in summary['failed_models']:
            print(f"  - {model}")
    
    if summary['missing_dependencies']:
        print(f"\n[WARNING] Missing dependencies ({len(summary['missing_dependencies'])}):")
        for model in summary['missing_dependencies']:
            print(f"  - {model}")
    
    print(f"\n🎯 Ensemble ready with {len(summary['ensemble_models'])} models:")
    for model in summary['ensemble_models']:
        print(f"  - {model}")
    
    if summary['installation_hints']:
        print_installation_hints(summary['installation_hints'])

def check_model_availability():
    """Check model availability without loading models"""
    print_separator("MODEL AVAILABILITY CHECK")
    
    print("Checking module availability...")
    availability_status = initialize_model_availability()
    
    print_model_status(availability_status, "Module Availability")
    
    hints = get_installation_hints()
    print_installation_hints(hints)
    
    return availability_status

def check_model_loading():
    """Check model loading with actual model initialization"""
    print_separator("MODEL LOADING CHECK")
    
    print("Loading all available models...")
    try:
        model_results = load_all_models()
        summary = get_startup_summary()
        
        print_startup_summary(summary)
        
        return summary
        
    except Exception as e:
        print(f"[ERROR] Model loading failed: {e}")
        return None

def main():
    """Main function to run startup checks"""
    setup_logging()
    
    print("🔍 Deepfake Detection Model Startup Check")
    print("This tool checks model availability and loading status")
    
    # Check availability first
    availability_status = check_model_availability()
    
    # Check actual loading
    loading_summary = check_model_loading()
    
    # Final status
    print_separator("FINAL STATUS")
    
    if loading_summary:
        successful_count = len(loading_summary['successful_models'])
        total_count = loading_summary['total_models_attempted']
        
        print(f"Model Loading: {successful_count}/{total_count} successful")
        
        if successful_count > 0:
            print("[OK] System is ready for deepfake detection!")
        else:
            print("[ERROR] No models loaded - system may not function properly")
            print("💡 Check installation hints above and install missing dependencies")
    else:
        print("[ERROR] Model loading check failed")
        print("💡 Check error messages above and fix issues")
    
    print("\n" + "="*60)
    print("Check complete!")
    print("="*60)

if __name__ == "__main__":
    main()
