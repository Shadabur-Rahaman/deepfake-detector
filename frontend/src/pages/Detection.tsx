import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { LoadingButton } from '@/components/ui/LoadingButton'
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import { ProgressIndicator } from '@/components/ui/ProgressIndicator'
import { toast } from "@/components/ui/use-toast"
import { useAuth } from '@/contexts/SimpleAuthContext'
import { useAccessControl, ACCESS_CONFIGS } from '@/hooks/useAccessControl'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { AdminBypass } from '@/components/admin/AdminBypass'
import { AccessRequestModal } from '@/components/auth/AccessRequestModal'
import { AccessControlCard } from '@/components/auth/AccessControlCard'
import { API_BASE_URL } from '@/config/api'
import { formatDetectionResult, getConfidenceColorClass, formatConfidenceDisplay, formatConfidenceValue, getBiasTooltipText } from '@/lib/detection-utils'
import { SecurePDFGenerator } from '@/lib/pdf-generator'
import { downloadFile, getDownloadInstructions } from '@/lib/download-utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { HeroCanvas } from "@/components/three/HeroCanvas"
import { 
  Camera, 
  Video, 
  StopCircle, 
  Play,
  AlertTriangle, 
  CheckCircle2, 
  Shield, 
  Zap,
  Brain,
  Eye,
  Activity,
  Settings,
  Users,
  Crown,
  Clock,
  Target,
  Gauge,
  Wifi,
  WifiOff,
  Loader2,
  RefreshCw,
  Download,
  Share,
  Database,
  FileText,
  FileSpreadsheet,
  BarChart3,
  ChevronDown
} from 'lucide-react';

interface DetectionResult {
  authentic: boolean;
  confidence: number;
  processingTime: number;
  facesDetected: number;
  frameRate: number;
  timestamp: Date;
  analysisDetails?: {
    manipulationIndicators: string[];
    faceCoordinates: { x: number; y: number; width: number; height: number };
    suspiciousRegions: number;
  };
  biasApplied?: number;
  metadataFlags?: string[];
  // Ultra Ensemble specific fields
  modelUsed?: string;
  totalModelsUsed?: number;
  individualResults?: Record<string, any>;
  advancedFeatures?: Record<string, any>;
  sophisticatedAnalysis?: Record<string, boolean>;
  ensembleScore?: number;
  modelWeights?: Record<string, number>;
}

interface CameraPermissionStatus {
  state: 'granted' | 'denied' | 'prompt' | 'unknown';
  error?: string;
}

