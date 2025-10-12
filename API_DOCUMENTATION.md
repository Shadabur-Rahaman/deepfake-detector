# 📚 API Documentation

Complete API reference for the Deepfake Detection System backend.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 📖 Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔐 Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Token Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "standard"
  }
}
```

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password",
  "full_name": "John Doe"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🎯 Detection Endpoints

### File Upload Detection

#### Traditional Mode
```http
POST /api/detect-deepfake-upload-mode
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: <image/video file>
- detection_mode: "traditional"
```

#### Modern AI Mode
```http
POST /api/detect-deepfake-upload-mode
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: <image/video file>
- detection_mode: "modern-ai"
```

#### Hybrid Mode
```http
POST /api/detect-deepfake-upload-mode
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: <image/video file>
- detection_mode: "hybrid"
```

**Response:**
```json
{
  "video_id": "uuid-string",
  "status": "processing",
  "message": "Detection started"
}
```

### YouTube URL Detection

```http
POST /api/detect-deepfake-youtube
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "detection_mode": "hybrid"
}
```

**Response:**
```json
{
  "video_id": "uuid-string",
  "status": "processing",
  "message": "YouTube video detection started"
}
```

### Detection Status

```http
GET /api/detection-status/{video_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "video_id": "uuid-string",
  "status": "completed",
  "progress_percentage": 100,
  "result": "deepfake",
  "confidence": 87.5,
  "analysis_details": {
    "faces_detected": 1,
    "frames_processed": 120,
    "models_used": ["efficientnet", "mesonet", "yolov8"],
    "processing_time": 45.2
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔄 Real-time WebSocket

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/detect');

// Send detection request
ws.send(JSON.stringify({
  type: 'detection',
  data: 'base64-encoded-image-data',
  mode: 'hybrid'
}));

// Receive real-time updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Detection result:', data);
};
```

### WebSocket Message Types

#### Detection Request
```json
{
  "type": "detection",
  "data": "base64-encoded-image",
  "mode": "hybrid"
}
```

#### Detection Response
```json
{
  "type": "result",
  "data": {
    "result": "authentic",
    "confidence": 92.3,
    "analysis": {
      "face_quality": 0.95,
      "temporal_consistency": 0.88,
      "frequency_analysis": 0.91
    }
  }
}
```

## 📊 System Status

### Startup Status
```http
GET /api/startup/status
```

**Response:**
```json
{
  "status": "ready",
  "models_loaded": 25,
  "gpu_available": false,
  "cpu_mode": true,
  "uptime": 3600,
  "memory_usage": "2.1GB"
}
```

### System Health
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "models": "loaded",
  "gpu": "unavailable",
  "cpu_usage": "45%",
  "memory_usage": "2.1GB / 8GB"
}
```

## 👥 User Management

### Get User Profile
```http
GET /api/users/me
Authorization: Bearer <token>
```

### Update User Profile
```http
PUT /api/users/me
Content-Type: application/json
Authorization: Bearer <token>

{
  "full_name": "John Doe",
  "email": "john.doe@example.com"
}
```

### Get Detection History
```http
GET /api/users/detections
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: Number of results (default: 50)
- `offset`: Offset for pagination (default: 0)
- `status`: Filter by status (`completed`, `processing`, `failed`)

## 🔧 Admin Endpoints

### System Statistics
```http
GET /api/admin/stats
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "total_detections": 15420,
  "successful_detections": 14890,
  "failed_detections": 530,
  "unique_users": 1250,
  "models_performance": {
    "efficientnet": 94.2,
    "mesonet": 91.8,
    "yolov8": 89.5
  }
}
```

### User Management
```http
GET /api/admin/users
Authorization: Bearer <admin-token>
```

### Model Management
```http
GET /api/admin/models
Authorization: Bearer <admin-token>
```

## 📁 File Management

### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: <file>
```

### Get File Info
```http
GET /api/files/{file_id}
Authorization: Bearer <token>
```

### Delete File
```http
DELETE /api/files/{file_id}
Authorization: Bearer <token>
```

## 🔍 Detection Modes

