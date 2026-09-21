# External AI API Integration Guide

## Overview

The deepfake detection system supports integration with external AI APIs for enhanced detection capabilities. These APIs provide additional visual analysis and cross-validation but are **completely optional**. The system works perfectly without them using local models only.

## Supported APIs

### 1. OpenAI GPT-4 Vision
- **Purpose**: Advanced visual analysis using GPT-4 Vision
- **Cost**: ~$0.01-0.10 per image analysis
- **Rate Limit**: 500 requests/minute
- **Get API Key**: https://platform.openai.com/api-keys

### 2. Claude 3.5 Sonnet (Anthropic)
- **Purpose**: High-quality visual analysis and reasoning
- **Cost**: ~$0.005-0.05 per image analysis
- **Rate Limit**: 100 requests/minute
- **Get API Key**: https://console.anthropic.com/

### 3. Gemini 2.0 Flash (Google)
- **Purpose**: Fast and efficient visual analysis
- **Cost**: ~$0.001-0.01 per image analysis
- **Rate Limit**: 1000 requests/minute
- **Get API Key**: https://makersuite.google.com/app/apikey

## Configuration

### Environment Variables

Add these to your `config.env` file:

```bash
# Enable/disable external AI APIs (default: false)
ENABLE_EXTERNAL_AI_APIS=false

# Individual API enable flags
ENABLE_OPENAI_API=false
ENABLE_CLAUDE_API=false
ENABLE_GEMINI_API=false

# API Keys (only needed if you enable the APIs)
OPENAI_API_KEY=your-openai-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### Usage Examples

#### Enable All APIs
```bash
ENABLE_EXTERNAL_AI_APIS=true
ENABLE_OPENAI_API=true
ENABLE_CLAUDE_API=true
ENABLE_GEMINI_API=true
```

#### Enable Only OpenAI
```bash
ENABLE_EXTERNAL_AI_APIS=true
ENABLE_OPENAI_API=true
ENABLE_CLAUDE_API=false
ENABLE_GEMINI_API=false
```

#### Disable All APIs (Default)
```bash
ENABLE_EXTERNAL_AI_APIS=false
```

## How It Works

### With APIs Enabled
1. Local models perform initial detection
2. External APIs provide additional analysis
3. Results are combined using ensemble methods
4. Higher confidence and accuracy

### Without APIs (Default)
1. Local models perform detection
2. Multiple local models provide ensemble results
3. Still very effective for most use cases
4. No external costs or dependencies

## API Response Format

Each API returns structured analysis:

```json
{
  "model": "GPT-4 Vision",
  "is_deepfake": false,
  "confidence": 0.85,
  "reason": "No signs of AI generation detected. Natural facial features and lighting.",
  "analysis_details": {
    "facial_consistency": "high",
    "lighting_analysis": "natural",
    "artifact_detection": "none"
  }
}
```

## Cost Management

### Recommended Settings

**For Development/Testing:**
```bash
ENABLE_EXTERNAL_AI_APIS=false
```

**For Production (Budget-Conscious):**
```bash
ENABLE_EXTERNAL_AI_APIS=true
ENABLE_GEMINI_API=true  # Cheapest option
ENABLE_OPENAI_API=false
ENABLE_CLAUDE_API=false
```

**For Production (Maximum Accuracy):**
```bash
ENABLE_EXTERNAL_AI_APIS=true
ENABLE_OPENAI_API=true
ENABLE_CLAUDE_API=true
ENABLE_GEMINI_API=true
```

### Cost Estimation

For 1000 image analyses per month:
- **No APIs**: $0 (local models only)
- **Gemini only**: ~$1-10
- **OpenAI only**: ~$10-100
- **Claude only**: ~$5-50
- **All APIs**: ~$16-160

## Fallback Behavior

### When APIs Are Disabled
- System uses local models only
- No external API calls made
- No additional costs
- Still provides good detection accuracy

### When APIs Fail
- Automatic fallback to local models
- Error logged but processing continues
- No interruption to detection pipeline
- Graceful degradation

### When API Keys Are Invalid
- APIs are automatically disabled
- Warning logged
- System continues with local models
- No crashes or errors

## Monitoring and Logging

### API Status in Health Check
```bash
GET /api/health
```

Response includes API status:
```json
{
  "status": "healthy",
  "apis": {
    "openai": {"enabled": true, "status": "available"},
    "claude": {"enabled": false, "status": "disabled"},
    "gemini": {"enabled": true, "status": "available"}
  }
}
```

### Logging
- API calls are logged with timing and success/failure
- Cost tracking available in logs
- Rate limit warnings logged
- Fallback behavior logged

## Best Practices

### 1. Start Without APIs
- Test the system with local models first
- Verify it meets your accuracy requirements
- Only enable APIs if you need higher accuracy

### 2. Enable Gradually
- Start with one API (recommend Gemini for cost-effectiveness)
- Monitor costs and accuracy improvements
- Add more APIs if needed

### 3. Monitor Usage
- Check logs regularly for API usage
- Set up cost alerts if using cloud providers
- Monitor rate limits

### 4. Cache Results
- The system caches API responses to reduce costs
- Identical images won't trigger new API calls
- Cache duration: 24 hours

## Troubleshooting

### Common Issues

**"API key not found"**
- Check that the API key is correctly set in config.env
- Verify the key is valid and has sufficient credits

**"Rate limit exceeded"**
- Reduce concurrent requests
- Enable only necessary APIs
- Consider upgrading API plan

**"API timeout"**
- Check internet connection
- APIs have 30-second timeout
- System will fallback to local models

**"High costs"**
- Disable unused APIs
- Reduce image analysis frequency
- Use caching effectively

### Getting Help

1. Check the logs for detailed error messages
2. Verify API keys and quotas
3. Test with a single API first
4. Contact support if issues persist

## Security Considerations

- API keys are stored in environment variables
- Never commit API keys to version control
- Use different keys for development and production
- Monitor API usage for unusual activity
- Rotate API keys regularly

## Conclusion

External AI APIs provide enhanced detection capabilities but are not required for the system to function effectively. The local models provide excellent deepfake detection on their own. Enable APIs only if you need the highest possible accuracy and are willing to pay the associated costs.