function DetectionContent() {
  const { user } = useAuth();
  const accessControl = useAccessControl(ACCESS_CONFIGS.detection);
  const [cameraPermission, setCameraPermission] = useState<CameraPermissionStatus>({ state: 'unknown' });
  const [isDetecting, setIsDetecting] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [detectionHistory, setDetectionHistory] = useState<DetectionResult[]>([]);
  const [frameRate, setFrameRate] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  const [processedFrames, setProcessedFrames] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isAdvancedSettingsOpen, setIsAdvancedSettingsOpen] = useState(false);
  const [showAccessRequest, setShowAccessRequest] = useState(false);
  const [debugMessages, setDebugMessages] = useState<any[]>([]);
  
  // Advanced Settings State
  const [settings, setSettings] = useState({
    confidenceThreshold: 75,
    frameRate: 'auto',
    detectionMode: 'modern-ai',
    enablePreprocessing: true,
    enableSmoothing: true,
    maxHistorySize: 100,
    showDetailedStats: true,
    autoDownload: false,
    notificationSound: false,
    useUltraEnsemble: false
  });
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const frameCountRef = useRef(0);
  const lastResultTimestampRef = useRef<number | null>(null);

  const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api', '') + '/ws/real-time-detection';

  // Access control is now handled by the useAccessControl hook

  // Check camera permissions on mount
  useEffect(() => {
    checkCameraPermissions();
    loadSettings();
  }, []);

  // Load settings from localStorage
  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('detectionSettings');
      if (saved) {
        const parsedSettings = JSON.parse(saved);
        setSettings(prev => ({ ...prev, ...parsedSettings }));
      }
    } catch (error) {
      console.warn('Failed to load settings:', error);
    }
  };

  // Save settings to localStorage
  const saveSettings = (newSettings: typeof settings) => {
    try {
      localStorage.setItem('detectionSettings', JSON.stringify(newSettings));
      setSettings(newSettings);
      toast({
        title: "Settings Saved",
        description: "Your detection settings have been saved successfully",
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast({
        title: "Save Failed",
        description: "Failed to save settings. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Reset settings to default
  const resetSettings = () => {
    const defaultSettings = {
      confidenceThreshold: 75,
      frameRate: 'auto',
      detectionMode: 'modern-ai',
      enablePreprocessing: true,
      enableSmoothing: true,
      maxHistorySize: 100,
      showDetailedStats: true,
      autoDownload: false,
      notificationSound: false,
      useUltraEnsemble: false
    };
    setSettings(defaultSettings);
    localStorage.setItem('detectionSettings', JSON.stringify(defaultSettings));
    toast({
      title: "Settings Reset",
      description: "Settings have been reset to default values",
    });
  };

  const checkCameraPermissions = async () => {
    try {
      const result = await navigator.permissions.query({ name: 'camera' as PermissionName });
      setCameraPermission({ state: result.state });
      
      result.onchange = () => {
        setCameraPermission({ state: result.state });
      };
    } catch (err) {
      console.warn('Permission API not supported, will request directly');
      setCameraPermission({ state: 'prompt' });
    }
  };

  const requestCameraAccess = async (): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          frameRate: { ideal: 30 }
        },
        audio: false
      });
      
      setCameraPermission({ state: 'granted' });
      return stream;
    } catch (err) {
      const error = err as Error;
      setCameraPermission({ 
        state: 'denied', 
        error: error.message || 'Camera access denied' 
      });
      throw error;
    }
  };

  const connectWebSocket = useCallback(() => {
    return new Promise<WebSocket>((resolve, reject) => {
      try {
        const ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          setConnectionStatus('connected');
          resolve(ws);
        };

        ws.onmessage = (event) => {
          try {
            const result = JSON.parse(event.data);
            console.log('📨 Raw WebSocket message:', result);
            console.log('📨 Message type:', result.type);
            console.log('📨 Message keys:', Object.keys(result));
            console.log('📨 Prediction:', result.prediction);
            console.log('📨 Confidence:', result.confidence);
            console.log('📨 Final result:', result.final_result);
            
            // Add to debug messages
            setDebugMessages(prev => [result, ...prev.slice(0, 9)]);
            
            // Handle different message types
            if (result.type === 'connection_ready') {
              console.log('🔗 Server ready for detection');
              console.log('🔗 Endpoint:', result.endpoint);
              console.log('🔗 Message:', result.message);
              setConnectionStatus('connected');
              setError(null);
              return;
            }
            
            if (result.type === 'detection_started') {
              console.log('Detection started successfully');
              
              // Start frame capture interval now that detection is confirmed to be running
              if (!frameIntervalRef.current) {
                frameIntervalRef.current = setInterval(() => {
                  if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    captureAndSendFrame();
                  } else {
                    console.warn('WebSocket not open, skipping frame capture');
                    // Clear interval if WebSocket is not open
                    if (frameIntervalRef.current) {
                      clearInterval(frameIntervalRef.current);
                      frameIntervalRef.current = null;
                    }
                  }
                }, 2500); // Every 2.5 seconds for real-time detection
                console.log('Frame capture started');
              }
              return;
            }
            
            if (result.type === 'detection_stopped') {
              console.log('Detection stopped');
              return;
            }
            
            if (result.type === 'heartbeat') {
              console.log('Heartbeat received');
              return;
            }
            
            if (result.type === 'error') {
              console.error('Server error:', result.message);
              setError(result.message);
              return;
            }
            
            // Handle detection results - check for multiple possible message types
            if (result.type === 'detection_result' || result.type === 'result' || result.prediction || result.final_result) {
              console.log('🔍 Received detection result:', result);
              console.log('🔍 Processing detection result with type:', result.type);
              console.log('🔍 Prediction from backend:', result.prediction);
              console.log('🔍 Confidence from backend:', result.confidence);
              console.log('🔍 Client ID from backend:', result.client_id);
              console.log('🔍 Server timestamp:', result.server_timestamp);
              
              // Check if this is a stale result (from a previous connection)
              if (result.server_timestamp && lastResultTimestampRef.current && 
                  result.server_timestamp <= lastResultTimestampRef.current) {
                console.warn('⚠️ Ignoring stale detection result - timestamp is older than last result');
                return;
              }
              if (result.server_timestamp) {
                lastResultTimestampRef.current = result.server_timestamp;
              }
              
              // Process backend JSON response with new format
              const backendData = {
                final_result: result.final_result || result.prediction,
                prediction: result.prediction,
                authentic: result.authentic,
                confidence: result.confidence,
                faces_analyzed: result.faces_analyzed || result.faces_detected,
                faces_detected: result.faces_detected || 0,
                processing_time: result.processing_time || 0,
                bias_applied: result.bias_applied,
                metadata_flags: result.metadata_flags || [],
                // Ultra Ensemble specific fields
                model_used: result.model_used || result.detection_method,
                total_models_used: result.total_models_used || result.models_used?.length,
                individual_results: result.individual_results || result.model_analysis,
                advanced_features: result.advanced_features,
                sophisticated_analysis: result.sophisticated_analysis,
                ensemble_score: result.ensemble_score || result.final_ensemble_score,
                model_weights: result.model_weights
              };
              
              // ✅ FIX: Real-time detector sends confidence as percentage (0-100), not decimal (0-1)
              // Only convert if confidence is less than 1 (indicating decimal format)
              const confidence = backendData.confidence < 1 ? (backendData.confidence || 0) * 100 : (backendData.confidence || 0);
              
              // Use backend timestamp if available, otherwise use current time
              const timestamp = result.timestamp ? new Date(result.timestamp * 1000) : new Date();
              
              const detectionData: DetectionResult = {
                authentic: backendData.final_result?.toLowerCase().includes('authentic') || 
                          backendData.prediction?.toLowerCase().includes('authentic') ||
                          backendData.final_result?.toLowerCase().includes('real') || 
                          backendData.prediction?.toLowerCase().includes('real') ||
                          backendData.prediction === 'Real Face' ||
                          backendData.authentic === true,
                confidence: confidence,
                processingTime: typeof backendData.processing_time === 'string' && backendData.processing_time === 'real-time' ? 0 : (backendData.processing_time || 0),
                facesDetected: backendData.faces_analyzed || backendData.faces_detected || 0,
                frameRate: frameRate,
                timestamp: timestamp,
                analysisDetails: {
                  manipulationIndicators: result.manipulation_indicators || backendData.metadata_flags || [],
                  faceCoordinates: result.face_coordinates ? {
                    x: result.face_coordinates.x || 0,
                    y: result.face_coordinates.y || 0,
                    width: result.face_coordinates.width || 0,
                    height: result.face_coordinates.height || 0
                  } : { x: 0, y: 0, width: 0, height: 0 },
                  suspiciousRegions: result.suspicious_regions || 0
                },
                // Store additional backend data for tooltips
                biasApplied: backendData.bias_applied || 0,
                metadataFlags: backendData.metadata_flags || [],
                // Ultra Ensemble specific fields
                modelUsed: backendData.model_used,
                totalModelsUsed: backendData.total_models_used,
                individualResults: backendData.individual_results,
                advancedFeatures: backendData.advanced_features,
                sophisticatedAnalysis: backendData.sophisticated_analysis,
                ensembleScore: backendData.ensemble_score,
                modelWeights: backendData.model_weights
              };
              
              console.log('✅ Processed detection data:', detectionData);
              console.log('✅ Authentic flag:', detectionData.authentic);
              console.log('✅ Final confidence:', detectionData.confidence);
              console.log('✅ Backend prediction:', backendData.prediction);
              console.log('✅ Backend final_result:', backendData.final_result);
              setDetectionResult(detectionData);
              setDetectionHistory(prev => [detectionData, ...prev.slice(0, 9)]);
              setProcessedFrames(prev => prev + 1);
            } else {
              // Fallback: Handle any message that looks like a detection result
              if (result.prediction || result.final_result || result.confidence !== undefined) {
                console.log('🔄 Fallback detection result handler:', result);
                console.log('🔄 Fallback - Prediction:', result.prediction);
                console.log('🔄 Fallback - Confidence:', result.confidence);
                console.log('🔄 Fallback - Final result:', result.final_result);
                
                const fallbackData: DetectionResult = {
                  authentic: result.prediction?.toLowerCase().includes('authentic') || 
                            result.final_result?.toLowerCase().includes('authentic') ||
                            result.prediction?.toLowerCase().includes('real') || 
                            result.final_result?.toLowerCase().includes('real') ||
                            result.authentic === true,
                  confidence: result.confidence < 1 ? (result.confidence || 0) * 100 : (result.confidence || 0),
                  processingTime: typeof result.processing_time === 'string' && result.processing_time === 'real-time' ? 0 : (result.processing_time || 0),
                  facesDetected: result.faces_detected || result.faces_analyzed || 0,
                  frameRate: frameRate,
                  timestamp: new Date(),
                  analysisDetails: {
                    manipulationIndicators: result.metadata_flags || [],
                    faceCoordinates: { x: 0, y: 0, width: 0, height: 0 },
                    suspiciousRegions: 0
                  },
                  biasApplied: result.bias_applied || 0,
                  metadataFlags: result.metadata_flags || []
                };
                
                console.log('✅ Fallback detection data:', fallbackData);
                console.log('✅ Fallback - Authentic flag:', fallbackData.authentic);
                console.log('✅ Fallback - Final confidence:', fallbackData.confidence);
                setDetectionResult(fallbackData);
                setDetectionHistory(prev => [fallbackData, ...prev.slice(0, 9)]);
                setProcessedFrames(prev => prev + 1);
              }
            }
            
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('disconnected');
          setError('WebSocket connection failed');
          reject(error);
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          setConnectionStatus('disconnected');
          
          // Handle different close codes
          if (event.code === 1000) {
            // Normal closure - this might happen during startup
            console.log('WebSocket closed normally');
            if (isDetecting) {
              setError('WebSocket connection closed. Please restart detection.');
              setIsConnecting(false);
            }
          } else if (event.code === 1005) {
            // No status code received - this is common during startup
            console.log('WebSocket closed without status code (startup issue)');
            if (isDetecting) {
              setError('WebSocket connection lost during startup. Please restart detection.');
              setIsConnecting(false);
            }
          } else if (!event.wasClean && isDetecting) {
            setError('Connection lost unexpectedly. Attempting to reconnect...');
            // Attempt to reconnect after 2 seconds
            setTimeout(() => {
              if (isDetecting) {
                console.log('Attempting to reconnect WebSocket...');
                connectWebSocket().then(newWs => {
                  wsRef.current = newWs;
                  setConnectionStatus('connected');
                  setError(null);
                  // Clear any stale detection results on reconnection
                  setDetectionResult(null);
                  setDetectionHistory([]);
                  setProcessedFrames(0);
                  lastResultTimestampRef.current = null; // Clear timestamp tracking
                  console.log('🔄 WebSocket reconnected - cleared stale state');
                }).catch(err => {
                  console.error('Reconnection failed:', err);
                  setError('Failed to reconnect. Please restart detection.');
                });
              }
            }, 2000);
          }
        };

      } catch (err) {
        reject(err);
      }
    });
  }, [WS_URL, frameRate]);

  const captureAndSendFrame = useCallback(() => {
    try {
      if (!videoRef.current || !canvasRef.current || !wsRef.current) {
        console.warn('Missing required refs for frame capture');
        return;
      }
      
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      if (!ctx || video.videoWidth === 0 || video.videoHeight === 0) {
        console.warn('Video not ready for frame capture');
        return;
      }

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64
      const frameData = canvas.toDataURL('image/jpeg', 0.8);
      const base64Data = frameData.split(',')[1];

      // Validate base64 data
      if (!base64Data || base64Data.length === 0) {
        console.warn('Invalid frame data generated');
        return;
      }

      // Send via WebSocket using new protocol
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const frameMessage = {
          type: "frame",
          frame: base64Data,
          timestamp: Date.now(),
          frameId: frameCountRef.current + 1
        };
        
        try {
          wsRef.current.send(JSON.stringify(frameMessage));
          frameCountRef.current += 1;
          console.log(`📸 Frame ${frameCountRef.current} sent successfully`);
        } catch (sendError) {
          console.error('Error sending frame:', sendError);
          setError('Failed to send frame data');
          // Stop frame capture if WebSocket is closed
          if (frameIntervalRef.current) {
            clearInterval(frameIntervalRef.current);
            frameIntervalRef.current = null;
          }
        }
      } else {
        console.warn('WebSocket not open, cannot send frame');
        setError('WebSocket connection lost');
        // Stop frame capture if WebSocket is not open
        if (frameIntervalRef.current) {
          clearInterval(frameIntervalRef.current);
          frameIntervalRef.current = null;
        }
      }
    } catch (error) {
      console.error('Error capturing and sending frame:', error);
      setError('Frame capture failed');
    }
  }, []);

  const startDetection = async () => {
    try {
      setIsConnecting(true);
      setError(null);

      // Request camera access
      const stream = await requestCameraAccess();
      streamRef.current = stream;

      // Connect video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      // Connect WebSocket
      const ws = await connectWebSocket();
      wsRef.current = ws;

      // Send start detection message
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: "start_detection",
          config: {
            max_faces_per_frame: 5,
            batch_size: 4,
            confidence_threshold: 0.3,
            debug_mode: false,
            detection_mode: settings.detectionMode
          }
        }));
        
        // Wait for detection to start before beginning frame capture
        // The frame capture will be started when we receive the detection_started message
        console.log('Waiting for detection to start...');
        
        // Set a timeout to start frame capture even if we don't get confirmation
        // This prevents the app from being stuck if there's a communication issue
        setTimeout(() => {
          if (!frameIntervalRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.warn('Detection start confirmation timeout, starting frame capture anyway');
            frameIntervalRef.current = setInterval(() => {
              if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                captureAndSendFrame();
              } else {
                console.warn('WebSocket not open, skipping frame capture');
                // Clear interval if WebSocket is not open
                if (frameIntervalRef.current) {
                  clearInterval(frameIntervalRef.current);
                  frameIntervalRef.current = null;
                }
              }
            }, 2500);
          } else if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error('WebSocket connection lost during startup');
            setError('WebSocket connection lost. Please restart detection.');
            setIsConnecting(false);
          }
        }, 3000); // Reduced to 3 second timeout
      }

      // Calculate frame rate
      const fpsInterval = setInterval(() => {
        setFrameRate(frameCountRef.current); // frames in last second (since we're sending every 2.5s)
        frameCountRef.current = 0;
      }, 1000);

      setIsDetecting(true);
      setIsConnecting(false);

      toast({
        title: "Detection Started",
        description: "Real-time deepfake detection is now active",
      });

      return () => clearInterval(fpsInterval);

    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to start detection');
      setIsConnecting(false);
      toast({
        title: "Detection Failed",
        description: error.message || 'Failed to start real-time detection',
        variant: "destructive"
      });
    }
  };

  const stopDetection = () => {
    // Send stop signal to backend before closing WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({
          type: "stop_detection",
          message: "User requested to stop detection"
        }));
      } catch (error) {
        console.warn("Failed to send stop signal:", error);
      }
    }

    // Stop frame capture
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Stop camera stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Clear video element
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsDetecting(false);
    setConnectionStatus('disconnected');
    setFrameRate(0);
    frameCountRef.current = 0;

    toast({
      title: "Detection Stopped",
      description: "Real-time detection has been stopped",
    });
  };

  const toggleDetection = () => {
    if (isDetecting) {
      stopDetection();
    } else {
      startDetection();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDetection();
    };
  }, []);

  const getPlanIcon = (roles: string[]) => {
    if (roles?.includes('admin')) return <Shield className="w-4 h-4 text-purple-500" />;
    if (roles?.includes('premium')) return <Crown className="w-4 h-4 text-yellow-500" />;
    return <Zap className="w-4 h-4 text-blue-500" />;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-success';
    if (confidence >= 70) return 'text-warning';
    return 'text-destructive';
  };

  const getAuthenticityStatus = (result: DetectionResult) => {
    return formatDetectionResult({
      final_result: result.authentic ? 'Authentic Video' : 'Deepfake Detected',
      confidence: result.confidence,
      faces_analyzed: result.facesDetected,
      processing_time: result.processingTime,
      bias_applied: result.biasApplied || 0,
      metadata_flags: result.metadataFlags || []
    });
  };

  const downloadReport = async (format: 'pdf' | 'json' | 'txt' | 'csv' = 'pdf') => {
    if (!detectionResult) {
      toast({
        title: "No Results",
        description: "No detection results available to download",
        variant: "destructive"
      });
      return;
    }

    try {
      const videoId = `detection_${Date.now()}`;
      let blob: Blob;
      let filename: string;

      if (format === 'pdf') {
        // Generate secure PDF report
        const { blob: pdfBlob, reportId } = await SecurePDFGenerator.generateSecureReport({
          videoId,
          timestamp: detectionResult.timestamp.toISOString(),
          prediction: detectionResult.authentic ? 'Authentic / Real' : 'Deepfake Detected',
          confidence: detectionResult.confidence,
          facesDetected: detectionResult.facesDetected,
          processingTime: detectionResult.processingTime,
          detectionMethod: 'Real-time Detection',
          enhancedAnalysis: true,
          frameCount: 1, // Real-time detection processes single frames
          videoDuration: undefined,
          biasApplied: detectionResult.biasApplied || 0,
          metadataFlags: detectionResult.metadataFlags || [],
          videoUrl: undefined, // Real-time detection doesn't have video URL
          thumbnailUrl: undefined,
          reportId: ''
        }, {
          includeThumbnail: false, // No thumbnail for real-time detection
          includeMetadata: true,
          includeTechnicalDetails: true,
          watermark: 'iFake Deepfake Detection',
          encryption: false
        });

        blob = pdfBlob;
        filename = `deepfake_detection_report_${reportId}.pdf`;
      } else {
        // Fallback to other formats
        const reportData = {
          video_id: videoId,
          status: 'completed',
          prediction: detectionResult.authentic ? 'Real Face' : 'Deepfake Detected',
          confidence: detectionResult.confidence,
          faces_detected: detectionResult.facesDetected,
          processing_time: detectionResult.processingTime,
          detection_method: 'Real-time Detection',
          timestamp: detectionResult.timestamp.toISOString(),
          results: [{
            method: 'Real-time Analysis',
            prediction: detectionResult.authentic ? 'Real Face' : 'Deepfake Detected',
            confidence: detectionResult.confidence,
            processing_time: detectionResult.processingTime
          }]
        };

        switch (format) {
          case 'json':
            blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
            filename = `deepfake_detection_report_${videoId}.json`;
            break;
          case 'txt':
            const txtContent = `Real-time Deepfake Detection Report
=====================================

Video ID: ${videoId}
Analysis Date: ${detectionResult.timestamp.toLocaleString()}
Status: ${reportData.status}

Detection Results:
- Prediction: ${reportData.prediction}
- Confidence: ${reportData.confidence.toFixed(2)}%
- Faces Detected: ${reportData.faces_detected}
- Processing Time: ${reportData.processing_time}s
- Detection Method: ${reportData.detection_method}

Generated by iFake Deepfake Detection System
`;
            blob = new Blob([txtContent], { type: 'text/plain' });
            filename = `deepfake_detection_report_${videoId}.txt`;
            break;
          case 'csv':
            const csvContent = `Video ID,Status,Prediction,Confidence,Faces Detected,Processing Time,Detection Method
${videoId},${reportData.status},${reportData.prediction},${reportData.confidence},${reportData.faces_detected},${reportData.processing_time},${reportData.detection_method}
`;
            blob = new Blob([csvContent], { type: 'text/csv' });
            filename = `deepfake_detection_report_${videoId}.csv`;
            break;
          default:
            throw new Error('Unsupported format');
        }
      }
      
      // Use enhanced download utility
      const success = await downloadFile(blob, {
        filename,
        mimeType: format === 'pdf' ? 'application/pdf' : 
                 format === 'json' ? 'application/json' :
                 format === 'txt' ? 'text/plain' : 'text/csv',
        fallbackText: getDownloadInstructions(filename)
      });

      if (success) {
        toast({
          title: "Report Downloaded",
          description: `Detection report downloaded as ${format.toUpperCase()}`,
        });
      } else {
        toast({
          title: "Download Started",
          description: "Please check your browser's download folder or follow the instructions shown.",
        });
      }
    } catch (error) {
      console.error('Download failed:', error);
      console.error('Error details:', {
        error: error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        userAgent: navigator.userAgent,
        supportsDownload: typeof window !== 'undefined' && 'URL' in window && 'createObjectURL' in window
      });
      
      toast({
        title: "Download Failed",
        description: `Failed to download the report. Error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again or check browser console for details.`,
        variant: "destructive"
      });
    }
  };

  const shareResults = async () => {
    if (!detectionResult) {
      toast({
        title: "No Results",
        description: "No detection results available to share",
        variant: "destructive"
      });
      return;
    }

    try {
      const videoId = `detection_${Date.now()}`;
      
      // Create the share data
      const shareData = {
        video_id: videoId,
        status: 'completed',
        prediction: detectionResult.authentic ? 'Real Face' : 'Deepfake Detected',
        confidence: detectionResult.confidence,
        faces_detected: detectionResult.facesDetected,
        processing_time: detectionResult.processingTime,
        detection_method: 'Real-time Detection',
        timestamp: detectionResult.timestamp.toISOString()
      };

      // Try to use Web Share API with PDF if available
      if (navigator.share && navigator.canShare) {
        try {
          // Generate PDF for sharing
          const { blob: pdfBlob, reportId } = await SecurePDFGenerator.generateSecureReport({
            videoId,
            timestamp: detectionResult.timestamp.toISOString(),
            prediction: detectionResult.authentic ? 'Authentic / Real' : 'Deepfake Detected',
            confidence: detectionResult.confidence,
            facesDetected: detectionResult.facesDetected,
            processingTime: detectionResult.processingTime,
            detectionMethod: 'Real-time Detection',
            enhancedAnalysis: true,
            frameCount: 1,
            videoDuration: undefined,
            biasApplied: detectionResult.biasApplied || 0,
            metadataFlags: detectionResult.metadataFlags || [],
            videoUrl: undefined,
            thumbnailUrl: undefined,
            reportId: ''
          }, {
            includeThumbnail: false,
            includeMetadata: true,
            includeTechnicalDetails: true,
            watermark: 'iFake Deepfake Detection',
            encryption: false
          });

          const pdfFile = new File([pdfBlob], `deepfake_detection_report_${reportId}.pdf`, { type: 'application/pdf' });
          
          if (navigator.canShare({ files: [pdfFile] })) {
            await navigator.share({
              title: 'Deepfake Detection Report',
              text: `Detection Result: ${shareData.prediction} (${shareData.confidence.toFixed(1)}% confidence) - Secure PDF Report`,
              files: [pdfFile]
            });
            return;
          }
        } catch (pdfError) {
          console.warn('PDF sharing failed, falling back to text:', pdfError);
        }
      }

      // Fallback: text sharing
      if (navigator.share) {
        await navigator.share({
          title: 'Deepfake Detection Results',
          text: `Detection Result: ${shareData.prediction} (${shareData.confidence.toFixed(1)}% confidence)`,
          url: window.location.href
        });
      } else {
        // Final fallback: copy to clipboard
        const shareText = `Deepfake Detection Results:
Prediction: ${shareData.prediction}
Confidence: ${shareData.confidence.toFixed(1)}%
Faces Detected: ${shareData.faces_detected}
Processing Time: ${shareData.processing_time}ms
Timestamp: ${shareData.timestamp}

Generated by iFake Deepfake Detection System
${window.location.href}`;
        
        await navigator.clipboard.writeText(shareText);
        
        toast({
          title: "Results Copied",
          description: "Detection results copied to clipboard",
        });
      }
    } catch (error) {
      console.error('Share failed:', error);
      toast({
        title: "Share Failed",
        description: "Failed to share the results. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Download all detection history
  const downloadAllHistory = async (format: 'pdf' | 'json' | 'txt' | 'csv' = 'pdf') => {
    if (detectionHistory.length === 0) {
      toast({
        title: "No History",
        description: "No detection history available to download",
        variant: "destructive"
      });
      return;
    }

    try {
      const sessionId = `session_${Date.now()}`;
      let blob: Blob;
      let filename: string;

      if (format === 'pdf') {
        // Generate comprehensive PDF report for all history
        const { blob: pdfBlob, reportId } = await SecurePDFGenerator.generateSecureReport({
          videoId: sessionId,
          timestamp: new Date().toISOString(),
          prediction: 'Session Summary',
          confidence: detectionHistory.reduce((sum, r) => sum + r.confidence, 0) / detectionHistory.length,
          facesDetected: detectionHistory.reduce((sum, r) => sum + r.facesDetected, 0),
          processingTime: detectionHistory.reduce((sum, r) => sum + r.processingTime, 0) / detectionHistory.length,
          detectionMethod: 'Real-time Detection Session',
          enhancedAnalysis: true,
          frameCount: detectionHistory.length,
          videoDuration: undefined,
          biasApplied: 0,
          metadataFlags: [],
          videoUrl: undefined,
          thumbnailUrl: undefined,
          reportId: ''
        }, {
          includeThumbnail: false,
          includeMetadata: true,
          includeTechnicalDetails: true,
          watermark: 'iFake Deepfake Detection',
          encryption: false
        });

        blob = pdfBlob;
        filename = `detection_session_report_${reportId}.pdf`;
      } else {
        // Generate data for other formats
        const sessionData = {
          session_id: sessionId,
          export_date: new Date().toISOString(),
          total_detections: detectionHistory.length,
          session_duration: detectionHistory.length > 0 ? 
            (detectionHistory[0].timestamp.getTime() - detectionHistory[detectionHistory.length - 1].timestamp.getTime()) / 1000 : 0,
          settings: settings,
          summary: {
            real_count: detectionHistory.filter(r => r.authentic).length,
            fake_count: detectionHistory.filter(r => !r.authentic).length,
            avg_confidence: detectionHistory.reduce((sum, r) => sum + r.confidence, 0) / detectionHistory.length,
            avg_processing_time: detectionHistory.reduce((sum, r) => sum + r.processingTime, 0) / detectionHistory.length
          },
          results: detectionHistory.map(result => ({
            timestamp: result.timestamp.toISOString(),
            prediction: result.authentic ? 'Real Face' : 'Deepfake Detected',
            confidence: result.confidence,
            faces_detected: result.facesDetected,
            processing_time: result.processingTime,
            bias_applied: result.biasApplied || 0,
            metadata_flags: result.metadataFlags || []
          }))
        };

        switch (format) {
          case 'json':
            blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
            filename = `detection_session_${sessionId}.json`;
            break;
          case 'txt':
            const txtContent = `Real-time Deepfake Detection Session Report
==============================================

Session ID: ${sessionId}
Export Date: ${new Date().toLocaleString()}
Total Detections: ${sessionData.total_detections}
Session Duration: ${sessionData.session_duration.toFixed(1)} seconds

Summary:
- Real Faces: ${sessionData.summary.real_count} (${(sessionData.summary.real_count/sessionData.total_detections*100).toFixed(1)}%)
- Fake Faces: ${sessionData.summary.fake_count} (${(sessionData.summary.fake_count/sessionData.total_detections*100).toFixed(1)}%)
- Average Confidence: ${sessionData.summary.avg_confidence.toFixed(1)}%
- Average Processing Time: ${sessionData.summary.avg_processing_time.toFixed(1)}ms

Settings Used:
- Confidence Threshold: ${settings.confidenceThreshold}%
- Frame Rate: ${settings.frameRate}
- Detection Mode: ${settings.detectionMode}
- Preprocessing: ${settings.enablePreprocessing ? 'Enabled' : 'Disabled'}
- Smoothing: ${settings.enableSmoothing ? 'Enabled' : 'Disabled'}

Detailed Results:
${sessionData.results.map((result, index) => 
  `${index + 1}. ${result.timestamp} - ${result.prediction} (${result.confidence.toFixed(1)}% confidence)`
).join('\n')}

Generated by iFake Deepfake Detection System
`;
            blob = new Blob([txtContent], { type: 'text/plain' });
            filename = `detection_session_${sessionId}.txt`;
            break;
          case 'csv':
            const csvContent = `Timestamp,Prediction,Confidence,Faces Detected,Processing Time,Bias Applied,Metadata Flags
${sessionData.results.map(result => 
  `${result.timestamp},${result.prediction},${result.confidence},${result.faces_detected},${result.processing_time},${result.bias_applied},"${result.metadata_flags.join(';')}"`
).join('\n')}
`;
            blob = new Blob([csvContent], { type: 'text/csv' });
            filename = `detection_session_${sessionId}.csv`;
            break;
          default:
            throw new Error('Unsupported format');
        }
      }
      
      // Use enhanced download utility
      const success = await downloadFile(blob, {
        filename,
        mimeType: format === 'pdf' ? 'application/pdf' : 
                 format === 'json' ? 'application/json' :
                 format === 'txt' ? 'text/plain' : 'text/csv',
        fallbackText: getDownloadInstructions(filename)
      });

      if (success) {
        toast({
          title: "Session Downloaded",
          description: `Detection session downloaded as ${format.toUpperCase()}`,
        });
      } else {
        toast({
          title: "Download Started",
          description: "Please check your browser's download folder or follow the instructions shown.",
        });
      }
    } catch (error) {
      console.error('Download failed:', error);
      toast({
        title: "Download Failed",
        description: `Failed to download the session. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        variant: "destructive"
      });
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      {/* Header Section */}
      <section className="relative py-12 px-4 border-b overflow-hidden bg-background">
        {/* 3D Background */}
        <HeroCanvas className="absolute inset-0 w-full h-full z-0" />
        {/* Header Content */}
        <div className="relative z-10 container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <Badge variant="secondary" className="neural-card mb-4 bg-primary/10 text-primary border-primary/20">
              <Eye className="w-3 h-3 mr-1" />
              Real-time MesoNet CNN
            </Badge>
            <h1 className="text-4xl font-bold mb-4 gradient-text neural-text">Real-Time Detection</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-6 neural-text">
              Live camera analysis using advanced AI multi-stage detection
            </p>
            
            {/* Super Advanced Detection Link */}
            <div className="flex justify-center mb-6">
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
            
            {/* Status Indicators */}
            <div className="flex flex-wrap justify-center gap-3 mb-6">
              <Badge variant="outline" className={`neural-card ${connectionStatus === 'connected' ? 'border-success/50 text-success' : 'border-muted'}`}>
                {connectionStatus === 'connected' ? <Wifi className="w-4 h-4 mr-1" /> : <WifiOff className="w-4 h-4 mr-1" />}
                {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </Badge>
              
              <Badge variant="outline" className="neural-card">
                <Target className="w-4 h-4 mr-1" />
                {frameRate} FPS
              </Badge>
              
              <Badge variant="outline" className="neural-card">
                <Activity className="w-4 h-4 mr-1" />
                {processedFrames} frames
              </Badge>
            </div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      {/* Access Control Section */}
      {!accessControl.hasAccess && !accessControl.isLoading && (
        <AccessControlCard
          feature="detection"
          onRequestAccess={() => setShowAccessRequest(true)}
        />
      )}

      <div className="container mx-auto max-w-7xl px-4 py-8">
        {accessControl.isLoading ? (
          <div className="flex items-center justify-center py-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center space-y-6"
            >
              <div className="neural-card p-8 rounded-xl bg-gradient-to-br from-accent/5 via-background to-primary/5 border border-accent/20">
                <div className="w-12 h-12 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <h3 className="text-xl font-semibold gradient-text neural-text mb-2">Verifying Access</h3>
                <p className="text-muted-foreground neural-text">Loading access permissions...</p>
              </div>
            </motion.div>
          </div>
        ) : accessControl.hasAccess ? (
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Main Camera Feed */}
          <div className="xl:col-span-3">
            <EnhancedCard 
              title="Live Detection Feed"
              className="neural-card h-fit"
            >
              <div className="space-y-6">
                {/* Camera Display */}
                <div className="relative">
                  <div className="relative aspect-video neural-card bg-black rounded-xl overflow-hidden">
                    {cameraPermission.state === 'denied' ? (
                      <div className="flex items-center justify-center h-full text-center p-8">
                        <div className="space-y-4">
                          <AlertTriangle className="w-16 h-16 mx-auto text-destructive" />
                          <div>
                            <h3 className="text-xl font-semibold mb-2 neural-text">Camera Access Denied</h3>
                            <p className="text-muted-foreground mb-4 neural-text">
                              Please allow camera access and refresh the page to use real-time detection.
                            </p>
                            <Button 
                              onClick={() => window.location.reload()}
                              variant="outline"
                              className="neural-button hover-lift"
                            >
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Refresh Page
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : cameraPermission.state === 'granted' || isDetecting ? (
                      <>
                        <video
                          ref={videoRef}
                          autoPlay
                          muted
                          playsInline
                          className="w-full h-full object-cover"
                        />
                        <canvas
                          ref={canvasRef}
                          className="hidden"
                        />
                        
                        {/* Live Detection Overlay */}
                        {isDetecting && (
                          <div className="absolute inset-0">
                            {/* Live indicator */}
                            <div className="absolute top-4 left-4 flex items-center gap-2">
                              <div className="flex items-center gap-2 neural-card px-3 py-1 rounded-full bg-destructive/90">
                                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                                <span className="text-white text-sm font-medium neural-text">LIVE</span>
                              </div>
                              {connectionStatus === 'connected' && (
                                <div className="neural-card px-3 py-1 rounded-full bg-success/90 text-white">
                                  <span className="text-sm font-medium neural-text">{frameRate} FPS</span>
                                </div>
                              )}
                            </div>

                            {/* Detection result overlay */}
                            {detectionResult && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="absolute top-4 right-4"
                              >
                                <div className={`neural-card px-4 py-2 rounded-lg ${getAuthenticityStatus(detectionResult).bgColor} ${getAuthenticityStatus(detectionResult).borderColor} border`}>
                                  <div 
                                    className="font-bold text-sm neural-text"
                                    style={{ color: getAuthenticityStatus(detectionResult).color }}
                                  >
                                    {getAuthenticityStatus(detectionResult).label}
                                  </div>
                                  <div className={`text-xs neural-text ${getConfidenceColorClass(detectionResult.confidence)}`}>
                                    {formatConfidenceDisplay(detectionResult.confidence)} confidence
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </div>
                        )}
                      </>
                    ) : isConnecting ? (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center space-y-4">
                          <Loader2 className="w-12 h-12 mx-auto text-primary animate-spin" />
                          <div>
                            <h3 className="text-xl font-semibold mb-2 neural-text">Connecting...</h3>
                            <p className="text-muted-foreground neural-text">Initializing camera and AI detection</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center space-y-4">
                          <Camera className="w-16 h-16 mx-auto text-muted-foreground" />
                          <div>
                            <h3 className="text-xl font-semibold mb-2 neural-text">Camera Inactive</h3>
                            <p className="text-muted-foreground neural-text">Click "Start Detection" to begin</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Error Display */}
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-4 neural-card p-4 bg-destructive/10 border border-destructive/20 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-destructive font-medium neural-text">Detection Error</p>
                          <p className="text-destructive/80 text-sm neural-text">{error}</p>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => setError(null)}
                          className="neural-button"
                        >
                          ×
                        </Button>
                      </div>
                    </motion.div>
                  )}
                </div>

                {/* Status and Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="neural-card p-4 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-1 neural-text">Status:</div>
                    <div className={`font-bold neural-text ${connectionStatus === 'connected' ? 'text-success' : 'text-muted-foreground'}`}>
                      {connectionStatus === 'connected' ? 'Active' : 'Inactive'}
                    </div>
                  </div>

                  <div className="neural-card p-4 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-1 neural-text">Confidence</div>
                    <div className={`font-bold neural-text ${detectionResult ? getConfidenceColor(detectionResult.confidence) : 'text-muted-foreground'}`}>
                      {formatConfidenceValue(detectionResult?.confidence)}%
                    </div>
                  </div>

                  <div className="neural-card p-4 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-1 neural-text">Faces Detected</div>
                    <div className="font-bold text-primary neural-text">
                      {detectionResult?.facesDetected || 0}
                    </div>
                  </div>

                  <div className="neural-card p-4 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-1 neural-text">Frames Processed</div>
                    <div className="font-bold text-primary neural-text">
                      {processedFrames}
                    </div>
                  </div>
                </div>

                {/* Processing Info */}
                {detectionResult?.analysisDetails?.faceCoordinates && detectionResult.analysisDetails.faceCoordinates.width > 0 && (
                  <div className="neural-card p-4 rounded-lg">
                    <h4 className="font-semibold mb-2 neural-text">Processing Details</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground neural-text">Processing:</span>
                        <span className="ml-2 neural-text">
                          {detectionResult?.processingTime 
                            ? (typeof detectionResult.processingTime === 'number' 
                                ? `${detectionResult.processingTime.toFixed(2)}s` 
                                : detectionResult.processingTime)
                            : 'real-time'
                          }
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground neural-text">Face Position:</span>
                        <span className="ml-2 neural-text">
                          ({detectionResult.analysisDetails.faceCoordinates.x}, {detectionResult.analysisDetails.faceCoordinates.y})
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Control Button */}
                <div className="flex justify-center">
                  <LoadingButton
                    onClick={toggleDetection}
                    loading={isConnecting}
                    size="lg"
                    variant={isDetecting ? 'destructive' : 'default'}
                    className={`${isDetecting ? 'bg-destructive hover:bg-destructive/90' : ''}`}
                    disabled={cameraPermission.state === 'denied'}
                    showIcon={false}
                  >
                    {isDetecting ? (
                      <>
                        <StopCircle className="w-5 h-5 mr-2" />
                        Stop Detection
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5 mr-2" />
                        Start Detection
                      </>
                    )}
                  </LoadingButton>
                </div>

                {/* Debug Info */}
                {isDetecting && (
                  <div className="mt-4 p-4 bg-muted/30 rounded-lg">
                    <div className="text-sm text-muted-foreground">
                      <div>🔗 Connection: {connectionStatus}</div>
                      <div>📊 Frames: {processedFrames}</div>
                      <div>📨 Messages: {debugMessages.length}</div>
                      {detectionResult && (
                        <div>✅ Last Result: {detectionResult.authentic ? 'Real' : 'Fake'} ({detectionResult.confidence.toFixed(1)}%)</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </EnhancedCard>
          </div>

          {/* Right Sidebar */}
          <div className="xl:col-span-1 space-y-4">
            {/* Detection Results - Main Card */}
            <EnhancedCard 
              title="Detection Results"
              className="neural-card"
            >
              <div className="space-y-4">
                {detectionResult ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    {/* Main Status Display */}
                    <div className="text-center">
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5 }}
                        className={`text-2xl font-bold mb-2 neural-text`}
                        style={{ color: getAuthenticityStatus(detectionResult).color }}
                      >
                        {getAuthenticityStatus(detectionResult).label}
                      </motion.div>
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className={`text-lg neural-text ${getConfidenceColorClass(detectionResult.confidence)}`}
                      >
                        {formatConfidenceDisplay(detectionResult.confidence)}
                      </motion.div>
                    </div>

                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="neural-card p-3 rounded-lg text-center">
                        <div className="text-xs text-muted-foreground neural-text mb-1">Faces</div>
                        <div className="text-lg font-bold text-primary neural-text">{detectionResult.facesDetected}</div>
                      </div>
                      <div className="neural-card p-3 rounded-lg text-center">
                        <div className="text-xs text-muted-foreground neural-text mb-1">Time</div>
                        <div className="text-lg font-bold text-primary neural-text">
                          {typeof detectionResult.processingTime === 'number' ? detectionResult.processingTime.toFixed(2) : detectionResult.processingTime}s
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="space-y-2">
                      <LoadingButton 
                        variant="outline" 
                        size="sm" 
                        className="w-full neural-button hover-lift"
                        onClick={() => downloadReport('pdf')}
                        showIcon={false}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Report
                      </LoadingButton>
                      <div className="flex gap-2">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-1 neural-button hover-lift"
                            >
                              <Database className="w-4 h-4 mr-1" />
                              Export
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="neural-card w-40">
                            <DropdownMenuItem 
                              onClick={() => downloadReport('json')}
                              className="cursor-pointer hover:bg-accent/50 text-xs"
                            >
                              JSON
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => downloadReport('txt')}
                              className="cursor-pointer hover:bg-accent/50 text-xs"
                            >
                              Text
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => downloadReport('csv')}
                              className="cursor-pointer hover:bg-accent/50 text-xs"
                            >
                              CSV
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                        <LoadingButton 
                          variant="outline" 
                          size="sm" 
                          className="flex-1 neural-button hover-lift"
                          onClick={() => shareResults()}
                          showIcon={false}
                        >
                          <Share className="w-4 h-4" />
                        </LoadingButton>
                      </div>
                    </div>

                    <div className="text-xs text-muted-foreground text-center neural-text">
                      {detectionResult.timestamp.toLocaleTimeString()}
                    </div>
                  </motion.div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    <Brain className="w-10 h-10 mx-auto mb-3" />
                    <h3 className="text-sm font-semibold mb-1 neural-text">Waiting for Detection</h3>
                    <p className="text-xs neural-text">Start detection to see results</p>
                    {isDetecting && (
                      <p className="text-xs mt-1 neural-text">AI analyzing frames...</p>
                    )}
                  </div>
                )}
              </div>
            </EnhancedCard>

            {/* System Status */}
            <EnhancedCard 
              title="System Status"
              className="neural-card"
            >
              <div className="space-y-3">
                {/* Connection Status */}
                <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                  <div className="flex items-center gap-2">
                    {connectionStatus === 'connected' ? (
                      <Wifi className="w-4 h-4 text-success" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-muted-foreground" />
                    )}
                    <div>
                      <div className="text-sm font-medium neural-text">Connection</div>
                      <div className={`text-xs ${connectionStatus === 'connected' ? 'text-success' : 'text-muted-foreground'}`}>
                        {connectionStatus === 'connected' ? 'Active' : 'Inactive'}
                      </div>
                    </div>
                  </div>
                  <Badge variant={connectionStatus === 'connected' ? 'default' : 'secondary'} className="text-xs">
                    {connectionStatus === 'connected' ? 'ON' : 'OFF'}
                  </Badge>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="neural-card p-3 rounded-lg text-center">
                    <div className="text-xs text-muted-foreground neural-text">Frames</div>
                    <div className="text-lg font-bold text-primary neural-text">{processedFrames}</div>
                  </div>
                  <div className="neural-card p-3 rounded-lg text-center">
                    <div className="text-xs text-muted-foreground neural-text">FPS</div>
                    <div className="text-lg font-bold text-primary neural-text">{frameRate}</div>
                  </div>
                </div>

                {/* Detection History */}
                {detectionHistory.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium neural-text">Recent</h4>
                      <Badge variant="outline" className="text-xs">{detectionHistory.length}</Badge>
                    </div>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      <AnimatePresence>
                        {detectionHistory.slice(0, 3).map((result, index) => (
                          <motion.div
                            key={result.timestamp.getTime()}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            className="neural-card p-2 rounded-lg"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {result.authentic ? (
                                  <CheckCircle2 className="w-3 h-3 text-success" />
                                ) : (
                                  <AlertTriangle className="w-3 h-3 text-destructive" />
                                )}
                                <div>
                                  <div className={`text-xs font-medium neural-text ${result.authentic ? 'text-success' : 'text-destructive'}`}>
                                    {result.authentic ? 'Real' : 'Fake'}
                                  </div>
                                  <div className="text-xs text-muted-foreground neural-text">
                                    {result.timestamp.toLocaleTimeString()}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className={`text-xs font-bold neural-text ${getConfidenceColor(result.confidence)}`}>
                                  {result.confidence.toFixed(0)}%
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </AnimatePresence>
                    </div>
                  </div>
                )}
              </div>
            </EnhancedCard>

            {/* Debug Panel */}
            {debugMessages.length > 0 && (
              <EnhancedCard 
                title="Debug Messages"
                className="neural-card"
              >
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {debugMessages.map((msg, index) => (
                    <div key={index} className="p-2 bg-muted/30 rounded text-xs">
                      <div className="font-mono text-xs">
                        <div><strong>Type:</strong> {msg.type || 'unknown'}</div>
                        <div><strong>Keys:</strong> {Object.keys(msg).join(', ')}</div>
                        {msg.prediction && <div><strong>Prediction:</strong> {msg.prediction}</div>}
                        {msg.confidence && <div><strong>Confidence:</strong> {msg.confidence}</div>}
                      </div>
                    </div>
                  ))}
                </div>
              </EnhancedCard>
            )}

            {/* Account & Session Management */}
            <EnhancedCard 
              title="Account & Session"
              className="neural-card"
            >
              <div className="space-y-3">
                {/* User Plan */}
                {user && (
                  <div className="neural-card p-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getPlanIcon(user.roles)}
                        <div>
                          <div className="text-sm font-medium neural-text">
                            {user.roles?.includes('admin') ? 'Admin' : 
                             user.roles?.includes('premium') ? 'Premium' : 'Free'} Plan
                          </div>
                          <div className="text-xs text-muted-foreground neural-text">
                            {user.roles?.includes('admin') || user.roles?.includes('premium') ? 'Unlimited access' : 'Limited detections'}
                          </div>
                        </div>
                      </div>
                      {!user.roles?.includes('admin') && !user.roles?.includes('premium') && (
                        <Badge variant="outline" className="text-xs">
                          Free User
                        </Badge>
                      )}
                    </div>
                    
                    {!user.roles?.includes('admin') && !user.roles?.includes('premium') ? (
                      <>
                        <div className="text-xs text-muted-foreground neural-text mb-2">
                          Detection features available
                        </div>
                        <Button variant="outline" size="sm" className="w-full neural-button hover-lift">
                          <Crown className="w-3 h-3 mr-1" />
                          Upgrade
                        </Button>
                      </>
                    ) : (
                      <div className="text-xs text-success neural-text">
                        ✨ Unlimited detections
                      </div>
                    )}
                  </div>
                )}

                {/* Session Export */}
                {detectionHistory.length > 0 && (
                  <div className="neural-card p-3 rounded-lg">
                    <h4 className="text-sm font-medium mb-2 neural-text">Export Session</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <LoadingButton 
                        variant="outline" 
                        size="sm" 
                        className="neural-button hover-lift text-xs"
                        onClick={() => downloadAllHistory('pdf')}
                        showIcon={false}
                      >
                        <FileText className="w-3 h-3 mr-1" />
                        PDF
                      </LoadingButton>
                      <LoadingButton 
                        variant="outline" 
                        size="sm" 
                        className="neural-button hover-lift text-xs"
                        onClick={() => downloadAllHistory('json')}
                        showIcon={false}
                      >
                        <Database className="w-3 h-3 mr-1" />
                        JSON
                      </LoadingButton>
                      <LoadingButton 
                        variant="outline" 
                        size="sm" 
                        className="neural-button hover-lift text-xs"
                        onClick={() => downloadAllHistory('csv')}
                        showIcon={false}
                      >
                        <FileSpreadsheet className="w-3 h-3 mr-1" />
                        CSV
                      </LoadingButton>
                      <LoadingButton 
                        variant="outline" 
                        size="sm" 
                        className="neural-button hover-lift text-xs"
                        onClick={() => downloadAllHistory('txt')}
                        showIcon={false}
                      >
                        <BarChart3 className="w-3 h-3 mr-1" />
                        TXT
                      </LoadingButton>
                    </div>
                    <div className="text-xs text-muted-foreground neural-text mt-1">
                      {detectionHistory.length} detection{detectionHistory.length !== 1 ? 's' : ''}
                    </div>
                  </div>
                )}

                {/* Settings */}
                <div className="neural-card p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium neural-text">Settings</h4>
                    <Dialog open={isAdvancedSettingsOpen} onOpenChange={setIsAdvancedSettingsOpen}>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="sm" className="neural-button text-xs">
                          <Settings className="w-3 h-3 mr-1" />
                          Advanced
                        </Button>
                      </DialogTrigger>
                  <DialogContent className="neural-card max-w-4xl max-h-[90vh] overflow-hidden">
                    <DialogHeader className="pb-4">
                      <DialogTitle className="neural-text text-xl">Advanced Detection Settings</DialogTitle>
                      <DialogDescription className="neural-text text-sm text-muted-foreground">
                        Configure detection parameters and processing options for optimal performance.
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="overflow-y-auto max-h-[60vh] pr-2">
                      <div className="space-y-8">
                        {/* Detection Parameters */}
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold neural-text border-b pb-2">Detection Parameters</h3>
                          
                          <div className="space-y-4">
                            <div className="space-y-3">
                              <Label htmlFor="confidenceThreshold" className="neural-text text-sm font-medium">
                                Confidence Threshold: {settings.confidenceThreshold}%
                              </Label>
                              <div className="px-2">
                                <Slider
                                  id="confidenceThreshold"
                                  min={50}
                                  max={95}
                                  step={5}
                                  value={[settings.confidenceThreshold]}
                                  onValueChange={(value) => setSettings(prev => ({ ...prev, confidenceThreshold: value[0] }))}
                                  className="w-full"
                                />
                              </div>
                              <div className="flex justify-between text-xs text-muted-foreground px-2">
                                <span>50%</span>
                                <span>95%</span>
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              <Label htmlFor="frameRate" className="neural-text text-sm font-medium">Frame Rate</Label>
                              <Select 
                                value={settings.frameRate} 
                                onValueChange={(value) => setSettings(prev => ({ ...prev, frameRate: value }))}
                              >
                                <SelectTrigger className="w-full">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="auto">Auto (Recommended)</SelectItem>
                                  <SelectItem value="30">30 FPS</SelectItem>
                                  <SelectItem value="15">15 FPS</SelectItem>
                                  <SelectItem value="10">10 FPS</SelectItem>
                                  <SelectItem value="5">5 FPS</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            
                            <div className="space-y-2">
                              <Label htmlFor="detectionMode" className="neural-text text-sm font-medium">Detection Mode</Label>
                              <Select 
                                value={settings.detectionMode} 
                                onValueChange={(value) => setSettings(prev => ({ ...prev, detectionMode: value }))}
                              >
                                <SelectTrigger className="w-full">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="traditional">Traditional (EfficientNet Only)</SelectItem>
                                  <SelectItem value="modern-ai">Modern AI (Multi-stage ensemble)</SelectItem>
                                  <SelectItem value="enhanced">Enhanced (Free AI ensemble)</SelectItem>
                                </SelectContent>
                              </Select>
                              <div className="text-xs text-muted-foreground space-y-1">
                                {settings.detectionMode === 'traditional' && (
                                  <div>⚡ Fast processing with EfficientNet-B0 model. Best for quick analysis.</div>
                                )}
                                {settings.detectionMode === 'modern-ai' && (
                                  <div>🎯 Balanced accuracy with multi-stage ensemble including title analysis and temporal detection.</div>
                                )}
                                {settings.detectionMode === 'enhanced' && (
                                  <div>🧠 Maximum accuracy using free AI ensemble with multiple model fallbacks. Slower but most comprehensive.</div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Processing Options */}
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold neural-text border-b pb-2">Processing Options</h3>
                          
                          <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="enablePreprocessing" className="neural-text text-sm font-medium">
                                  Enable Image Preprocessing
                                </Label>
                                <p className="text-xs text-muted-foreground">Enhance image quality before analysis</p>
                              </div>
                              <Switch
                                id="enablePreprocessing"
                                checked={settings.enablePreprocessing}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, enablePreprocessing: checked }))}
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="useUltraEnsemble" className="neural-text text-sm font-medium">
                                  Use Ultra Ensemble (25+ Models)
                                </Label>
                                <p className="text-xs text-muted-foreground">Enable comprehensive analysis with 25+ AI models for maximum accuracy</p>
                              </div>
                              <Switch
                                id="useUltraEnsemble"
                                checked={settings.useUltraEnsemble}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, useUltraEnsemble: checked }))}
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="enableSmoothing" className="neural-text text-sm font-medium">
                                  Enable Result Smoothing
                                </Label>
                                <p className="text-xs text-muted-foreground">Smooth detection results over time</p>
                              </div>
                              <Switch
                                id="enableSmoothing"
                                checked={settings.enableSmoothing}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, enableSmoothing: checked }))}
                              />
                            </div>
                            
                            <div className="space-y-2">
                              <Label htmlFor="maxHistorySize" className="neural-text text-sm font-medium">Max History Size</Label>
                              <Select 
                                value={settings.maxHistorySize.toString()} 
                                onValueChange={(value) => setSettings(prev => ({ ...prev, maxHistorySize: parseInt(value) }))}
                              >
                                <SelectTrigger className="w-full">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="50">50 results</SelectItem>
                                  <SelectItem value="100">100 results</SelectItem>
                                  <SelectItem value="200">200 results</SelectItem>
                                  <SelectItem value="500">500 results</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                        </div>

                        {/* Display Options */}
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold neural-text border-b pb-2">Display Options</h3>
                          
                          <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="showDetailedStats" className="neural-text text-sm font-medium">
                                  Show Detailed Statistics
                                </Label>
                                <p className="text-xs text-muted-foreground">Display comprehensive analysis data</p>
                              </div>
                              <Switch
                                id="showDetailedStats"
                                checked={settings.showDetailedStats}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, showDetailedStats: checked }))}
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="autoDownload" className="neural-text text-sm font-medium">
                                  Auto-download Results
                                </Label>
                                <p className="text-xs text-muted-foreground">Automatically download detection reports</p>
                              </div>
                              <Switch
                                id="autoDownload"
                                checked={settings.autoDownload}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, autoDownload: checked }))}
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-3 neural-card rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor="notificationSound" className="neural-text text-sm font-medium">
                                  Enable Notification Sound
                                </Label>
                                <p className="text-xs text-muted-foreground">Play sound alerts for detection results</p>
                              </div>
                              <Switch
                                id="notificationSound"
                                checked={settings.notificationSound}
                                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, notificationSound: checked }))}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <DialogFooter className="flex gap-3 pt-4 border-t">
                      <Button 
                        variant="outline" 
                        onClick={resetSettings}
                        className="neural-button flex-1"
                      >
                        Reset to Default
                      </Button>
                      <Button 
                        onClick={() => {
                          saveSettings(settings);
                          setIsAdvancedSettingsOpen(false);
                        }}
                        className="neural-button flex-1"
                      >
                        Save Settings
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                  </div>

                  {/* Quick Settings Summary */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground neural-text">Threshold:</span>
                      <span className="font-medium neural-text">{settings.confidenceThreshold}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground neural-text">Mode:</span>
                      <span className="font-medium neural-text capitalize">{settings.detectionMode}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground neural-text">FPS:</span>
                      <span className="font-medium neural-text">{settings.frameRate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground neural-text">Model:</span>
                      <span className="font-medium neural-text">MesoNet v2.1</span>
                    </div>
                  </div>
                </div>
              </div>
            </EnhancedCard>
          </div>
        </div>
        ) : null}
      </div>

      {/* Access Request Modal */}
      <AccessRequestModal
        isOpen={showAccessRequest}
        onClose={() => setShowAccessRequest(false)}
        requestType="detection_access"
      />
    </main>
  );
}

export default function Detection() {
  return (
    <AdminBypass 
      feature="detection"
      fallbackComponent={({ children }) => (
        <ProtectedRoute
          requireAuth={true}
          requiredPermissions={['detection:create', 'detection:read']}
          requiredRoles={['user', 'admin', 'premium']}
        >
          {children}
        </ProtectedRoute>
      )}
    >
      <DetectionContent />
    </AdminBypass>
  )
}
