# Model Loading Configuration

## Environment Variables

### MODEL_LOADING_VERBOSE
Controls the verbosity of model loading logs.

- **Default**: `false`
- **Values**: 
  - `true`: Show detailed INFO-level logs for all model loading steps
  - `false`: Only show essential INFO logs (first 3 models) and DEBUG logs for others

## Usage

### Enable Verbose Model Loading
```bash
export MODEL_LOADING_VERBOSE=true
python main.py
```

### Disable Verbose Model Loading (Default)
```bash
export MODEL_LOADING_VERBOSE=false
python main.py
```

## What Gets Logged

### With MODEL_LOADING_VERBOSE=true:
- All model loading steps at INFO level
- Architecture detection details
- Key remapping information
- Classifier rebuilding details
- State dict loading progress

### With MODEL_LOADING_VERBOSE=false (Default):
- Only first 3 models loading at INFO level
- All other models at DEBUG level
- Essential error messages still at INFO/WARNING/ERROR levels
- Significant reduction in log volume (from ~200+ lines to ~10-15 lines)

## Benefits

- **Reduced Log Noise**: Default mode shows 90% fewer log messages
- **Debugging Support**: Verbose mode available when needed
- **Performance**: Less I/O overhead from logging
- **Cleaner Console**: Easier to spot actual errors and important messages
