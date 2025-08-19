"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, Target, Zap } from 'lucide-react';

const accuracyData = [
  { dataset: 'FaceForensics++', accuracy: 96.8, samples: 1000 },
  { dataset: 'Celeb-DF', accuracy: 94.2, samples: 800 },
  { dataset: 'DFDC', accuracy: 91.5, samples: 1200 },
  { dataset: 'DeeperForensics', accuracy: 89.7, samples: 600 },
  { dataset: 'Real Videos', accuracy: 98.1, samples: 2000 }
];

const processingData = [
  { fileSize: '< 10MB', avgTime: 8.2, videoLength: '< 30s' },
  { fileSize: '10-50MB', avgTime: 24.7, videoLength: '30s-2min' },
  { fileSize: '50-100MB', avgTime: 45.3, videoLength: '2-5min' },
  { fileSize: '100-500MB', avgTime: 128.6, videoLength: '5-15min' },
  { fileSize: '> 500MB', avgTime: 310.4, videoLength: '> 15min' }
];

const modelContribution = [
  { name: 'YOLOv8-Face', value: 25, color: '#3b82f6' },
  { name: 'ResNet-50', value: 30, color: '#8b5cf6' },
  { name: 'Vision Transformer', value: 28, color: '#10b981' },
  { name: 'ViViT + LSTM', value: 17, color: '#f59e0b' }
];

export function PerformanceMetrics() {
  const [activeTab, setActiveTab] = useState('accuracy');

  return (
    <div className="max-w-6xl mx-auto">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="accuracy" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Accuracy Metrics
          </TabsTrigger>
          <TabsTrigger value="speed" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Processing Speed
          </TabsTrigger>
        </TabsList>

        <TabsContent value="accuracy" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid lg:grid-cols-3 gap-6"
          >
            {/* Accuracy Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  Detection Accuracy by Dataset
                </CardTitle>
                <CardDescription>
                  Performance across industry-standard deepfake datasets
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={accuracyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="dataset" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis domain={[85, 100]} />
                    <Tooltip 
                      formatter={(value) => [`${value}%`, 'Accuracy']}
                      labelFormatter={(label) => `Dataset: ${label}`}
                    />
                    <Bar 
                      dataKey="accuracy" 
                      fill="url(#accuracyGradient)"
                      radius={[4, 4, 0, 0]}
                    />
                    <defs>
                      <linearGradient id="accuracyGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#8b5cf6" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Model Contribution */}
            <Card>
              <CardHeader>
                <CardTitle>Model Contribution</CardTitle>
                <CardDescription>
                  How each AI model contributes to final accuracy
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={modelContribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {modelContribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {modelContribution.map((model, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: model.color }}
                        />
                        <span className="text-sm">{model.name}</span>
                      </div>
                      <Badge variant="secondary">{model.value}%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Accuracy Statistics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid md:grid-cols-4 gap-4"
          >
            {[
              { label: 'Overall Accuracy', value: '94.1%', color: 'text-green-600' },
              { label: 'False Positive Rate', value: '2.3%', color: 'text-orange-600' },
              { label: 'False Negative Rate', value: '3.6%', color: 'text-red-600' },
              { label: 'F1 Score', value: '0.947', color: 'text-blue-600' }
            ].map((stat, index) => (
              <Card key={index}>
                <CardContent className="p-6 text-center">
                  <div className={`text-2xl font-bold ${stat.color} mb-1`}>
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        </TabsContent>

        <TabsContent value="speed" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid lg:grid-cols-3 gap-6"
          >
            {/* Processing Time Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  Processing Time by File Size
                </CardTitle>
                <CardDescription>
                  Average analysis time across different media sizes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={processingData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fileSize" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value) => [`${value}s`, 'Processing Time']}
                      labelFormatter={(label) => `File Size: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="avgTime" 
                      stroke="#3b82f6"
                      strokeWidth={3}
                      dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                      activeDot={{ r: 8, stroke: '#3b82f6', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Processing Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Speed Statistics</CardTitle>
                <CardDescription>
                  Real-time processing capabilities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    2.4s
                  </div>
                  <div className="text-sm text-gray-600">Average per frame</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-1">
                    25fps
                  </div>
                  <div className="text-sm text-gray-600">Maximum throughput</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-1">
                    99.2%
                  </div>
                  <div className="text-sm text-gray-600">Uptime reliability</div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Processing Time Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Processing Time Breakdown</CardTitle>
                <CardDescription>
                  Time distribution across different analysis stages
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-5 gap-4">
                  {[
                    { stage: 'Media Loading', time: '0.8s', percentage: 15 },
                    { stage: 'Face Detection', time: '1.2s', percentage: 25 },
                    { stage: 'Feature Extraction', time: '1.8s', percentage: 35 },
                    { stage: 'Temporal Analysis', time: '0.9s', percentage: 18 },
                    { stage: 'Final Classification', time: '0.3s', percentage: 7 }
                  ].map((stage, index) => (
                    <div key={index} className="text-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                          style={{ width: `${stage.percentage}%` }}
                        />
                      </div>
                      <div className="text-sm font-medium text-gray-900 mb-1">
                        {stage.time}
                      </div>
                      <div className="text-xs text-gray-600">
                        {stage.stage}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}