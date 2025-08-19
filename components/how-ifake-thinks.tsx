"use client";

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, Brain, Zap, Target, Shield, ArrowRight } from 'lucide-react';

const steps = [
  {
    step: 1,
    title: "Media Ingestion",
    description: "Upload videos, or provide YouTube URLs for comprehensive analysis",
    icon: <Eye className="h-8 w-8" />,
    color: "from-blue-500 to-blue-600",
    details: "Supports MP4, MOV, formats and direct YouTube URL integration"
  },
  {
    step: 2,
    title: "Face Detection",
    description: "YOLOv8-Face model identifies and extracts facial regions with high precision",
    icon: <Target className="h-8 w-8" />,
    color: "from-purple-500 to-purple-600",
    details: "Advanced object detection specialized for facial recognition"
  },
  {
    step: 3,
    title: "Feature Extraction",
    description: "ResNet-50 and Vision Transformer analyze spatial artifacts and inconsistencies",
    icon: <Brain className="h-8 w-8" />,
    color: "from-green-500 to-green-600",
    details: "Deep learning models extract 2048+ dimensional feature vectors"
  },
  {
    step: 4,
    title: "Temporal Analysis",
    description: "ViViT and LSTM models examine frame-to-frame consistency patterns",
    icon: <Zap className="h-8 w-8" />,
    color: "from-orange-500 to-orange-600",
    details: "Analyzes temporal inconsistencies across video sequences"
  },
  {
    step: 5,
    title: "Final Verdict",
    description: "Ensemble classifier provides confidence score and detailed analysis report",
    icon: <Shield className="h-8 w-8" />,
    color: "from-red-500 to-red-600",
    details: "Gradient boosting combines all models for final prediction"
  }
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

export function HowiFakeThinks() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="grid lg:grid-cols-5 gap-6"
    >
      {steps.map((step, index) => (
        <motion.div
          key={step.step}
          variants={cardVariants}
          className="relative"
        >
          <Card className="h-full hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border-0 bg-gradient-to-br from-white to-gray-50">
            <CardHeader className="text-center">
              <div className={`w-16 h-16 mx-auto rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center text-white mb-4`}>
                {step.icon}
              </div>
              <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r ${step.color} text-white text-sm font-bold mb-2`}>
                {step.step}
              </div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                {step.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <CardDescription className="text-gray-600 mb-3 leading-relaxed">
                {step.description}
              </CardDescription>
              <p className="text-sm text-gray-500 italic">
                {step.details}
              </p>
            </CardContent>
          </Card>
          
          {/* Arrow connector for desktop */}
          {index < steps.length - 1 && (
            <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
              <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                <ArrowRight className="h-4 w-4 text-gray-500" />
              </div>
            </div>
          )}
        </motion.div>
      ))}
    </motion.div>
  );
}