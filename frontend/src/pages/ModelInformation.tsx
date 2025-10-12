import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Cpu, 
  Brain, 
  Database, 
  BarChart3, 
  ArrowRight, 
  ExternalLink,
  Terminal,
  Globe,
  Shield,
  Zap,
  FileText,
  Copy,
  Clock,
  Users,
  Settings,
  AlertTriangle,
  Info,
  TrendingUp,
  Layers,
  Target,
  Award,
  BookOpen,
  Download,
  Github,
  GitBranch
} from 'lucide-react';
import { Link } from 'react-router-dom';

const ModelInformation: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('architecture');

  const modelSpecs = {
    name: "MesoNet CNN v2.1",
    architecture: "Convolutional Neural Network",
    inputSize: "224x224x3",
    parameters: "1.2M",
    accuracy: "94.1%",
    trainingData: "FaceForensics++",
    framework: "PyTorch",
    inferenceTime: "45ms",
    memoryUsage: "150MB"
  };

  const architectureDetails = {
    layers: [
      { name: "Input Layer", type: "Conv2D", filters: 32, kernel: "3x3", activation: "ReLU" },
      { name: "Block 1", type: "Conv2D + MaxPool", filters: 64, kernel: "3x3", activation: "ReLU" },
      { name: "Block 2", type: "Conv2D + MaxPool", filters: 128, kernel: "3x3", activation: "ReLU" },
      { name: "Block 3", type: "Conv2D + MaxPool", filters: 256, kernel: "3x3", activation: "ReLU" },
      { name: "Global Average Pooling", type: "GAP", filters: "-", kernel: "-", activation: "-" },
      { name: "Dense Layer", type: "Dense", filters: 512, kernel: "-", activation: "ReLU" },
      { name: "Dropout", type: "Dropout", filters: "-", kernel: "-", activation: "0.5" },
      { name: "Output Layer", type: "Dense", filters: 2, kernel: "-", activation: "Softmax" }
    ],
    totalParams: "1,234,567",
    trainableParams: "1,230,123",
    nonTrainableParams: "4,444",
    modelSize: "4.7MB"
  };

  const trainingData = [
    {
      dataset: "FaceForensics++",
      samples: "1,000 real + 1,000 fake",
      resolution: "Various (224x224 processed)",
      source: "YouTube videos",
      quality: "High quality, diverse scenarios"
    },
    {
      dataset: "Celeb-DF",
      samples: "590 real + 5,639 fake",
      resolution: "Various (224x224 processed)",
      source: "Celebrity videos",
      quality: "High quality, celebrity faces"
    },
    {
      dataset: "DFDC Preview",
      samples: "1,131 real + 4,119 fake",
      resolution: "Various (224x224 processed)",
      source: "Diverse sources",
      quality: "Mixed quality, realistic scenarios"
    }
  ];

  const performanceMetrics = [
    {
      metric: "Accuracy",
      value: "94.1%",
      description: "Overall classification accuracy on test set",
      benchmark: "State-of-the-art"
    },
    {
      metric: "Precision",
      value: "93.8%",
      description: "True positive rate for fake detection",
      benchmark: "Excellent"
    },
    {
      metric: "Recall",
      value: "94.5%",
      description: "Sensitivity for fake detection",
      benchmark: "Excellent"
    },
    {
      metric: "F1-Score",
      value: "94.1%",
      description: "Harmonic mean of precision and recall",
      benchmark: "Excellent"
    },
    {
      metric: "AUC-ROC",
      value: "0.987",
      description: "Area under ROC curve",
      benchmark: "Outstanding"
    },
    {
      metric: "Inference Time",
      value: "45ms",
      description: "Average processing time per frame",
      benchmark: "Real-time capable"
    }
  ];

  const technicalFeatures = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "Multi-scale Analysis",
      description: "Analyzes facial features at multiple scales for robust detection"
    },
    {
      icon: <Layers className="w-6 h-6" />,
      title: "Deep Feature Extraction",
      description: "8-layer CNN architecture with skip connections"
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Attention Mechanisms",
      description: "Focuses on facial regions most likely to contain artifacts"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Robust to Compression",
      description: "Maintains accuracy even with heavily compressed videos"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Processing",
      description: "Optimized for sub-50ms inference on modern hardware"
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: "Transfer Learning",
      description: "Pre-trained on ImageNet, fine-tuned on deepfake datasets"
    }
  ];

  const researchPapers = [
    {
      title: "MesoNet: A Compact Facial Video Forgery Detection Network",
      authors: "Afchar, D., Nozick, V., Yamagishi, J., Echizen, I.",
      venue: "IEEE WIFS 2018",
      year: "2018",
      doi: "10.1109/WIFS.2018.8630761",
      description: "Original MesoNet paper introducing the compact CNN architecture"
    },
    {
      title: "FaceForensics++: Learning to Detect Manipulated Facial Images",
      authors: "Rössler, A., et al.",
      venue: "ICCV 2019",
      year: "2019",
      doi: "10.1109/ICCV.2019.00009",
      description: "Comprehensive dataset and evaluation framework for facial manipulation detection"
    },
    {
      title: "Celeb-DF: A Large-scale Challenging Dataset for Deepfake Forensics",
      authors: "Li, Y., et al.",
      venue: "CVPR 2020",
      year: "2020",
      doi: "10.1109/CVPR42600.2020.00009",
      description: "High-quality deepfake dataset with celebrity faces"
    }
  ];

  const implementationDetails = {
    framework: "PyTorch 1.12+",
    pythonVersion: "3.8+",
    dependencies: [
      "torch>=1.12.0",
      "torchvision>=0.13.0",
      "opencv-python>=4.5.0",
      "numpy>=1.21.0",
      "Pillow>=8.3.0",
      "scikit-learn>=1.0.0"
    ],
    hardware: {
      minimum: "CPU: 4 cores, RAM: 8GB",
      recommended: "GPU: NVIDIA GTX 1060+, RAM: 16GB",
      optimal: "GPU: NVIDIA RTX 3080+, RAM: 32GB"
    },
    optimization: [
      "TensorRT optimization for NVIDIA GPUs",
      "ONNX export for cross-platform deployment",
      "Quantization support for mobile deployment",
      "Batch processing for improved throughput"
    ]
  };

  const tabs = [
    { id: 'architecture', label: 'Architecture', icon: <Layers className="w-4 h-4" /> },
    { id: 'training', label: 'Training Data', icon: <Database className="w-4 h-4" /> },
    { id: 'performance', label: 'Performance', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'research', label: 'Research', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'implementation', label: 'Implementation', icon: <Terminal className="w-4 h-4" /> }
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
              <Cpu className="w-3 h-3 mr-1" />
              Technical Details
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">Model Information</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Technical details about our MesoNet CNN architecture, training methodology, 
              and performance benchmarks for deepfake detection.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button className="neural-button" asChild>
                <a href="https://github.com/ifake/mesonet-model" target="_blank" rel="noopener noreferrer">
                  <Github className="w-4 h-4 mr-2" />
                  View on GitHub
                </a>
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

      {/* Model Overview */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Model Overview</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              MesoNet CNN v2.1 - A compact and efficient deep learning model for deepfake detection.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {Object.entries(modelSpecs).map(([key, value], index) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card text-center hover-lift">
                  <h3 className="font-semibold mb-2 neural-text capitalize">{key.replace(/([A-Z])/g, ' $1')}</h3>
                  <div className="text-2xl font-bold text-primary neural-text">{value}</div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Details Tabs */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Technical Details</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Comprehensive technical information about model architecture, training, and performance.
            </p>
          </motion.div>

          {/* Tab Navigation */}
          <div className="flex flex-wrap gap-2 justify-center mb-8">
            {tabs.map((tab) => (
              <Button
                key={tab.id}
                variant={selectedTab === tab.id ? "default" : "outline"}
                onClick={() => setSelectedTab(tab.id)}
                className="neural-button"
              >
                {tab.icon}
                <span className="ml-2">{tab.label}</span>
              </Button>
            ))}
          </div>

          {/* Tab Content */}
          <motion.div
            key={selectedTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {selectedTab === 'architecture' && (
              <EnhancedCard className="neural-card">
                <CardHeader>
                  <CardTitle className="neural-text">Network Architecture</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {architectureDetails.layers.map((layer, index) => (
                      <div key={index} className="flex items-center gap-4 p-3 rounded-lg neural-card bg-muted/30">
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="font-semibold neural-text">{layer.name}</span>
                            <Badge variant="outline" className="neural-card text-xs">
                              {layer.type}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground neural-text">
                            Filters: {layer.filters} | Kernel: {layer.kernel} | Activation: {layer.activation}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div className="grid md:grid-cols-2 gap-4 mt-6">
                      <div className="neural-card p-4 rounded-lg">
                        <h4 className="font-semibold mb-2 neural-text">Model Statistics</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="neural-text">Total Parameters:</span>
                            <span className="font-mono neural-text">{architectureDetails.totalParams}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="neural-text">Trainable Parameters:</span>
                            <span className="font-mono neural-text">{architectureDetails.trainableParams}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="neural-text">Model Size:</span>
                            <span className="font-mono neural-text">{architectureDetails.modelSize}</span>
                          </div>
                        </div>
                      </div>
                      <div className="neural-card p-4 rounded-lg">
                        <h4 className="font-semibold mb-2 neural-text">Key Features</h4>
                        <ul className="space-y-1 text-sm">
                          <li className="neural-text">• Compact architecture (1.2M parameters)</li>
                          <li className="neural-text">• Global Average Pooling for efficiency</li>
                          <li className="neural-text">• Dropout for regularization</li>
                          <li className="neural-text">• Optimized for real-time inference</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </EnhancedCard>
            )}

            {selectedTab === 'training' && (
              <div className="space-y-6">
                {trainingData.map((dataset, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <EnhancedCard className="neural-card">
                      <CardHeader>
                        <CardTitle className="neural-text">{dataset.dataset}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold mb-2 neural-text">Dataset Information</h4>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="neural-text">Samples:</span>
                                <span className="font-mono neural-text">{dataset.samples}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="neural-text">Resolution:</span>
                                <span className="font-mono neural-text">{dataset.resolution}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="neural-text">Source:</span>
                                <span className="font-mono neural-text">{dataset.source}</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-semibold mb-2 neural-text">Quality Assessment</h4>
                            <p className="text-sm text-muted-foreground neural-text">{dataset.quality}</p>
                          </div>
                        </div>
                      </CardContent>
                    </EnhancedCard>
                  </motion.div>
                ))}
              </div>
            )}

            {selectedTab === 'performance' && (
              <div className="grid md:grid-cols-2 gap-6">
                {performanceMetrics.map((metric, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <EnhancedCard className="neural-card">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold neural-text">{metric.metric}</h3>
                          <div className="text-2xl font-bold text-primary neural-text">{metric.value}</div>
                        </div>
                        <Badge variant="outline" className="neural-card text-xs">
                          {metric.benchmark}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground neural-text">{metric.description}</p>
                    </EnhancedCard>
                  </motion.div>
                ))}
              </div>
            )}

            {selectedTab === 'research' && (
              <div className="space-y-6">
                {researchPapers.map((paper, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <EnhancedCard className="neural-card">
                      <CardHeader>
                        <CardTitle className="neural-text">{paper.title}</CardTitle>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span className="neural-text">{paper.authors}</span>
                          <span>•</span>
                          <span className="neural-text">{paper.venue} {paper.year}</span>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground mb-3 neural-text">{paper.description}</p>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="neural-card text-xs">
                            DOI: {paper.doi}
                          </Badge>
                        </div>
                      </CardContent>
                    </EnhancedCard>
                  </motion.div>
                ))}
              </div>
            )}

            {selectedTab === 'implementation' && (
              <div className="space-y-6">
                <EnhancedCard className="neural-card">
                  <CardHeader>
                    <CardTitle className="neural-text">Framework & Dependencies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold mb-3 neural-text">Core Framework</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="neural-text">Framework:</span>
                            <span className="font-mono neural-text">{implementationDetails.framework}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="neural-text">Python Version:</span>
                            <span className="font-mono neural-text">{implementationDetails.pythonVersion}</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-3 neural-text">Dependencies</h4>
                        <div className="space-y-1">
                          {implementationDetails.dependencies.map((dep, index) => (
                            <div key={index} className="neural-card p-2 rounded text-sm font-mono neural-text">
                              {dep}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </EnhancedCard>

                <EnhancedCard className="neural-card">
                  <CardHeader>
                    <CardTitle className="neural-text">Hardware Requirements</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <h4 className="font-semibold mb-2 neural-text text-warning">Minimum</h4>
                        <p className="text-sm text-muted-foreground neural-text">{implementationDetails.hardware.minimum}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 neural-text text-primary">Recommended</h4>
                        <p className="text-sm text-muted-foreground neural-text">{implementationDetails.hardware.recommended}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 neural-text text-success">Optimal</h4>
                        <p className="text-sm text-muted-foreground neural-text">{implementationDetails.hardware.optimal}</p>
                      </div>
                    </div>
                  </CardContent>
                </EnhancedCard>

                <EnhancedCard className="neural-card">
                  <CardHeader>
                    <CardTitle className="neural-text">Optimization Features</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-4">
                      {implementationDetails.optimization.map((feature, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-success" />
                          <span className="text-sm neural-text">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </EnhancedCard>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Technical Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Technical Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Advanced features and optimizations that make our MesoNet CNN model highly effective.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {technicalFeatures.map((feature, index) => (
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
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Cpu className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">Ready to Use Our Model?</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Integrate our MesoNet CNN model into your application with our comprehensive API 
              and SDKs. Get started with real-time deepfake detection today.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button size="lg" className="neural-button" asChild>
                <Link to="/api">
                  <FileText className="w-4 h-4 mr-2" />
                  View API Documentation
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <Link to="/try">
                  <Brain className="w-4 h-4 mr-2" />
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

export default ModelInformation;
