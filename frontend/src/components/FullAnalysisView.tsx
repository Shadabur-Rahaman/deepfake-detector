import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, 
  ChevronUp, 
  Brain, 
  Activity, 
  Eye, 
  Clock, 
  Target,
  Zap,
  Shield,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { DetectionMetadata } from '@/utils/summaryGenerator';
import { ModelInformationCard } from './ModelInformationCard';

interface FullAnalysisViewProps {
  detectionResult: DetectionMetadata;
  showConfidence?: boolean;
  onToggleConfidence?: () => void;
  className?: string;
}

export const FullAnalysisView: React.FC<FullAnalysisViewProps> = ({ 
  detectionResult, 
  showConfidence = false,
  onToggleConfidence,
  className = '' 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getMetricIcon = (metric: string) => {
    switch (metric.toLowerCase()) {
      case 'confidence':
        return <Target className="w-4 h-4" />;
      case 'faces':
        return <Eye className="w-4 h-4" />;
      case 'processing':
        return <Clock className="w-4 h-4" />;
      case 'temporal':
        return <Activity className="w-4 h-4" />;
      case 'spatial':
        return <Brain className="w-4 h-4" />;
      case 'frequency':
        return <Zap className="w-4 h-4" />;
      case 'quality':
        return <Shield className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getMetricColor = (value: number, type: string) => {
    if (type === 'confidence' || type === 'quality' || type === 'temporal') {
      if (value >= 0.8) return 'text-green-600';
      if (value >= 0.6) return 'text-yellow-600';
      return 'text-red-600';
    }
    
    if (type === 'processing') {
      if (value <= 5) return 'text-green-600';
      if (value <= 10) return 'text-yellow-600';
      return 'text-red-600';
    }
    
    return 'text-blue-600';
  };

  const getProgressColor = (value: number, type: string) => {
    if (type === 'confidence' || type === 'quality' || type === 'temporal') {
      if (value >= 0.8) return 'bg-green-500';
      if (value >= 0.6) return 'bg-yellow-500';
      return 'bg-red-500';
    }
    return 'bg-blue-500';
  };

  const formatMetricValue = (value: number, type: string) => {
    switch (type) {
      case 'confidence':
      case 'quality':
      case 'temporal':
      case 'spatial':
      case 'frequency':
        return `${(value * 100).toFixed(1)}%`;
      case 'processing':
        return `${value.toFixed(1)}s`;
      case 'faces':
        return value.toString();
      default:
        return value.toFixed(2);
    }
  };

  const getRiskBadge = (value: number, type: string) => {
    if (type === 'confidence' || type === 'quality' || type === 'temporal') {
      if (value >= 0.8) return <Badge className="bg-green-100 text-green-800">Excellent</Badge>;
      if (value >= 0.6) return <Badge className="bg-yellow-100 text-yellow-800">Good</Badge>;
      return <Badge className="bg-red-100 text-red-800">Poor</Badge>;
    }
    
    if (type === 'processing') {
      if (value <= 5) return <Badge className="bg-green-100 text-green-800">Fast</Badge>;
      if (value <= 10) return <Badge className="bg-yellow-100 text-yellow-800">Moderate</Badge>;
      return <Badge className="bg-red-100 text-red-800">Slow</Badge>;
    }
    
    return null;
  };

  // Prepare metrics data
  const metrics = [
    ...(showConfidence ? [{
      key: 'confidence',
      label: 'Detection Confidence',
      value: detectionResult.confidence / 100 || 0,
      type: 'confidence',
      description: 'Overall confidence in the detection result'
    }] : []),
    {
      key: 'faces',
      label: 'Faces Analyzed',
      value: detectionResult.faces_detected || detectionResult.faces_analyzed || detectionResult.faces_found || 0,
      type: 'faces',
      description: 'Number of faces detected and analyzed'
    },
    {
      key: 'processing',
      label: 'Processing Time',
      value: detectionResult.processing_time || 0,
      type: 'processing',
      description: 'Time taken to complete the analysis'
    },
    // Temporal Consistency, Spatial Analysis, Frequency Analysis, and Face Quality Score removed per user request
    // Only showing Faces Analyzed and Processing Time as requested
  ].filter(metric => {
    // Only filter out if value is truly undefined/null, not 0 (0 is a valid value)
    // For faces and processing, 0 is not valid, but for scores, 0 might be valid
    if (metric.type === 'faces' || metric.type === 'processing') {
      return metric.value > 0;
    }
    // For score-based metrics, show if value is defined (including 0)
    return metric.value !== undefined && metric.value !== null;
  });

  return (
    <div className={`${className}`}>
      {/* Toggle Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex justify-center mb-4"
      >
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="neural-button hover-lift border-muted-foreground/30 text-muted-foreground hover:text-foreground hover:border-foreground/50"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-4 h-4 mr-2" />
              Hide Full Analysis
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4 mr-2" />
              🔍 View Full Analysis
            </>
          )}
        </Button>
      </motion.div>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="space-y-6">
              {/* Metrics Grid */}
              <Card className="neural-card border-border/30 bg-muted/20">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="w-5 h-5 text-primary" />
                    <span className="neural-text">Analysis Metrics</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {metrics.map((metric, index) => (
                      <motion.div
                        key={metric.key}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            {getMetricIcon(metric.type)}
                            <span className="text-sm font-medium neural-text">
                              {metric.label}
                            </span>
                          </div>
                          {getRiskBadge(metric.value, metric.type)}
                        </div>
                        
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className={`font-semibold ${getMetricColor(metric.value, metric.type)}`}>
                              {formatMetricValue(metric.value, metric.type)}
                            </span>
                          </div>
                          
                          {metric.type !== 'faces' && metric.type !== 'processing' && (
                            <Progress 
                              value={metric.value * 100} 
                              className="h-2"
                              style={{
                                '--progress-background': getProgressColor(metric.value, metric.type)
                              } as React.CSSProperties}
                            />
                          )}
                        </div>
                        
                        <p className="text-xs text-muted-foreground">
                          {metric.description}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Enhanced Model Information */}
              <ModelInformationCard 
                detectionResult={detectionResult} 
                showConfidence={showConfidence}
                onToggleConfidence={onToggleConfidence}
              />

              {/* Additional Flags */}
              {(detectionResult.metadata_flags && detectionResult.metadata_flags.length > 0) && (
                <Card className="neural-card border-border/30 bg-muted/20">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5 text-primary" />
                      <span className="neural-text">Detection Flags</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {detectionResult.metadata_flags.map((flag, index) => (
                        <Badge key={index} variant="destructive" className="neural-card">
                          {flag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FullAnalysisView;
