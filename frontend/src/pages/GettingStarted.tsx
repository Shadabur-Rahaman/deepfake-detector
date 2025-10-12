import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Book, 
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
  Download,
  Copy,
  Clock,
  Users,
  Settings,
  AlertTriangle,
  Info
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useNavigation } from '@/contexts/NavigationContext';

const GettingStarted: React.FC = () => {
  const { setLastApiDocsSection } = useNavigation();
  const steps = [
    {
      number: 1,
      title: "Choose Your Integration Method",
      description: "Select between our REST API, WebSocket real-time detection, or official SDKs",
      icon: <Settings className="w-6 h-6" />,
      details: [
        "REST API for file uploads and YouTube URL analysis",
        "WebSocket API for real-time camera feed detection", 
        "Official Python and JavaScript SDKs for easy integration",
        "Interactive FastAPI documentation for testing"
      ]
    },
    {
      number: 2,
      title: "Get Your API Access",
      description: "Sign up for a free account and obtain your API credentials",
      icon: <Shield className="w-6 h-6" />,
      details: [
        "Free tier: 100 analysis requests per month",
        "No credit card required for free tier",
        "Instant access to all API endpoints",
        "Comprehensive documentation and examples"
      ]
    },
    {
      number: 3,
      title: "Install SDK or Setup API Client",
      description: "Choose your preferred method and set up the client library",
      icon: <Code className="w-6 h-6" />,
      details: [
        "Python: pip install ifake-api",
        "JavaScript: npm install @ifake/api-client",
        "Direct API calls with cURL or any HTTP client",
        "WebSocket connections for real-time detection"
      ]
    },
    {
      number: 4,
      title: "Make Your First API Call",
      description: "Upload a video file or analyze a YouTube URL to test the integration",
      icon: <Play className="w-6 h-6" />,
      details: [
        "Test with our sample video files",
        "Try YouTube URL analysis",
        "Monitor real-time processing status",
        "Review detailed analysis results"
      ]
    },
    {
      number: 5,
      title: "Integrate into Your Application",
      description: "Implement error handling, progress tracking, and result processing",
      icon: <Database className="w-6 h-6" />,
      details: [
        "Handle API responses and errors gracefully",
        "Implement progress tracking for long-running jobs",
        "Process and display analysis results",
        "Add retry logic for failed requests"
      ]
    }
  ];

  const codeExamples = {
    python: `# Install the Python SDK
pip install ifake-api

# Basic usage example
from ifake_api import iFakeClient

# Initialize the client
client = iFakeClient(api_key="your_api_key_here")

# Analyze a video file
try:
    result = client.analyze_file("path/to/video.mp4")
    print(f"Analysis Result: {result.prediction}")
    print(f"Confidence: {result.confidence}%")
    print(f"Processing Time: {result.processing_time}s")
except Exception as e:
    print(f"Error: {e}")

# Analyze a YouTube URL
try:
    result = client.analyze_youtube("https://youtube.com/watch?v=example")
    print(f"YouTube Analysis: {result.prediction}")
except Exception as e:
    print(f"Error: {e}")`,

    javascript: `// Install the JavaScript SDK
npm install @ifake/api-client

// Basic usage example
import { iFakeClient } from '@ifake/api-client';

// Initialize the client
const client = new iFakeClient({
  apiKey: 'your_api_key_here',
  baseUrl: 'https://api.ifake.com'
});

// Analyze a video file
async function analyzeVideo(file) {
  try {
    const result = await client.analyzeFile(file);
    console.log('Analysis Result:', result.prediction);
    console.log('Confidence:', result.confidence + '%');
    console.log('Processing Time:', result.processing_time + 's');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Analyze a YouTube URL
async function analyzeYouTube(url) {
  try {
    const result = await client.analyzeYouTube(url);
    console.log('YouTube Analysis:', result.prediction);
  } catch (error) {
    console.error('Error:', error.message);
  }
}`,

    curl: `# Basic cURL example for file upload
curl -X POST "https://api.ifake.com/detect-modern-ai-content" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@video.mp4" \\
  -F "enhanced=true"

# YouTube URL analysis
curl -X POST "https://api.ifake.com/detect-deepfake-youtube" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://youtube.com/watch?v=example"}'

# Check analysis status
curl -X GET "https://api.ifake.com/detection-status/JOB_ID" \\
  -H "Authorization: Bearer YOUR_API_KEY"`
  };

  const features = [
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
      icon: <Globe className="w-6 h-6" />,
      title: "Multi-format Support",
      description: "Supports MP4, AVI, MOV video files and YouTube URLs"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "Advanced AI Models",
      description: "MesoNet CNN architecture trained on FaceForensics++ dataset"
    }
  ];

  const troubleshooting = [
    {
      issue: "API Key Authentication Failed",
      solution: "Verify your API key is correct and has proper permissions. Check the Authorization header format.",
      icon: <AlertTriangle className="w-5 h-5" />
    },
    {
      issue: "File Upload Size Limit Exceeded",
      solution: "Ensure your video file is under 100MB. Consider compressing the video or using YouTube URL analysis.",
      icon: <AlertTriangle className="w-5 h-5" />
    },
    {
      issue: "Analysis Job Timeout",
      solution: "Long videos may take more time to process. Implement proper polling with exponential backoff.",
      icon: <AlertTriangle className="w-5 h-5" />
    },
    {
      issue: "WebSocket Connection Issues",
      solution: "Check your network connection and ensure WebSocket support. Verify the WebSocket URL format.",
      icon: <AlertTriangle className="w-5 h-5" />
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
              <Book className="w-3 h-3 mr-1" />
              Essential Guide
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">Getting Started Guide</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Complete walkthrough for integrating iFake's MesoNet CNN API into your application. 
              From setup to production deployment in minutes.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button className="neural-button" asChild>
                <Link to="/try">
                  <Play className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Interactive API Docs
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Quick Start Steps */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Quick Start Steps</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Follow these 5 simple steps to integrate iFake's MesoNet CNN API into your application.
            </p>
          </motion.div>

          <div className="space-y-8">
            {steps.map((step, index) => (
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
                        <span className="text-primary-foreground font-bold text-lg">{step.number}</span>
                      </div>
                      <div className="text-primary">{step.icon}</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-3 neural-text">{step.title}</h3>
                      <p className="text-muted-foreground mb-4 neural-text">{step.description}</p>
                      <ul className="space-y-2">
                        {step.details.map((detail, detailIndex) => (
                          <li key={detailIndex} className="flex items-start gap-2">
                            <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-muted-foreground neural-text">{detail}</span>
                          </li>
                        ))}
                      </ul>
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
              Ready-to-use code examples for your favorite programming language with complete error handling.
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

      {/* Features Overview */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Key Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Powerful MesoNet CNN detection capabilities with enterprise-grade reliability.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
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

      {/* Troubleshooting */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Common Issues & Solutions</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Quick solutions to common integration challenges and API usage issues.
            </p>
          </motion.div>

          <div className="space-y-6">
            {troubleshooting.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card">
                  <div className="flex items-start gap-4">
                    <div className="text-warning flex-shrink-0">{item.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-2 neural-text">{item.issue}</h3>
                      <p className="text-muted-foreground neural-text">{item.solution}</p>
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Brain className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Ready to Build?</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              You're all set to integrate iFake's MesoNet CNN API into your application. 
              Explore our comprehensive documentation and start building today.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button 
                size="lg" 
                className="neural-button" 
                asChild
                onClick={() => setLastApiDocsSection('resources')}
              >
                <Link to="/api">
                  <Code className="w-4 h-4 mr-2" />
                  Back to API Documentation
                </Link>
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

export default GettingStarted;
