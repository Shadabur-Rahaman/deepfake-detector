import { useState, useCallback, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/SimpleAuthContext'
import { useAccessControl, ACCESS_CONFIGS } from '@/hooks/useAccessControl'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { AdminBypass } from '@/components/admin/AdminBypass'
import { AccessRequestModal } from '@/components/auth/AccessRequestModal'
import { AccessControlCard } from '@/components/auth/AccessControlCard'
import { API_BASE_URL } from '@/config/api'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { LoadingButton } from '@/components/ui/LoadingButton'
import { ProgressIndicator } from '@/components/ui/ProgressIndicator'
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import { toast } from "@/components/ui/use-toast"
import { formatDetectionResult, getConfidenceColorClass, formatConfidenceDisplay, formatConfidenceValue, getBiasTooltipText } from '@/lib/detection-utils'
import { generateDetectionReport, SecurePDFGenerator } from '@/lib/pdf-generator'
import { downloadFile, getDownloadInstructions } from '@/lib/download-utils'
import { ResponsiveVideoPlayer } from '@/components/ui/ResponsiveVideoPlayer'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { LoadingState } from '@/components/ui/LoadingState'
import { AISummaryDisplay } from '@/components/AISummaryDisplay'
import { FullAnalysisView } from '@/components/FullAnalysisView'
import { HeroCanvas } from "@/components/three/HeroCanvas"
import { 
  Upload, 
  Youtube, 
  Play, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  FileVideo, 
  RefreshCw,
  Shield,
  Zap,
  Brain,
  Database,
  Cpu,
  Users,
  ChevronDown,
  FileText,
  FileSpreadsheet,
  Activity,
  Eye,
  EyeOff
} from "lucide-react"

const howItWorksSteps = [
  {
    icon: Upload,
    title: "Upload Content",
    description: "Drag and drop files or paste YouTube URLs for instant analysis"
  },
  {
    icon: Brain,
    title: "MesoNet CNN Processing", 
    description: "Our advanced neural networks analyze every frame using deep learning"
  },
  {
    icon: CheckCircle,
    title: "Get Results",
    description: "Receive detailed authenticity report with confidence scores"
  }
]

const detectionFeatures = [
  {
    icon: Shield,
    title: "94.1% Accuracy",
    description: "State-of-the-art MesoNet CNN detection"
  },
  {
    icon: Zap,
    title: "Real-time Analysis",
    description: "FastAPI WebSocket processing"
  },
  {
    icon: FileVideo,
    title: "Multi-format Support",
    description: "MP4, AVI, MOV and YouTube URLs"
  }
]

// Helper function to extract YouTube video ID from URL
const extractYouTubeId = (url: string): string => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : '';
}

interface AnalysisResult {
  result: string
  confidence: number
  faces_found: number
  faces_detected?: number
  faces_analyzed?: number
  processing_time: number
  model_used: string
  video_url?: string
  enhanced_analysis?: boolean
  frame_count?: number
  video_duration?: number
  bias_applied?: number
  metadata_flags?: string[]
  // Sophisticated detection data
  ensemble_results?: Record<string, any>
  individual_results?: Record<string, number>
  model_weights?: Record<string, number>
  final_ensemble_score?: number
  total_models_used?: number
  advanced_features?: Record<string, boolean>
  sophisticated_analysis?: Record<string, boolean>
  // Additional metadata for AI Summary Generation
  efficientnet_result?: string
  efficientnet_confidence?: number
  temporal_score?: number
  spatial_score?: number
  frequency_score?: number
  model_type?: string
  analysis_method?: string
  ensemble_scores?: Record<string, number>
  temporal_consistency?: number
  face_quality_score?: number
  ai_tool_detected?: string
  title_analysis?: {
    detected_keywords?: string[]
    likely_ai_tool?: string
    title_boost?: number
  }
  // Additional fields for compatibility
  processing_stages?: any
  markdown_report?: string
  video_id?: string
  // Enhanced fields for dynamic AI summaries
  detection_mode?: 'Traditional' | 'Modern AI' | 'Hybrid'
  anomalies?: string[]
  lighting_consistency?: number
  motion_coherence?: number
  texture_quality?: number
  // Enhanced model information from backend
  model_info?: {
    primary_model?: string
    model_type?: string
    detection_mode?: string
    models_used?: string[]
    model_count?: number
    is_ensemble?: boolean
  }
  // Extended backend data for detailed summaries
  model_categories?: {
    traditional_models?: number
    modern_ai_models?: number
    cloud_ai_models?: number
  }
  stage_results?: any[]
  ai_api_used?: string
  cross_validation_score?: number
  hybrid_ensemble_score?: number
  method_breakdown?: Record<string, any>
  model_contributions?: any[]
}

