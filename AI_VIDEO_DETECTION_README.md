# AI Video Detection System

A comprehensive backend AI video detection system that implements a multi-stage pipeline for detecting deepfakes in videos. The system combines face-level analysis with CNN/Transformer hybrid models, frame-level aggregation, metadata analysis, and temporal smoothing.

## Features

### Multi-Stage Detection Pipeline

1. **Face Extraction**: Extracts faces from video frames using deterministic face detection
2. **CNN/Transformer Hybrid Analysis**: Uses ensemble models including EfficientNet-B0 and other deep learning models
3. **Frame-Level Aggregation**: Combines probabilities using mean, median, and max aggregation
4. **Metadata Analysis**: Analyzes video titles, descriptions, and filenames for AI tool keywords
5. **Temporal Smoothing**: Reduces noise across frames using exponential weighted moving average
6. **Bias Adjustment**: Applies metadata bias to final probability calculation

### Detection Logic

The system follows the specified logic:

1. Extract all faces per frame (up to N frames or faces for efficiency)
2. Run each face through the visual deepfake model to get per-face probability
3. Smooth probabilities over time (median filter or moving average)
4. Compute mean probability across faces (mean_prob)
5. Compute metadata bias score based on AI tool keywords in title, description, etc.
6. Combine final probability: `final_prob = clip(mean_prob + metadata_bias, 0, 1)`
7. Classify:
   - **Authentic / Real**: `final_prob <= 0.45` → color="green"
   - **Borderline / Review**: `0.45 < final_prob < 0.55` → color="orange"
   - **Deepfake Detected**: `final_prob >= 0.55` → color="red"

### API Endpoints

#### 1. Upload Video Detection
```http
POST /detect/ai-video
Content-Type: multipart/form-data

video_file: [video file]
```

**Response:**
```json
{
  "video_id": "uuid",
  "message": "AI video detection started",
  "status": "processing",
  "features": {
    "multi_stage_pipeline": true,
    "face_extraction": true,
    "cnn_transformer_hybrid": true,
    "frame_aggregation": true,
    "metadata_analysis": true,
    "temporal_smoothing": true,
    "bias_adjustment": true
  }
}
```

#### 2. YouTube Video Detection
```http
POST /detect/ai-video-youtube
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "video_id": "uuid",
  "message": "AI video detection for YouTube started",
  "status": "processing",
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "features": {
    "multi_stage_pipeline": true,
    "youtube_download": true,
    "face_extraction": true,
    "cnn_transformer_hybrid": true,
    "frame_aggregation": true,
    "metadata_analysis": true,
    "temporal_smoothing": true,
    "bias_adjustment": true
  }
}
```

#### 3. Check Detection Status
```http
GET /detection-status/{video_id}
```

**Response:**
```json
{
  "video_id": "uuid",
  "status": "completed",
  "message": "AI video detection completed successfully",
  "progress_percentage": 100,
  "result": {
    "label": "Deepfake Detected",
    "confidence": 68.27,
    "color": "red",
    "metadata_bias": 0.15,
    "mean_probability": 0.53,
    "temporal_smoothed": true,
    "processing_time": 2500.5,
    "frames_analyzed": 25,
    "faces_detected": 45,
    "model_agreement": true,
    "method": "ai_video_detector",
    "features": {
      "multi_stage_pipeline": true,
      "face_extraction": true,
      "cnn_transformer_hybrid": true,
      "frame_aggregation": true,
      "metadata_analysis": true,
      "temporal_smoothing": true,
      "bias_adjustment": true
    }
  }
}
```

## Architecture

### Core Components

1. **AIVideoDetector**: Main detection service class
2. **TemporalSmoother**: Handles temporal smoothing across frames
3. **DetectionResult**: Structured result data class
4. **MetadataClassifier**: Analyzes metadata for AI tool keywords

### Dependencies

- **Face Detection**: Deterministic face detection using YOLOv8
- **Deep Learning Models**: EfficientNet-B0, MesoNet, and other ensemble models
- **Video Processing**: OpenCV for video frame extraction
- **YouTube Integration**: yt-dlp for YouTube video downloading
- **Metadata Analysis**: Custom keyword-based classifier

### Configuration

The system uses configurable thresholds:

```python
thresholds = {
    "authentic_threshold": 0.45,  # <= 0.45 = Authentic
    "uncertain_min": 0.45,       # 0.45 < x < 0.55 = Uncertain
    "uncertain_max": 0.55,       # 0.45 < x < 0.55 = Uncertain
    "deepfake_threshold": 0.55,  # >= 0.55 = Deepfake
    "max_frames": 30,            # Maximum frames to analyze
    "max_faces_per_frame": 5     # Maximum faces per frame
}
```

## Usage

### Python API

```python
from backend.app.services.ai_video_detector import detect_video_ai, detect_youtube_ai

# Detect uploaded video
result = await detect_video_ai("path/to/video.mp4", filename="video.mp4")

# Detect YouTube video
result = await detect_youtube_ai("https://www.youtube.com/watch?v=...")

print(f"Label: {result.label}")
print(f"Confidence: {result.confidence:.2f}%")
print(f"Color: {result.color}")
```

### HTTP API

```bash
# Upload video
curl -X POST "http://localhost:8000/detect/ai-video" \
  -F "video_file=@video.mp4"

# YouTube detection
curl -X POST "http://localhost:8000/detect/ai-video-youtube" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=..."}'

# Check status
curl "http://localhost:8000/detection-status/{video_id}"
```

## Performance

### Optimization Features

- **Frame Sampling**: Processes up to 30 frames per video for efficiency
- **Face Limiting**: Limits to 5 faces per frame to prevent overload
- **Batch Processing**: Processes faces in batches for better GPU utilization
- **Temporal Smoothing**: Reduces noise and improves stability
- **Model Caching**: Caches loaded models for faster subsequent detections

### Expected Performance

- **Processing Time**: 2-5 seconds per video (depending on length and complexity)
- **Accuracy**: High accuracy with low false positives on real videos
- **Scalability**: Handles multiple concurrent detections
- **Memory Usage**: Optimized for efficient memory usage

## Error Handling

The system includes comprehensive error handling:

- **Graceful Degradation**: Falls back to available models if some fail
- **Input Validation**: Validates video files and YouTube URLs
- **Resource Cleanup**: Automatically cleans up temporary files
- **Detailed Logging**: Comprehensive logging for debugging

## Testing

Run the test script to verify the system:

```bash
python test_ai_video_detector.py
```

This will test:
- Detector initialization
- Video processing pipeline
- YouTube integration
- API endpoints
- Error handling

## Requirements

- Python 3.8+
- PyTorch with CUDA support (recommended)
- OpenCV
- yt-dlp (for YouTube support)
- All dependencies from requirements.txt

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python backend/app/main.py
```

3. The API will be available at `http://localhost:8000`

## Frontend Integration

The detection results are designed to be compatible with the frontend cursor prompt format:

```json
{
  "label": "Deepfake Detected",
  "confidence": 68.27,
  "color": "red"
}
```

This matches the expected format for the frontend display system.

## Monitoring

The system provides comprehensive statistics:

- Videos processed
- Total processing time
- Frames processed
- Faces detected
- Temporal corrections applied
- Model usage statistics

Access statistics via the detector's `get_stats()` method or through the API endpoints.

## Future Enhancements

- Real-time video streaming detection
- Additional model architectures
- Enhanced metadata analysis
- Performance optimizations
- Advanced temporal analysis
- Custom model training capabilities
