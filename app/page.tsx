"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Shield, Zap, Target, Brain, Eye, CheckCircle2, TrendingUp, Clock } from 'lucide-react';
import Link from 'next/link';
import { HowiFakeThinks } from '@/components/how-ifake-thinks';
import { PerformanceMetrics } from '@/components/performance-metrics';

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation */}

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center"
            variants={staggerContainer}
            initial="initial"
            animate="animate"
          >
            <motion.div variants={fadeInUp}>
              <Badge className="mb-6 bg-blue-100 text-blue-800 hover:bg-blue-200">
                <Zap className="w-3 h-3 mr-1" />
                AI-Powered Detection
              </Badge>
            </motion.div>
            
            <motion.h1 
              className="text-4xl md:text-6xl font-bold text-gray-900 mb-6"
              variants={fadeInUp}
            >
              Detect Deepfakes with{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Advanced AI
              </span>
            </motion.h1>
            
            <motion.p 
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed"
              variants={fadeInUp}
            >
              iFake combines cutting-edge computer vision and machine learning to detect manipulated media 
              with unprecedented accuracy. Upload videos to get instant, reliable analysis.
            </motion.p>
            
            <motion.div 
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
              variants={fadeInUp}
            >
              <Button 
                size="lg" 
                asChild
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3"
              >
                <Link href="/try-it">
                  Start Detection <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              
              <Button 
                size="lg" 
                variant="outline" 
                asChild
                className="border-gray-300 hover:border-blue-400 hover:bg-blue-50"
              >
                <Link href="/features">
                  Learn More <Brain className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How iFake Thinks Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How iFake Thinks
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our transparent 5-step process breaks down exactly how we analyze media to detect deepfakes
            </p>
          </motion.div>
          
          <HowiFakeThinks />
        </div>
      </section>

      {/* Performance Metrics Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Performance Metrics
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Real-world performance data showing our AI's accuracy and processing capabilities
            </p>
          </motion.div>
          
          <PerformanceMetrics />
        </div>
      </section>

      {/* Simple Steps to Clarity Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Simple Steps to Clarity
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get started with deepfake detection in just three easy steps
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Upload Media",
                description: "Upload your video file or paste a YouTube URL for analysis",
                icon: <ArrowRight className="h-8 w-8" />,
                color: "from-blue-500 to-blue-600"
              },
              {
                step: "02", 
                title: "AI Analysis",
                description: "Our advanced AI models analyze the media for deepfake indicators",
                icon: <Brain className="h-8 w-8" />,
                color: "from-purple-500 to-purple-600"
              },
              {
                step: "03",
                title: "Get Results",
                description: "Receive detailed analysis with confidence scores and explanations",
                icon: <CheckCircle2 className="h-8 w-8" />,
                color: "from-green-500 to-green-600"
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="relative p-6 hover:shadow-lg transition-shadow duration-300 border-0 bg-gradient-to-br from-gray-50 to-white">
                  <div className={`absolute top-4 right-4 w-12 h-12 rounded-full bg-gradient-to-r ${item.color} flex items-center justify-center text-white text-xl font-bold`}>
                    {item.step}
                  </div>
                  <CardHeader className="pb-4">
                    <div className={`w-16 h-16 rounded-lg bg-gradient-to-r ${item.color} flex items-center justify-center text-white mb-4`}>
                      {item.icon}
                    </div>
                    <CardTitle className="text-xl font-semibold text-gray-900">
                      {item.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 leading-relaxed">
                      {item.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Detect Deepfakes?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join thousands of users who trust iFake for reliable deepfake detection. 
              Start your analysis today.
            </p>
            <Button 
              size="lg" 
              asChild
              className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-3"
            >
              <Link href="/try-it">
                Try iFake Now <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="h-6 w-6 text-blue-400" />
                <span className="text-xl font-bold">iFake</span>
              </div>
              <p className="text-gray-400">
                Advanced AI-powered deepfake detection for a safer digital world.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/try-it" className="hover:text-white transition-colors">Try It</Link></li>
                {/* <li><Link href="/api-docs" className="hover:text-white transition-colors">API Docs</Link></li> */}
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Connect</h3>
              <p className="text-gray-400">
                Follow us for the latest updates on AI and deepfake detection.
              </p>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 iFake. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}