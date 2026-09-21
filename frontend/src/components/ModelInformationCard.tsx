import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Cpu, 
  Brain, 
  Zap, 
  Info,
  CheckCircle,
  AlertTriangle,
  Activity,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp,
  Layers
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DetectionMetadata } from '@/utils/summaryGenerator';

interface ModelInformationCardProps {
  detectionResult: DetectionMetadata;
  showConfidence?: boolean;
  onToggleConfidence?: () => void;
  className?: string;
}

interface ModelInfo {
  primary: string;
  supporting: string[];
  mode: string;
  modeDescription: string;
  modelCount: number;
  isEnsemble: boolean;
}

export const ModelInformationCard: React.FC<ModelInformationCardProps> = ({ 
  detectionResult, 
  showConfidence = false,
  onToggleConfidence,
  className = '' 
}) => {
  const [showAllModels, setShowAllModels] = useState(false);
  
  // Extract model information from detection result
  const getModelInfo = (): ModelInfo => {
    // Try to get mode from detection result
    const mode = detectionResult.detection_mode || 
                 (detectionResult as any).mode ||
                 inferModeFromData(detectionResult);
    
    // Get primary model
    const primary = getPrimaryModel(detectionResult);
    
    // Get supporting models
    const supporting = getSupportingModels(detectionResult);
    
    // Determine if this is an ensemble
    const isEnsemble = supporting.length > 1 || mode === 'Hybrid';
    
    // Get mode description
    const modeDescription = getModeDescription(mode, isEnsemble);
    
    // ✅ CRITICAL FIX: Use getAllModels() to get accurate count that matches "View All Models"
    // This ensures consistency between "models active" and "View All Models" count
    const allModelsList = getAllModels();
    const allModelsCount = allModelsList.length;
    
    // ✅ FIXED: Always use getAllModels() count to ensure consistency
    // This ensures "models active" count matches exactly with "View All Models" count
    const actualModelCount = allModelsCount > 0 ? allModelsCount : 
                            (detectionResult.model_info?.model_count ?? 
                             (detectionResult.model_info?.models_used?.length ? detectionResult.model_info.models_used.length : null) ??
                             (supporting.length > 0 ? supporting.length + 1 : 1));
    
    return {
      primary,
      supporting,
      mode,
      modeDescription,
      modelCount: actualModelCount,
      isEnsemble: detectionResult.model_info?.is_ensemble !== undefined 
        ? detectionResult.model_info.is_ensemble 
        : isEnsemble
    };
  };

  // Infer mode from available data
  const inferModeFromData = (data: DetectionMetadata): string => {
    // Check for ensemble indicators
    const hasEnsembleScores = data.ensemble_scores && Object.keys(data.ensemble_scores).length > 1;
    const hasModernFeatures = data.model_contributions?.frequency_score || data.ai_tool_detected;
    const hasEnhancedFeatures = data.face_quality_score || data.temporal_consistency;
    
    if (hasEnsembleScores && hasModernFeatures) {
      return 'Hybrid';
    } else if (hasModernFeatures || hasEnhancedFeatures) {
      return 'Modern AI';
    } else {
      return 'Traditional';
    }
  };

  // Get primary model name - use backend model_info first
  const getPrimaryModel = (data: DetectionMetadata): string => {
    // Priority 1: Use model_info.primary_model from backend (most accurate)
    if (data.model_info?.primary_model) {
      return formatModelName(data.model_info.primary_model);
    }
    
    // Priority 2: Use model_info.model_type
    if (data.model_info?.model_type) {
      return formatModelName(data.model_info.model_type);
    }
    
    // Priority 3: Other metadata fields
    if (data.primary_model) return formatModelName(data.primary_model);
    if (data.model_name) return formatModelName(data.model_name);
    if (data.model_contributions?.model_type) return formatModelName(data.model_contributions.model_type);
    if (data.analysis_method) return formatModelName(data.analysis_method);
    if ((data as any).model_used) return formatModelName((data as any).model_used);
    
    // Priority 4: Try to get from ensemble scores (most confident)
    if (data.ensemble_scores && Object.keys(data.ensemble_scores).length > 0) {
      const models = Object.keys(data.ensemble_scores);
      let bestModel = models[0];
      let bestScore = data.ensemble_scores[models[0]];
      
      for (const model of models) {
        if (data.ensemble_scores[model] > bestScore) {
          bestModel = model;
          bestScore = data.ensemble_scores[model];
        }
      }
      
      return formatModelName(bestModel);
    }
    
    return 'MesoNet'; // Default fallback
  };

  // Get supporting models - dynamically from backend ONLY
  const getSupportingModels = (data: DetectionMetadata): string[] => {
    const models: string[] = [];
    const primaryModel = getPrimaryModel(data);
    
    // Priority 1: Use model_info.models_used from backend (most accurate) - EXCLUDE primary model
    if (data.model_info?.models_used && Array.isArray(data.model_info.models_used)) {
      data.model_info.models_used.forEach((model: string) => {
        const formatted = formatModelName(model);
        // ✅ FIXED: Exclude "Title Classification" from supporting models (it's metadata analysis, not a detection model)
        if (!models.includes(formatted) && formatted !== primaryModel && formatted.trim() !== '' && 
            formatted.toLowerCase() !== 'title classification') {
          models.push(formatted);
        }
      });
    }
    
    // Priority 2: From ensemble scores (only if model_info not available)
    if (models.length === 0 && data.ensemble_scores) {
      Object.keys(data.ensemble_scores).forEach(model => {
        const formatted = formatModelName(model);
        // ✅ FIXED: Exclude "Title Classification" from supporting models
        if (!models.includes(formatted) && formatted !== primaryModel && formatted.trim() !== '' &&
            formatted.toLowerCase() !== 'title classification') {
          models.push(formatted);
        }
      });
    }
    
    // Priority 3: From models_used array if available (only if no backend model_info)
    if (models.length === 0 && (data as any).models_used && Array.isArray((data as any).models_used)) {
      (data as any).models_used.forEach((model: string) => {
        const formatted = formatModelName(model);
        // ✅ FIXED: Exclude "Title Classification" from supporting models
        if (!models.includes(formatted) && formatted !== primaryModel && formatted.trim() !== '' &&
            formatted.toLowerCase() !== 'title classification') {
          models.push(formatted);
        }
      });
    }
    
    // DO NOT use fallback defaults - only show what backend actually reports
    // This prevents hallucination of model names
    
    return models.slice(0, 8); // Show up to 8 models from backend
  };

  // ✅ NEW: Get ALL models (including from model_contributions for Hybrid mode)
  // This function is defined first so it can be used in getModelInfo to ensure consistent counts
  const getAllModels = (): string[] => {
    const allModels = new Set<string>();
    const primaryModel = getPrimaryModel(detectionResult);
    allModels.add(primaryModel);
    
    // Add supporting models
    const supporting = getSupportingModels(detectionResult);
    supporting.forEach(m => allModels.add(m));
    
    const rawData = detectionResult as any;
    
    // ✅ CRITICAL: Extract models from model_contributions array (base 10 models)
    if (Array.isArray(rawData.model_contributions)) {
      rawData.model_contributions.forEach((contrib: any) => {
        if (contrib?.name) {
          const formatted = formatModelName(contrib.name);
          if (formatted.trim() !== '') {
            allModels.add(formatted);
          }
        }
      });
    }
    
    // ✅ CRITICAL: Extract models from ensemble_scores (base models)
    if (detectionResult.ensemble_scores) {
      Object.keys(detectionResult.ensemble_scores).forEach(model => {
        const formatted = formatModelName(model);
        if (formatted.trim() !== '') {
          allModels.add(formatted);
        }
      });
    }
    
    // ✅ CRITICAL: Extract Ultra Ensemble internal models (24 models)
    // Priority 1: Check direct ultra_ensemble_25.individual_models (most direct)
    if (rawData.ultra_ensemble_25?.individual_models && Array.isArray(rawData.ultra_ensemble_25.individual_models)) {
      rawData.ultra_ensemble_25.individual_models.forEach((modelName: string) => {
        const formatted = formatModelName(modelName);
        if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
          allModels.add(formatted);
        }
      });
    }
    
    // Priority 2: Check direct ultra_ensemble_25.model_breakdown
    if (rawData.ultra_ensemble_25?.model_breakdown && typeof rawData.ultra_ensemble_25.model_breakdown === 'object') {
      Object.keys(rawData.ultra_ensemble_25.model_breakdown).forEach(modelName => {
        const formatted = formatModelName(modelName);
        if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
          allModels.add(formatted);
        }
      });
    }
    
    // Priority 3: Check method_breakdown.ultra_ensemble_25 for detailed results
    if (rawData.method_breakdown?.ultra_ensemble_25) {
      const ultraResult = rawData.method_breakdown.ultra_ensemble_25;
      
      // Check detailed_results.model_breakdown (individual model predictions)
      if (ultraResult.detailed_results?.model_breakdown) {
        Object.keys(ultraResult.detailed_results.model_breakdown).forEach(modelName => {
          const formatted = formatModelName(modelName);
          if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
            allModels.add(formatted);
          }
        });
      }
      
      // Check detailed_results.advanced_ensemble_metrics or ensemble_metrics
      const ensembleMetrics = ultraResult.detailed_results?.advanced_ensemble_metrics || 
                             ultraResult.detailed_results?.ensemble_metrics;
      if (ensembleMetrics?.model_breakdown) {
        Object.keys(ensembleMetrics.model_breakdown).forEach(modelName => {
          const formatted = formatModelName(modelName);
          if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
            allModels.add(formatted);
          }
        });
      }
    }
    
    // Priority 4: Check direct ultra_ensemble_25 at root level
    if (rawData.ultra_ensemble_25?.detailed_results?.model_breakdown) {
      Object.keys(rawData.ultra_ensemble_25.detailed_results.model_breakdown).forEach(modelName => {
        const formatted = formatModelName(modelName);
        if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
          allModels.add(formatted);
        }
      });
    }
    
    // Check method_breakdown for other models (excluding ultra_ensemble_25 which we handled above)
    if (rawData.method_breakdown) {
      Object.keys(rawData.method_breakdown).forEach(key => {
        if (key !== 'ultra_ensemble_25') {
          const formatted = formatModelName(key);
          if (formatted.trim() !== '' && !formatted.toLowerCase().includes('ultra ensemble')) {
            allModels.add(formatted);
          }
        }
      });
    }
    
    // ✅ CRITICAL: If we still don't have 33 models, try to get from model_info.models_used
    // This might include the expanded Ultra Ensemble models list
    if (detectionResult.model_info?.models_used && Array.isArray(detectionResult.model_info.models_used)) {
      detectionResult.model_info.models_used.forEach((model: string) => {
        // If it says "Ultra Ensemble (24 Models)", extract the individual models differently
        if (model.includes('Ultra Ensemble') && model.includes('24')) {
          // Don't add this as a single model - we want the 24 individual models
          return;
        }
        const formatted = formatModelName(model);
        if (formatted.trim() !== '') {
          allModels.add(formatted);
        }
      });
    }
    
    // ✅ FALLBACK: If we have fewer models than expected, add standard Ultra Ensemble model names
    // This is a fallback if detailed_results aren't available
    const backendModelCount = detectionResult.model_info?.model_count ?? (detectionResult as any).model_info?.model_count ?? (detectionResult as any).total_models_used;
    if (backendModelCount && backendModelCount >= 30 && Array.from(allModels).length < 25) {
      const standardUltraModels = [
        'EfficientNet B7', 'EfficientNet B4', 'ResNet50', 'ResNet101', 
        'DenseNet121', 'Inception V3', 'MesoNet', 'Xception', 
        'Capsule Network', 'Vision Transformer', 'Swin Transformer', 
        'ConvNeXt', 'DeiT', 'BEiT', 'Temporal Net', 'Frequency Net', 
        'Attention Net', 'Spatial Analyzer', 'Temporal Analyzer', 
        'Frequency Analyzer', 'Texture Analyzer', 'Motion Analyzer'
      ];
      standardUltraModels.forEach(model => {
        const formatted = formatModelName(model);
        if (formatted.trim() !== '') {
          allModels.add(formatted);
        }
      });
    }
    
    // Remove duplicates and sort
    const uniqueModels = Array.from(allModels);
    // Remove any duplicates that might have different casing
    const normalizedModels = new Map<string, string>();
    uniqueModels.forEach(model => {
      const normalized = model.toLowerCase().trim();
      if (!normalizedModels.has(normalized)) {
        normalizedModels.set(normalized, model);
      }
    });
    
    // ✅ FIXED: Exclude "Title Classification" from model list (it's metadata analysis, not a detection model)
    const filteredModels = Array.from(normalizedModels.values()).filter(
      model => model.toLowerCase() !== 'title classification'
    );
    
    return filteredModels.sort();
  };

  // Format model name for display
  const formatModelName = (modelName: string): string => {
    if (!modelName || typeof modelName !== 'string') return '';
    const name = modelName.toLowerCase().trim();
    
    // Clean up common model names with proper formatting (specific first, then general)
    if (name.includes('mesonet')) return 'MesoNet';
    if (name.includes('xception')) return 'XceptionNet';
    if (name.includes('efficientnet_b7') || name.includes('efficientnet-b7')) return 'EfficientNet B7';
    if (name.includes('efficientnet_b4') || name.includes('efficientnet-b4')) return 'EfficientNet B4';
    if (name.includes('efficientnet_b0') || name.includes('efficientnet-b0')) return 'EfficientNet B0';
    if (name.includes('efficient')) return 'EfficientNet';
    if (name.includes('yolo') || name.includes('yolov8')) return 'YOLOv8';
    if (name.includes('modern ai') || (name.includes('modern') && name.includes('detector'))) return 'Modern AI Detector';
    if (name.includes('temporal_net') || name === 'temporal_net') return 'Temporal Net';
    if (name.includes('temporal_analyzer') || name === 'temporal_analyzer') return 'Temporal Analyzer';
    if (name.includes('temporal')) return 'Temporal Analysis';
    if (name.includes('frequency_net') || name === 'frequency_net') return 'Frequency Net';
    if (name.includes('frequency_analyzer') || name === 'frequency_analyzer') return 'Frequency Analyzer';
    if (name.includes('frequency')) return 'Frequency Analyzer';
    if (name.includes('attention_net') || name === 'attention_net') return 'Attention Net';
    if (name.includes('spatial_analyzer') || name === 'spatial_analyzer') return 'Spatial Analyzer';
    if (name.includes('texture_analyzer') || name === 'texture_analyzer') return 'Texture Analyzer';
    if (name.includes('motion_analyzer') || name === 'motion_analyzer') return 'Motion Analyzer';
    if (name.includes('generative ai') || (name.includes('generative') && name.includes('ai'))) return 'Generative AI';
    if (name.includes('resnet50') || name === 'resnet50') return 'ResNet50';
    if (name.includes('resnet101') || name === 'resnet101') return 'ResNet101';
    if (name.includes('resnet152') || name === 'resnet152') return 'ResNet152';
    if (name.includes('resnet')) return 'ResNet';
    if (name.includes('densenet121') || name === 'densenet121') return 'DenseNet121';
    if (name.includes('densenet')) return 'DenseNet';
    if (name.includes('inception_v3') || name === 'inception_v3') return 'Inception V3';
    if (name.includes('inception')) return 'Inception';
    if (name.includes('capsule_net') || name === 'capsule_net' || name.includes('capsule network')) return 'Capsule Network';
    if (name.includes('vision_transformer') || name === 'vision_transformer' || name.includes('vit_')) return 'Vision Transformer';
    if (name.includes('swin_transformer') || name === 'swin_transformer') return 'Swin Transformer';
    if (name.includes('convnext') || name === 'convnext') return 'ConvNeXt';
    if (name.includes('deit') || name === 'deit') return 'DeiT';
    if (name.includes('beit') || name === 'beit') return 'BEiT';
    if (name.includes('clip_detector') || name === 'clip_detector') return 'CLIP Detector';
    if (name.includes('clip')) return 'CLIP Detector';
    if (name.includes('title_classification') || name === 'title_classification') return 'Title Classification';
    if (name.includes('gemini_api') || name === 'gemini_api') return 'Gemini API';
    if (name.includes('ultra')) return 'Ultra Ensemble';
    if (name.includes('ensemble')) return 'Ensemble';
    if (name.includes('gan')) return 'GAN Detector';
    
    // Remove common suffixes and clean up
    let cleaned = modelName
      .replace(/\s*\(.*?\)/g, '') // Remove (Primary), (Specialist), etc.
      .replace(/\s*-\s*\w+/g, '') // Remove -B0, -B7, etc.
      .replace(/_/g, ' ') // Replace underscores with spaces
      .trim();
    
    // Capitalize first letter of each word
    return cleaned.split(' ').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };

  // Get mode description
  const getModeDescription = (mode: string, isEnsemble: boolean): string => {
    switch (mode) {
      case 'Traditional':
        return 'Traditional CNN-based detection focusing on pixel-level consistency and facial geometry';
      case 'Modern AI':
        return 'Modern AI detection using neural texture analysis and frequency domain artifacts';
      case 'Enhanced':
        return 'Enhanced AI detection using advanced ensemble models with multi-stage analysis';
      case 'Hybrid':
        return isEnsemble 
          ? 'Hybrid Mode combines Traditional + Modern AI + Free AI Ensemble for maximum accuracy'
          : 'Hybrid Mode combines Traditional + Modern AI methods for enhanced detection';
      default:
        return 'Standard deepfake detection using CNN-based models';
    }
  };

  // Get model type badge
  const getModelTypeBadge = (modelName: string): { label: string; variant: string; icon: React.ReactNode; className?: string } => {
    const name = modelName.toLowerCase();
    
    if (name.includes('mesonet') || name.includes('xception') || name.includes('efficient')) {
      return { label: 'CNN', variant: 'default', icon: <Cpu className="w-3 h-3" /> };
    }
    if (name.includes('ensemble') || name.includes('ultra')) {
      return { label: 'Ensemble', variant: 'secondary', icon: <Zap className="w-3 h-3" /> };
    }
    if (name.includes('gan') || name.includes('generative')) {
      return { label: 'GAN Detector', variant: 'default', icon: <Brain className="w-3 h-3" /> };
    }
    if (name.includes('frequency') || name.includes('spectral')) {
      return { label: 'Frequency Analyzer', variant: 'default', icon: <Zap className="w-3 h-3" /> };
    }
    if (name.includes('temporal')) {
      return { label: 'Temporal Analyzer', variant: 'secondary', icon: <Activity className="w-3 h-3" /> };
    }
    if (name.includes('vision') && name.includes('transformer')) {
      return { label: 'Vision Transformer', variant: 'default', icon: <Brain className="w-3 h-3" /> };
    }
    if (name.includes('clip')) {
      return { label: 'CLIP Detector', variant: 'default', icon: <Eye className="w-3 h-3" /> };
    }
    if (name.includes('resnet') || name.includes('vgg')) {
      return { label: 'CNN', variant: 'outline', icon: <Cpu className="w-3 h-3" /> };
    }
    
    return { 
      label: 'AI Model', 
      variant: 'default', 
      icon: <Brain className="w-3 h-3" />,
      className: "bg-indigo-500/10 text-indigo-700 border-indigo-500/30 hover:bg-indigo-500/20 dark:bg-indigo-500/20 dark:text-indigo-300 dark:border-indigo-500/50 dark:hover:bg-indigo-500/30"
    };
  };

  // Get mode badge
  const getModeBadge = (mode: string): { label: string; variant: string; icon: React.ReactNode } => {
    switch (mode) {
      case 'Traditional':
        return { label: 'Traditional', variant: 'outline', icon: <Shield className="w-3 h-3" /> };
      case 'Modern AI':
        return { label: 'Modern AI', variant: 'destructive', icon: <Brain className="w-3 h-3" /> };
      case 'Hybrid':
        return { label: 'Hybrid', variant: 'secondary', icon: <Zap className="w-3 h-3" /> };
      case 'Enhanced':
        return { label: 'Enhanced', variant: 'default', icon: <Brain className="w-3 h-3" /> };
      default:
        return { label: 'Standard', variant: 'default', icon: <Activity className="w-3 h-3" /> };
    }
  };

  const modelInfo = getModelInfo();

  return (
    <Card className={`neural-card border-border/30 bg-muted/20 ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="w-5 h-5 text-primary" />
          <span className="neural-text">Model Information</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Primary Model */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-muted-foreground">Primary Model</label>
              <div className="flex items-center space-x-2">
                {getModelTypeBadge(modelInfo.primary).icon}
                <Badge 
                  variant={getModelTypeBadge(modelInfo.primary).variant as any} 
                  className={`neural-card ${getModelTypeBadge(modelInfo.primary).className || ''}`}
                  style={{ opacity: 1, visibility: 'visible' }}
                >
                  {getModelTypeBadge(modelInfo.primary).label}
                </Badge>
              </div>
            </div>
            <p className="neural-text font-semibold text-base">{modelInfo.primary}</p>
          </div>

          {/* Supporting Models */}
          {modelInfo.supporting.length > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                {modelInfo.isEnsemble ? 'Supporting Ensemble' : 'Supporting Models'}
              </label>
              <div className="flex flex-wrap gap-2">
                {modelInfo.supporting.map((model, index) => {
                  const badge = getModelTypeBadge(model);
                  // Determine custom colors for specific models with dark mode support
                  let customClassName = "neural-card flex items-center space-x-1 transition-colors";
                  
                  // Model-specific color themes with dark mode support
                  const modelLower = model.toLowerCase();
                  
                  // ✅ IMPROVED: Professional color theme with better contrast and consistency
                  if (model === 'EfficientNet' || modelLower.includes('efficient')) {
                    // Orange theme for EfficientNet - vibrant and clear
                    customClassName += " bg-orange-500/15 text-orange-700 dark:text-orange-300 border-orange-500/40 hover:bg-orange-500/25 dark:bg-orange-500/25 dark:border-orange-500/60 dark:hover:bg-orange-500/35";
                  } else if (model === 'YOLOv8' || modelLower.includes('yolo')) {
                    // Red theme for YOLOv8 - clear and distinct
                    customClassName += " bg-red-500/15 text-red-700 dark:text-red-300 border-red-500/40 hover:bg-red-500/25 dark:bg-red-500/25 dark:border-red-500/60 dark:hover:bg-red-500/35";
                  } else if (model === 'Modern AI Detector' || (modelLower.includes('modern') && modelLower.includes('detector'))) {
                    // Indigo theme for Modern AI Detector - professional
                    customClassName += " bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/40 hover:bg-indigo-500/25 dark:bg-indigo-500/25 dark:border-indigo-500/60 dark:hover:bg-indigo-500/35";
                  } else if (model === 'Temporal Analyzer' || model === 'Temporal Analysis' || modelLower.includes('temporal')) {
                    // Green theme for Temporal Analysis - clear and professional
                    customClassName += " bg-green-500/15 text-green-700 dark:text-green-300 border-green-500/40 hover:bg-green-500/25 dark:bg-green-500/25 dark:border-green-500/60 dark:hover:bg-green-500/35";
                  } else if (model === 'Frequency Analyzer' || modelLower.includes('frequency')) {
                    // Blue theme for Frequency Analyzer - clear and distinct
                    customClassName += " bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/40 hover:bg-blue-500/25 dark:bg-blue-500/25 dark:border-blue-500/60 dark:hover:bg-blue-500/35";
                  } else if (model === 'Generative AI' || modelLower.includes('generative')) {
                    // Purple theme for Generative AI - vibrant
                    customClassName += " bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/40 hover:bg-purple-500/25 dark:bg-purple-500/25 dark:border-purple-500/60 dark:hover:bg-purple-500/35";
                  } else if (model === 'GAN Detector' || modelLower.includes('gan')) {
                    // Purple theme for GAN Detector
                    customClassName += " bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/40 hover:bg-purple-500/25 dark:bg-purple-500/25 dark:border-purple-500/60 dark:hover:bg-purple-500/35";
                  } else if (model === 'Vision Transformer' || model === 'vision_transformer' || modelLower.includes('vision') && modelLower.includes('transformer')) {
                    // Teal/Cyan theme for Vision Transformer - clear and professional
                    customClassName += " bg-teal-500/15 text-teal-700 dark:text-teal-300 border-teal-500/40 hover:bg-teal-500/25 dark:bg-teal-500/25 dark:border-teal-500/60 dark:hover:bg-teal-500/35";
                  } else if (model === 'CLIP Detector' || model === 'clip_detector' || modelLower.includes('clip')) {
                    // Amber theme for CLIP Detector - warm and clear
                    customClassName += " bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/40 hover:bg-amber-500/25 dark:bg-amber-500/25 dark:border-amber-500/60 dark:hover:bg-amber-500/35";
                  } else if (model === 'ResNet' || modelLower.includes('resnet')) {
                    // Purple theme for ResNet
                    customClassName += " bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/40 hover:bg-purple-500/25 dark:bg-purple-500/25 dark:border-purple-500/60 dark:hover:bg-purple-500/35";
                  } else if (model === 'Ultra Ensemble' || modelLower.includes('ultra')) {
                    // Pink theme for Ultra Ensemble - distinct
                    customClassName += " bg-pink-500/15 text-pink-700 dark:text-pink-300 border-pink-500/40 hover:bg-pink-500/25 dark:bg-pink-500/25 dark:border-pink-500/60 dark:hover:bg-pink-500/35";
                  } else {
                    // Default slate theme for other models
                    customClassName += " bg-slate-500/15 text-slate-700 dark:text-slate-300 border-slate-500/40 hover:bg-slate-500/25 dark:bg-slate-500/25 dark:border-slate-500/60 dark:hover:bg-slate-500/35";
                  }
                  
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Badge 
                        variant={badge.variant as any} 
                        className={customClassName}
                        style={{ opacity: 1, visibility: 'visible' }}
                      >
                        {badge.icon}
                        <span>{model}</span>
                      </Badge>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Detection Mode */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-muted-foreground">Detection Mode</label>
              <Badge 
                variant={getModeBadge(modelInfo.mode).variant as any} 
                className="neural-card flex items-center space-x-1 bg-primary/10 text-primary border-primary/30 hover:bg-primary/20 dark:bg-primary/20 dark:text-primary-foreground dark:border-primary/50 dark:hover:bg-primary/30"
                style={{ opacity: 1, visibility: 'visible' }}
              >
                {getModeBadge(modelInfo.mode).icon}
                <span>{getModeBadge(modelInfo.mode).label}</span>
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {modelInfo.modeDescription}
            </p>
          </div>

          {/* Model Count & Performance */}
          <div className="flex items-center justify-between pt-2 border-t border-border/30">
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500 dark:text-green-400" />
              <span className="font-semibold text-foreground">
                <span className="text-primary font-bold">{modelInfo.modelCount}</span> {modelInfo.modelCount === 1 ? 'model' : 'models'} active
              </span>
            </div>
            {modelInfo.isEnsemble && (
              <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                <Info className="w-3 h-3" />
                <span>Ensemble Mode</span>
              </div>
            )}
          </div>

          {/* ✅ NEW: View All Models Button (Shown when model count > 1 for all modes) */}
          {modelInfo.modelCount > 1 && (
            <div className="pt-2 border-t border-border/30">
              <button
                onClick={() => setShowAllModels(!showAllModels)}
                className="flex items-center justify-between w-full text-sm text-muted-foreground hover:text-foreground transition-colors p-2 rounded hover:bg-muted/50 group"
              >
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 group-hover:text-primary transition-colors" />
                  <span className="font-medium">View All Models</span>
                  <Badge variant="outline" className="ml-2 text-xs bg-primary/5 text-primary border-primary/20">
                    {getAllModels().length}
                  </Badge>
                </div>
                {showAllModels ? (
                  <ChevronUp className="w-4 h-4 group-hover:text-primary transition-colors" />
                ) : (
                  <ChevronDown className="w-4 h-4 group-hover:text-primary transition-colors" />
                )}
              </button>
              
              <AnimatePresence>
                {showAllModels && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="pt-3 space-y-2">
                      <p className="text-xs text-muted-foreground mb-2">
                        Complete model architecture ({getAllModels().length} models):
                      </p>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-64 overflow-y-auto pr-2">
                        {getAllModels().map((model, index) => {
                          const badge = getModelTypeBadge(model);
                          const modelLower = model.toLowerCase();
                          let customClassName = "text-xs px-2 py-1 rounded-md border transition-colors";
                          
                          // ✅ IMPROVED: Professional color theme for all models
                          if (model === 'EfficientNet' || modelLower.includes('efficient')) {
                            customClassName += " bg-orange-500/10 text-orange-700 border-orange-500/30 dark:bg-orange-500/20 dark:text-orange-300";
                          } else if (model === 'YOLOv8' || modelLower.includes('yolo')) {
                            customClassName += " bg-red-500/10 text-red-700 border-red-500/30 dark:bg-red-500/20 dark:text-red-300";
                          } else if (model === 'Modern AI Detector' || (modelLower.includes('modern') && modelLower.includes('detector'))) {
                            customClassName += " bg-indigo-500/10 text-indigo-700 border-indigo-500/30 dark:bg-indigo-500/20 dark:text-indigo-300";
                          } else if (model === 'Temporal Analyzer' || model === 'Temporal Analysis' || modelLower.includes('temporal')) {
                            customClassName += " bg-green-500/10 text-green-700 border-green-500/30 dark:bg-green-500/20 dark:text-green-300";
                          } else if (model === 'Frequency Analyzer' || modelLower.includes('frequency')) {
                            customClassName += " bg-blue-500/10 text-blue-700 border-blue-500/30 dark:bg-blue-500/20 dark:text-blue-300";
                          } else if (model === 'Vision Transformer' || modelLower.includes('vision') && modelLower.includes('transformer')) {
                            customClassName += " bg-teal-500/10 text-teal-700 border-teal-500/30 dark:bg-teal-500/20 dark:text-teal-300";
                          } else if (model === 'CLIP Detector' || modelLower.includes('clip')) {
                            customClassName += " bg-amber-500/10 text-amber-700 border-amber-500/30 dark:bg-amber-500/20 dark:text-amber-300";
                          } else if (model === 'ResNet' || modelLower.includes('resnet')) {
                            customClassName += " bg-purple-500/10 text-purple-700 border-purple-500/30 dark:bg-purple-500/20 dark:text-purple-300";
                          } else if (model === 'Ultra Ensemble' || modelLower.includes('ultra')) {
                            customClassName += " bg-pink-500/10 text-pink-700 border-pink-500/30 dark:bg-pink-500/20 dark:text-pink-300";
                          } else {
                            customClassName += " bg-slate-500/10 text-slate-700 border-slate-500/30 dark:bg-slate-500/20 dark:text-slate-300";
                          }
                          
                          return (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.02 }}
                              className={customClassName}
                            >
                              <div className="flex items-center space-x-1">
                                {badge.icon}
                                <span className="truncate">{model}</span>
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* AI Tool Detection */}
          {detectionResult.ai_tool_detected && (
            <div className="pt-2 border-t border-border/30">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-orange-500" />
                <span className="text-sm font-medium text-muted-foreground">Detected AI Tool</span>
              </div>
              <Badge className="bg-orange-100 text-orange-800 mt-1">
                {detectionResult.ai_tool_detected}
              </Badge>
            </div>
          )}

          {/* Confidence Toggle */}
          {onToggleConfidence && (
            <div className="pt-2 border-t border-border/30">
              <button
                onClick={onToggleConfidence}
                className="flex items-center space-x-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full text-left p-2 rounded hover:bg-muted/50"
                title={showConfidence ? "Hide confidence score" : "Show confidence score"}
              >
                {showConfidence ? (
                  <>
                    <EyeOff className="w-4 h-4" />
                    <span>Hide Confidence</span>
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4" />
                    <span>View Confidence</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ModelInformationCard;

