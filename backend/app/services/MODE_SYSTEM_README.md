# Deepfake Detection Mode System

## Overview

The Deepfake Detection Mode System provides a production-grade, maintainable architecture for dynamic switching between different inference modes. This system allows users to select between traditional and modern AI detection methods, with automatic fallbacks and comprehensive error handling.

## Architecture

### Core Components

1. **ModeRegistry** (`mode_registry.py`) - Centralized management of available detection modes
2. **ModelLoader** (`model_loader.py`) - Dynamic model loading based on selected mode
3. **ModeFactory** (`mode_factory.py`) - Factory pattern for creating detection mode instances
4. **EnhancedModeDetector** (`enhanced_mode_detector.py`) - High-level service interface

### Design Patterns

- **Registry Pattern**: Centralized mode management
- **Factory Pattern**: Clean instantiation of detection modes
- **Singleton Pattern**: Global service instances
- **Strategy Pattern**: Different detection algorithms per mode

## Available Modes

### 1. Traditional Mode (`traditional`)
- **Model**: EfficientNet-B0 Fine-tuned
- **Accuracy**: 94.1%
- **Processing Time**: ~1.2 seconds
- **Memory Usage**: 45 MB
- **Use Case**: Proven reliability, faster processing

### 2. Modern AI Mode (`modern_ai`)
- **Model**: Advanced AI Model
- **Accuracy**: 96.5%
- **Processing Time**: ~1.5 seconds
- **Memory Usage**: 65 MB
- **Use Case**: Highest accuracy, advanced features

### 3. Auto Mode (`auto`)
- **Behavior**: Automatically selects best mode
- **Logic**: Prefers modern AI if available, falls back to traditional
- **Use Case**: Optimal performance without manual selection

## API Endpoints

### Detection Endpoints

#### `POST /detect-enhanced`
Enhanced detection with mode selection support.

**Parameters:**
- `file`: Video file (multipart/form-data)
- `mode`: Detection mode (`traditional`, `modern_ai`, or `auto`)

**Response:**
```json
{
  "video_id": "uuid",
  "message": "Enhanced detection completed",
  "result": {
    "detection_id": "uuid",
    "status": "completed",
    "prediction": "Real" | "Fake",
    "confidence": 0.95,
    "processing_time": 1.2,
    "model_used": "EfficientNet-B0 Fine-tuned",
    "mode_used": "traditional",
    "faces_detected": 3
  },
  "filename": "video.mp4"
}
```

### Mode Management Endpoints

#### `GET /modes`
Get information about available detection modes.

**Response:**
```json
{
  "status": "success",
  "modes": {
    "available_modes": ["traditional", "modern_ai"],
    "mode_details": {
      "traditional": {
        "mode_id": "traditional",
        "display_name": "Traditional Detection",
        "description": "Classical deepfake detection using fine-tuned EfficientNet-B0 model",
        "enabled": true,
        "primary_model": {
          "name": "EfficientNet-B0 Fine-tuned",
          "accuracy": 94.1,
          "processing_time_ms": 1200,
          "memory_usage_mb": 45
        }
      }
    }
  }
}
```

#### `GET /modes/status`
Get comprehensive status of all detection modes.

#### `POST /modes/preload`
Preload a specific detection mode for faster subsequent detection.

#### `DELETE /modes/{mode}`
Cleanup a specific detection mode to free resources.

## Usage Examples

### Python Client

```python
import requests

# Upload video with mode selection
files = {'file': open('video.mp4', 'rb')}
data = {'mode': 'modern_ai'}  # or 'traditional' or 'auto'

response = requests.post('http://localhost:8000/detect-enhanced', 
                        files=files, data=data)
result = response.json()

print(f"Prediction: {result['result']['prediction']}")
print(f"Confidence: {result['result']['confidence']}")
print(f"Mode Used: {result['result']['mode_used']}")
```

### JavaScript/TypeScript Client

```typescript
const formData = new FormData();
formData.append('file', videoFile);
formData.append('mode', 'modern_ai');

const response = await fetch('/detect-enhanced', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Detection result:', result.result);
```

### cURL

```bash
# Traditional mode
curl -X POST "http://localhost:8000/detect-enhanced" \
  -F "file=@video.mp4" \
  -F "mode=traditional"

# Modern AI mode
curl -X POST "http://localhost:8000/detect-enhanced" \
  -F "file=@video.mp4" \
  -F "mode=modern_ai"

# Auto mode (default)
curl -X POST "http://localhost:8000/detect-enhanced" \
  -F "file=@video.mp4"
```

## Frontend Integration

The frontend includes a mode selection interface in the TryIt component:

```tsx
// Mode selection state
const [selectedMode, setSelectedMode] = useState<string>('auto');

// Mode selection UI
<div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
  <button onClick={() => setSelectedMode('auto')}>
    Auto Select
  </button>
  <button onClick={() => setSelectedMode('traditional')}>
    Traditional
  </button>
  <button onClick={() => setSelectedMode('modern_ai')}>
    Modern AI
  </button>
</div>
```

## Error Handling

The system provides comprehensive error handling:

