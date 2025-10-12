import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, Eye, Cpu, Shield, Zap, Users, BarChart3, Clock } from "lucide-react"
import { HeroCanvas } from "@/components/three/HeroCanvas"

// Animation variants for live animations
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      duration: 0.6
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] as any
    }
  }
}

const glowVariants = {
  initial: { 
    boxShadow: "0 0 0 0 rgba(59, 130, 246, 0.4)",
    scale: 1
  },
  animate: {
    boxShadow: [
      "0 0 0 0 rgba(59, 130, 246, 0.4)",
      "0 0 20px 10px rgba(59, 130, 246, 0.1)",
      "0 0 0 0 rgba(59, 130, 246, 0.4)"
    ],
    scale: [1, 1.02, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut" as const
    }
  }
}

const features = [
  {
    icon: Brain,
    title: "MesoNet CNN Architecture",
    description: "Advanced mesoscopic-level convolutional neural network specifically designed for deepfake detection",
    category: "AI Core",
    color: "text-ai-core"
  },
  {
    icon: Eye,
    title: "Real-Time WebSocket Analysis",
    description: "Live camera feed processing through WebSocket connections with instant frame-by-frame detection",
    category: "Detection",
    color: "text-ai-neural"
  },
  {
    icon: Cpu,
    title: "FastAPI Async Processing",
    description: "High-performance async Python backend with job queuing delivering results in under 30 seconds",
    category: "Performance",
    color: "text-ai-data"
  },
  {
    icon: Shield,
    title: "Secure Job Management",
    description: "Enterprise-grade async job tracking with status monitoring and secure result delivery",
    category: "Security",
    color: "text-success"
  },
  {
    icon: BarChart3,
    title: "Multi-Stage Detection Pipeline",
    description: "Sophisticated ensemble combining MesoNet with temporal and frequency domain analysis",
    category: "Analytics",
    color: "text-warning"
  },
  {
    icon: Zap,
    title: "YouTube & File Processing",
    description: "Direct YouTube URL analysis and multi-format video file processing with batch capabilities",
    category: "Scalability", 
    color: "text-accent"
  }
]

const architectureSteps = [
  {
    title: "Video Upload & Processing",
    description: "FastAPI endpoint receives video files or YouTube URLs through /analyze with async job creation",
    stage: "Stage 1"
  },
  {
    title: "Face Detection & Extraction", 
    description: "Advanced YOLO and MTCNN algorithms identify and extract facial regions with precision",
    stage: "Stage 2"
  },
  {
    title: "MesoNet CNN Analysis",
    description: "Specialized deepfake detection model analyzes extracted faces for manipulation artifacts",
    stage: "Stage 3"
  },
  {
    title: "Status Tracking & Monitoring",
    description: "Real-time job status updates through /status/{job_id} endpoint with progress tracking",
    stage: "Stage 4"
  },
  {
    title: "Results & Confidence Scoring",
    description: "Final verdict delivery through /results/{job_id} with detailed confidence metrics",
    stage: "Stage 5"
  }
]

const modelCards = [
  {
    name: "MesoNet CNN",
    accuracy: "94.1%",
    specialty: "Facial manipulation detection",
    description: "Mesoscopic-level convolutional neural network trained on FaceForensics++, DFDC datasets"
  },
  {
    name: "Modern AI Detector", 
    accuracy: "96.8%",
    specialty: "Latest AI-generated content",
    description: "Specialized model for detecting Sora, Runway, and other emerging AI generation tools"
  },
  {
    name: "Real-Time Processor",
    accuracy: "92.3%", 
    specialty: "WebSocket live analysis",
    description: "Optimized for live camera feed processing through WebSocket connections"
  }
]

