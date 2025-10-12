import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { LoadingButton } from '@/components/ui/LoadingButton'
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import { CopyButton } from '@/components/ui/CopyButton'
import { useToast } from "@/components/ui/use-toast"
import { useNavigation } from '@/contexts/NavigationContext'
import { HeroCanvas } from "@/components/three/HeroCanvas"
import { 
  Code, Copy, CheckCircle2, ExternalLink, Book, Key, 
  Zap, Shield, Globe, ArrowRight, Terminal, FileText,
  Sparkles, Clock, Users, Database, Cpu, Cloud,
  Play, Brain, Network, Layers
} from 'lucide-react';
import { Link } from 'react-router-dom';

const ApiDocs: React.FC = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('javascript');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState(0);
  const [progress, setProgress] = useState(0); // ✅ Fixed: Added missing progress state
  const { toast } = useToast();
  const { navigationState, setLastApiDocsSection } = useNavigation();

  const languages = [
    { id: 'javascript', name: 'JavaScript', icon: '🟨' },
    { id: 'python', name: 'Python', icon: '🐍' },
    { id: 'curl', name: 'cURL', icon: '📡' },
    { id: 'php', name: 'PHP', icon: '🐘' }
  ];

  const endpoints = [
    {
      method: 'POST',
      endpoint: '/detect-modern-ai-content',
      description: 'Submit media files for advanced MesoNet CNN deepfake analysis. Supports multiple formats with high-accuracy detection.',
      parameters: [
        { name: 'file', type: 'multipart/form-data', description: 'Media file (MP4, MOV, AVI, JPG, PNG) - max 100MB', required: true },
        { name: 'enhanced', type: 'boolean', description: 'Enable enhanced analysis mode for higher accuracy (optional)', required: false }
      ],
      responseTime: '15-45 seconds',
      accuracy: '94.1%'
    },
    {
      method: 'POST', 
      endpoint: '/detect-deepfake-youtube',
      description: 'Analyze YouTube videos directly by URL using our MesoNet CNN pipeline with automatic video processing.',
      parameters: [
        { name: 'url', type: 'string', description: 'Valid YouTube video URL for analysis', required: true },
        { name: 'quality', type: 'string', description: 'Video quality preference: "high", "medium", "low" (optional)', required: false }
      ],
      responseTime: '30-90 seconds',
      accuracy: '94.1%'
    },
    {
      method: 'GET',
      endpoint: '/detection-status/{job_id}', 
      description: 'Monitor real-time processing status and progress of your MesoNet CNN analysis job with detailed metrics.',
      parameters: [
        { name: 'job_id', type: 'string', description: 'Unique job identifier returned from analysis endpoints', required: true }
      ],
      responseTime: 'Instant',
      accuracy: 'N/A'
    },
    {
      method: 'WebSocket',
      endpoint: '/ws/real-time-detection',
      description: 'Real-time deepfake detection via WebSocket for live camera feeds with instant MesoNet CNN processing.',
      parameters: [
        { name: 'frame', type: 'base64', description: 'Base64 encoded video frame for real-time analysis', required: true },
        { name: 'threshold', type: 'float', description: 'Detection confidence threshold (0.0-1.0)', required: false }
      ],
      responseTime: '<200ms',
      accuracy: '92.3%'
    }
  ];

  const codeExamples = {
    javascript: `// iFake MesoNet CNN API Client
class iFakeAPIClient {
  constructor(baseURL = 'http://127.0.0.1:8000') {
    this.baseURL = baseURL;
  }

  // File Upload Analysis with Enhanced Mode
  async analyzeFile(file, enhanced = false) {
    const formData = new FormData();
    formData.append('file', file);
    if (enhanced) formData.append('enhanced', 'true');
    
    try {
      const response = await fetch(\`\${this.baseURL}/detect-modern-ai-content\`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }
      
      const { job_id } = await response.json();
      console.log('Analysis started:', job_id);
      return job_id;
    } catch (error) {
      console.error('Analysis failed:', error);
      throw error;
    }
  }

  // YouTube URL Analysis
  async analyzeYouTube(url, quality = 'medium') {
    try {
      const response = await fetch(\`\${this.baseURL}/detect-deepfake-youtube\`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, quality })
      });
      
      const { job_id } = await response.json();
      return job_id;
    } catch (error) {
      console.error('YouTube analysis failed:', error);
      throw error;
    }
  }

  // Monitor Analysis Progress
  async checkStatus(jobId) {
    const response = await fetch(\`\${this.baseURL}/detection-status/\${jobId}\`);
    return await response.json();
  }

  // Poll for Results with Auto-retry
  async waitForResults(jobId, maxAttempts = 30) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const status = await this.checkStatus(jobId);
      
      if (status.status === 'completed') {
        return status;
      } else if (status.status === 'failed') {
        throw new Error(status.error || 'Analysis failed');
      }
      
      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    throw new Error('Analysis timeout');
  }

  // Real-time WebSocket Detection
  connectRealTime(onResult, onError) {
    const ws = new WebSocket(\`ws://\${this.baseURL.replace('http', 'ws')}/ws/real-time-detection\`);
    
    ws.onopen = () => console.log('Real-time detection connected');
    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);
      onResult(result);
    };
    ws.onerror = (error) => onError(error);
    
    return ws;
  }
}

// Usage Example
const client = new iFakeAPIClient();

// Analyze a video file
const fileInput = document.getElementById('video-upload');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    try {
      const jobId = await client.analyzeFile(file, true); // Enhanced mode
      const result = await client.waitForResults(jobId);
      
      console.log('Detection Result:', result.prediction);
      console.log('Confidence:', result.confidence + '%');
      console.log('Processing Time:', result.processing_time);
    } catch (error) {
      console.error('Error:', error.message);
    }
  }
});`,

    python: `import requests
import asyncio
import websockets
import json
import base64
import time
from typing import Optional, Dict, Any

class iFakeAPIClient:
    """
    Official Python client for iFake MesoNet CNN API
    Provides comprehensive deepfake detection capabilities
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'iFake-Python-Client/1.0'
        })
    
    def analyze_file(self, file_path: str, enhanced: bool = False) -> str:
        """
        Analyze a local video/image file using MesoNet CNN
        
        Args:
            file_path: Path to the media file
            enhanced: Enable enhanced analysis mode
            
        Returns:
            job_id: Unique identifier for tracking analysis
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'enhanced': 'true'} if enhanced else {}
                
                response = self.session.post(
                    f"{self.base_url}/detect-modern-ai-content",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()['job_id']
                
        except requests.RequestException as e:
            raise Exception(f"File analysis failed: {str(e)}")
    
    def analyze_youtube(self, youtube_url: str, quality: str = "medium") -> str:
        """
        Analyze a YouTube video using MesoNet CNN
        
        Args:
            youtube_url: Valid YouTube video URL
            quality: Video quality preference
            
        Returns:
            job_id: Unique identifier for tracking analysis
        """
        try:
            data = {'url': youtube_url, 'quality': quality}
            response = self.session.post(
                f"{self.base_url}/detect-deepfake-youtube",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()['job_id']
            
        except requests.RequestException as e:
            raise Exception(f"YouTube analysis failed: {str(e)}")
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check analysis job status and progress"""
        try:
            response = self.session.get(f"{self.base_url}/detection-status/{job_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Status check failed: {str(e)}")
    
    def wait_for_results(self, job_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Wait for analysis completion with automatic polling
        
        Args:
            job_id: Job identifier
            max_wait: Maximum wait time in seconds
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_status(job_id)
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(status.get('error', 'Analysis failed'))
            
            print(f"Progress: {status.get('progress', 0)}%")
            time.sleep(2)
        
        raise Exception("Analysis timeout - consider increasing max_wait")
    
    async def real_time_detection(self, frame_data: bytes, threshold: float = 0.5):
        """
        Real-time detection via WebSocket connection
        
        Args:
            frame_data: Raw image/frame data
            threshold: Detection confidence threshold
        """
        uri = f"ws://{self.base_url.replace('http://', '')}/ws/real-time-detection"
        
        try:
            async with websockets.connect(uri) as websocket:
                frame_b64 = base64.b64encode(frame_data).decode()
                payload = {
                    "frame": frame_b64,
                    "threshold": threshold
                }
                
                await websocket.send(json.dumps(payload))
                result = await websocket.recv()
                return json.loads(result)
                
        except Exception as e:
            raise Exception(f"Real-time detection failed: {str(e)}")

# Usage Examples
def main():
    # Initialize client
    client = iFakeAPIClient()
    
    # Example 1: Analyze video file
    try:
        print("Starting video analysis...")
        job_id = client.analyze_file("test_video.mp4", enhanced=True)
        print(f"Job ID: {job_id}")
        
        # Wait for results
        results = client.wait_for_results(job_id)
        
        print("\\n=== ANALYSIS RESULTS ===")
        print(f"Verdict: {results['prediction']}")
        print(f"Confidence: {results['confidence']:.1f}%")
        print(f"Processing Time: {results['processing_time']}")
        print(f"Faces Detected: {results.get('faces_detected', 0)}")
        print(f"Model Used: {results.get('detection_method', 'MesoNet CNN')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()`,

    curl: `#!/bin/bash

# iFake MesoNet CNN API - cURL Examples
BASE_URL="http://127.0.0.1:8000"

echo "=== iFake API Testing with cURL ==="

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "Warning: jq not found. Install for better JSON parsing."
        echo "Ubuntu/Debian: sudo apt-get install jq"
        echo "macOS: brew install jq"
    fi
}

# Function to wait for job completion
wait_for_completion() {
    local job_id=$1
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for job $job_id to complete..."
    
    while [ $attempt -lt $max_attempts ]; do
        response=$(curl -s "$BASE_URL/detection-status/$job_id")
        status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
        
        case $status in
            "completed")
                echo "✅ Analysis completed!"
                echo "$response" | jq '.' 2>/dev/null || echo "$response"
                return 0
                ;;
            "failed")
                echo "❌ Analysis failed!"
                echo "$response" | jq '.error' 2>/dev/null || echo "$response"
                return 1
                ;;
            "processing")
                progress=$(echo "$response" | jq -r '.progress' 2>/dev/null || echo "0")
                echo "⏳ Processing... \${progress}%"
                ;;
            *)
                echo "⏳ Status: $status"
                ;;
        esac
        
        sleep 2
        ((attempt++))
    done
    
    echo "⏰ Timeout waiting for completion"
    return 1
}

check_jq

# Example 1: Analyze video file with enhanced mode
echo "\\n1. Analyzing video file..."
if [ -f "test_video.mp4" ]; then
    response=$(curl -s -X POST "$BASE_URL/detect-modern-ai-content" \\
        -F "file=@test_video.mp4" \\
        -F "enhanced=true")
    
    job_id=$(echo "$response" | jq -r '.job_id' 2>/dev/null)
    
    if [ "$job_id" != "null" ] && [ -n "$job_id" ]; then
        echo "📤 Upload successful! Job ID: $job_id"
        wait_for_completion "$job_id"
    else
        echo "❌ Upload failed:"
        echo "$response"
    fi
else
    echo "⚠️  test_video.mp4 not found. Skipping file upload test."
fi

# Example 2: Analyze YouTube URL
echo "\\n2. Analyzing YouTube URL..."
response=$(curl -s -X POST "$BASE_URL/detect-deepfake-youtube" \\
    -H "Content-Type: application/json" \\
    -d '{
        "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "quality": "medium"
    }')

job_id=$(echo "$response" | jq -r '.job_id' 2>/dev/null)

if [ "$job_id" != "null" ] && [ -n "$job_id" ]; then
    echo "🎥 YouTube analysis started! Job ID: $job_id"
    wait_for_completion "$job_id"
else
    echo "❌ YouTube analysis failed:"
    echo "$response"
fi

echo "\\n=== Testing Complete ==="`,

    php: `<?php
/**
 * iFake MesoNet CNN API - PHP Client
 * Official PHP SDK for deepfake detection
 */

class iFakeAPIClient {
    private $baseUrl;
    private $httpClient;
    
    public function __construct($baseUrl = 'http://127.0.0.1:8000') {
        $this->baseUrl = rtrim($baseUrl, '/');
    }
    
    /**
     * Analyze a local video/image file
     */
    public function analyzeFile($filePath, $enhanced = false) {
        if (!file_exists($filePath)) {
            throw new Exception("File not found: $filePath");
        }
        
        $curl = curl_init();
        
        $postData = [
            'file' => new \\CURLFile($filePath),
        ];
        
        if ($enhanced) {
            $postData['enhanced'] = 'true';
        }
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->baseUrl . '/detect-modern-ai-content',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postData,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_HTTPHEADER => [
                'User-Agent: iFake-PHP-Client/1.0'
            ]
        ]);
        
        $response = curl_exec($curl);
        $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }
        
        $data = json_decode($response, true);
        return $data['job_id'];
    }
    
    /**
     * Analyze YouTube video
     */
    public function analyzeYouTube($url, $quality = 'medium') {
        $postData = json_encode([
            'url' => $url,
            'quality' => $quality
        ]);
        
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->baseUrl . '/detect-deepfake-youtube',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postData,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'User-Agent: iFake-PHP-Client/1.0'
            ],
            CURLOPT_TIMEOUT => 30
        ]);
        
        $response = curl_exec($curl);
        $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }
        
        $data = json_decode($response, true);
        return $data['job_id'];
    }
    
    /**
     * Check analysis status
     */
    public function checkStatus($jobId) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->baseUrl . "/detection-status/$jobId",
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10
        ]);
        
        $response = curl_exec($curl);
        curl_close($curl);
        
        return json_decode($response, true);
    }
    
    /**
     * Wait for analysis completion
     */
    public function waitForResults($jobId, $maxWait = 300) {
        $startTime = time();
        
        while ((time() - $startTime) < $maxWait) {
            $status = $this->checkStatus($jobId);
            
            switch ($status['status']) {
                case 'completed':
                    return $status;
                    
                case 'failed':
                    throw new Exception($status['error'] ?? 'Analysis failed');
                    
                case 'processing':
                    echo "Progress: " . ($status['progress'] ?? 0) . "%\\n";
                    break;
            }
            
            sleep(2);
        }
        
        throw new Exception('Analysis timeout');
    }
}

// Usage Examples
try {
    $client = new iFakeAPIClient();
    
    // Example 1: Analyze video file
    echo "Starting video analysis...\\n";
    $jobId = $client->analyzeFile('test_video.mp4', true);
    echo "Job ID: $jobId\\n";
    
    $results = $client->waitForResults($jobId);
    
    echo "\\n=== ANALYSIS RESULTS ===\\n";
    echo "Verdict: " . $results['prediction'] . "\\n";
    echo "Confidence: " . $results['confidence'] . "%\\n";
    echo "Processing Time: " . $results['processing_time'] . "\\n";
    echo "Faces Detected: " . ($results['faces_detected'] ?? 0) . "\\n";
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\\n";
}
?>`
  };

  const responseExamples = {
    success: `{
  "job_id": "abc123def456",
  "status": "completed",
  "prediction": "fake",
  "confidence": 94.1,
  "processing_time": "23.4 seconds",
  "faces_detected": 1,
  "detection_method": "MesoNet CNN v2.1",
  "enhanced_analysis": true,
  "analysis_details": {
    "face_coordinates": {
      "x": 120, "y": 80,
      "width": 200, "height": 240
    },
    "manipulation_indicators": [
      "temporal_inconsistency",
      "compression_artifacts",
      "facial_warping"
    ],
    "frame_analysis": {
      "total_frames": 1847,
      "analyzed_frames": 1847,
      "suspicious_frames": 342
    }
  },
  "file_metadata": {
    "filename": "test_video.mp4",
    "file_size": "45.2MB",
    "duration": "2m 15s",
    "resolution": "1920x1080",
    "format": "mp4",
    "fps": 30,
    "bitrate": "2.1 Mbps"
  },
  "model_info": {
    "model_version": "MesoNet-CNN-v2.1",
    "training_dataset": "FaceForensics++",
    "accuracy_benchmark": "94.1%"
  },
  "timestamp": "2025-01-21T09:15:30Z",
  "processing_node": "gpu-node-01"
}`,
    processing: `{
  "job_id": "abc123def456",
  "status": "processing",
  "progress": ${progress},
  "current_stage": "mesonet_cnn_analysis",
  "stages_completed": [
    "file_validation",
    "face_detection", 
    "frame_extraction"
  ],
  "estimated_completion": "2025-01-21T09:18:00Z",
  "processing_stats": {
    "frames_processed": 1200,
    "total_frames": 1847,
    "faces_detected": 1,
    "current_fps": 45
  },
  "message": "Running MesoNet CNN analysis on extracted frames..."
}`
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCode(id);
      toast({
        title: "Code copied!",
        description: "The code has been copied to your clipboard.",
      });
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please copy the code manually.",
        variant: "destructive"
      });
    }
  };

  const pricingPlans = [
    {
      name: "Free Tier",
      price: "Free",
      period: "",
      description: "Perfect for testing and small-scale projects",
      requests: "100 analysis requests/month",
      features: [
        "MesoNet CNN detection",
        "File & YouTube URL support", 
        "Basic API access",
        "Community support",
        "48-hour processing",
        "Standard accuracy (94.1%)"
      ],
      cta: "Get Started Free",
      popular: false
    },
    {
      name: "Developer", 
      price: "$5",
      period: "/month",
      description: "Ideal for developers and growing applications",
      requests: "2,500 analysis requests/month", 
      features: [
        "Priority processing (2x faster)",
        "Real-time WebSocket API",
        "Enhanced analysis mode",
        "Advanced analytics dashboard",
        "Email support",
        "Webhook notifications",
        "99.5% uptime SLA"
      ],
      cta: "Start Developer Plan",
      popular: true
    },
    {
      name: "Enterprise",
      price: "Contact Us",
      period: "",
      description: "Custom solutions for large-scale deployments",
      requests: "Unlimited analysis requests",
      features: [
        "Custom MesoNet models",
        "On-premise deployment",
        "Dedicated account manager",
        "99.9% uptime SLA",
        "Custom integrations",
        "White-label options",
        "24/7 phone support"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  const resources = [
    {
      title: "Getting Started Guide",
      description: "Complete walkthrough for integrating iFake's MesoNet CNN API into your application",
      icon: <Book className="w-5 h-5" />,
      link: "/docs/getting-started",
      badge: "Essential",
      external: false
    },
    {
      title: "FastAPI Documentation", 
      description: "Interactive API documentation powered by FastAPI with live testing capabilities",
      icon: <Key className="w-5 h-5" />,
      link: "/docs/fastapi",
      badge: "Live",
      external: false
    },
    {
      title: "Python SDK",
      description: "Official Python client library with comprehensive examples and error handling", 
      icon: <Code className="w-5 h-5" />,
      link: "/docs/python-sdk",
      badge: "Popular",
      external: false
    },
    {
      title: "System Status",
      description: "Real-time API health monitoring and MesoNet model performance metrics dashboard",
      icon: <Globe className="w-5 h-5" />,
      link: "/status",
      badge: "Live",
      external: false
    },
    {
      title: "WebSocket Guide",
      description: "Real-time detection implementation guide with WebSocket connection examples",
      icon: <Zap className="w-5 h-5" />,
      link: "/docs/websocket",
      badge: "Advanced",
      external: false
    },
    {
      title: "Model Information",
      description: "Technical details about our MesoNet CNN architecture and training methodology",
      icon: <Cpu className="w-5 h-5" />,
      link: "/docs/model-info",
      badge: "Technical",
      external: false
    }
  ];

  const apiFeatures = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: "94.1% Accuracy",
      description: "State-of-the-art MesoNet CNN detection with industry-leading accuracy rates"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Processing",
      description: "WebSocket API for live video analysis with sub-200ms response times"
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      title: "Scalable Infrastructure",
      description: "Auto-scaling FastAPI backend handling thousands of concurrent requests"
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: "Comprehensive Analytics",
      description: "Detailed analysis reports with face detection and manipulation indicators"
    }
  ];

  // ✅ Fixed: Initialize progress on component mount
  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => (prev >= 100 ? 0 : prev + 10));
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Handle navigation state restoration
  useEffect(() => {
    if (navigationState.lastApiDocsSection) {
      // Scroll to the specific section if we have navigation state
      const element = document.getElementById(navigationState.lastApiDocsSection);
      if (element) {
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }
    } else {
      // Scroll to top if no specific section
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [navigationState.lastApiDocsSection]);

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
        {/* 3D Background */}
        <HeroCanvas className="absolute inset-0 w-full h-full" />
        
        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="secondary" className="neural-card mb-6 bg-primary/10 text-primary border-primary/20">
              <Terminal className="w-3 h-3 mr-1" />
              MesoNet CNN API
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">Developer API</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Integrate powerful MesoNet CNN deepfake detection into your applications. 
              Support for file uploads, YouTube URLs, and real-time WebSocket analysis.
            </p>

            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Link to="/try">
                <LoadingButton className="neural-button">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </LoadingButton>
              </Link>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Interactive Docs
                </a>
              </Button>
            </div>
            
            {/* Live Animation Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto mt-12"
            >
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-core mb-2">94.1%</div>
                <div className="text-sm text-muted-foreground">MesoNet Accuracy</div>
              </motion.div>
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-neural mb-2">&lt;200ms</div>
                <div className="text-sm text-muted-foreground">WebSocket Latency</div>
              </motion.div>
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-data mb-2">4</div>
                <div className="text-sm text-muted-foreground">API Endpoints</div>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      {/* Quick Start */}
      <section id="quick-start" className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Quick Start</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Get started with iFake API in minutes. Our FastAPI backend provides reliable 
              MesoNet CNN-powered deepfake detection with comprehensive documentation.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card h-full">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <Terminal className="w-5 h-5 mr-2" />
                    Local Development
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="neural-card p-4 rounded-lg">
                      <code className="text-sm neural-text">pip install ifake-api</code>
                    </div>
                    <div className="neural-card p-4 rounded-lg">
                      <code className="text-sm neural-text">npm install @ifake/api-client</code>
                    </div>
                    <p className="text-muted-foreground neural-text">
                      Install our official SDKs for Python and JavaScript to get started quickly.
                    </p>
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card h-full">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <Globe className="w-5 h-5 mr-2" />
                    Interactive Docs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4 neural-text">
                    FastAPI automatically generates interactive documentation:
                  </p>
                  <div className="space-y-2">
                    <div className="neural-card p-3 rounded-lg">
                      <code className="text-sm neural-text">http://127.0.0.1:8000/docs</code>
                    </div>
                    <div className="neural-card p-3 rounded-lg">
                      <code className="text-sm neural-text">http://127.0.0.1:8000/redoc</code>
                    </div>
                  </div>
                  <p className="text-muted-foreground mt-4 text-sm neural-text">
                    All responses follow FastAPI's JSON format with detailed error handling.
                  </p>
                </CardContent>
              </EnhancedCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Endpoints */}
      <section id="endpoints" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">API Endpoints</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Four powerful endpoints covering file analysis, YouTube processing, job tracking, and real-time detection.
            </p>
          </motion.div>
          
          <div className="space-y-6">
            {endpoints.map((endpoint, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card hover-lift">
                  <div className="flex flex-col lg:flex-row lg:items-start gap-6">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-4 mb-4">
                        <Badge variant={
                          endpoint.method === 'POST' ? 'default' : 
                          endpoint.method === 'WebSocket' ? 'secondary' : 'outline'
                        } className="neural-button">
                          {endpoint.method}
                        </Badge>
                        <code className="neural-card px-4 py-2 rounded-lg font-mono text-sm">
                          {endpoint.endpoint}
                        </code>
                        <div className="flex gap-2 ml-auto">
                          <Badge variant="outline" className="neural-card text-xs">
                            <Clock className="w-3 h-3 mr-1" />
                            {endpoint.responseTime}
                          </Badge>
                          {endpoint.accuracy !== 'N/A' && (
                            <Badge variant="outline" className="neural-card text-xs">
                              <Shield className="w-3 h-3 mr-1" />
                              {endpoint.accuracy}
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-muted-foreground mb-6 neural-text">{endpoint.description}</p>
                      
                      {endpoint.parameters.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-4 neural-text">Parameters:</h4>
                          <div className="space-y-3">
                            {endpoint.parameters.map((param, paramIndex) => (
                              <div key={paramIndex} className="flex items-start gap-4 p-3 rounded-lg neural-card bg-muted/30">
                                <code className="bg-primary/10 text-primary px-3 py-1 rounded font-medium min-w-fit text-sm">
                                  {param.name}
                                </code>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="text-muted-foreground text-sm neural-text">({param.type})</span>
                                    {param.required && (
                                      <Badge variant="outline" className="text-xs px-2 py-0 neural-card">
                                        Required
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-muted-foreground text-sm neural-text">{param.description}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section id="code-examples" className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Code Examples</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Ready-to-use code examples for your favorite programming language with complete error handling.
            </p>
          </motion.div>
          
          <EnhancedCard className="neural-card overflow-hidden">
            {/* Language Tabs */}
            <div className="flex border-b border-border overflow-x-auto">
              {languages.map((lang) => (
                <button
                  key={lang.id}
                  onClick={() => setSelectedLanguage(lang.id)}
                  className={`px-6 py-4 font-medium text-sm neural-text transition-colors whitespace-nowrap ${
                    selectedLanguage === lang.id
                      ? 'neural-button text-primary border-b-2 border-primary'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <span className="mr-2">{lang.icon}</span>
                  {lang.name}
                </button>
              ))}
            </div>

            {/* Code Block */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="absolute top-4 right-4 neural-button z-10"
                onClick={() => copyToClipboard(codeExamples[selectedLanguage as keyof typeof codeExamples], selectedLanguage)}
              >
                {copiedCode === selectedLanguage ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
              <pre className="overflow-x-auto p-6 text-sm">
                <code className="neural-text">
                  {codeExamples[selectedLanguage as keyof typeof codeExamples]}
                </code>
              </pre>
            </div>
          </EnhancedCard>
        </div>
      </section>

      {/* Response Examples */}
      <section id="response-examples" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Response Examples</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Sample responses from our MesoNet CNN analysis engine showing real detection results.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <CheckCircle2 className="w-5 h-5 mr-2 text-success" />
                    Completed Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative">
                    <CopyButton 
                      text={responseExamples.success}
                      className="absolute top-2 right-2" 
                    />
                    <pre className="overflow-x-auto text-xs neural-card p-4 rounded-lg">
                      <code className="neural-text">{responseExamples.success}</code>
                    </pre>
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <Clock className="w-5 h-5 mr-2 text-warning" />
                    Processing Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative">
                    <CopyButton 
                      text={responseExamples.processing}
                      className="absolute top-2 right-2" 
                    />
                    <pre className="overflow-x-auto text-xs neural-card p-4 rounded-lg">
                      <code className="neural-text">{responseExamples.processing}</code>
                    </pre>
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">API Pricing</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Flexible pricing plans to match your needs. All plans include MesoNet CNN detection and FastAPI reliability.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="neural-button bg-primary text-primary-foreground">
                      <Sparkles className="w-3 h-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <EnhancedCard className={`neural-card h-full hover-lift ${plan.popular ? 'ring-2 ring-primary/20' : ''}`}>
                  <CardHeader className="text-center">
                    <h3 className="font-bold text-xl neural-text">{plan.name}</h3>
                    <div className="neural-text">
                      <span className="text-3xl font-bold">{plan.price}</span>
                      <span className="text-muted-foreground">{plan.period}</span>
                    </div>
                    <p className="text-muted-foreground neural-text">{plan.description}</p>
                    <Badge variant="outline" className="neural-card">
                      {plan.requests}
                    </Badge>
                  </CardHeader>
                  
                  <CardContent>
                    <ul className="space-y-3 mb-8">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center neural-text">
                          <CheckCircle2 className="w-4 h-4 text-success mr-3 flex-shrink-0" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <Button 
                      className={`w-full neural-button ${plan.popular ? 'bg-primary hover:bg-primary/90' : ''}`}
                      variant={plan.popular ? 'default' : 'outline'}
                    >
                      {plan.cta}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </CardContent>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Resources */}
      <section id="resources" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Resources</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Everything you need to integrate MesoNet CNN deepfake detection into your application.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card hover-lift h-full">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center">
                        <div className="text-primary mr-3">{resource.icon}</div>
                        <Badge variant="outline" className="neural-card text-xs">
                          {resource.badge}
                        </Badge>
                      </div>
                    </div>
                    <CardTitle className="neural-text text-lg">{resource.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground neural-text mb-4">{resource.description}</p>
                    <Button 
                      variant="ghost" 
                      className="neural-button w-full" 
                      asChild
                      onClick={() => setLastApiDocsSection('resources')}
                    >
                      {resource.external ? (
                        <a href={resource.link} target="_blank" rel="noopener noreferrer">
                          View Resource
                          <ExternalLink className="w-4 h-4 ml-2" />
                        </a>
                      ) : (
                        <Link to={resource.link}>
                          View Resource
                          <ExternalLink className="w-4 h-4 ml-2" />
                        </Link>
                      )}
                    </Button>
                  </CardContent>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Brain className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Ready to Get Started?</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Join developers integrating iFake's MesoNet CNN API for reliable deepfake detection. 
              Start building with our FastAPI-powered backend today.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button size="lg" className="neural-button" asChild>
                <Link to="/try-it">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Interactive API Docs
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default ApiDocs;
