import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Key, 
  Code, 
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
  BookOpen,
  Download,
  Github,
  GitBranch,
  Server,
  Activity,
  BarChart3,
  Layers
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useNavigation } from '@/contexts/NavigationContext';

const FastAPIDocs: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState(0);
  const { setLastApiDocsSection } = useNavigation();

  const endpoints = [
    {
      method: 'POST',
      path: '/detect-modern-ai-content',
      title: 'File Upload Analysis',
      description: 'Submit media files for advanced MesoNet CNN deepfake analysis',
      parameters: [
        { name: 'file', type: 'multipart/form-data', required: true, description: 'Media file (MP4, MOV, AVI, JPG, PNG) - max 100MB' },
        { name: 'enhanced', type: 'boolean', required: false, description: 'Enable enhanced analysis mode for higher accuracy' }
      ],
      responses: [
        { code: 200, description: 'Analysis job started successfully', example: '{"job_id": "abc123", "status": "processing"}' },
        { code: 400, description: 'Invalid file format or size', example: '{"detail": "File too large or invalid format"}' },
        { code: 422, description: 'Validation error', example: '{"detail": [{"loc": ["file"], "msg": "field required"}]}' }
      ]
    },
    {
      method: 'POST',
      path: '/detect-deepfake-youtube',
      title: 'YouTube URL Analysis',
      description: 'Analyze YouTube videos directly by URL using MesoNet CNN pipeline',
      parameters: [
        { name: 'url', type: 'string', required: true, description: 'Valid YouTube video URL for analysis' },
        { name: 'quality', type: 'string', required: false, description: 'Video quality preference: "high", "medium", "low"' }
      ],
      responses: [
        { code: 200, description: 'YouTube analysis job started', example: '{"job_id": "def456", "status": "processing"}' },
        { code: 400, description: 'Invalid YouTube URL', example: '{"detail": "Invalid YouTube URL format"}' },
        { code: 422, description: 'Validation error', example: '{"detail": [{"loc": ["url"], "msg": "field required"}]}' }
      ]
    },
    {
      method: 'GET',
      path: '/detection-status/{job_id}',
      title: 'Job Status Check',
      description: 'Monitor real-time processing status and progress of analysis jobs',
      parameters: [
        { name: 'job_id', type: 'string', required: true, description: 'Unique job identifier returned from analysis endpoints' }
      ],
      responses: [
        { code: 200, description: 'Job status retrieved successfully', example: '{"job_id": "abc123", "status": "completed", "progress": 100}' },
        { code: 404, description: 'Job not found', example: '{"detail": "Job not found"}' }
      ]
    },
    {
      method: 'WebSocket',
      path: '/ws/real-time-detection',
      title: 'Real-time Detection',
      description: 'WebSocket endpoint for live camera feed analysis with instant results',
      parameters: [
        { name: 'frame', type: 'base64', required: true, description: 'Base64 encoded video frame for real-time analysis' },
        { name: 'threshold', type: 'float', required: false, description: 'Detection confidence threshold (0.0-1.0)' }
      ],
      responses: [
        { code: 'message', description: 'Real-time detection result', example: '{"prediction": "fake", "confidence": 0.923, "processing_time": 45}' }
      ]
    }
  ];

  const interactiveDocs = {
    swagger: {
      title: 'Swagger UI',
      description: 'Interactive API documentation with live testing capabilities',
      url: 'http://127.0.0.1:8000/docs',
      features: [
        'Try out API endpoints directly in the browser',
        'View request/response schemas',
        'Test with sample data',
        'Download OpenAPI specification'
      ]
    },
    redoc: {
      title: 'ReDoc',
      description: 'Beautiful, responsive API documentation with search',
      url: 'http://127.0.0.1:8000/redoc',
      features: [
        'Clean, readable documentation format',
        'Advanced search functionality',
        'Mobile-responsive design',
        'Schema validation examples'
      ]
    },
    openapi: {
      title: 'OpenAPI Specification',
      description: 'Machine-readable API specification in JSON format',
      url: 'http://127.0.0.1:8000/openapi.json',
      features: [
        'Complete API specification',
        'Code generation support',
        'Integration with development tools',
        'Automated testing support'
      ]
    }
  };

  const codeExamples = {
    python: `# Python client example
import requests
import time

# Initialize client
base_url = "http://127.0.0.1:8000"
api_key = "your_api_key_here"

# File upload analysis
def analyze_file(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'enhanced': 'true'}
        
        response = requests.post(
            f"{base_url}/detect-modern-ai-content",
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {api_key}'}
        )
    
    if response.status_code == 200:
        return response.json()['job_id']
    else:
        raise Exception(f"Upload failed: {response.json()}")

# YouTube analysis
def analyze_youtube(url):
    data = {
        'url': url,
        'quality': 'medium'
    }
    
    response = requests.post(
        f"{base_url}/detect-deepfake-youtube",
        json=data,
        headers={'Authorization': f'Bearer {api_key}'}
    )
    
    if response.status_code == 200:
        return response.json()['job_id']
    else:
        raise Exception(f"YouTube analysis failed: {response.json()}")

# Check job status
def check_status(job_id):
    response = requests.get(
        f"{base_url}/detection-status/{job_id}",
        headers={'Authorization': f'Bearer {api_key}'}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Status check failed: {response.json()}")

# Wait for completion
def wait_for_completion(job_id, max_wait=300):
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status = check_status(job_id)
        
        if status['status'] == 'completed':
            return status
        elif status['status'] == 'failed':
            raise Exception(f"Analysis failed: {status.get('error', 'Unknown error')}")
        
        print(f"Progress: {status.get('progress', 0)}%")
        time.sleep(2)
    
    raise Exception("Analysis timeout")

# Usage example
try:
    # Analyze a video file
    job_id = analyze_file("test_video.mp4")
    print(f"Analysis started: {job_id}")
    
    result = wait_for_completion(job_id)
    print(f"Result: {result['prediction']}")
    print(f"Confidence: {result['confidence']}%")
    
except Exception as e:
    print(f"Error: {e}")`,

    javascript: `// JavaScript client example
class iFakeAPIClient {
  constructor(baseUrl = 'http://127.0.0.1:8000', apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async request(endpoint, options = {}) {
    const url = \`\${this.baseUrl}\${endpoint}\`;
    const config = {
      headers: {
        'Authorization': \`Bearer \${this.apiKey}\`,
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(\`API Error: \${error.detail || response.statusText}\`);
    }
    
    return response.json();
  }

  async analyzeFile(file, enhanced = false) {
    const formData = new FormData();
    formData.append('file', file);
    if (enhanced) formData.append('enhanced', 'true');

    return this.request('/detect-modern-ai-content', {
      method: 'POST',
      body: formData
    });
  }

  async analyzeYouTube(url, quality = 'medium') {
    return this.request('/detect-deepfake-youtube', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, quality })
    });
  }

  async checkStatus(jobId) {
    return this.request(\`/detection-status/\${jobId}\`);
  }

  async waitForCompletion(jobId, maxWait = 300) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWait * 1000) {
      const status = await this.checkStatus(jobId);
      
      if (status.status === 'completed') {
        return status;
      } else if (status.status === 'failed') {
        throw new Error(\`Analysis failed: \${status.error || 'Unknown error'}\`);
      }
      
      console.log(\`Progress: \${status.progress || 0}%\`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    throw new Error('Analysis timeout');
  }
}

// Usage example
const client = new iFakeAPIClient('http://127.0.0.1:8000', 'your_api_key_here');

async function analyzeVideo() {
  try {
    const fileInput = document.getElementById('videoFile');
    const file = fileInput.files[0];
    
    if (!file) {
      throw new Error('Please select a file');
    }
    
    // Start analysis
    const { job_id } = await client.analyzeFile(file, true);
    console.log(\`Analysis started: \${job_id}\`);
    
    // Wait for completion
    const result = await client.waitForCompletion(job_id);
    console.log(\`Result: \${result.prediction}\`);
    console.log(\`Confidence: \${result.confidence}%\`);
    
  } catch (error) {
    console.error(\`Error: \${error.message}\`);
  }
}`,

    curl: `# cURL examples for all endpoints

# 1. File Upload Analysis
curl -X POST "http://127.0.0.1:8000/detect-modern-ai-content" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@video.mp4" \\
  -F "enhanced=true"

# Response:
# {
#   "job_id": "abc123def456",
#   "status": "processing",
#   "message": "Analysis started successfully"
# }

# 2. YouTube URL Analysis
curl -X POST "http://127.0.0.1:8000/detect-deepfake-youtube" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://youtube.com/watch?v=example",
    "quality": "medium"
  }'

# Response:
# {
#   "job_id": "def456ghi789",
#   "status": "processing",
#   "message": "YouTube analysis started"
# }

# 3. Check Job Status
curl -X GET "http://127.0.0.1:8000/detection-status/abc123def456" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Response (Processing):
# {
#   "job_id": "abc123def456",
#   "status": "processing",
#   "progress": 45,
#   "current_stage": "mesonet_cnn_analysis",
#   "estimated_completion": "2024-01-21T10:30:00Z"
# }

# Response (Completed):
# {
#   "job_id": "abc123def456",
#   "status": "completed",
#   "prediction": "fake",
#   "confidence": 94.1,
#   "processing_time": "23.4 seconds",
#   "faces_detected": 1,
#   "detection_method": "MesoNet CNN v2.1"
# }

# 4. WebSocket Connection (using wscat or similar)
# wscat -c "ws://127.0.0.1:8000/ws/real-time-detection?api_key=YOUR_API_KEY"
# 
# Send message:
# {
#   "frame": "base64_encoded_frame_data",
#   "threshold": 0.5,
#   "timestamp": 1642680000000
# }
# 
# Receive response:
# {
#   "prediction": "real",
#   "confidence": 0.876,
#   "processing_time": 45,
#   "faces_detected": 1,
#   "timestamp": 1642680000045
# }`
  };

  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Auto-generated Documentation",
      description: "FastAPI automatically generates interactive API docs from your code"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Data Validation",
      description: "Automatic request/response validation using Pydantic models"
    },
    {
      icon: <Code className="w-6 h-6" />,
      title: "Type Hints",
      description: "Full type safety with Python type hints and IDE support"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "Real-time Testing",
      description: "Test API endpoints directly in the browser with Swagger UI"
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "OpenAPI Standard",
      description: "Fully compliant with OpenAPI 3.0 specification"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Performance Monitoring",
      description: "Built-in metrics and performance monitoring capabilities"
    }
  ];

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'POST': return 'bg-green-500';
      case 'GET': return 'bg-blue-500';
      case 'WebSocket': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

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
              <Key className="w-3 h-3 mr-1" />
              Live Documentation
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">FastAPI Documentation</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Interactive API documentation powered by FastAPI with live testing capabilities. 
              Explore endpoints, test requests, and integrate with confidence.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button className="neural-button" asChild>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open Swagger UI
                </a>
              </Button>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <a href="http://127.0.0.1:8000/redoc" target="_blank" rel="noopener noreferrer">
                  <BookOpen className="w-4 h-4 mr-2" />
                  View ReDoc
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Interactive Documentation */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Interactive Documentation</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Three different ways to explore and interact with our FastAPI-powered deepfake detection API.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {Object.entries(interactiveDocs).map(([key, doc], index) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card h-full hover-lift">
                  <CardHeader>
                    <CardTitle className="neural-text flex items-center">
                      <BookOpen className="w-5 h-5 mr-2" />
                      {doc.title}
                    </CardTitle>
                    <p className="text-muted-foreground neural-text">{doc.description}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="neural-card p-3 rounded-lg">
                        <code className="text-sm neural-text break-all">{doc.url}</code>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 neural-text">Features:</h4>
                        <ul className="space-y-1">
                          {doc.features.map((feature, featureIndex) => (
                            <li key={featureIndex} className="flex items-start gap-2 text-sm">
                              <CheckCircle2 className="w-3 h-3 text-success mt-1 flex-shrink-0" />
                              <span className="neural-text">{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <Button className="w-full neural-button" asChild>
                        <a href={doc.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          Open {doc.title}
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* API Endpoints */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">API Endpoints</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Complete reference for all available API endpoints with detailed parameters and responses.
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
                      <div className="flex items-center gap-4 mb-4">
                        <Badge 
                          className={`neural-button text-white ${getMethodColor(endpoint.method)}`}
                        >
                          {endpoint.method}
                        </Badge>
                        <code className="neural-card px-4 py-2 rounded-lg font-mono text-sm">
                          {endpoint.path}
                        </code>
                      </div>
                      
                      <h3 className="text-xl font-semibold mb-3 neural-text">{endpoint.title}</h3>
                      <p className="text-muted-foreground mb-6 neural-text">{endpoint.description}</p>
                      
                      {/* Parameters */}
                      <div className="mb-6">
                        <h4 className="font-semibold mb-3 neural-text">Parameters:</h4>
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
                                    <Badge variant="outline" className="text-xs neural-card">
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

                      {/* Responses */}
                      <div>
                        <h4 className="font-semibold mb-3 neural-text">Responses:</h4>
                        <div className="space-y-3">
                          {endpoint.responses.map((response, responseIndex) => (
                            <div key={responseIndex} className="p-3 rounded-lg neural-card bg-muted/30">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge 
                                  variant="outline" 
                                  className={`neural-card text-xs ${
                                    response.code === 200 ? 'text-success' : 
                                    response.code === 400 ? 'text-warning' : 
                                    'text-destructive'
                                  }`}
                                >
                                  {response.code}
                                </Badge>
                                <span className="text-sm font-medium neural-text">{response.description}</span>
                              </div>
                              <code className="text-xs neural-card p-2 rounded block">
                                {response.example}
                              </code>
                            </div>
                          ))}
                        </div>
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
              Ready-to-use code examples for integrating with our FastAPI endpoints.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {Object.entries(codeExamples).map(([language, code], index) => (
              <motion.div
                key={language}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card h-full">
                  <CardHeader>
                    <CardTitle className="neural-text flex items-center">
                      <Terminal className="w-5 h-5 mr-2" />
                      {language.charAt(0).toUpperCase() + language.slice(1)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="relative">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute top-2 right-2 neural-button z-10"
                        onClick={() => navigator.clipboard.writeText(code)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      <pre className="overflow-x-auto text-xs neural-card p-4 rounded-lg">
                        <code className="neural-text">{code}</code>
                      </pre>
                    </div>
                  </CardContent>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FastAPI Features */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">FastAPI Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Why we chose FastAPI for our deepfake detection API and what makes it special.
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

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Key className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Start Building Today</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Explore our interactive API documentation and start integrating deepfake detection 
              into your applications with confidence.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button 
                size="lg" 
                className="neural-button" 
                asChild
                onClick={() => setLastApiDocsSection('resources')}
              >
                <Link to="/api">
                  <Key className="w-4 h-4 mr-2" />
                  Back to API Documentation
                </Link>
              </Button>
              <Button size="lg" className="neural-button" asChild>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open Swagger UI
                </a>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <Link to="/try">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default FastAPIDocs;
