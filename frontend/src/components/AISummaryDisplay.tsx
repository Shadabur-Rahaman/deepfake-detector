import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Eye, EyeOff, Brain, Zap, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { generateDetectionSummary, generateDetectionSummarySync, DetectionMetadata, SummaryResult } from '@/utils/summaryGenerator';

interface AISummaryDisplayProps {
  detectionResult: DetectionMetadata;
  showConfidence?: boolean;
  className?: string;
}

export const AISummaryDisplay: React.FC<AISummaryDisplayProps> = ({ 
  detectionResult, 
  showConfidence = false,
  className = '' 
}) => {
  const [summary, setSummary] = useState<SummaryResult | null>(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [isGenerating, setIsGenerating] = useState(true);

  useEffect(() => {
    // Generate AI-powered summary
    const generateSummary = async () => {
      setIsGenerating(true);
      
      try {
        // Generate AI-powered summary (async, tries AI API first)
        const generatedSummary = await generateDetectionSummary(detectionResult);
        setSummary(generatedSummary);
      } catch (error) {
        console.error('Failed to generate AI summary:', error);
        // Fallback to synchronous template-based summary
        const generatedSummary = generateDetectionSummarySync(detectionResult);
        setSummary(generatedSummary);
      } finally {
        setIsGenerating(false);
      }
    };

    generateSummary();
  }, [detectionResult]);

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'moderate':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <Brain className="w-4 h-4 text-blue-500" />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600';
      case 'moderate':
        return 'text-yellow-600';
      case 'high':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  };

  if (isGenerating) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`neural-card p-6 rounded-xl bg-gradient-to-br from-muted/30 to-muted/10 ${className}`}
      >
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
          <span className="text-sm text-muted-foreground neural-text">
            AI is analyzing detection results...
          </span>
        </div>
        
        <div className="space-y-2">
          <div className="h-4 bg-muted/40 rounded animate-pulse" />
          <div className="h-4 bg-muted/40 rounded animate-pulse w-3/4" />
          <div className="h-4 bg-muted/40 rounded animate-pulse w-1/2" />
        </div>
      </motion.div>
    );
  }

  if (!summary) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`neural-card p-6 rounded-xl bg-gradient-to-br from-muted/30 to-muted/10 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            {getRiskIcon(summary.riskLevel)}
            <span className="text-sm font-medium neural-text">AI Analysis Summary</span>
            {summary.aiGenerated && (
              <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-600 border-blue-500/30 dark:bg-blue-500/20 dark:text-blue-300">
                <Brain className="w-3 h-3 mr-1" />
                AI Generated
              </Badge>
            )}
          </div>
          <Badge 
            variant="outline" 
            className={`neural-card border-current ${getRiskColor(summary.riskLevel)}`}
          >
            {summary.riskLevel.charAt(0).toUpperCase() + summary.riskLevel.slice(1)} Risk
          </Badge>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          className="neural-button hover-lift text-muted-foreground hover:text-foreground"
        >
          {showTechnicalDetails ? (
            <>
              <EyeOff className="w-4 h-4 mr-2" />
              Hide Details
            </>
          ) : (
            <>
              <Eye className="w-4 h-4 mr-2" />
              View Details
            </>
          )}
        </Button>
      </div>

      {/* Main Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-4"
      >
        <p className="text-muted-foreground leading-relaxed neural-text text-base">
          {summary.summary}
        </p>
      </motion.div>

      {/* Confidence Explanation - Only show if confidence is visible */}
      {showConfidence && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-4"
        >
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Zap className="w-4 h-4" />
            <span className="neural-text">{summary.confidenceExplanation}</span>
          </div>
        </motion.div>
      )}

      {/* Technical Details (Expandable) */}
      <AnimatePresence>
        {showTechnicalDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <Card className="neural-card border-border/30 bg-muted/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Brain className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium neural-text">Technical Analysis</span>
                </div>
                
                <div className="space-y-2">
                  {summary.technicalDetails.map((detail, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-muted-foreground neural-text">{detail}</span>
                      <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse" />
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Decorative Elements */}
      <div className="absolute -top-2 -right-2 w-4 h-4 bg-primary/20 rounded-full animate-pulse delay-500" />
      <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-accent/20 rounded-full animate-pulse delay-1500" />
    </motion.div>
  );
};

export default AISummaryDisplay;