### Invalid Mode
```json
{
  "detail": "Invalid mode 'invalid_mode'. Available modes: traditional, modern_ai, modern, ai_generated, latest"
}
```

### Model Loading Failure
```json
{
  "status": "failed",
  "prediction": "Error",
  "error": "Model loading failed: deepfake_detector_latest.pth not found"
}
```

### Graceful Fallbacks
- If modern AI mode fails, automatically falls back to traditional mode
- If all models fail, creates a basic fallback model
- Comprehensive logging for debugging

## Extending the System

### Adding a New Mode

1. **Update ModeRegistry**:
```python
# Add new mode to DetectionMode enum
class DetectionMode(Enum):
    TRADITIONAL = "traditional"
    MODERN_AI = "modern_ai"
    CUSTOM_MODE = "custom_mode"  # New mode

# Add configuration
custom_config = ModeConfig(
    mode_id=DetectionMode.CUSTOM_MODE,
    display_name="Custom Detection",
    description="Custom detection mode",
    primary_model=ModelConfig(...),
    fallback_models=[],
    enabled=True,
    priority=3
)
```

2. **Create Mode Class**:
```python
class CustomDetectionMode(BaseDetectionMode):
    def __init__(self, mode_config: ModeConfig, model: Any):
        super().__init__(mode_config, model)
        self.model_name = "Custom Model"
    
    async def detect(self, input_data: Any, **kwargs) -> DetectionResult:
        # Implement custom detection logic
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        # Return model information
        pass
```

3. **Register in ModeFactory**:
```python
self._mode_classes: Dict[DetectionMode, Type[BaseDetectionMode]] = {
    DetectionMode.TRADITIONAL: TraditionalDetectionMode,
    DetectionMode.MODERN_AI: ModernAIDetectionMode,
    DetectionMode.CUSTOM_MODE: CustomDetectionMode  # Add new mode
}
```

### Adding a New Model Type

1. **Update ModelType enum**:
```python
class ModelType(Enum):
    EFFICIENTNET_B0 = "efficientnet_b0"
    MESONET = "mesonet"
    CUSTOM = "custom"
    NEW_MODEL_TYPE = "new_model_type"  # Add new type
```

2. **Implement loading method**:
```python
def _load_new_model_type(self, model_path: str, mode_config: ModeConfig) -> ModelLoadResult:
    # Implement model loading logic
    pass
```

3. **Update model creation logic**:
```python
def _create_model_from_checkpoint(self, state_dict: Dict[str, Any]) -> Optional[nn.Module]:
    # Add detection logic for new model type
    if any('new_model' in key.lower() for key in state_dict.keys()):
        return self._create_new_model()
    # ... existing logic
```

## Performance Considerations

### Memory Management
- Models are loaded on-demand (lazy loading)
- Automatic cleanup of unused modes
- Memory usage monitoring and reporting

### Caching
- Detection results are cached for 5 minutes
- Cache key includes video hash and mode
- Configurable cache TTL

### Optimization
- Model preloading for faster subsequent detection
- Background task processing
- Efficient model switching

## Monitoring and Logging

### Logging Levels
- **INFO**: Normal operations, mode switching
- **WARNING**: Fallbacks, missing models
- **ERROR**: Detection failures, model loading errors

### Key Metrics
- Detection accuracy per mode
- Processing time per mode
- Memory usage per mode
- Error rates and fallback frequency

### Health Checks
- Mode availability status
- Model loading status
- Resource usage monitoring

## Security Considerations

### Input Validation
- File type validation
- File size limits (100MB)
- Mode parameter validation

### Error Information
- Sanitized error messages
- No sensitive information in logs
- Graceful error handling

### Resource Limits
- Memory usage monitoring
- Processing time limits
- Concurrent request limits

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Check model file paths
   - Verify model file integrity
   - Check available disk space

2. **Mode Selection Issues**
   - Verify mode is enabled in registry
   - Check mode configuration
   - Review error logs

3. **Performance Issues**
   - Monitor memory usage
   - Check model preloading
   - Review cache statistics

### Debug Commands

```bash
# Check available modes
curl http://localhost:8000/modes

# Check mode status
curl http://localhost:8000/modes/status

# Preload specific mode
curl -X POST http://localhost:8000/modes/preload -d "mode=traditional"

# Cleanup mode
curl -X DELETE http://localhost:8000/modes/traditional
```

## Future Enhancements

### Planned Features
- Dynamic model updates without restart
- A/B testing framework for modes
- Performance analytics dashboard
- Custom model upload interface

### Scalability Improvements
- Distributed model loading
- Load balancing across modes
- Horizontal scaling support

### Advanced Features
- Real-time mode switching
- Adaptive mode selection based on content
- Multi-modal detection (video + audio)
- Ensemble mode combining multiple models

## Contributing

When contributing to the mode system:

1. Follow the existing architecture patterns
2. Add comprehensive error handling
3. Include unit tests for new functionality
4. Update documentation
5. Add logging for debugging
6. Consider performance implications

## License

This mode system is part of the iFake Deepfake Detection System and follows the same licensing terms.
