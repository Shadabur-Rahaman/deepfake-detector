import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Clock, Target, Award } from "lucide-react"

const metrics = {
  accuracy: {
    title: "Detection Accuracy",
    icon: Target,
    data: [
      { label: "Video Analysis", value: 98.7, color: "text-success" },
      { label: "Image Detection", value: 99.2, color: "text-success" },
      { label: "Audio Analysis", value: 96.8, color: "text-success" },
      { label: "Real-time Stream", value: 97.4, color: "text-success" }
    ],
    summary: "Industry-leading accuracy across all media types"
  },
  speed: {
    title: "Processing Speed", 
    icon: Clock,
    data: [
      { label: "Image (1080p)", value: 85, color: "text-ai-core", suffix: "ms" },
      { label: "Video (30s clip)", value: 75, color: "text-ai-core", suffix: "s" },
      { label: "Live Stream", value: 90, color: "text-ai-core", suffix: "fps" },
      { label: "Batch Processing", value: 95, color: "text-ai-core", suffix: "files/min" }
    ],
    summary: "Optimized for real-time and batch processing"
  }
}

export function PerfMetrics() {
  const [activeTab, setActiveTab] = useState<'accuracy' | 'speed'>('accuracy')

  return (
    <section className="py-20 px-4 bg-muted/30">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-section font-bold mb-6">
            Performance Metrics
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Benchmark results from our latest AI models, tested against industry standards
            and real-world scenarios.
          </p>
        </motion.div>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full">
          <div className="flex justify-center mb-8">
            <TabsList className="grid w-full max-w-md grid-cols-2 bg-card border">
              <TabsTrigger value="accuracy" className="flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span>Accuracy</span>
              </TabsTrigger>
              <TabsTrigger value="speed" className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Speed</span>
              </TabsTrigger>
            </TabsList>
          </div>

          {Object.entries(metrics).map(([key, metric]) => (
            <TabsContent key={key} value={key} className="mt-0">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card className="bg-card/80 backdrop-blur-sm border-border/50">
                  <CardHeader className="text-center pb-6">
                    <div className="flex items-center justify-center space-x-3 mb-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center">
                        <metric.icon className="w-6 h-6 text-primary-foreground" />
                      </div>
                      <CardTitle className="text-2xl">{metric.title}</CardTitle>
                    </div>
                    <p className="text-muted-foreground">{metric.summary}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {metric.data.map((item, index) => (
                        <motion.div
                          key={item.label}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                          className="space-y-3"
                        >
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{item.label}</span>
                            <Badge variant="secondary" className={item.color}>
                              {item.value}
                              {key === 'accuracy' ? '%' : item.suffix}
                            </Badge>
                          </div>
                          <Progress 
                            value={key === 'accuracy' ? item.value : (item.value / 100) * 100} 
                            className="h-2"
                          />
                        </motion.div>
                      ))}
                    </div>

                    {key === 'accuracy' && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                        className="mt-8 p-4 bg-muted/50 rounded-lg border border-border/50"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <Award className="w-5 h-5 text-ai-core" />
                          <span className="font-semibold">Industry Recognition</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Consistently outperforms competing solutions in independent benchmarks
                          and peer-reviewed studies.
                        </p>
                      </motion.div>
                    )}

                    {key === 'speed' && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                        className="mt-8 p-4 bg-muted/50 rounded-lg border border-border/50"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <TrendingUp className="w-5 h-5 text-ai-neural" />
                          <span className="font-semibold">Optimized Infrastructure</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          GPU-accelerated processing with automatic scaling for enterprise workloads.
                        </p>
                      </motion.div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </section>
  )
}