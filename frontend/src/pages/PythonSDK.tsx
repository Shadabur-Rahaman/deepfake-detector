import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import { CopyButton } from '@/components/ui/CopyButton'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Code, 
  Download, 
  Play, 
  CheckCircle2, 
  ArrowRight, 
  ExternalLink,
  Terminal,
  Globe,
  Shield,
  Zap,
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
  Package,
  GitBranch,
  Star,
  Github
} from 'lucide-react';
import { Link } from 'react-router-dom';

const PythonSDK: React.FC = () => {
  const [selectedExample, setSelectedExample] = useState('basic');

  const installationSteps = [
    {
      step: 1,
      title: "Install via pip",
      command: "pip install ifake-api",
      description: "Install the official Python SDK from PyPI"
    },
    {
      step: 2,
      title: "Import the client",
      command: "from ifake_api import iFakeClient",
      description: "Import the main client class"
    },
    {
      step: 3,
      title: "Initialize client",
      command: 'client = iFakeClient(api_key="your_key")',
      description: "Create a client instance with your API key"
    },
    {
      step: 4,
      title: "Start analyzing",
      command: "result = client.analyze_file('video.mp4')",
      description: "Begin analyzing videos with a single method call"
    }
  ];

  const codeExamples = {
    basic: `from ifake_api import iFakeClient
import asyncio

# Initialize the client
client = iFakeClient(
    api_key="your_api_key_here",
    base_url="https://api.ifake.com"  # Optional, defaults to production
)

# Analyze a video file
def analyze_video():
    try:
        result = client.analyze_file("path/to/video.mp4")
        print(f"Prediction: {result.prediction}")
        print(f"Confidence: {result.confidence}%")
        print(f"Processing Time: {result.processing_time}s")
        print(f"Faces Detected: {result.faces_detected}")
    except Exception as e:
        print(f"Error: {e}")

# Analyze YouTube URL
def analyze_youtube():
    try:
        result = client.analyze_youtube("https://youtube.com/watch?v=example")
        print(f"YouTube Analysis: {result.prediction}")
        print(f"Confidence: {result.confidence}%")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_video()
    analyze_youtube()`,

    advanced: `from ifake_api import iFakeClient
import asyncio
import base64
from typing import Optional, Dict, Any

class AdvancediFakeClient(iFakeClient):
    """Extended client with advanced features"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.analysis_history = []
    
    def analyze_with_enhanced_mode(self, file_path: str, 
                                 enhanced: bool = True,
                                 quality: str = "high") -> Dict[str, Any]:
        """Analyze with enhanced mode and quality settings"""
        try:
            result = self.analyze_file(file_path, enhanced=enhanced)
            
            # Store analysis in history
            self.analysis_history.append({
                'file': file_path,
                'result': result.prediction,
                'confidence': result.confidence,
                'timestamp': result.timestamp
            })
            
            return {
                'prediction': result.prediction,
                'confidence': result.confidence,
                'enhanced_analysis': enhanced,
                'quality': quality,
                'processing_time': result.processing_time,
                'faces_detected': result.faces_detected,
                'analysis_id': result.job_id
            }
        except Exception as e:
            raise Exception(f"Enhanced analysis failed: {str(e)}")
    
    async def batch_analyze(self, file_paths: list) -> Dict[str, Any]:
        """Analyze multiple files concurrently"""
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(
                self.analyze_file_async(file_path)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'total_files': len(file_paths),
            'successful': len([r for r in results if not isinstance(r, Exception)]),
            'failed': len([r for r in results if isinstance(r, Exception)]),
            'results': results
        }
    
    def get_analysis_history(self) -> list:
        """Get analysis history"""
        return self.analysis_history
    
    def export_results(self, format: str = "json") -> str:
        """Export analysis results"""
        if format == "json":
            import json
            return json.dumps(self.analysis_history, indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'file', 'result', 'confidence', 'timestamp'
            ])
            writer.writeheader()
            writer.writerows(self.analysis_history)
            return output.getvalue()
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'")

# Usage example
async def main():
    client = AdvancediFakeClient("your_api_key_here")
    
    # Single file analysis with enhanced mode
    result = client.analyze_with_enhanced_mode("video.mp4", enhanced=True)
    print(f"Enhanced Analysis: {result}")
    
    # Batch analysis
    files = ["video1.mp4", "video2.mp4", "video3.mp4"]
    batch_results = await client.batch_analyze(files)
    print(f"Batch Results: {batch_results}")
    
    # Export results
    json_export = client.export_results("json")
    print(f"JSON Export: {json_export}")

if __name__ == "__main__":
    asyncio.run(main())`,

    websocket: `import asyncio
import websockets
import json
import base64
from ifake_api import iFakeClient

class RealtimeDetector:
    """Real-time detection using WebSocket"""
    
    def __init__(self, api_key: str, websocket_url: str = None):
        self.api_key = api_key
        self.websocket_url = websocket_url or "wss://api.ifake.com/ws/real-time-detection"
        self.websocket = None
        self.is_connected = False
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(
                f"{self.websocket_url}?api_key={self.api_key}"
            )
            self.is_connected = True
            print("Connected to real-time detection service")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise
    
    async def send_frame(self, frame_data: bytes, threshold: float = 0.5):
        """Send frame for real-time analysis"""
        if not self.is_connected:
            raise Exception("Not connected to WebSocket")
        
        try:
            # Encode frame as base64
            frame_b64 = base64.b64encode(frame_data).decode()
            
            # Send frame data
            message = {
                "frame": frame_b64,
                "threshold": threshold,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.websocket.send(json.dumps(message))
            
            # Wait for response
            response = await self.websocket.recv()
            result = json.loads(response)
            
            return {
                'prediction': result.get('prediction'),
                'confidence': result.get('confidence'),
                'processing_time': result.get('processing_time'),
                'faces_detected': result.get('faces_detected'),
                'timestamp': result.get('timestamp')
            }
            
        except Exception as e:
            print(f"Frame analysis failed: {e}")
            raise
    
    async def start_continuous_detection(self, frame_generator, 
                                       callback=None, 
                                       threshold: float = 0.5):
        """Start continuous detection from frame generator"""
        try:
            await self.connect()
            
            async for frame_data in frame_generator:
                try:
                    result = await self.send_frame(frame_data, threshold)
                    
                    if callback:
                        await callback(result)
                    else:
                        print(f"Detection: {result['prediction']} "
                              f"({result['confidence']:.1f}%)")
                
                except Exception as e:
                    print(f"Frame processing error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Continuous detection failed: {e}")
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("Disconnected from real-time detection service")

# Example usage
async def frame_generator():
    """Example frame generator (replace with your camera source)"""
    import cv2
    
    cap = cv2.VideoCapture(0)  # Use camera
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert frame to bytes
        _, buffer = cv2.imencode('.jpg', frame)
        yield buffer.tobytes()
        
        await asyncio.sleep(0.1)  # 10 FPS

async def detection_callback(result):
    """Callback for detection results"""
    print(f"Real-time Detection: {result['prediction']} "
          f"({result['confidence']:.1f}%) - "
          f"{result['faces_detected']} faces")

async def main():
    detector = RealtimeDetector("your_api_key_here")
    
    try:
        await detector.start_continuous_detection(
            frame_generator(),
            detection_callback,
            threshold=0.7
        )
    except KeyboardInterrupt:
        print("Stopping detection...")
    finally:
        await detector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())`,

    error_handling: `from ifake_api import iFakeClient, iFakeError, RateLimitError, AuthenticationError
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustiFakeClient(iFakeClient):
    """Client with comprehensive error handling and retry logic"""
    
    def __init__(self, api_key: str, max_retries: int = 3, **kwargs):
        super().__init__(api_key, **kwargs)
        self.max_retries = max_retries
        self.retry_delay = 1  # seconds
    
    def analyze_file_with_retry(self, file_path: str, **kwargs):
        """Analyze file with automatic retry on failure"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt + 1} to analyze {file_path}")
                result = self.analyze_file(file_path, **kwargs)
                logger.info(f"Analysis successful: {result.prediction}")
                return result
                
            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded: {e}")
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
                    
            except AuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                raise e  # Don't retry auth errors
                
            except iFakeError as e:
                logger.error(f"API error: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e
        
        # If we get here, all retries failed
        raise last_exception or Exception("All retry attempts failed")
    
    def analyze_with_fallback(self, file_path: str, fallback_url: str = None):
        """Analyze with fallback to YouTube URL if file analysis fails"""
        try:
            # Try file analysis first
            return self.analyze_file_with_retry(file_path)
            
        except Exception as e:
            logger.warning(f"File analysis failed: {e}")
            
            if fallback_url:
                try:
                    logger.info(f"Trying fallback YouTube analysis: {fallback_url}")
                    return self.analyze_youtube(fallback_url)
                except Exception as fallback_error:
                    logger.error(f"Fallback analysis also failed: {fallback_error}")
                    raise Exception(f"Both file and YouTube analysis failed. "
                                  f"File error: {e}, YouTube error: {fallback_error}")
            else:
                raise e
    
    def get_analysis_with_metadata(self, file_path: str):
        """Get analysis with comprehensive metadata"""
        try:
            result = self.analyze_file_with_retry(file_path)
            
            # Add metadata
            metadata = {
                'file_path': file_path,
                'file_size': self._get_file_size(file_path),
                'analysis_timestamp': time.time(),
                'client_version': self._get_client_version(),
                'api_endpoint': self.base_url
            }
            
            return {
                'analysis': result,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Analysis with metadata failed: {e}")
            raise e
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        import os
        return os.path.getsize(file_path)
    
    def _get_client_version(self) -> str:
        """Get client version"""
        try:
            import ifake_api
            return getattr(ifake_api, '__version__', 'unknown')
        except:
            return 'unknown'

# Usage examples
def main():
    client = RobustiFakeClient("your_api_key_here", max_retries=3)
    
    try:
        # Basic analysis with retry
        result = client.analyze_file_with_retry("video.mp4")
        print(f"Analysis Result: {result.prediction}")
        
        # Analysis with fallback
        result = client.analyze_with_fallback(
            "video.mp4", 
            "https://youtube.com/watch?v=example"
        )
        print(f"Fallback Analysis: {result.prediction}")
        
        # Analysis with metadata
        result_with_meta = client.get_analysis_with_metadata("video.mp4")
        print(f"Analysis with metadata: {result_with_meta}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()`
  };

  const features = [
    {
      icon: <Package className="w-6 h-6" />,
      title: "Easy Installation",
      description: "Install with a single pip command and start analyzing immediately"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Type Safety",
      description: "Full type hints and comprehensive error handling for robust applications"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Async Support",
      description: "Built-in async/await support for high-performance applications"
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: "Batch Processing",
      description: "Analyze multiple files concurrently with built-in batch processing"
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "WebSocket Support",
      description: "Real-time detection capabilities with WebSocket integration"
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: "Configurable",
      description: "Flexible configuration options for different use cases"
    }
  ];

  const apiMethods = [
    {
      method: "analyze_file",
      description: "Analyze a local video or image file",
      parameters: ["file_path", "enhanced", "quality"],
      return_type: "AnalysisResult"
    },
    {
      method: "analyze_youtube",
      description: "Analyze a YouTube video by URL",
      parameters: ["url", "quality"],
      return_type: "AnalysisResult"
    },
    {
      method: "check_status",
      description: "Check the status of an analysis job",
      parameters: ["job_id"],
      return_type: "JobStatus"
    },
    {
      method: "wait_for_results",
      description: "Wait for analysis completion with polling",
      parameters: ["job_id", "max_wait"],
      return_type: "AnalysisResult"
    },
    {
      method: "real_time_detection",
      description: "Real-time detection via WebSocket",
      parameters: ["frame_data", "threshold"],
      return_type: "RealtimeResult"
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
              <Code className="w-3 h-3 mr-1" />
              Popular SDK
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">Python SDK</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Official Python client library with comprehensive examples, error handling, 
              and async support for integrating MesoNet CNN deepfake detection.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button className="neural-button" asChild>
                <a href="https://pypi.org/project/ifake-api" target="_blank" rel="noopener noreferrer">
                  <Download className="w-4 h-4 mr-2" />
                  Install from PyPI
                </a>
              </Button>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <a href="https://github.com/ifake/python-sdk" target="_blank" rel="noopener noreferrer">
                  <Github className="w-4 h-4 mr-2" />
                  View on GitHub
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Installation */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Quick Installation</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Get started with the Python SDK in minutes. Install via pip and start analyzing videos immediately.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {installationSteps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card text-center hover-lift">
                  <div className="w-12 h-12 rounded-full bg-gradient-primary neural-glow flex items-center justify-center mx-auto mb-4">
                    <span className="text-primary-foreground font-bold text-lg">{step.step}</span>
                  </div>
                  <h3 className="font-semibold mb-3 neural-text">{step.title}</h3>
                  <div className="neural-card p-3 rounded-lg mb-3">
                    <code className="text-sm neural-text">{step.command}</code>
                  </div>
                  <p className="text-sm text-muted-foreground neural-text">{step.description}</p>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Code Examples</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Comprehensive examples covering basic usage, advanced features, and real-time detection.
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
                  {example.charAt(0).toUpperCase() + example.slice(1).replace('_', ' ')}
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
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">SDK Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Powerful features designed for production-ready Python applications.
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

      {/* API Reference */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">API Reference</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Complete reference for all available methods and their parameters.
            </p>
          </motion.div>

          <div className="space-y-6">
            {apiMethods.map((method, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card">
                  <div className="flex flex-col lg:flex-row lg:items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <code className="neural-card px-3 py-1 rounded font-mono text-sm font-semibold">
                          {method.method}()
                        </code>
                        <Badge variant="outline" className="neural-card text-xs">
                          {method.return_type}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground mb-3 neural-text">{method.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {method.parameters.map((param, paramIndex) => (
                          <Badge key={paramIndex} variant="secondary" className="neural-card text-xs">
                            {param}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Code className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Start Building</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Ready to integrate MesoNet CNN deepfake detection into your Python application? 
              Install the SDK and start building today.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button size="lg" className="neural-button" asChild>
                <a href="https://pypi.org/project/ifake-api" target="_blank" rel="noopener noreferrer">
                  <Download className="w-4 h-4 mr-2" />
                  Install SDK
                </a>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <Link to="/api">
                  <FileText className="w-4 h-4 mr-2" />
                  View Full API Docs
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default PythonSDK;
