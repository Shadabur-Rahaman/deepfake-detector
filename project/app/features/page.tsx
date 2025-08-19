"use client";

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Brain, Eye, Zap, Shield, Target, Layers, GitBranch, Database, Cpu } from 'lucide-react';
import Link from 'next/link';

export default function Features() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation */}


      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge className="mb-6 bg-blue-100 text-blue-800">
              <Brain className="w-3 h-3 mr-1" />
              Advanced Technology
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Technology Behind iFake
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover the cutting-edge AI models and architecture that power our deepfake detection system
            </p>
          </motion.div>
        </div>
      </section>

      {/* Detection Architecture */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.h2 
            className="text-3xl font-bold text-center text-gray-900 mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Detection Architecture
          </motion.h2>
          
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <Card className="p-8">
                <CardHeader>
                  <CardTitle className="text-2xl mb-4">Multi-Stage Pipeline</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {[
                    { icon: <Database className="h-6 w-6" />, title: "Input Media", desc: "Videos, images, YouTube URLs" },
                    { icon: <Eye className="h-6 w-6" />, title: "Preprocessing", desc: "Frame extraction, normalization" },
                    { icon: <Target className="h-6 w-6" />, title: "Face Detection", desc: "YOLOv8-Face model" },
                    { icon: <Brain className="h-6 w-6" />, title: "Feature Analysis", desc: "ResNet-50, ViT processing" },
                    { icon: <Zap className="h-6 w-6" />, title: "Temporal Analysis", desc: "ViViT, LSTM models" },
                    { icon: <Shield className="h-6 w-6" />, title: "Final Verdict", desc: "Ensemble classification" }
                  ].map((stage, index) => (
                    <div key={index} className="flex items-start gap-4">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center text-white flex-shrink-0">
                        {stage.icon}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{stage.title}</h4>
                        <p className="text-gray-600 text-sm">{stage.desc}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="space-y-6"
            >
              <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
                <div className="flex items-center gap-3 mb-4">
                  <Cpu className="h-8 w-8 text-blue-600" />
                  <h3 className="text-xl font-semibold">Parallel Processing</h3>
                </div>
                <p className="text-gray-700">
                  Our architecture processes multiple aspects simultaneously, reducing analysis time 
                  while maintaining high accuracy through distributed computing.
                </p>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <div className="flex items-center gap-3 mb-4">
                  <Layers className="h-8 w-8 text-green-600" />
                  <h3 className="text-xl font-semibold">Ensemble Learning</h3>
                </div>
                <p className="text-gray-700">
                  Multiple specialized models work together, each contributing their strengths 
                  to achieve superior detection accuracy across various deepfake types.
                </p>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
                <div className="flex items-center gap-3 mb-4">
                  <GitBranch className="h-8 w-8 text-purple-600" />
                  <h3 className="text-xl font-semibold">Adaptive Pipeline</h3>
                </div>
                <p className="text-gray-700">
                  The system adapts its processing strategy based on media type, quality, and 
                  content characteristics for optimal performance.
                </p>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Core AI Models */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Core AI Models</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Each model in our ensemble brings specialized capabilities to detect different aspects of deepfakes
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                name: "YOLOv8-Face",
                category: "Face Detection",
                description: "Ultra-fast face detection and localization with 99.1% accuracy on facial regions",
                features: ["Real-time processing", "Multi-face detection", "Rotation invariant", "Edge optimization"],
                color: "from-blue-500 to-blue-600"
              },
              {
                name: "ResNet-50",
                category: "Spatial Analysis", 
                description: "Deep residual network for identifying spatial artifacts and inconsistencies in facial features",
                features: ["2048-D feature vectors", "Transfer learning", "Spatial attention", "Artifact detection"],
                color: "from-purple-500 to-purple-600"
              },
              {
                name: "Vision Transformer",
                category: "Global Context",
                description: "Transformer architecture analyzing global image patterns and contextual inconsistencies",
                features: ["Self-attention mechanism", "Patch-based analysis", "Global feature fusion", "Context awareness"],
                color: "from-green-500 to-green-600"
              },
              {
                name: "ViViT",
                category: "Video Analysis",
                description: "Video Vision Transformer specialized in temporal consistency analysis across frames",
                features: ["3D attention", "Temporal modeling", "Motion analysis", "Frame coherence"],
                color: "from-orange-500 to-orange-600"
              },
              {
                name: "LSTM Networks",
                category: "Sequence Modeling",
                description: "Long Short-Term Memory networks for sequential pattern analysis in video streams",
                features: ["Temporal dependencies", "Sequence memory", "Pattern recognition", "State persistence"],
                color: "from-red-500 to-red-600"
              },
              {
                name: "Ensemble Classifier",
                category: "Final Decision",
                description: "Gradient boosting classifier combining all model outputs for final verdict",
                features: ["Model fusion", "Confidence scoring", "Weighted voting", "Uncertainty estimation"],
                color: "from-indigo-500 to-indigo-600"
              }
            ].map((model, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${model.color} flex items-center justify-center text-white mb-4`}>
                      <Brain className="h-6 w-6" />
                    </div>
                    <Badge className="w-fit mb-2">{model.category}</Badge>
                    <CardTitle className="text-xl">{model.name}</CardTitle>
                    <CardDescription className="leading-relaxed">
                      {model.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {model.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Training Methodology */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Training Methodology</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our models are trained on diverse datasets using advanced techniques to ensure robust performance
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <Card className="p-8">
                <CardHeader>
                  <CardTitle className="text-2xl mb-6">Dataset Diversity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { dataset: "FaceForensics++", samples: "1,000+ videos", type: "Face swap, face reenactment" },
                    { dataset: "Celeb-DF", samples: "800+ videos", type: "Celebrity deepfakes" },
                    { dataset: "DFDC", samples: "1,200+ videos", type: "Facebook competition dataset" },
                    { dataset: "DeeperForensics", samples: "600+ videos", type: "High-quality deepfakes" },
                    { dataset: "Real Videos", samples: "2,000+ videos", type: "Authentic content baseline" }
                  ].map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-semibold text-gray-900">{item.dataset}</h4>
                        <p className="text-sm text-gray-600">{item.type}</p>
                      </div>
                      <Badge variant="outline">{item.samples}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="space-y-6"
            >
              <Card className="p-6">
                <h3 className="text-xl font-semibold mb-4">Training Techniques</h3>
                <ul className="space-y-3">
                  {[
                    "Transfer learning from pre-trained models",
                    "Data augmentation with geometric transformations",
                    "Adversarial training for robustness",
                    "Cross-validation with temporal splits",
                    "Ensemble training with diverse architectures",
                    "Continuous learning from new deepfake types"
                  ].map((technique, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-gray-700">{technique}</span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50">
                <h3 className="text-xl font-semibold mb-4">Performance Optimization</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">94.1%</div>
                    <div className="text-sm text-gray-600">Overall Accuracy</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">2.4s</div>
                    <div className="text-sm text-gray-600">Avg Processing</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">0.947</div>
                    <div className="text-sm text-gray-600">F1 Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">99.2%</div>
                    <div className="text-sm text-gray-600">Uptime</div>
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Experience Our Technology
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              See how our advanced AI models work together to detect deepfakes with industry-leading accuracy.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="bg-white text-blue-600 hover:bg-blue-50">
                <Link href="/try-it">
                  Try Detection Now
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="border-white text-white hover:bg-white hover:text-blue-600">
                <Link href="/api-docs">
                  View API Docs
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}