function TryItContent() {
  const { user } = useAuth()
  const accessControl = useAccessControl(ACCESS_CONFIGS.try)
  const [uploadMethod, setUploadMethod] = useState<'file' | 'url'>('file')
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [stageDetails, setStageDetails] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [currentVideoId, setCurrentVideoId] = useState<string | null>(null)
  const [selectedMode, setSelectedMode] = useState<string>('modern-ai')
  const [availableModes, setAvailableModes] = useState<any[]>([])
  const [currentModeInfo, setCurrentModeInfo] = useState<any>(null)
  const [showAccessRequest, setShowAccessRequest] = useState(false)
  const [showConfidence, setShowConfidence] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Set default modes for the new 3-mode system
  useEffect(() => {
    setAvailableModes([
      { mode: 'traditional', display_name: 'Traditional (Your Trained Model)', description: 'Fast processing with your trained deepfake_detector_finetuned1.pth model in ensemble. Best for quick analysis.' },
      { mode: 'modern-ai', display_name: 'Modern AI (Services Directory Models)', description: 'Advanced accuracy using all models from services/ directory including generative AI, advanced models integration, and modern AI detectors.' },
      { mode: 'hybrid', display_name: 'Hybrid (All Detection Methods)', description: 'Maximum accuracy combining Traditional + Modern AI + Free AI Ensemble. Most comprehensive analysis.' }
    ]);
    setSelectedMode('modern-ai');
  }, [])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type !== 'dragleave')
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) {
      if (!droppedFile.type.startsWith('video/')) {
        toast({
          title: "Invalid file type",
          description: "Please select a valid video file",
          variant: "destructive"
        })
        return
      }
      
      if (droppedFile.size > 100 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please select a video file smaller than 100MB",
          variant: "destructive"
        })
        return
      }

      setFile(droppedFile)
      setUploadMethod('file')
      setError(null)
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.type.startsWith('video/')) {
        toast({
          title: "Invalid file type",
          description: "Please select a valid video file",
          variant: "destructive"
        })
        return
      }
      
      if (selectedFile.size > 100 * 1024 * 1024) {
        toast({
          title: "File too large", 
          description: "Please select a video file smaller than 100MB",
          variant: "destructive"
        })
        return
      }

      setFile(selectedFile)
      setUploadMethod('file')
      setError(null)
    }
  }, [])

  const handleModeChange = async (newMode: string) => {
    setSelectedMode(newMode)
    toast({
      title: "Mode Updated",
      description: `Switched to ${newMode} mode`,
      variant: "default"
    })
  }

  const startAnalysis = async () => {
    if (!file && !youtubeUrl) {
      setError('Please select a video file or enter a YouTube URL')
      return
    }

    setIsProcessing(true)
    setProgress(0)
    setStageDetails('Starting video analysis...')
    setError(null)
    setResult(null)

    try {
      let res: Response
      
      if (uploadMethod === 'file' && file) {
        const formData = new FormData()
        formData.append('file', file)
        
        // Use the new mode-based upload endpoint
        const formDataWithMode = new FormData()
        formDataWithMode.append('file', file)
        formDataWithMode.append('detection_mode', selectedMode)
        
        res = await fetch(`${API_BASE_URL}/api/detect-deepfake-upload-mode`, {
          method: 'POST',
          body: formDataWithMode,
        })
      } else if (uploadMethod === 'url' && youtubeUrl) {
        res = await fetch(`${API_BASE_URL}/api/detect-deepfake-youtube`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            url: youtubeUrl,
            detection_mode: selectedMode
          }),
        })
      } else {
        return
      }

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }
      
      // All modes now use the same polling approach with MVP detection
      const { video_id } = await res.json()
      setCurrentVideoId(video_id)
      pollForResults(video_id)
    } catch (err) {
      const error = err as Error
      let errorMessage = error.message
      
      // Check if it's a connection error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        const modeText = selectedMode === 'traditional' ? 'Traditional Analysis' : 
                        selectedMode === 'modern-ai' ? 'Modern AI Analysis' :
                        selectedMode === 'hybrid' ? 'Hybrid Analysis' : 'Analysis'
        
        errorMessage = `Backend Connection Failed\n(Server unreachable at ${API_BASE_URL})`
      }
      
      setError(errorMessage)
      setIsProcessing(false)
    }
  }

  const pollForResults = (videoId: string) => {
    let pollCount = 0
    const maxPolls = 60 // Increased from 20 to 60 (2 minutes with 2s intervals, then 5 min total with backoff)
    let pollInterval = 2000 // Start with 2 seconds
    
    const poll = async () => {
      pollCount++
      
      // Timeout after max polls
      if (pollCount > maxPolls) {
        setError('Analysis timeout - please try again')
        setIsProcessing(false)
        return
      }
      
      // Implement exponential backoff for long-running operations
      if (pollCount > 15) {  // Changed from 10
        pollInterval = Math.min(pollInterval * 1.15, 5000) // Gentler increase, max 5 seconds
      }
      try {
        // Try direct status endpoint first (uses DETECTION_RESULTS dictionary)
        let endpoint = `http://127.0.0.1:8000/detection-status/${videoId}`
        let statusRes = await fetch(endpoint)
        
        // If direct endpoint fails, try mode detection endpoint as fallback
        if (!statusRes.ok) {
          endpoint = `${API_BASE_URL}/mode-detection/detection-status/${videoId}`
          statusRes = await fetch(endpoint)
        }
        
        if (!statusRes.ok) {
          // If both endpoints fail, check if it's a "Not Found" error
          if (statusRes.status === 404) {
            // Video ID not found - might be processing or cleaned up
            console.log(`Video ID ${videoId} not found in results. Continuing to poll...`)
            // Continue polling but with a limit
            if (pollCount > 10) { // After 20 seconds, give up
              setError('Video analysis not found. Please try uploading again.')
              setIsProcessing(false)
              return
            }
            // Schedule next poll with current interval
            setTimeout(poll, pollInterval)
            return
          }
          throw new Error('Failed to fetch status')
        }
        
        const data = await statusRes.json()
        console.log(`🔍 Polling response for ${videoId}:`, data)
        
        // Handle database unavailable error gracefully
        if (data.status === 'database_unavailable') {
          console.log('Database unavailable, continuing to poll...')
          // Continue polling but with a limit
          if (pollCount > 15) { // After 30 seconds, give up
            setError('Database unavailable. Please try again later.')
            setIsProcessing(false)
            return
          }
          // Schedule next poll with current interval
          setTimeout(poll, pollInterval)
          return
        }
        
        if (data.progress !== undefined) {
          console.log(`📊 Progress update: ${data.progress}% - ${data.stage_details || data.message || 'No stage details'}`)
          setProgress(data.progress)
        }
        
        // Update stage details from backend response (prioritize stage_details, fallback to message)
        if (data.stage_details || data.message) {
          const details = data.stage_details || data.message || ''
          if (details && details.trim()) {
            setStageDetails(details.trim())
            console.log(`📋 Stage details updated: ${details.trim()}`)
          }
        }
        
        // Also update if status is processing but no details yet
        if (data.status === 'processing' && !stageDetails && !data.stage_details && !data.message) {
          setStageDetails('Processing video...')
        }
        
        // Handle different response formats from different endpoints
        if (data.status === 'completed' || data.job_status === 'completed') {
          // Polling completed successfully
          
          // Extract result from different possible response formats
          let result = data.final_result || data.prediction || data.result || data.job_result
          let confidence = data.confidence !== undefined ? data.confidence : (data.job_confidence !== undefined ? data.job_confidence : 0)
          const facesFound = data.faces_detected || data.faces_analyzed || data.job_faces_analyzed || data.faces_found || 0
          const processingTime = data.processing_time || data.job_processing_time || 0
          
          // Debug logging to see what we're getting
          console.log('🔍 Raw API response:', data)
          console.log('🔍 Response keys:', Object.keys(data))
          console.log('🔍 Extracted result:', result)
          console.log('🔍 Extracted confidence:', confidence)
          console.log('🔍 Extracted faces:', facesFound)
          console.log('🔍 Processing time:', processingTime)
          
          // Additional validation and fallback
          if (!result || result === 'Unknown') {
            console.error('❌ No valid result found in response:', data)
            // Try to get result from other possible fields
            const fallbackResult = data.final_result || data.prediction || data.result || data.job_result || 'Unknown'
            if (fallbackResult !== 'Unknown') {
              console.log('🔄 Using fallback result:', fallbackResult)
              result = fallbackResult
            }
          }
          
          // Fix confidence extraction - handle both percentage and decimal formats
          if (confidence === 0 && data.confidence !== 0 && data.confidence !== undefined) {
            console.error('❌ Confidence extraction failed:', { 
              raw: data.confidence, 
              extracted: confidence,
              data: data 
            })
            // Use the raw confidence if extraction failed
            confidence = data.confidence
            console.log('🔄 Using raw confidence:', confidence)
          }
          
          // Convert confidence to percentage if it's in decimal format (0-1)
          if (confidence > 0 && confidence <= 1) {
            confidence = confidence * 100
            console.log('🔄 Converted confidence to percentage:', confidence)
          }
          
          // Final validation before setting result
          console.log('🔍 Final values before setting result:')
          console.log('  - result:', result)
          console.log('  - confidence:', confidence)
          console.log('  - faces_found:', facesFound)
          console.log('  - processing_time:', processingTime)
          
          // Helper function to get the proper detection method display based on selected mode
          const getDetectionMethodDisplay = (mode: string, apiData: any) => {
            switch (mode) {
              case 'traditional':
                return 'Traditional (Your Trained Model)'
              case 'modern-ai':
                return 'Modern AI (Services Directory Models)'
              case 'hybrid':
                return 'Hybrid (All Detection Methods)'
              default:
                return apiData.detection_method || apiData.job_detection_method || 'Standard Mode'
            }
          }

          // Map backend detection_mode to frontend format, with fallback to selectedMode
          const backendDetectionMode = data.detection_mode || data.model_info?.detection_mode;
          const mappedMode = backendDetectionMode || 
            (selectedMode === 'traditional' ? 'Traditional' : 
             selectedMode === 'modern-ai' ? 'Modern AI' : 
             selectedMode === 'enhanced' ? 'Enhanced' : 
             selectedMode === 'hybrid' ? 'Hybrid' : 'Traditional');
          
          // Extract detailed scores from backend response
          const modelContributions = data.model_contributions || {};
          const temporalScore = data.temporal_consistency ?? modelContributions.temporal_score ?? (data.ensemble_scores?.temporal ?? 0.5);
          const frequencyScore = modelContributions.frequency_score ?? (data.ensemble_scores?.frequency ?? 0.5);
          const spatialScore = modelContributions.spatial_score ?? (data.ensemble_scores?.spatial ?? 0.5);
          const ensembleScores = data.ensemble_scores || {};
          
          setResult({
            result: result || 'Unknown',
            confidence: confidence,
            faces_found: facesFound || 0,
            processing_time: processingTime || 0,
            model_used: getDetectionMethodDisplay(selectedMode, data),
            video_url: data.video_url || data.job_video_url,
            enhanced_analysis: data.sophisticated_analysis?.comprehensive_logging || data.job_enhanced_analysis || false,
            frame_count: data.frame_count || data.job_frame_count,
            video_duration: data.video_duration || data.job_video_duration,
            bias_applied: data.bias_applied || data.job_bias_applied || 0,
            metadata_flags: data.metadata_flags || data.job_metadata_flags || [],
            // Sophisticated detection data
            ensemble_results: data.ensemble_results || data.job_ensemble_results || {},
            individual_results: data.individual_results || {},
            model_weights: data.model_weights || data.ensemble_weights || {},
            final_ensemble_score: data.final_ensemble_score || data.hybrid_ensemble_score || 0.5,
            total_models_used: data.model_count || data.total_models_used || 0,
            advanced_features: data.advanced_features || {},
            sophisticated_analysis: data.sophisticated_analysis || {},
            // Detailed scores for summary generation
            temporal_score: temporalScore,
            spatial_score: spatialScore,
            frequency_score: frequencyScore,
            temporal_consistency: temporalScore,  // Alias for compatibility
            ensemble_scores: ensembleScores,
            // Extended backend data for detailed summaries
            model_categories: data.model_categories || {},
            stage_results: data.stage_results || [],
            ai_api_used: data.ai_api_used || data.ai_tool_detected,
            cross_validation_score: data.cross_validation_score,
            hybrid_ensemble_score: data.hybrid_ensemble_score,
            method_breakdown: data.method_breakdown || data.detection_results || {},
            model_contributions: data.model_contributions || [],
            // Detection mode information for summary generation
            detection_mode: mappedMode,
            model_info: data.model_info || {
              detection_mode: mappedMode,
              primary_model: data.detection_method || getDetectionMethodDisplay(selectedMode, data),
              model_type: mappedMode,
              models_used: data.model_info?.models_used || [],
              model_count: data.model_count || data.total_models_used || 1,
              is_ensemble: data.model_info?.is_ensemble || false
            },
            // Additional fields for compatibility
            faces_detected: facesFound || 0,  // Add this for compatibility
            faces_analyzed: facesFound || 0   // Add this for compatibility
          })
          setIsProcessing(false)
          setProgress(100)
          return // Exit polling
        } else if (data.status === 'failed' || data.job_status === 'failed' || data.error) {
          const errorMessage = data.error || data.job_error || 'Analysis failed'
          setError(errorMessage)
          setIsProcessing(false)
          return // Exit polling
        } else if (data.status === 'processing' || data.job_status === 'processing') {
          // Continue polling for processing status
          console.log(`Video ${videoId} is still processing... (${pollCount}/${maxPolls})`)
          // Schedule next poll with current interval
          setTimeout(poll, pollInterval)
          return
        }
      } catch (err) {
        console.error('Polling error:', err)
        const errorMessage = 'Failed to fetch analysis status'
        setError(errorMessage)
        setIsProcessing(false)
        return
      }
    }
    
    // Start the first poll
    setTimeout(poll, pollInterval)
  }

  const resetAnalysis = () => {
    setFile(null)
    setYoutubeUrl('')
    setResult(null)
    setError(null)
    setProgress(0)
    setStageDetails('')
    setCurrentVideoId(null)
    setIsProcessing(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const downloadReport = async (format: 'pdf' | 'json' | 'txt' | 'csv' = 'pdf') => {
    if (!result) {
      toast({
        title: "No Results",
        description: "No analysis results available to download",
        variant: "destructive"
      })
      return
    }

    try {
      const videoId = `analysis_${Date.now()}`
      let blob: Blob
      let filename: string
      let mimeType: string

      if (format === 'pdf') {
        // Get detection mode from result with fallback
        const detectionMode = (result as any).detection_mode || 
          (selectedMode === 'traditional' ? 'Traditional' : 
           selectedMode === 'modern-ai' ? 'Modern AI' : 
           selectedMode === 'enhanced' ? 'Enhanced' : 
           selectedMode === 'hybrid' ? 'Hybrid' : 'Standard');
        
        // Get model info for report
        const modelInfo = (result as any).model_info || {};
        
        // Generate secure PDF report with mode-specific information
        const { blob: pdfBlob, reportId, hash } = await SecurePDFGenerator.generateSecureReport({
          videoId,
          timestamp: new Date().toISOString(),
          prediction: result.result,
          confidence: result.confidence,
          facesDetected: result.faces_found,
          processingTime: result.processing_time,
          detectionMethod: `${detectionMode} - ${result.model_used}`,
          enhancedAnalysis: result.enhanced_analysis || false,
          frameCount: result.frame_count,
          videoDuration: result.video_duration,
          biasApplied: result.bias_applied || 0,
          metadataFlags: result.metadata_flags || [],
          videoUrl: youtubeUrl || (file ? URL.createObjectURL(file) : undefined),
          thumbnailUrl: undefined, // Could be enhanced to capture video thumbnail
          reportId: '',
          // Mode-specific metadata
          detectionMode: detectionMode,
          modelCount: modelInfo.model_count || result.total_models_used || 1,
          modelsUsed: modelInfo.models_used || []
        }, {
          includeThumbnail: true,
          includeMetadata: true,
          includeTechnicalDetails: true,
          watermark: 'iFake Deepfake Detection',
          encryption: false
        })

        blob = pdfBlob
        filename = `deepfake_analysis_report_${reportId}.pdf`
        mimeType = 'application/pdf'
      } else {
        // Get detection mode from result with fallback
        const detectionMode = (result as any).detection_mode || 
          (selectedMode === 'traditional' ? 'Traditional' : 
           selectedMode === 'modern-ai' ? 'Modern AI' : 
           selectedMode === 'enhanced' ? 'Enhanced' : 
           selectedMode === 'hybrid' ? 'Hybrid' : 'Standard');
        
        const modelInfo = (result as any).model_info || {};
        
        // Fallback to other formats for compatibility with mode-specific information
        const reportData = {
          video_id: videoId,
          status: 'completed',
          prediction: result.result,
          confidence: result.confidence,
          faces_detected: result.faces_found,
          processing_time: result.processing_time,
          detection_method: `${detectionMode} - ${result.model_used}`,
          detection_mode: detectionMode,
          timestamp: new Date().toISOString(),
          enhanced_analysis: result.enhanced_analysis || false,
          frame_count: result.frame_count,
          video_duration: result.video_duration,
          bias_applied: result.bias_applied || 0,
          metadata_flags: result.metadata_flags || [],
          model_info: {
            detection_mode: detectionMode,
            primary_model: modelInfo.primary_model || result.model_used,
            model_type: modelInfo.model_type || detectionMode,
            models_used: modelInfo.models_used || [],
            model_count: modelInfo.model_count || result.total_models_used || 1,
            is_ensemble: modelInfo.is_ensemble || false
          },
          results: [{
            method: result.model_used,
            prediction: result.result,
            confidence: result.confidence,
            processing_time: result.processing_time,
            faces_analyzed: result.faces_found,
            detection_mode: detectionMode
          }]
        }

        switch (format) {
          case 'json':
            blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
            filename = `deepfake_analysis_report_${videoId}.json`
            mimeType = 'application/json'
            break
          case 'txt':
            const modeInfo = reportData.detection_mode ? `- Detection Mode: ${reportData.detection_mode}\n` : '';
            const modelInfo = reportData.model_info ? `- Models Used: ${reportData.model_info.models_used.join(', ') || 'N/A'}\n- Model Count: ${reportData.model_info.model_count || 1}\n` : '';
            
            const txtContent = `Deepfake Analysis Report
========================

Video ID: ${videoId}
Analysis Date: ${new Date().toLocaleString()}
Status: ${reportData.status}

Detection Results:
- Prediction: ${reportData.prediction}
- Confidence: ${reportData.confidence.toFixed(2)}%
- Faces Detected: ${reportData.faces_detected}
- Processing Time: ${reportData.processing_time}s
- Detection Method: ${reportData.detection_method}
${modeInfo}${modelInfo}- Enhanced Analysis: ${reportData.enhanced_analysis ? 'Yes' : 'No'}

Technical Details:
- Frame Count: ${reportData.frame_count || 'N/A'}
- Video Duration: ${reportData.video_duration ? `${reportData.video_duration}s` : 'N/A'}
- Bias Applied: ${(reportData.bias_applied * 100).toFixed(1)}%
- Metadata Flags: ${reportData.metadata_flags.length > 0 ? reportData.metadata_flags.join(', ') : 'None'}

Generated by iFake Deepfake Detection System
`
            blob = new Blob([txtContent], { type: 'text/plain' })
            filename = `deepfake_analysis_report_${videoId}.txt`
            mimeType = 'text/plain'
            break
          case 'csv':
            const csvContent = `Video ID,Status,Prediction,Confidence,Faces Detected,Processing Time,Detection Method,Detection Mode,Enhanced Analysis,Frame Count,Video Duration,Bias Applied,Metadata Flags,Model Count,Models Used
${videoId},${reportData.status},${reportData.prediction},${reportData.confidence},${reportData.faces_detected},${reportData.processing_time},${reportData.detection_method},${reportData.detection_mode || 'N/A'},${reportData.enhanced_analysis},${reportData.frame_count || ''},${reportData.video_duration || ''},${reportData.bias_applied},${reportData.metadata_flags.join(';')},${reportData.model_info?.model_count || 1},${reportData.model_info?.models_used.join(';') || 'N/A'}
`
            blob = new Blob([csvContent], { type: 'text/csv' })
            filename = `deepfake_analysis_report_${videoId}.csv`
            mimeType = 'text/csv'
            break
          default:
            throw new Error('Unsupported format')
        }
      }
      
      // Use enhanced download utility
      const success = await downloadFile(blob, {
        filename,
        mimeType,
        fallbackText: getDownloadInstructions(filename)
      })

      if (success) {
        toast({
          title: "Report Downloaded",
          description: `Analysis report downloaded as ${format.toUpperCase()}`,
        })
      } else {
        toast({
          title: "Download Started",
          description: "Please check your browser's download folder or follow the instructions shown.",
        })
      }
    } catch (error) {
      console.error('Download failed:', error)
      console.error('Error details:', {
        error: error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        userAgent: navigator.userAgent,
        supportsDownload: typeof window !== 'undefined' && 'URL' in window && 'createObjectURL' in window
      })
      
      toast({
        title: "Download Failed",
        description: `Failed to download the report. Error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again or check browser console for details.`,
        variant: "destructive"
      })
    }
  }


  const shareResults = async () => {
    if (!result) {
      toast({
        title: "No Results",
        description: "No analysis results available to share",
        variant: "destructive"
      })
      return
    }

    try {
      const videoId = `analysis_${Date.now()}`
      
      // Create the share data
      const shareData = {
        video_id: videoId,
        status: 'completed',
        prediction: result.result,
        confidence: result.confidence,
        faces_detected: result.faces_found,
        processing_time: result.processing_time,
        detection_method: result.model_used,
        timestamp: new Date().toISOString(),
        enhanced_analysis: result.enhanced_analysis || false,
        bias_applied: result.bias_applied || 0
      }

      // Try to use Web Share API with PDF if available
      if (navigator.share && navigator.canShare) {
        try {
          // Generate PDF for sharing
          const { blob: pdfBlob, reportId } = await SecurePDFGenerator.generateSecureReport({
            videoId,
            timestamp: new Date().toISOString(),
            prediction: result.result,
            confidence: result.confidence,
            facesDetected: result.faces_found,
            processingTime: result.processing_time,
            detectionMethod: result.model_used,
            enhancedAnalysis: result.enhanced_analysis || false,
            frameCount: result.frame_count,
            videoDuration: result.video_duration,
            biasApplied: result.bias_applied || 0,
            metadataFlags: result.metadata_flags || [],
            videoUrl: youtubeUrl || (file ? URL.createObjectURL(file) : undefined),
            thumbnailUrl: undefined,
            reportId: ''
          }, {
            includeThumbnail: true,
            includeMetadata: true,
            includeTechnicalDetails: true,
            watermark: 'iFake Deepfake Detection',
            encryption: false
          })

          const pdfFile = new File([pdfBlob], `deepfake_report_${reportId}.pdf`, { type: 'application/pdf' })
          
          if (navigator.canShare({ files: [pdfFile] })) {
            await navigator.share({
              title: 'Deepfake Analysis Report',
              text: `Analysis Result: ${shareData.prediction} (${shareData.confidence.toFixed(2)}% confidence) - Secure PDF Report`,
              files: [pdfFile]
            })
            return
          }
        } catch (pdfError) {
          console.warn('PDF sharing failed, falling back to text:', pdfError)
        }
      }

      // Fallback: text sharing
      if (navigator.share) {
        await navigator.share({
          title: 'Deepfake Analysis Results',
          text: `Analysis Result: ${shareData.prediction} (${shareData.confidence.toFixed(2)}% confidence) - Generated by iFake Deepfake Detection`,
          url: window.location.href
        })
      } else {
        // Final fallback: copy to clipboard
        const shareText = `Deepfake Analysis Results:
Prediction: ${shareData.prediction}
Confidence: ${shareData.confidence.toFixed(2)}%
Faces Detected: ${shareData.faces_detected}
Processing Time: ${shareData.processing_time}s
Detection Method: ${shareData.detection_method}
Enhanced Analysis: ${shareData.enhanced_analysis ? 'Yes' : 'No'}
Bias Applied: ${(shareData.bias_applied * 100).toFixed(1)}%

Generated by iFake Deepfake Detection System
${window.location.href}`
        
        await navigator.clipboard.writeText(shareText)
        
        toast({
          title: "Results Copied",
          description: "Analysis results copied to clipboard",
        })
      }
    } catch (error) {
      console.error('Share failed:', error)
      toast({
        title: "Share Failed",
        description: "Failed to share the results. Please try again.",
        variant: "destructive"
      })
    }
  }

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
        {/* 3D Background */}
        <HeroCanvas className="absolute inset-0 w-full h-full z-0" />
        {/* Hero Content */}
        <div className="relative z-10 container mx-auto max-w-6xl text-center">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">Try Detection</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Experience iFake's MesoNet CNN detection capabilities with your own video content. 
              Upload files or analyze YouTube videos instantly with 94.1% accuracy.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mb-8">
              <Badge variant="secondary" className="neural-card bg-success/10 text-success border-success/20">
                <CheckCircle className="w-4 h-4 mr-1" />
                Free analysis
              </Badge>
              <Badge variant="secondary" className="neural-card bg-primary/10 text-primary border-primary/20">
                <Shield className="w-4 h-4 mr-1" />
                94.1% accuracy
              </Badge>
              <Badge variant="secondary" className="neural-card bg-accent/10 text-accent border-accent/20">
                <Zap className="w-4 h-4 mr-1" />
                Real-time processing
              </Badge>
            </div>
            
            {/* Super Advanced Detection Link */}
            <div className="flex justify-center mb-8">
              <Button 
                asChild
                variant="outline" 
                size="lg"
                className="neural-button hover-lift bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-purple-500/20 text-purple-600 hover:bg-gradient-to-r hover:from-purple-500/20 hover:to-blue-500/20 hover:border-purple-500/40"
              >
                <a href="/super-advanced">
                  <Brain className="w-5 h-5 mr-2" />
                  Try Super Advanced Detection Mode
                  <Badge variant="secondary" className="ml-2 bg-purple-500/20 text-purple-600 border-purple-500/30">
                    NEW
                  </Badge>
                </a>
              </Button>
            </div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      {/* Access Control Section */}
      {!accessControl.hasAccess && !accessControl.isLoading && (
        <div className="mt-16">
          <AccessControlCard
            feature="try"
            onRequestAccess={() => setShowAccessRequest(true)}
          />
        </div>
      )}

      <div className="container mx-auto max-w-7xl px-4 pb-16 mt-16">
        {accessControl.isLoading ? (
          <div className="flex items-center justify-center py-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center space-y-6"
            >
              <div className="neural-card p-8 rounded-xl bg-gradient-to-br from-primary/5 via-background to-accent/5 border border-primary/20">
                <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <h3 className="text-xl font-semibold gradient-text neural-text mb-2">Verifying Access</h3>
                <p className="text-muted-foreground neural-text">Loading access permissions...</p>
              </div>
            </motion.div>
          </div>
        ) : accessControl.hasAccess ? (
          !result ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Upload Area */}
            <div className="lg:col-span-2">
              <EnhancedCard 
                title="Upload Video for Analysis"
                description="Choose your preferred method to submit video content for deepfake detection."
                className="neural-card"
                hover={false}
              >
                <Tabs value={uploadMethod} onValueChange={(v) => setUploadMethod(v as any)}>
                  <TabsList className="neural-card grid w-full grid-cols-2 mb-6">
                    <TabsTrigger value="file" className="neural-text flex items-center space-x-2">
                      <Upload className="w-4 h-4" />
                      <span>Upload Video</span>
                    </TabsTrigger>
                    <TabsTrigger value="url" className="neural-text flex items-center space-x-2">
                      <Youtube className="w-4 h-4" />
                      <span>YouTube URL</span>
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="file" className="space-y-4">
                    <div
                      className={`neural-card border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 cursor-pointer hover:neural-glow ${
                        dragActive
                          ? 'border-primary bg-primary/5 scale-105 neural-glow'
                          : file
                          ? 'border-success bg-success/5'
                          : 'border-border hover:border-primary/50 hover:bg-accent/5'
                      }`}
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="video/*"
                        className="hidden"
                        onChange={handleFileSelect}
                      />
                      <div className="flex flex-col items-center space-y-6">
                        <motion.div 
                          className={`w-20 h-20 rounded-full flex items-center justify-center neural-card ${
                            file ? 'bg-success/20 neural-glow' : 'bg-muted'
                          }`}
                          animate={{ 
                            scale: dragActive ? 1.1 : 1,
                            rotate: dragActive ? 5 : 0
                          }}
                        >
                          {file ? (
                            <CheckCircle className="w-10 h-10 text-success" />
                          ) : (
                            <FileVideo className="w-10 h-10 text-muted-foreground" />
                          )}
                        </motion.div>
                        <div>
                          <p className="text-xl font-medium mb-2 neural-text">
                            {file ? file.name : 'Drag and drop your video here'}
                          </p>
                          <p className="text-muted-foreground mb-4 neural-text">
                            {file
                              ? `Ready to analyze • ${(file.size / 1024 / 1024).toFixed(1)} MB`
                              : 'Supports MP4, AVI, MOV (max 100MB)'}
                          </p>
                          <Button 
                            variant="outline" 
                            size="lg" 
                            className="neural-button hover-lift bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300"
                          >
                            {file ? 'Change Video' : 'Browse Videos'}
                          </Button>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-center space-x-6 text-sm text-muted-foreground">
                      <div className="flex items-center space-x-2">
                        <FileVideo className="w-4 h-4" />
                        <span className="neural-text">Video files only</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Shield className="w-4 h-4" />
                        <span className="neural-text">Secure processing</span>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="url" className="space-y-4">
                    <div className="space-y-4">
                      <Input
                        placeholder="https://youtube.com/watch?v=example"
                        className="neural-card text-lg p-6 focus-visible-ring focus:neural-glow transition-all"
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                      />
                      
                      <div className="neural-card p-6 bg-muted/50 rounded-xl border border-border/50">
                        <div className="flex items-start space-x-3">
                          <Youtube className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-medium mb-2 neural-text">YouTube Analysis</p>
                            <p className="text-muted-foreground text-sm leading-relaxed neural-text">
                              We'll download and analyze the video content using our MesoNet CNN model. 
                              Processing may take longer for high-resolution or lengthy videos.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>

                {/* Mode Selection */}
                <div className="mt-6">
                  <label className="block text-sm font-medium mb-3 neural-text">
                    Detection Mode
                  </label>
                  
                  {/* Enhanced Current Mode Info */}
                  {currentModeInfo && (
                    <div className="mb-4 p-4 rounded-lg bg-accent/10 border border-accent/20">
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                          <Activity className="w-4 h-4 text-accent" />
                          <span className="text-sm font-medium neural-text">
                            Current: {currentModeInfo.display_name || currentModeInfo.mode}
                          </span>
                        </div>
                        {currentModeInfo.model_name && (
                          <div className="bg-muted/30 rounded p-2 border border-border/30">
                            <div className="flex items-center gap-2">
                              <Database className="w-3 h-3 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground neural-text">
                                Model: {currentModeInfo.model_name}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <button
                      onClick={() => handleModeChange('traditional')}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 neural-card ${
                        selectedMode === 'traditional'
                          ? 'border-primary bg-primary/10 neural-glow'
                          : 'border-border hover:border-primary/50 hover:bg-accent/5'
                      }`}
                    >
                      <div className="text-center space-y-2">
                        <Zap className="w-6 h-6 mx-auto text-primary" />
                        <div className="font-medium neural-text">Traditional (EfficientNet-B0)</div>
                        <div className="bg-muted/30 rounded p-2 border border-border/30">
                          <div className="flex items-center justify-center gap-1">
                            <Database className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground neural-text">
                              EfficientNet-B0  deepfake_detector_finetuned1.pth
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground neural-text mt-1">
                            Fast processing
                          </div>
                        </div>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => handleModeChange('modern-ai')}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 neural-card ${
                        selectedMode === 'modern-ai'
                          ? 'border-primary bg-primary/10 neural-glow'
                          : 'border-border hover:border-primary/50 hover:bg-accent/5'
                      }`}
                    >
                      <div className="text-center space-y-2">
                        <Brain className="w-6 h-6 mx-auto text-accent" />
                        <div className="font-medium neural-text">Modern AI (Multi-stage Ensemble)</div>
                        <div className="bg-muted/30 rounded p-2 border border-border/30">
                          <div className="flex items-center justify-center gap-1">
                            <Database className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground neural-text">
                              Multi-stage ensemble
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground neural-text mt-1">
                            Balanced accuracy
                          </div>
                        </div>
                      </div>
                    </button>

                    <button
                      onClick={() => handleModeChange('hybrid')}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 neural-card ${
                        selectedMode === 'hybrid'
                          ? 'border-primary bg-primary/10 neural-glow'
                          : 'border-border hover:border-primary/50 hover:bg-accent/5'
                      }`}
                    >
                      <div className="text-center space-y-2">
                        <Shield className="w-6 h-6 mx-auto text-primary" />
                        <div className="font-medium neural-text">Enhanced (Free AI Ensemble)</div>
                        <div className="bg-muted/30 rounded p-2 border border-border/30">
                          <div className="flex items-center justify-center gap-1">
                            <Database className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground neural-text">
                              Free AI ensemble
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground neural-text mt-1">
                            Maximum accuracy
                          </div>
                        </div>
                      </div>
                    </button>
                  </div>
                  
                  <div className="mt-3 text-xs text-muted-foreground neural-text">
                    {selectedMode === 'traditional' && 'Traditional Mode uses your trained deepfake_detector_finetuned1.pth model in ensemble for fast processing with proven accuracy.'}
                    {selectedMode === 'modern-ai' && 'Modern AI Mode uses all models from services/ directory including generative AI models, advanced models integration, modern AI detectors, temporal analysis, and frequency analysis.'}
                    {selectedMode === 'hybrid' && 'Hybrid Mode combines Traditional + Modern AI + Free AI Ensemble for maximum accuracy and comprehensive analysis.'}
                  </div>
                </div>

                {/* Analyze Button */}
                {((uploadMethod === 'file' && file) || (uploadMethod === 'url' && youtubeUrl)) && (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8"
                  >
                    <LoadingButton
                      onClick={startAnalysis}
                      loading={isProcessing}
                      loadingText="Analyzing Video..."
                      size="lg"
                      className="w-full"
                    >
                      {selectedMode === 'traditional' && 'Start Traditional Analysis'}
                      {selectedMode === 'modern-ai' && 'Start Modern AI Analysis'}
                      {selectedMode === 'hybrid' && 'Start Hybrid Analysis'}
                    </LoadingButton>
                  </motion.div>
                )}

                {/* Processing State */}
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8"
                  >
                    <EnhancedCard className="neural-card bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
                      <ErrorBoundary>
                        <LoadingState
                          variant="detection"
                          progress={progress}
                          message={stageDetails || (
                            selectedMode === 'enhanced' 
                              ? progress < 20 ? "Initializing Enhanced Free AI Ensemble..." :
                                progress < 40 ? "Extracting faces from video..." :
                                progress < 60 ? "Loading AI models..." :
                                progress < 80 ? "Running Enhanced AI analysis..." :
                                progress < 95 ? "Processing results..." :
                                "Finalizing Enhanced analysis..."
                              : selectedMode === 'modern-ai'
                              ? progress < 20 ? "Initializing Modern AI Multi-stage Ensemble..." :
                                progress < 40 ? "Extracting faces from video..." :
                                progress < 60 ? "Loading Modern AI models..." :
                                progress < 80 ? "Running Modern AI analysis..." :
                                progress < 95 ? "Processing results..." :
                                "Finalizing Modern AI analysis..."
                              : selectedMode === 'hybrid'
                              ? progress < 20 ? "Initializing Hybrid Detection..." :
                                progress < 40 ? "Extracting faces from video..." :
                                progress < 60 ? "Loading all detection models..." :
                                progress < 80 ? "Running Hybrid analysis..." :
                                progress < 95 ? "Processing results..." :
                                "Finalizing Hybrid analysis..."
                              : progress < 20 ? "Initializing Traditional Detection..." :
                                progress < 40 ? "Extracting faces from video..." :
                                progress < 60 ? "Loading EfficientNet model..." :
                                progress < 80 ? "Running Traditional analysis..." :
                                progress < 95 ? "Processing results..." :
                                "Finalizing Traditional analysis..."
                          )}
                          className="py-8"
                        />
                          {currentVideoId && (
                          <div className="text-center mt-4">
                            <div className="text-sm text-muted-foreground neural-text">
                              Job ID: {currentVideoId}
                            </div>
                          </div>
                        )}
                      </ErrorBoundary>
                    </EnhancedCard>
                  </motion.div>
                )}

                {/* Enhanced Error Display with Backend-Agent Style */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8"
                  >
                    <ErrorBoundary>
                      <div className="neural-card p-6 bg-destructive/10 border border-destructive/20 rounded-xl">
                        <div className="space-y-4">
                          {/* Mode Status Indicator */}
                          <div className="flex items-center gap-3">
                            <div className="w-3 h-3 bg-destructive rounded-full animate-pulse" />
                            <span className="font-semibold text-destructive neural-text">
                              {selectedMode === 'traditional' ? '⚡ Traditional Mode Selected' : 
                               selectedMode === 'modern-ai' ? '🧠 Modern AI Mode Selected' :
                               selectedMode === 'hybrid' ? '🛡️ Hybrid Mode Selected' : '🟢 Mode Selected'}
                            </span>
                          </div>
                          
                          {/* Model Information */}
                          <div className="bg-muted/30 rounded-lg p-4 border border-border/50">
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <Database className="w-4 h-4 text-muted-foreground" />
                                <span className="text-sm font-medium neural-text">
                                  Model: {
                                    selectedMode === 'traditional' ? 'EfficientNet-B0 Only' :
                                    selectedMode === 'modern-ai' ? 'Multi-stage Ensemble with Title Analysis' :
                                    selectedMode === 'enhanced' ? 'Free AI Ensemble with Fallbacks' : 'Unknown Model'
                                  }
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Analysis Status */}
                          <div className="space-y-3">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium neural-text">➡️ Starting {
                                selectedMode === 'traditional' ? 'Traditional Analysis...' :
                                selectedMode === 'modern-ai' ? 'Modern AI Analysis...' :
                                selectedMode === 'enhanced' ? 'Enhanced Analysis...' : 'Analysis...'
                              }</span>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <AlertTriangle className="w-4 h-4 text-destructive" />
                              <span className="text-destructive font-medium neural-text">
                                ❌ Analysis Failed: {error.includes('Backend Connection Failed') ? 'Backend Connection Failed' :
                                                  error.includes('404') ? 'Model Not Found' : 
                                                  error.includes('Not Found') ? 'Model Not Found' :
                                                  error.includes('Failed to fetch') ? 'Backend Connection Failed' :
                                                  error}
                              </span>
                            </div>
                            
                            {/* Show server unreachable message for connection errors */}
                            {error.includes('Backend Connection Failed') && (
                              <div className="bg-destructive/5 border border-destructive/20 rounded-lg p-3 mt-2">
                                <div className="text-sm text-destructive/80 font-mono">
                                  (Server unreachable at {API_BASE_URL})
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {/* Action Buttons */}
                          <div className="flex gap-3 pt-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => setError(null)}
                              className="neural-button bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300"
                            >
                              Dismiss
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={resetAnalysis}
                              className="neural-button bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300"
                            >
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Retry
                            </Button>
                          </div>
                        </div>
                      </div>
                    </ErrorBoundary>
                  </motion.div>
                )}
              </EnhancedCard>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* How It Works */}
              <EnhancedCard 
                title="How iFake Works"
                className="neural-card"
              >
                <div className="space-y-6">
                  {howItWorksSteps.map((step, idx) => (
                    <motion.div
                      key={step.title}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.2 }}
                      className="flex space-x-4"
                    >
                      <div className="w-12 h-12 rounded-full bg-gradient-primary neural-glow flex items-center justify-center flex-shrink-0">
                        <step.icon className="w-6 h-6 text-primary-foreground" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-2 neural-text">{step.title}</h4>
                        <p className="text-sm text-muted-foreground leading-relaxed neural-text">
                          {step.description}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </EnhancedCard>

              {/* Detection Features */}
              <EnhancedCard 
                title="Detection Features"
                className="neural-card"
              >
                <div className="space-y-4">
                  {detectionFeatures.map((feature, idx) => (
                    <motion.div
                      key={feature.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="flex items-center space-x-3 p-3 rounded-lg neural-card bg-muted/30"
                    >
                      <feature.icon className="w-5 h-5 text-primary" />
                      <div>
                        <p className="font-medium text-sm neural-text">{feature.title}</p>
                        <p className="text-xs text-muted-foreground neural-text">{feature.description}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </EnhancedCard>

              {/* Enterprise Card */}
              <Card className="neural-card p-6 bg-gradient-ai text-white hover-lift">
                <CardContent className="px-0">
                  <div className="text-center space-y-4">
                    <motion.div 
                      className="w-12 h-12 rounded-full bg-white/20 neural-glow flex items-center justify-center mx-auto"
                      whileHover={{ scale: 1.1 }}
                    >
                      <Shield className="w-6 h-6" />
                    </motion.div>
                    <div>
                      <h4 className="font-semibold mb-2 neural-text">Enterprise Solutions</h4>
                      <p className="text-sm text-white/80 mb-4 leading-relaxed neural-text">
                        Need higher limits, API access, or custom models? 
                        Contact us for enterprise-grade deepfake detection.
                      </p>
                      <Button variant="secondary" size="sm" className="neural-button hover-lift">
                        Contact Sales
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          /* Results Display */
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }}
            className="max-w-6xl mx-auto"
          >
            <EnhancedCard className="neural-card">
              <div className="flex items-center justify-between mb-8">
                <CardTitle className="text-3xl gradient-text neural-text">Analysis Results</CardTitle>
                <Button 
                  onClick={resetAnalysis} 
                  variant="outline"
                  className="neural-button hover-lift bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Analyze Another
                </Button>
              </div>
              
              {/* Sophisticated Video Display Section */}
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="mb-12"
              >
                {/* Section Header */}
                <div className="text-center mb-12">
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2, duration: 0.6 }}
                    className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 border border-primary/30 mb-6"
                  >
                    <FileVideo className="w-8 h-8 text-primary" />
                  </motion.div>
                  <h4 className="text-3xl font-bold mb-4 neural-text gradient-text">
                    Analyzed Video Content
                  </h4>
                  <p className="text-lg text-muted-foreground max-w-2xl mx-auto neural-text">
                    Experience your video analysis with our sophisticated display interface
                  </p>
                </div>
                
                {/* Main Video Container */}
                <div className="max-w-7xl mx-auto">
                  <div className="grid grid-cols-1 2xl:grid-cols-2 gap-8 lg:gap-12">
                    {/* Original Video Display */}
                    <motion.div 
                      className="flex flex-col"
                      initial={{ opacity: 0, x: -30, scale: 0.95 }}
                      animate={{ opacity: 1, x: 0, scale: 1 }}
                      transition={{ delay: 0.3, duration: 0.7, ease: "easeOut" }}
                    >
                      <div className="relative group">
                        {/* Card with sophisticated styling */}
                        <div className="neural-card p-8 rounded-2xl bg-gradient-to-br from-primary/8 via-background to-accent/8 border border-primary/20 hover:border-primary/40 transition-all duration-500 hover:shadow-2xl hover:shadow-primary/20 hover:scale-[1.02] backdrop-blur-sm">
                          {/* Header */}
                          <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/30 flex items-center justify-center">
                                <Play className="w-5 h-5 text-primary" />
                              </div>
                              <div>
                                <h5 className="text-xl font-bold neural-text">
                                  {uploadMethod === 'file' ? 'Uploaded Video' : 'YouTube Video'}
                                </h5>
                                <p className="text-sm text-muted-foreground neural-text">
                                  Original content source
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                              <span className="text-xs text-muted-foreground neural-text">Live</span>
                            </div>
                          </div>
                          
                          {/* Video Player Container */}
                          <div className="relative group/video">
                            <div className="relative overflow-hidden rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-700 hover:scale-[1.01] bg-black">
                              {uploadMethod === 'file' && file ? (
                                <ResponsiveVideoPlayer
                                  src={URL.createObjectURL(file)}
                                  className="w-full"
                                  controls
                                  onLoadStart={() => {/* console.log('Uploaded video loading started') */}}
                                  onLoadedData={() => {/* console.log('Uploaded video loaded successfully') */}}
                                  onError={(error) => console.error('Uploaded video loading error:', error)}
                                />
                              ) : uploadMethod === 'url' && youtubeUrl ? (
                                <div className="relative aspect-video w-full overflow-hidden rounded-2xl bg-black">
                                  <iframe
                                    src={`https://www.youtube.com/embed/${extractYouTubeId(youtubeUrl)}`}
                                    className="h-full w-full"
                                    // frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                    title="YouTube Video"
                                  />
                                </div>
                              ) : result.video_url ? (
                                <ResponsiveVideoPlayer
                                  src={`${API_BASE_URL}${result.video_url}`}
                                  className="w-full"
                                  controls
                                  onLoadStart={() => console.log('Processed video loading started')}
                                  onLoadedData={() => console.log('Processed video loaded successfully')}
                                  onError={(error) => console.error('Processed video loading error:', error)}
                                />
                              ) : (
                                <div className="aspect-video w-full flex items-center justify-center bg-gradient-to-br from-muted/50 to-muted/30 rounded-2xl">
                                  <div className="text-center">
                                    <FileVideo className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                                    <p className="text-muted-foreground neural-text text-lg">No video available</p>
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* Sophisticated Overlay Effects */}
                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover/video:opacity-100 transition-all duration-500 pointer-events-none" />
                            <div className="absolute top-4 right-4 opacity-0 group-hover/video:opacity-100 transition-all duration-300">
                              <div className="bg-black/60 backdrop-blur-sm rounded-full px-3 py-1 text-white text-xs font-medium">
                                HD Quality
                              </div>
                            </div>
                          </div>
                          
                          {/* Enhanced Video Info */}
                          <div className="mt-8 space-y-4">
                            {uploadMethod === 'file' && file && (
                              <div className="flex justify-between items-center p-4 rounded-xl bg-gradient-to-r from-muted/40 to-muted/20 border border-border/30 hover:border-border/50 transition-all duration-300">
                                <div className="flex items-center space-x-3">
                                  <FileVideo className="w-5 h-5 text-primary" />
                                  <span className="neural-text font-medium truncate max-w-xs">{file.name}</span>
                                </div>
                                <Badge variant="secondary" className="neural-card bg-primary/10 text-primary border-primary/20">
                                  {(file.size / 1024 / 1024).toFixed(1)} MB
                                </Badge>
                              </div>
                            )}
                            {uploadMethod === 'url' && youtubeUrl && (
                              <div className="p-4 rounded-xl bg-gradient-to-r from-muted/40 to-muted/20 border border-border/30 hover:border-border/50 transition-all duration-300">
                                <div className="flex items-center space-x-3 mb-2">
                                  <Youtube className="w-5 h-5 text-red-500" />
                                  <span className="neural-text font-medium">YouTube Source</span>
                                </div>
                                <span className="neural-text text-sm break-all text-muted-foreground">{youtubeUrl}</span>
                              </div>
                            )}
                            {result.video_duration && (
                              <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-accent/10 to-primary/10 border border-accent/30 hover:border-accent/50 transition-all duration-300">
                                <div className="flex items-center space-x-3">
                                  <Clock className="w-5 h-5 text-accent" />
                                  <span className="neural-text font-medium">Duration</span>
                                </div>
                                <Badge variant="outline" className="neural-card bg-accent/20 text-accent border-accent/30">
                                  {result.video_duration.toFixed(1)}s
                                </Badge>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {/* Decorative Elements */}
                        <div className="absolute -top-2 -right-2 w-4 h-4 bg-primary/20 rounded-full animate-pulse" />
                        <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-accent/20 rounded-full animate-pulse delay-1000" />
                      </div>
                    </motion.div>

                    {/* Processed Video Display (if different from original) */}
                    {result.video_url && (uploadMethod === 'file' || uploadMethod === 'url') && (
                      <motion.div 
                        className="flex flex-col"
                        initial={{ opacity: 0, x: 30, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        transition={{ delay: 0.5, duration: 0.7, ease: "easeOut" }}
                      >
                        <div className="relative group">
                          {/* Card with sophisticated styling */}
                          <div className="neural-card p-8 rounded-2xl bg-gradient-to-br from-accent/8 via-background to-primary/8 border border-accent/20 hover:border-accent/40 transition-all duration-500 hover:shadow-2xl hover:shadow-accent/20 hover:scale-[1.02] backdrop-blur-sm">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-6">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent/20 to-accent/30 flex items-center justify-center">
                                  <Cpu className="w-5 h-5 text-accent" />
                                </div>
                                <div>
                                  <h5 className="text-xl font-bold neural-text">
                                    Processed Video
                                  </h5>
                                  <p className="text-sm text-muted-foreground neural-text">
                                    Analysis-ready format
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                                <span className="text-xs text-muted-foreground neural-text">Processed</span>
                              </div>
                            </div>
                            
                            {/* Video Player Container */}
                            <div className="relative group/video">
                              <div className="relative overflow-hidden rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-700 hover:scale-[1.01] bg-black">
                                <ResponsiveVideoPlayer
                                  src={`${API_BASE_URL}${result.video_url}`}
                                  className="w-full"
                                  controls
                                  onLoadStart={() => console.log('Processed video loading started')}
                                  onLoadedData={() => console.log('Processed video loaded successfully')}
                                  onError={(error) => console.error('Processed video loading error:', error)}
                                />
                              </div>
                              
                              {/* Sophisticated Overlay Effects */}
                              <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover/video:opacity-100 transition-all duration-500 pointer-events-none" />
                              <div className="absolute top-4 right-4 opacity-0 group-hover/video:opacity-100 transition-all duration-300">
                                <div className="bg-black/60 backdrop-blur-sm rounded-full px-3 py-1 text-white text-xs font-medium">
                                  AI Processed
                                </div>
                              </div>
                            </div>
                            
                            {/* Enhanced Video Info */}
                            <div className="mt-8 space-y-4">
                              <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-accent/10 to-primary/10 border border-accent/30 hover:border-accent/50 transition-all duration-300">
                                <div className="flex items-center space-x-3">
                                  <Shield className="w-5 h-5 text-accent" />
                                  <span className="neural-text font-medium">Analysis Format</span>
                                </div>
                                <Badge variant="outline" className="neural-card bg-accent/20 text-accent border-accent/30">
                                  Ready
                                </Badge>
                              </div>
                              {result.frame_count && (
                                <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-muted/40 to-muted/20 border border-border/30 hover:border-border/50 transition-all duration-300">
                                  <div className="flex items-center space-x-3">
                                    <Activity className="w-5 h-5 text-primary" />
                                    <span className="neural-text font-medium">Frames Analyzed</span>
                                  </div>
                                  <Badge variant="secondary" className="neural-card bg-primary/10 text-primary border-primary/20">
                                    {result.frame_count.toLocaleString()}
                                  </Badge>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Decorative Elements */}
                          <div className="absolute -top-2 -right-2 w-4 h-4 bg-accent/20 rounded-full animate-pulse delay-500" />
                          <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-primary/20 rounded-full animate-pulse delay-1500" />
                        </div>
                      </motion.div>
                    )}
                  </div>
                </div>
              </motion.div>

              {/* Main Result */}
              <div className="relative text-center mb-10 neural-card p-8 rounded-xl bg-gradient-to-br from-muted/30 to-muted/10">
                {(() => {
                  // Clean the result text to remove any trailing numbers
                  const cleanResult = result.result ? result.result.replace(/\s+\d+$/, '') : result.result;
                  
                  const formattedResult = formatDetectionResult({
                    final_result: cleanResult,
                    confidence: result.confidence,
                    faces_analyzed: result.faces_found,
                    processing_time: result.processing_time,
                    bias_applied: result.bias_applied || 0,
                    metadata_flags: result.metadata_flags || []
                  });
                  
                  return (
                    <>
                <motion.div 
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", bounce: 0.4 }}
                        className="text-5xl font-bold mb-4 neural-text"
                        style={{ color: formattedResult.color }}
                      >
                        {formattedResult.label}
                      </motion.div>
                      {result.bias_applied && result.bias_applied > 0 && (
                        <motion.div 
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 }}
                          className="text-sm text-muted-foreground mb-4"
                          title={getBiasTooltipText(result.bias_applied)}
                        >
                          <span className="inline-flex items-center gap-1">
                            <Brain className="w-4 h-4" />
                            Bias applied: {(result.bias_applied * 100).toFixed(1)}%
                          </span>
                </motion.div>
                      )}
                      {/* AI-Powered Summary Display */}
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="max-w-4xl mx-auto"
                      >
                        <AISummaryDisplay 
                          detectionResult={{
                            final_result: cleanResult,
                            confidence: result.confidence,
                            faces_analyzed: result.faces_found,
                            processing_time: result.processing_time,
                            bias_applied: result.bias_applied || 0,
                            metadata_flags: result.metadata_flags || [],
                            model_contributions: {
                              efficientnet_result: result.efficientnet_result,
                              efficientnet_confidence: result.efficientnet_confidence,
                              temporal_score: result.temporal_score || result.temporal_consistency || 0.5,
                              spatial_score: result.spatial_score || 0.5,
                              frequency_score: result.frequency_score || 0.5,
                              model_type: result.model_type || 'MesoNet CNN'
                            },
                            analysis_method: result.analysis_method,
                            ensemble_scores: result.ensemble_scores,
                            temporal_consistency: result.temporal_consistency,
                            face_quality_score: result.face_quality_score,
                            ai_tool_detected: result.ai_tool_detected,
                            title_analysis: result.title_analysis,
                            // Enhanced fields for dynamic summaries - use detection_mode from result
                            detection_mode: (result as any).detection_mode || (result as any).model_info?.detection_mode || 
                              (selectedMode === 'traditional' ? 'Traditional' : 
                               selectedMode === 'modern-ai' ? 'Modern AI' : 
                               selectedMode === 'enhanced' ? 'Enhanced' : 
                               selectedMode === 'hybrid' ? 'Hybrid' : 'Traditional'),
                            primary_model: (result as any).model_info?.primary_model || result.model_type || result.model_used || 'MesoNet',
                            model_name: (result as any).model_info?.primary_model || result.model_type || result.model_used || 'MesoNet',
                            anomalies: (result as any).anomalies || [],
                            lighting_consistency: (result as any).lighting_consistency,
                            motion_coherence: (result as any).motion_coherence,
                            texture_quality: (result as any).texture_quality,
                            model_info: (result as any).model_info
                          }}
                          showConfidence={showConfidence}
                          className="mb-6"
                        />
                      </motion.div>

                      {/* Full Analysis View */}
                      <FullAnalysisView 
                        detectionResult={{
                          final_result: cleanResult,
                          confidence: result.confidence,
                          faces_analyzed: result.faces_found,
                          processing_time: result.processing_time,
                          bias_applied: result.bias_applied || 0,
                          metadata_flags: result.metadata_flags || [],
                          model_contributions: {
                            efficientnet_result: result.efficientnet_result,
                            efficientnet_confidence: result.efficientnet_confidence,
                            temporal_score: result.temporal_score,
                            spatial_score: result.spatial_score,
                            frequency_score: result.frequency_score,
                            model_type: result.model_type || 'MesoNet CNN'
                          },
                          analysis_method: result.analysis_method,
                          ensemble_scores: result.ensemble_scores,
                          temporal_consistency: result.temporal_consistency,
                          face_quality_score: result.face_quality_score,
                          ai_tool_detected: result.ai_tool_detected,
                          title_analysis: result.title_analysis,
                          // Enhanced fields for dynamic summaries
                          detection_mode: (result as any).detection_mode || (result as any).model_info?.detection_mode || (result.ensemble_scores && Object.keys(result.ensemble_scores).length > 1 ? 'Hybrid' : 'Traditional'),
                          primary_model: (result as any).model_info?.primary_model || result.model_type || result.model_used || 'MesoNet',
                          model_name: (result as any).model_info?.primary_model || result.model_type || result.model_used || 'MesoNet',
                          anomalies: (result as any).anomalies || [],
                          lighting_consistency: (result as any).lighting_consistency,
                          motion_coherence: (result as any).motion_coherence,
                          texture_quality: (result as any).texture_quality,
                          model_info: (result as any).model_info
                        }}
                        showConfidence={showConfidence}
                        onToggleConfidence={() => setShowConfidence(!showConfidence)}
                        className="mb-6"
                      />
                      
                      {/* Confidence Toggle Button */}
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="mt-6"
                      >
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowConfidence(!showConfidence)}
                          className="neural-button hover-lift border-muted-foreground/30 text-muted-foreground hover:text-foreground hover:border-foreground/50"
                        >
                          {showConfidence ? (
                            <>
                              <EyeOff className="w-4 h-4 mr-2" />
                              Hide Confidence
                            </>
                          ) : (
                            <>
                              <Eye className="w-4 h-4 mr-2" />
                              View Confidence
                            </>
                          )}
                        </Button>
                      </motion.div>
                    </>
                  );
                })()}
                
                {/* Confidence Panel */}
                {showConfidence && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3 }}
                    className="absolute top-4 right-4 bg-muted/80 backdrop-blur-sm border border-border/50 rounded-lg p-4 max-w-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="text-sm text-muted-foreground">Confidence Score</div>
                      <button
                        onClick={() => setShowConfidence(false)}
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors p-1 rounded hover:bg-muted/50"
                        title="Hide confidence"
                      >
                        <EyeOff className="w-3 h-3" />
                      </button>
                    </div>
                    {result.confidence > 0 && (
                      <div className={`text-2xl font-bold ${getConfidenceColorClass(result.confidence)}`}>
                        {formatConfidenceDisplay(result.confidence)}
                      </div>
                    )}
                    {result.confidence > 0 && (
                      <div className="text-xs text-muted-foreground mt-1">
                        AI Analysis Confidence
                      </div>
                    )}
                  </motion.div>
                )}
              </div>

              {/* Detailed Metrics */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="neural-card p-6 text-center hover-lift">
                  <div className="text-3xl font-bold text-primary mb-2 neural-text">{result.faces_found || 0}</div>
                  <div className="text-sm text-muted-foreground neural-text">Faces Detected</div>
                </Card>
                <Card className="neural-card p-6 text-center hover-lift">
                  <div className="text-lg font-bold text-primary mb-2 neural-text">
                    {result.model_used || 'Standard Detection'}
                  </div>
                  <div className="text-sm text-muted-foreground neural-text">Detection Method</div>
                </Card>
                <Card className="neural-card p-6 text-center hover-lift">
                  <div className="text-3xl font-bold text-primary mb-2 neural-text">
                    {typeof result.processing_time === 'string' ? result.processing_time : `${result.processing_time || 0}s`}
                  </div>
                  <div className="text-sm text-muted-foreground neural-text">Processing Time</div>
                </Card>
                <Card className="neural-card p-6 text-center hover-lift">
                  <div className="text-lg font-bold text-primary mb-2 neural-text">
                    {selectedMode === 'traditional' ? 'Traditional' : 
                     selectedMode === 'modern-ai' ? 'Modern AI' : 
                     selectedMode === 'enhanced' ? 'Enhanced' : 'Standard'}
                  </div>
                  <div className="text-sm text-muted-foreground neural-text">Analysis Type</div>
                </Card>
              </div>

              {/* Step-by-Step Processing Display */}
              {result.processing_stages && (
                <motion.div 
                  className="mt-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <Card className="neural-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 neural-text">
                        <Activity className="w-5 h-5 text-accent" />
                        Processing Stages
                        <Badge variant="outline" className="ml-auto bg-accent/20 text-accent border-accent/30">
                          {result.processing_stages.stages_completed}/{result.processing_stages.total_stages} Complete
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {result.processing_stages.stages.map((stage: any, index: number) => (
                        <motion.div
                          key={stage.name}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.7 + index * 0.1 }}
                          className="border rounded-lg p-4 space-y-3"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                stage.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                                stage.status === 'in_progress' ? 'bg-blue-500/20 text-blue-500' :
                                stage.status === 'failed' ? 'bg-red-500/20 text-red-500' :
                                'bg-gray-500/20 text-gray-500'
                              }`}>
                                {stage.status === 'completed' ? '✓' :
                                 stage.status === 'in_progress' ? '⏳' :
                                 stage.status === 'failed' ? '✗' : '○'}
                              </div>
                              <div>
                                <h4 className="font-medium neural-text">{stage.name}</h4>
                                {stage.message && (
                                  <p className="text-sm text-muted-foreground">{stage.message}</p>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {stage.duration && (
                                <Badge variant="secondary" className="text-xs">
                                  {stage.duration}s
                                </Badge>
                              )}
                              {stage.models_count > 0 && (
                                <Badge variant="outline" className="text-xs">
                                  {stage.models_count} models
                                </Badge>
                              )}
                            </div>
                          </div>
                          
                          {stage.models && stage.models.length > 0 && (
                            <div className="ml-11 space-y-2">
                              <h5 className="text-sm font-medium text-muted-foreground">Model Results:</h5>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {stage.models.map((model: any, modelIndex: number) => (
                                  <div key={modelIndex} className="flex items-center justify-between p-2 bg-muted/30 rounded text-xs">
                                    <span className="font-medium">{model.name}</span>
                                    <div className="flex items-center gap-2">
                                      <span className={`px-2 py-1 rounded text-xs ${
                                        model.prediction.includes('Real') ? 'bg-green-500/20 text-green-600' :
                                        model.prediction.includes('Deepfake') ? 'bg-red-500/20 text-red-600' :
                                        'bg-gray-500/20 text-gray-600'
                                      }`}>
                                        {model.prediction}
                                      </span>
                                      <span className="text-muted-foreground">
                                        {(model.confidence * 100).toFixed(1)}%
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {stage.errors && stage.errors.length > 0 && (
                            <div className="ml-11">
                              <div className="text-red-500 text-sm">
                                <strong>Errors:</strong> {stage.errors.join(', ')}
                              </div>
                            </div>
                          )}
                          
                          {stage.warnings && stage.warnings.length > 0 && (
                            <div className="ml-11">
                              <div className="text-yellow-500 text-sm">
                                <strong>Warnings:</strong> {stage.warnings.join(', ')}
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Markdown Report Display */}
              {result.markdown_report && (
                <motion.div 
                  className="mt-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                >
                  <Card className="neural-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 neural-text">
                        <FileText className="w-5 h-5 text-accent" />
                        Detailed Processing Report
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const blob = new Blob([result.markdown_report], { type: 'text/markdown' })
                            const url = URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = `deepfake_processing_report_${result.video_id || 'unknown'}.md`
                            document.body.appendChild(a)
                            a.click()
                            document.body.removeChild(a)
                            URL.revokeObjectURL(url)
                          }}
                          className="ml-auto"
                        >
                          Download Report
                        </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="bg-muted/30 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <pre className="text-sm whitespace-pre-wrap neural-text font-mono">
                          {result.markdown_report}
                        </pre>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Additional Metrics */}
              {(result.frame_count || result.video_duration) && (
                <div className="grid md:grid-cols-2 gap-6 mt-6">
                  {result.frame_count && (
                    <Card className="neural-card p-6 text-center hover-lift">
                      <div className="text-2xl font-bold text-accent mb-2 neural-text">
                        {result.frame_count.toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground neural-text">Frames Analyzed</div>
                    </Card>
                  )}
                  {result.video_duration && (
                    <Card className="neural-card p-6 text-center hover-lift">
                      <div className="text-2xl font-bold text-accent mb-2 neural-text">
                        {result.video_duration.toFixed(1)}s
                      </div>
                      <div className="text-sm text-muted-foreground neural-text">Video Duration</div>
                    </Card>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="border-t border-border/30 mt-8 pt-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 place-items-center w-full">
                <LoadingButton 
                  onClick={resetAnalysis}
                  size="lg"
                  variant="default"
                  className="neural-button hover-lift w-full"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Analyze Another Video
                </LoadingButton>
                <LoadingButton 
                  onClick={() => downloadReport('pdf')}
                  size="lg"
                  variant="outline"
                  className="neural-button hover-lift w-full"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Download PDF Report
                </LoadingButton>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button 
                      size="lg"
                      variant="outline"
                      className="neural-button hover-lift w-full bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300"
                    >
                      <Database className="w-4 h-4 mr-2" />
                      Other Formats
                      <ChevronDown className="w-4 h-4 ml-2" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="neural-card w-48">
                    <DropdownMenuItem 
                      onClick={() => downloadReport('json')}
                      className="cursor-pointer hover:bg-accent/50"
                    >
                      <Database className="w-4 h-4 mr-2" />
                      JSON Format
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => downloadReport('txt')}
                      className="cursor-pointer hover:bg-accent/50"
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Text Format
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => downloadReport('csv')}
                      className="cursor-pointer hover:bg-accent/50"
                    >
                      <FileSpreadsheet className="w-4 h-4 mr-2" />
                      CSV Format
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <LoadingButton 
                  onClick={() => shareResults()}
                  size="lg"
                  variant="outline"
                  className="neural-button hover-lift w-full"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Share Results
                </LoadingButton>
                </div>
              </div>
            </EnhancedCard>
          </motion.div>
        )) : null}
      </div>

      {/* Access Request Modal */}
      <AccessRequestModal
        isOpen={showAccessRequest}
        onClose={() => setShowAccessRequest(false)}
        requestType="try_access"
      />
    </main>
  )
}

export default function TryIt() {
  return (
    <AdminBypass 
      feature="try"
      fallbackComponent={({ children }) => (
        <ProtectedRoute
          requireAuth={true}
          requiredPermissions={['detection:create']}
          requiredRoles={['user', 'admin', 'premium']}
        >
          {children}
        </ProtectedRoute>
      )}
    >
      <TryItContent />
    </AdminBypass>
  )
}