export default function Features() {
  return (
    <main>
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
            <Badge 
              variant="secondary" 
              className="mb-6 bg-primary/10 text-primary border-primary/20"
            >
              <Brain className="w-4 h-4 mr-2" />
              MesoNet Detection Architecture
            </Badge>
            <motion.h1 
              className="text-hero font-bold mb-6 gradient-text"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Detection Features
            </motion.h1>
            <motion.p 
              className="text-xl text-muted-foreground max-w-3xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              Discover the cutting-edge MesoNet CNN and FastAPI technologies powering iFake's 
              real-time deepfake detection capabilities.
            </motion.p>
            
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
                <div className="text-3xl font-bold text-ai-neural mb-2">&lt;30s</div>
                <div className="text-sm text-muted-foreground">Processing Time</div>
              </motion.div>
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-data mb-2">&lt;2s</div>
                <div className="text-sm text-muted-foreground">WebSocket Latency</div>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      {/* Core Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6">Core Technologies</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Our FastAPI-powered backend combines MesoNet CNN architecture with 
              WebSocket real-time processing and async job management.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                variants={itemVariants}
                className="group"
              >
                <motion.div
                  whileHover={{ 
                    y: -5,
                    transition: { duration: 0.2 }
                  }}
                  className="h-full"
                >
                  <Card className="h-full border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-glow">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-4">
                        <motion.div 
                          className={`w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center group-hover:glow-primary transition-all duration-300`}
                          whileHover={{ 
                            scale: 1.1,
                            rotate: 5,
                            transition: { duration: 0.2 }
                          }}
                        >
                          <feature.icon className="w-6 h-6 text-primary-foreground" />
                        </motion.div>
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Badge variant="outline" className="text-xs">
                            {feature.category}
                          </Badge>
                        </motion.div>
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Detection Architecture */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6">Detection Architecture</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Our FastAPI-powered five-stage pipeline ensures comprehensive analysis of every uploaded file.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="space-y-8"
          >
            {architectureSteps.map((step, index) => (
              <motion.div
                key={step.title}
                variants={itemVariants}
                className={`flex flex-col md:flex-row items-center gap-8 ${
                  index % 2 === 1 ? 'md:flex-row-reverse' : ''
                }`}
              >
                <div className="flex-1">
                  <motion.div
                    whileHover={{ 
                      y: -3,
                      transition: { duration: 0.2 }
                    }}
                  >
                    <Card className="p-6 border-border/50 bg-card/80 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-glow">
                      <div className="flex items-center space-x-4 mb-4">
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Badge variant="outline" className="text-ai-core border-ai-core">
                            {step.stage}
                          </Badge>
                        </motion.div>
                        <h3 className="text-xl font-semibold">{step.title}</h3>
                      </div>
                      <p className="text-muted-foreground leading-relaxed">
                        {step.description}
                      </p>
                    </Card>
                  </motion.div>
                </div>
                <motion.div 
                  className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground font-bold"
                  whileHover={{ 
                    scale: 1.2,
                    rotate: 360,
                    transition: { duration: 0.5 }
                  }}
                  variants={glowVariants}
                  initial="initial"
                  animate="animate"
                >
                  {index + 1}
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Model Cards */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6">Specialized Models</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Each model is optimized for specific detection scenarios and media processing requirements.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {modelCards.map((model, index) => (
              <motion.div
                key={model.name}
                variants={itemVariants}
                className="group"
              >
                <motion.div
                  whileHover={{ 
                    y: -8,
                    transition: { duration: 0.3 }
                  }}
                  className="h-full"
                >
                  <Card className="text-center h-full border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-glow">
                    <CardHeader>
                      <CardTitle className="text-xl mb-2">{model.name}</CardTitle>
                      <motion.div 
                        className="text-3xl font-bold text-ai-core mb-2"
                        whileHover={{ 
                          scale: 1.1,
                          transition: { duration: 0.2 }
                        }}
                      >
                        {model.accuracy}
                      </motion.div>
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Badge variant="secondary">{model.specialty}</Badge>
                      </motion.div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground leading-relaxed">
                        {model.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
          
          {/* Live Processing Indicator */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="text-center mt-16"
          >
            <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground bg-muted/50 px-4 py-2 rounded-full">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Zap className="w-4 h-4 text-ai-core" />
              </motion.div>
              <span>Live MesoNet CNN processing: &lt;2 seconds per analysis</span>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  )
}