### Traditional Mode
- **Description**: Fast processing with trained models
- **Best for**: Classic deepfakes, face swaps
- **Models**: EfficientNet, MesoNet, YOLOv8
- **Speed**: 0.5-2 seconds per image

### Modern AI Mode
- **Description**: Advanced generative AI integration
- **Best for**: Modern AI tools (VEO, SORA, Runway)
- **Models**: GPT-4 Vision, Gemini Pro, Vision Transformers
- **Speed**: 2-5 seconds per image

### Hybrid Mode
- **Description**: Combines all detection methods
- **Best for**: Maximum accuracy and coverage
- **Models**: All 25+ models
- **Speed**: 3-8 seconds per image

## 📈 Response Formats

### Detection Result
```json
{
  "video_id": "uuid-string",
  "status": "completed",
  "result": "deepfake|authentic|borderline",
  "confidence": 87.5,
  "faces_detected": 1,
  "faces_found": 1,
  "analysis_method": "Hybrid Multi-Modal Detection",
  "processing_stages": [
    {
      "stage": "Face Detection",
      "status": "completed",
      "duration": 0.5,
      "details": "1 face detected"
    },
    {
      "stage": "Model Analysis",
      "status": "completed",
      "duration": 3.2,
      "details": "25 models processed",
      "models": [
        {
          "name": "EfficientNet",
          "confidence": 0.89,
          "result": "deepfake"
        }
      ]
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "Validation failed",
  "detail": "File size exceeds maximum limit",
  "code": "FILE_TOO_LARGE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚨 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_TOKEN` | 401 | JWT token is invalid or expired |
| `INSUFFICIENT_PERMISSIONS` | 403 | User doesn't have required permissions |
| `FILE_TOO_LARGE` | 413 | Uploaded file exceeds size limit |
| `UNSUPPORTED_FORMAT` | 415 | File format not supported |
| `DETECTION_FAILED` | 500 | Detection process failed |
| `MODEL_UNAVAILABLE` | 503 | Required AI model is not available |

## 🔒 Rate Limiting

- **Standard Users**: 10 requests per minute
- **Premium Users**: 50 requests per minute
- **Admin Users**: 100 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1642248600
```

## 📝 Request/Response Examples

### Complete Detection Flow

1. **Upload File**
```bash
curl -X POST "http://localhost:8000/api/detect-deepfake-upload-mode" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_video.mp4" \
  -F "detection_mode=hybrid"
```

2. **Check Status**
```bash
curl -X GET "http://localhost:8000/api/detection-status/video-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Get Results**
```json
{
  "video_id": "video-id",
  "status": "completed",
  "result": "deepfake",
  "confidence": 87.5,
  "analysis_details": {
    "faces_detected": 1,
    "frames_processed": 120,
    "models_used": ["efficientnet", "mesonet", "yolov8"],
    "processing_time": 45.2
  }
}
```

## 🔧 SDK Examples

### Python
```python
import requests

# Set up client
base_url = "http://localhost:8000"
token = "your-jwt-token"
headers = {"Authorization": f"Bearer {token}"}

# Upload file for detection
with open("test_video.mp4", "rb") as f:
    files = {"file": f}
    data = {"detection_mode": "hybrid"}
    response = requests.post(
        f"{base_url}/api/detect-deepfake-upload-mode",
        headers=headers,
        files=files,
        data=data
    )

video_id = response.json()["video_id"]

# Check status
status_response = requests.get(
    f"{base_url}/api/detection-status/{video_id}",
    headers=headers
)

print(status_response.json())
```

### JavaScript
```javascript
const baseUrl = 'http://localhost:8000';
const token = 'your-jwt-token';

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('detection_mode', 'hybrid');

const response = await fetch(`${baseUrl}/api/detect-deepfake-upload-mode`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const { video_id } = await response.json();

// Poll for results
const checkStatus = async () => {
  const statusResponse = await fetch(`${baseUrl}/api/detection-status/${video_id}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return statusResponse.json();
};
```

## 📞 Support

For API support and questions:

- **GitHub Issues**: [Report API issues](https://github.com/YOUR_USERNAME/deepfake-detector/issues)
- **Documentation**: [API Documentation](http://localhost:8000/docs)
- **Email**: api-support@deepfake-detector.com
