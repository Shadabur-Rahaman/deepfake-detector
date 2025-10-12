import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import { CopyButton } from '@/components/ui/CopyButton'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Zap, 
  Code, 
  Play, 
  CheckCircle2, 
  ArrowRight, 
  ExternalLink,
  Terminal,
  Globe,
  Shield,
  Brain,
  Database,
  Cpu,
  FileText,
  Copy,
  Clock,
  Users,
  Settings,
  AlertTriangle,
  Info,
  Wifi,
  WifiOff,
  Activity,
  Monitor,
  Camera,
  Video
} from 'lucide-react';
import { Link } from 'react-router-dom';

const WebSocketGuide: React.FC = () => {
  const [selectedExample, setSelectedExample] = useState('javascript');

  const connectionSteps = [
    {
      step: 1,
      title: "Establish Connection",
      description: "Connect to the WebSocket endpoint with your API key",
      code: `const ws = new WebSocket('wss://api.ifake.com/ws/real-time-detection?api_key=YOUR_KEY');`
    },
    {
      step: 2,
      title: "Handle Connection Events",
      description: "Set up event listeners for connection status and errors",
      code: `ws.onopen = () => console.log('Connected');
ws.onerror = (error) => console.error('Connection error:', error);
ws.onclose = () => console.log('Disconnected');`
    },
    {
      step: 3,
      title: "Send Frame Data",
      description: "Send base64-encoded video frames for real-time analysis",
      code: `const message = {
  frame: base64FrameData,
  threshold: 0.5,
  timestamp: Date.now()
};
ws.send(JSON.stringify(message));`
    },
    {
      step: 4,
      title: "Process Results",
      description: "Handle incoming detection results and update your UI",
      code: `ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Detection:', result.prediction);
  console.log('Confidence:', result.confidence);
};`
    }
  ];

  const codeExamples = {
    javascript: `// Real-time WebSocket Detection - JavaScript
class RealtimeDetector {
  constructor(apiKey, options = {}) {
    this.apiKey = apiKey;
    this.baseUrl = options.baseUrl || 'wss://api.ifake.com';
    this.ws = null;
    this.isConnected = false;
    this.callbacks = {
      onResult: options.onResult || (() => {}),
      onError: options.onError || (() => {}),
      onConnect: options.onConnect || (() => {}),
      onDisconnect: options.onDisconnect || (() => {})
    };
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = \`\${this.baseUrl}/ws/real-time-detection?api_key=\${this.apiKey}\`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.isConnected = true;
          console.log('WebSocket connected');
          this.callbacks.onConnect();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const result = JSON.parse(event.data);
            this.callbacks.onResult(result);
          } catch (error) {
            console.error('Failed to parse message:', error);
            this.callbacks.onError(error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.callbacks.onError(error);
          reject(error);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          console.log('WebSocket disconnected');
          this.callbacks.onDisconnect();
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  sendFrame(frameData, threshold = 0.5) {
    if (!this.isConnected || !this.ws) {
      throw new Error('WebSocket not connected');
    }

    const message = {
      frame: frameData, // Base64 encoded frame
      threshold: threshold,
      timestamp: Date.now()
    };

    this.ws.send(JSON.stringify(message));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  // Utility method to capture frame from video element
  captureFrameFromVideo(videoElement) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    
    ctx.drawImage(videoElement, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.8).split(',')[1]; // Remove data:image/jpeg;base64,
  }
}

// Usage Example
const detector = new RealtimeDetector('your_api_key_here', {
  onResult: (result) => {
    console.log('Detection Result:', result);
    // Update UI with result
    updateDetectionUI(result);
  },
  onError: (error) => {
    console.error('Detection Error:', error);
    showErrorMessage(error.message);
  },
  onConnect: () => {
    console.log('Ready for real-time detection');
    startCamera();
  },
  onDisconnect: () => {
    console.log('Detection stopped');
    stopCamera();
  }
});

// Connect and start detection
async function startDetection() {
  try {
    await detector.connect();
    
    // Start camera capture
    const video = document.getElementById('camera');
    const interval = setInterval(() => {
      if (detector.isConnected) {
        const frameData = detector.captureFrameFromVideo(video);
        detector.sendFrame(frameData, 0.7); // 70% confidence threshold
      } else {
        clearInterval(interval);
      }
    }, 100); // 10 FPS
    
  } catch (error) {
    console.error('Failed to start detection:', error);
  }
}

// Stop detection
function stopDetection() {
  detector.disconnect();
}`,

    python: `# Real-time WebSocket Detection - Python
import asyncio
import websockets
import json
import base64
import cv2
import numpy as np
from typing import Optional, Callable, Dict, Any

class RealtimeDetector:
    """Real-time deepfake detection using WebSocket"""
    
    def __init__(self, api_key: str, base_url: str = "wss://api.ifake.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.websocket = None
        self.is_connected = False
        self.callbacks = {}
    
    def on_result(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for detection results"""
        self.callbacks['on_result'] = callback
        return self
    
    def on_error(self, callback: Callable[[Exception], None]):
        """Set callback for errors"""
        self.callbacks['on_error'] = callback
        return self
    
    def on_connect(self, callback: Callable[[], None]):
        """Set callback for connection"""
        self.callbacks['on_connect'] = callback
        return self
    
    def on_disconnect(self, callback: Callable[[], None]):
        """Set callback for disconnection"""
        self.callbacks['on_disconnect'] = callback
        return self
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            uri = f"{self.base_url}/ws/real-time-detection?api_key={self.api_key}"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            if 'on_connect' in self.callbacks:
                self.callbacks['on_connect']()
                
            print("WebSocket connected successfully")
            
        except Exception as e:
            if 'on_error' in self.callbacks:
                self.callbacks['on_error'](e)
            raise e
    
    async def send_frame(self, frame_data: bytes, threshold: float = 0.5):
        """Send frame for real-time analysis"""
        if not self.is_connected or not self.websocket:
            raise Exception("WebSocket not connected")
        
        try:
            # Encode frame as base64
            frame_b64 = base64.b64encode(frame_data).decode()
            
            message = {
                "frame": frame_b64,
                "threshold": threshold,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.websocket.send(json.dumps(message))
            
        except Exception as e:
            if 'on_error' in self.callbacks:
                self.callbacks['on_error'](e)
            raise e
    
    async def listen_for_results(self):
        """Listen for incoming detection results"""
        try:
            async for message in self.websocket:
                try:
                    result = json.loads(message)
                    if 'on_result' in self.callbacks:
                        self.callbacks['on_result'](result)
                except json.JSONDecodeError as e:
                    if 'on_error' in self.callbacks:
                        self.callbacks['on_error'](e)
                        
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            if 'on_disconnect' in self.callbacks:
                self.callbacks['on_disconnect']()
        except Exception as e:
            if 'on_error' in self.callbacks:
                self.callbacks['on_error'](e)
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.is_connected = False
            if 'on_disconnect' in self.callbacks:
                self.callbacks['on_disconnect']()
    
    def capture_frame_from_camera(self, camera_index: int = 0) -> bytes:
        """Capture frame from camera"""
        cap = cv2.VideoCapture(camera_index)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return buffer.tobytes()
        else:
            raise Exception("Failed to capture frame from camera")

# Usage Example
async def main():
    detector = (RealtimeDetector("your_api_key_here")
                .on_result(lambda result: print(f"Detection: {result['prediction']} ({result['confidence']:.1f}%)"))
                .on_error(lambda error: print(f"Error: {error}"))
                .on_connect(lambda: print("Connected to real-time detection"))
                .on_disconnect(lambda: print("Disconnected")))
    
    try:
        # Connect to WebSocket
        await detector.connect()
        
        # Start listening for results in background
        listen_task = asyncio.create_task(detector.listen_for_results())
        
        # Capture and send frames
        for i in range(100):  # Capture 100 frames
            try:
                frame_data = detector.capture_frame_from_camera()
                await detector.send_frame(frame_data, threshold=0.7)
                await asyncio.sleep(0.1)  # 10 FPS
            except Exception as e:
                print(f"Frame capture error: {e}")
                break
        
        # Clean up
        listen_task.cancel()
        await detector.disconnect()
        
    except Exception as e:
        print(f"Detection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())`,

    react: `// Real-time WebSocket Detection - React Hook
import { useState, useEffect, useCallback, useRef } from 'react';

interface DetectionResult {
  prediction: 'real' | 'fake';
  confidence: number;
  processing_time: number;
  faces_detected: number;
  timestamp: number;
}

interface UseRealtimeDetectionOptions {
  apiKey: string;
  baseUrl?: string;
  threshold?: number;
  frameRate?: number;
  onResult?: (result: DetectionResult) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export const useRealtimeDetection = (options: UseRealtimeDetectionOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [lastResult, setLastResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const connect = useCallback(async () => {
    try {
      const wsUrl = \`\${options.baseUrl || 'wss://api.ifake.com'}/ws/real-time-detection?api_key=\${options.apiKey}\`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        options.onConnect?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const result = JSON.parse(event.data) as DetectionResult;
          setLastResult(result);
          options.onResult?.(result);
        } catch (err) {
          const error = new Error('Failed to parse detection result');
          setError(error.message);
          options.onError?.(error);
        }
      };

      wsRef.current.onerror = (err) => {
        const error = new Error('WebSocket connection error');
        setError(error.message);
        options.onError?.(error);
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        setIsDetecting(false);
        options.onDisconnect?.();
      };

    } catch (err) {
      const error = new Error('Failed to connect to WebSocket');
      setError(error.message);
      options.onError?.(error);
    }
  }, [options]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsDetecting(false);
  }, []);

  const startDetection = useCallback((videoElement: HTMLVideoElement) => {
    if (!isConnected || !wsRef.current) {
      throw new Error('WebSocket not connected');
    }

    videoRef.current = videoElement;
    setIsDetecting(true);

    const captureFrame = () => {
      if (!videoRef.current || !wsRef.current) return;

      try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        
        ctx?.drawImage(videoRef.current, 0, 0);
        const frameData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];

        const message = {
          frame: frameData,
          threshold: options.threshold || 0.5,
          timestamp: Date.now()
        };

        wsRef.current.send(JSON.stringify(message));
      } catch (err) {
        const error = new Error('Failed to capture frame');
        setError(error.message);
        options.onError?.(error);
      }
    };

    intervalRef.current = setInterval(captureFrame, 1000 / (options.frameRate || 10));
  }, [isConnected, options]);

  const stopDetection = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsDetecting(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isDetecting,
    lastResult,
    error,
    connect,
    disconnect,
    startDetection,
    stopDetection
  };
};

// React Component Example
const RealtimeDetectionComponent = ({ apiKey }: { apiKey: string }) => {
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const {
    isConnected,
    isDetecting,
    lastResult,
    error,
    connect,
    disconnect,
    startDetection,
    stopDetection
  } = useRealtimeDetection({
    apiKey,
    threshold: 0.7,
    frameRate: 10,
    onResult: (result) => {
      console.log('Detection result:', result);
    },
    onError: (error) => {
      console.error('Detection error:', error);
    }
  });

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setVideoStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Failed to start camera:', err);
    }
  };

  const stopCamera = () => {
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
      setVideoStream(null);
    }
  };

  const handleStartDetection = () => {
    if (videoRef.current && isConnected) {
      startDetection(videoRef.current);
    }
  };

  return (
    <div className="realtime-detection">
      <div className="status">
        <p>Connection: {isConnected ? 'Connected' : 'Disconnected'}</p>
        <p>Detection: {isDetecting ? 'Active' : 'Inactive'}</p>
        {error && <p className="error">Error: {error}</p>}
      </div>

      <div className="controls">
        <button onClick={connect} disabled={isConnected}>
          Connect
        </button>
        <button onClick={disconnect} disabled={!isConnected}>
          Disconnect
        </button>
        <button onClick={startCamera} disabled={!!videoStream}>
          Start Camera
        </button>
        <button onClick={stopCamera} disabled={!videoStream}>
          Stop Camera
        </button>
        <button onClick={handleStartDetection} disabled={!isConnected || isDetecting}>
          Start Detection
        </button>
        <button onClick={stopDetection} disabled={!isDetecting}>
          Stop Detection
        </button>
      </div>

      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        style={{ width: '100%', maxWidth: '500px' }}
      />

      {lastResult && (
        <div className="result">
          <h3>Last Detection Result:</h3>
          <p>Prediction: {lastResult.prediction}</p>
          <p>Confidence: {lastResult.confidence.toFixed(1)}%</p>
          <p>Faces Detected: {lastResult.faces_detected}</p>
          <p>Processing Time: {lastResult.processing_time}ms</p>
        </div>
      )}
    </div>
  );
};

export default RealtimeDetectionComponent;`
  };

  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Processing",
      description: "Sub-200ms response times for live video analysis"
    },
    {
      icon: <Camera className="w-6 h-6" />,
      title: "Live Camera Support",
      description: "Direct integration with webcam and mobile camera feeds"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "Continuous Detection",
      description: "Stream-based analysis for ongoing video monitoring"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "High Accuracy",
      description: "92.3% accuracy for real-time detection scenarios"
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: "Configurable Thresholds",
      description: "Adjustable confidence thresholds for different use cases"
    },
    {
      icon: <Monitor className="w-6 h-6" />,
      title: "Cross-platform",
      description: "Works on web, mobile, and desktop applications"
    }
  ];

  const messageTypes = [
    {
      type: "frame",
      description: "Base64-encoded video frame for analysis",
      required: true,
      format: "string"
    },
    {
      type: "threshold",
      description: "Confidence threshold for detection (0.0-1.0)",
      required: false,
      format: "float",
      default: "0.5"
    },
    {
      type: "timestamp",
      description: "Client-side timestamp for frame ordering",
      required: false,
      format: "number"
    }
  ];

  const responseTypes = [
    {
      field: "prediction",
      type: "string",
      description: "Detection result: 'real' or 'fake'",
      example: '"real"'
    },
    {
      field: "confidence",
      type: "float",
      description: "Confidence score (0.0-1.0)",
      example: "0.923"
    },
    {
      field: "processing_time",
      type: "number",
      description: "Processing time in milliseconds",
      example: "156"
    },
    {
      field: "faces_detected",
      type: "integer",
      description: "Number of faces detected in frame",
      example: "1"
    },
    {
      field: "timestamp",
      type: "number",
      description: "Server timestamp of analysis",
      example: "1642680000000"
    }
  ];

  return (
    <main className="min-h-screen">
      <ScrollToTop />
      {/* Hero Section */}
      <section className="py-24 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="secondary" className="neural-card mb-6 bg-primary/10 text-primary border-primary/20">
              <Zap className="w-3 h-3 mr-1" />
              Advanced Guide
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">WebSocket Guide</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Real-time detection implementation guide with WebSocket connection examples. 
              Build live video analysis applications with sub-200ms response times.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button className="neural-button" asChild>
                <Link to="/try">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <Link to="/api">
                  <FileText className="w-4 h-4 mr-2" />
                  API Documentation
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Connection Steps */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Connection Steps</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Follow these steps to establish a WebSocket connection for real-time detection.
            </p>
          </motion.div>

          <div className="space-y-8">
            {connectionSteps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card hover-lift">
                  <div className="flex flex-col lg:flex-row lg:items-start gap-6">
                    <div className="flex items-center lg:items-start gap-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-primary neural-glow flex items-center justify-center flex-shrink-0">
                        <span className="text-primary-foreground font-bold text-lg">{step.step}</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-3 neural-text">{step.title}</h3>
                      <p className="text-muted-foreground mb-4 neural-text">{step.description}</p>
                      <div className="neural-card p-4 rounded-lg">
                        <code className="text-sm neural-text">{step.code}</code>
                      </div>
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Code Examples</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Complete implementation examples for JavaScript, Python, and React applications.
            </p>
          </motion.div>

          {/* Example Tabs */}
          <div className="mb-8">
            <div className="flex flex-wrap gap-2 justify-center">
              {Object.keys(codeExamples).map((example) => (
                <Button
                  key={example}
                  variant={selectedExample === example ? "default" : "outline"}
                  onClick={() => setSelectedExample(example)}
                  className="neural-button"
                >
                  {example.charAt(0).toUpperCase() + example.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          <EnhancedCard className="neural-card overflow-hidden">
            <div className="relative">
              <CopyButton 
                text={codeExamples[selectedExample as keyof typeof codeExamples]}
                className="absolute top-4 right-4 z-10" 
              />
              <pre className="overflow-x-auto p-6 text-sm">
                <code className="neural-text">
                  {codeExamples[selectedExample as keyof typeof codeExamples]}
                </code>
              </pre>
            </div>
          </EnhancedCard>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">WebSocket Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Powerful real-time detection capabilities for live video applications.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card text-center hover-lift">
                  <div className="mx-auto mb-4 text-primary">{feature.icon}</div>
                  <h3 className="font-semibold mb-2 neural-text">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground neural-text">{feature.description}</p>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Message Format */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Message Format</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              WebSocket message structure and response format specifications.
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
                  <CardTitle className="neural-text">Request Message</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {messageTypes.map((message, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 rounded-lg neural-card bg-muted/30">
                        <code className="bg-primary/10 text-primary px-2 py-1 rounded text-sm font-medium min-w-fit">
                          {message.type}
                        </code>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-muted-foreground text-sm neural-text">({message.format})</span>
                            {message.required && (
                              <Badge variant="outline" className="text-xs neural-card">
                                Required
                              </Badge>
                            )}
                            {message.default && (
                              <Badge variant="secondary" className="text-xs neural-card">
                                Default: {message.default}
                              </Badge>
                            )}
                          </div>
                          <p className="text-muted-foreground text-sm neural-text">{message.description}</p>
                        </div>
                      </div>
                    ))}
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
                  <CardTitle className="neural-text">Response Message</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {responseTypes.map((response, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 rounded-lg neural-card bg-muted/30">
                        <code className="bg-accent/10 text-accent px-2 py-1 rounded text-sm font-medium min-w-fit">
                          {response.field}
                        </code>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-muted-foreground text-sm neural-text">({response.type})</span>
                          </div>
                          <p className="text-muted-foreground text-sm neural-text mb-1">{response.description}</p>
                          <code className="text-xs neural-card px-2 py-1 rounded">
                            {response.example}
                          </code>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Zap className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Start Building Real-time Detection</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Ready to implement real-time deepfake detection in your application? 
              Use our WebSocket API for live video analysis with industry-leading performance.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button size="lg" className="neural-button" asChild>
                <Link to="/try">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <Link to="/api">
                  <FileText className="w-4 h-4 mr-2" />
                  View API Docs
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default WebSocketGuide;
