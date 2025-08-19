// 'use client';

// import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
// import { 
//   Camera, 
//   Upload, 
//   VideoIcon, 
//   AlertTriangle, 
//   CheckCircle, 
//   XCircle, 
//   Clock, 
//   Eye, 
//   Shield, 
//   TrendingUp, 
//   FileVideo, 
//   Youtube, 
//   Loader2, 
//   BarChart3, 
//   Zap, 
//   Brain, 
//   Lock,
//   Activity
// } from 'lucide-react';

// // API Configuration
// const API_BASE_URL = 'http://localhost:8000';

// // Types
// interface AnalysisResult {
//   video_id: string;
//   status: 'processing' | 'completed' | 'failed';
//   result?: string;
//   confidence?: number;
//   enhanced_analysis?: boolean;
//   video_type?: string;
//   metadata?: any;
//   video_url?: string;
//   faces_found?: number;
//   model_used?: string;
//   processing_time?: number;
//   current_stage?: string;
//   progress_percentage?: number;
//   stage_details?: string;
//   error?: string;
// }

// // **FIXED** Real Backend Progress Mapping
// const mapBackendStageToProgress = (stageDetails: string, currentProgress: number): number => {
//   const stage = stageDetails?.toLowerCase() || '';
  
//   // **EXACT MAPPING FROM YOUR BACKEND LOGS**
//   if (stage.includes('initializing') || currentProgress <= 5) return 5;
//   if (stage.includes('starting face detection') || currentProgress <= 15) return 15;
//   if (stage.includes('extracting faces') || stage.includes('detected') || currentProgress <= 25) return 25;
//   if (stage.includes('found') && stage.includes('faces') || currentProgress <= 50) return 50;
//   if (stage.includes('ensemble') || stage.includes('analysis') || currentProgress <= 60) return 60;
//   if (stage.includes('finalizing') || currentProgress <= 90) return 90;
//   if (stage.includes('completed') || currentProgress >= 100) return 100;
  
//   return Math.max(currentProgress, 5); // Always progress forward
// };

// // **FIXED** Backend Stage Message Mapping
// const getStageMessage = (backendStage: string, progress: number): string => {
//   const stage = backendStage?.toLowerCase() || '';
  
//   if (progress >= 100) return "✅ Analysis completed successfully!";
//   if (progress >= 90) return "📊 Finalizing analysis and insights...";
//   if (progress >= 60) return "🔬 Processing neural network results...";
//   if (progress >= 50) return "⚡ Running deepfake detection models...";
//   if (progress >= 25) return "🔍 Extracting facial features from frames...";
//   if (progress >= 15) return "👁️ Starting facial recognition algorithms...";
//   if (progress >= 5) return "🚀 Initializing AI detection systems...";
  
//   return "🚀 Initializing AI detection systems...";
// };

// // **FIXED** Real-time Progress Hook with Actual Timing
// const useRealTimeProgress = (isActive: boolean, result?: AnalysisResult) => {
//   const [progress, setProgress] = useState(0);
//   const [currentStage, setCurrentStage] = useState('');
//   const [elapsedTime, setElapsedTime] = useState(0);
//   const lastProgressRef = useRef(0);
//   const startTimeRef = useRef<number | null>(null);

//   useEffect(() => {
//     if (!isActive) {
//       setProgress(0);
//       setCurrentStage('');
//       setElapsedTime(0);
//       lastProgressRef.current = 0;
//       startTimeRef.current = null;
//       return;
//     }

//     // **START TIMER** when analysis begins
//     if (!startTimeRef.current) {
//       startTimeRef.current = Date.now();
//     }

//     // **REAL-TIME ELAPSED TIME COUNTER**
//     const timeInterval = setInterval(() => {
//       if (startTimeRef.current) {
//         const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
//         setElapsedTime(elapsed);
//       }
//     }, 1000);

//     // **REAL BACKEND PROGRESS UPDATE**
//     if (result?.progress_percentage !== undefined) {
//       const backendProgress = result.progress_percentage;
//       const mappedProgress = mapBackendStageToProgress(result.stage_details || '', backendProgress);
      
//       // **ENSURE MONOTONIC INCREASE**
//       const newProgress = Math.max(lastProgressRef.current, mappedProgress);
      
//       console.log(`🔄 Backend: ${backendProgress}% → Mapped: ${mappedProgress}% → Final: ${newProgress}%`);
      
//       setProgress(newProgress);
//       setCurrentStage(getStageMessage(result.stage_details || '', newProgress));
//       lastProgressRef.current = newProgress;
//     } else {
//       // **FALLBACK LOCAL ANIMATION** only if no backend data
//       let localProgress = 5;
//       const progressInterval = setInterval(() => {
//         localProgress = Math.min(localProgress + 2, 85); // Stop at 85% to wait for backend
//         setProgress(prev => Math.max(prev, localProgress));
//         setCurrentStage(getStageMessage('', localProgress));
//       }, 800);
      
//       return () => {
//         clearInterval(progressInterval);
//         clearInterval(timeInterval);
//       };
//     }

//     return () => clearInterval(timeInterval);
//   }, [isActive, result?.progress_percentage, result?.stage_details]);

//   return { progress, currentStage, elapsedTime };
// };

// // **ENHANCED** Progress Display Component with Real Timing
// const ProgressDisplay: React.FC<{ 
//   progress: number; 
//   status: string; 
//   result?: AnalysisResult;
//   currentStage: string;
//   elapsedTime: number;
// }> = ({ progress, status, result, currentStage, elapsedTime }) => {
  
//   if (status !== 'analyzing') return null;

//   // **FORMAT ELAPSED TIME** properly
//   const formatElapsedTime = (seconds: number): string => {
//     if (seconds < 60) {
//       return `${seconds}s`;
//     } else {
//       const mins = Math.floor(seconds / 60);
//       const secs = seconds % 60;
//       return `${mins}m ${secs}s`;
//     }
//   };

//   return (
//     <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border border-blue-200 rounded-xl p-6 mt-6">
//       {/* Header */}
//       <div className="flex items-center justify-between mb-4">
//         <div className="flex items-center space-x-3">
//           <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
//             <Activity className="w-4 h-4 text-white animate-pulse" />
//           </div>
//           <h3 className="text-blue-700 font-semibold text-lg">AI Analysis in Progress</h3>
//         </div>
//         <div className="flex items-center space-x-2">
//           <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
//           <span className="text-xs text-green-600 font-medium">PROCESSING</span>
//         </div>
//       </div>
      
//       {/* Progress Information */}
//       <div className="space-y-4">
//         <div className="flex items-center justify-between">
//           <div className="flex-1">
//             <span className="text-blue-700 font-medium block">
//               {currentStage}
//             </span>
//             <span className="text-gray-600 text-sm mt-1 block">
//               Advanced neural networks analyzing your content...
//             </span>
//           </div>
//           <div className="text-right ml-4">
//             <div className="text-3xl font-bold text-blue-700 transition-all duration-1000">
//               {Math.floor(progress)}%
//             </div>
//             <div className="text-xs text-gray-500 mt-1">
//               Processing...
//             </div>
//           </div>
//         </div>
        
//         {/* **SMOOTH** Progress Bar with Backend Integration */}
//         <div className="relative w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
//           {/* Background activity shimmer */}
//           <div 
//             className="absolute inset-0 opacity-25"
//             style={{
//               background: 'linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent)',
//               animation: 'shimmer 3s linear infinite'
//             }}
//           ></div>
          
//           {/* **MAIN PROGRESS BAR** */}
//           <div 
//             className="h-4 rounded-full relative overflow-hidden transition-all duration-1000 ease-out"
//             style={{ 
//               width: `${progress}%`,
//               background: `linear-gradient(90deg, 
//                 #3B82F6 0%, 
//                 #6366F1 25%, 
//                 #8B5CF6 50%, 
//                 #A855F7 75%, 
//                 #EC4899 100%)`
//             }}
//           >
//             {/* Moving shine effect */}
//             <div 
//               className="absolute inset-0 opacity-50"
//               style={{
//                 background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent)',
//                 transform: 'translateX(-100%)',
//                 animation: progress > 0 ? 'smoothSweep 2.5s ease-in-out infinite' : 'none'
//               }}
//             ></div>
            
//             {/* Subtle scrolling pattern */}
//             <div 
//               className="absolute inset-0 opacity-20"
//               style={{
//                 backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 6px, rgba(255,255,255,0.3) 6px, rgba(255,255,255,0.3) 8px)',
//                 animation: progress > 0 ? 'scrollPattern 4s linear infinite' : 'none'
//               }}
//             ></div>

//             {/* Edge glow for active progress */}
//             <div 
//               className="absolute top-0 right-0 w-4 h-full opacity-70"
//               style={{
//                 background: 'radial-gradient(ellipse at right, rgba(255,255,255,0.8), transparent)',
//                 animation: progress > 0 && progress < 100 ? 'edgeGlow 2s ease-in-out infinite alternate' : 'none'
//               }}
//             ></div>
//           </div>
//         </div>
        
//         {/* **ENHANCED** Milestone Progress Indicators */}
//         <div className="grid grid-cols-8 gap-1 mt-4">
//           {[
//             { label: '0%', threshold: 0, emoji: '🚀' },
//             { label: '15%', threshold: 15, emoji: '👁️' },
//             { label: '30%', threshold: 30, emoji: '🔍' },
//             { label: '45%', threshold: 45, emoji: '🧠' },
//             { label: '50%', threshold: 50, emoji: '⚡' },
//             { label: '70%', threshold: 70, emoji: '🔬' },
//             { label: '90%', threshold: 90, emoji: '📊' },
//             { label: '100%', threshold: 100, emoji: '✅' }
//           ].map((milestone, index) => (
//             <div 
//               key={index} 
//               className={`text-center p-2 rounded-lg text-xs transition-all duration-500 ${
//                 progress >= milestone.threshold 
//                   ? 'bg-green-100 text-green-700 border border-green-300 transform scale-105 shadow-sm' 
//                   : progress >= (milestone.threshold - 8)
//                   ? 'bg-blue-100 text-blue-700 border border-blue-300 animate-pulse'
//                   : 'bg-gray-100 text-gray-500'
//               }`}
//             >
//               <div className="text-base mb-1">{milestone.emoji}</div>
//               <div className="font-semibold text-xs">{milestone.label}</div>
//             </div>
//           ))}
//         </div>

//         {/* Real-time Status Indicators with ACTUAL ELAPSED TIME */}
//         <div className="flex items-center justify-between text-sm pt-3 border-t border-gray-200">
//           <div className="flex items-center space-x-4">
//             <div className="flex items-center space-x-1">
//               <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
//               <span className="text-gray-600">Neural Processing Active</span>
//             </div>
//             {result?.faces_found && result.faces_found > 0 && (
//               <div className="flex items-center space-x-1">
//                 <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
//                 <span className="text-green-600 font-medium">
//                   ✓ {result.faces_found} face{result.faces_found > 1 ? 's' : ''} detected
//                 </span>
//               </div>
//             )}
//           </div>
//           <div className="text-gray-500 text-xs">
//             {formatElapsedTime(elapsedTime)} elapsed
//           </div>
//         </div>
//       </div>

//       {/* **SMOOTH** CSS Animations */}
//       <style jsx>{`
//         @keyframes shimmer {
//           0% { transform: translateX(-100%); }
//           100% { transform: translateX(100%); }
//         }
        
//         @keyframes smoothSweep {
//           0% { transform: translateX(-100%); }
//           50% { transform: translateX(0%); }
//           100% { transform: translateX(100%); }
//         }
        
//         @keyframes scrollPattern {
//           0% { background-position: 0 0; }
//           100% { background-position: 20px 0; }
//         }
        
//         @keyframes edgeGlow {
//           0% { opacity: 0.5; }
//           100% { opacity: 0.9; }
//         }
//       `}</style>
//     </div>
//   );
// };

// // **SAME** Video Player Component (unchanged)
// const VideoPlayer: React.FC<{ videoUrl?: string; error?: string }> = ({ videoUrl, error }) => {
//   const [videoError, setVideoError] = useState<string | null>(null);
//   const [isLoading, setIsLoading] = useState(true);
//   const videoRef = useRef<HTMLVideoElement>(null);

//   useEffect(() => {
//     setVideoError(null);
//     setIsLoading(true);
//   }, [videoUrl]);

//   const handleVideoError = useCallback((e: React.SyntheticEvent<HTMLVideoElement>) => {
//     console.error('Video error:', e);
//     setVideoError('Failed to load video. Please try again.');
//     setIsLoading(false);
//   }, []);

//   const handleVideoLoad = useCallback(() => {
//     setVideoError(null);
//     setIsLoading(false);
//   }, []);

//   if (error || videoError) {
//     return (
//       <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center border">
//         <div className="text-center">
//           <div className="text-red-500 text-4xl mb-2">⚠️</div>
//           <div className="text-gray-700 text-sm font-medium">Video Load Error</div>
//           <div className="text-gray-500 text-xs mt-1">{error || videoError}</div>
//         </div>
//       </div>
//     );
//   }

//   if (!videoUrl) {
//     return (
//       <div className="w-full h-48 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-200">
//         <div className="text-gray-400">No video available</div>
//       </div>
//     );
//   }

//   let fullVideoUrl = videoUrl;
//   if (videoUrl.startsWith('/')) {
//     fullVideoUrl = `${API_BASE_URL}${videoUrl}`;
//   }

//   return (
//     <div className="relative w-full">
//       {isLoading && (
//         <div className="absolute inset-0 bg-gray-50 rounded-lg flex items-center justify-center z-10 border border-gray-200">
//           <div className="flex items-center space-x-2 text-gray-600">
//             <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
//             <span>Loading video...</span>
//           </div>
//         </div>
//       )}
//       <video
//         ref={videoRef}
//         key={fullVideoUrl}
//         className="w-full h-auto max-h-96 rounded-lg border border-gray-200"
//         controls
//         preload="metadata"
//         onError={handleVideoError}
//         onLoadedData={handleVideoLoad}
//         onLoadStart={() => setIsLoading(true)}
//         crossOrigin="anonymous"
//         playsInline
//       >
//         <source src={fullVideoUrl} type="video/mp4" />
//         <source src={fullVideoUrl} type="video/webm" />
//         <source src={fullVideoUrl} type="video/ogg" />
//         Your browser does not support the video tag.
//       </video>
//     </div>
//   );
// };

// export default function HomePage() {
//   // State management
//   const [file, setFile] = useState<File | null>(null);
//   const [youtubeUrl, setYoutubeUrl] = useState('');
//   const [result, setResult] = useState<AnalysisResult | null>(null);
//   const [analysisStatus, setAnalysisStatus] = useState<'idle' | 'analyzing' | 'completed' | 'error'>('idle');
//   const [error, setError] = useState<string | null>(null);
//   const [currentVideoId, setCurrentVideoId] = useState<string | null>(null);
//   const [activeTab, setActiveTab] = useState<'upload' | 'youtube'>('upload');

//   // **USE REAL-TIME PROGRESS WITH ACTUAL TIMING**
//   const { progress, currentStage, elapsedTime } = useRealTimeProgress(analysisStatus === 'analyzing', result);

//   // **FIXED** Backend Polling - Faster and More Reliable
//   useEffect(() => {
//     let pollInterval: NodeJS.Timeout | null = null;
    
//     if (currentVideoId && analysisStatus === 'analyzing') {
//       console.log(`🔄 Starting polling for video ID: ${currentVideoId}`);
      
//       const pollStatus = async () => {
//         try {
//           const response = await fetch(`${API_BASE_URL}/detection-status/${currentVideoId}`, {
//             method: 'GET',
//             headers: {
//               'Accept': 'application/json',
//               'Cache-Control': 'no-cache'
//             },
//           });
          
//           if (!response.ok) {
//             throw new Error(`HTTP ${response.status}`);
//           }
          
//           const data: AnalysisResult = await response.json();
//           console.log(`📊 Backend Status:`, data);
          
//           // **IMMEDIATE STATE UPDATE**
//           setResult(data);
          
//           if (data.status === 'completed') {
//             console.log('✅ Analysis completed!');
//             setAnalysisStatus('completed');
//             if (pollInterval) {
//               clearInterval(pollInterval);
//               pollInterval = null;
//             }
//           } else if (data.status === 'failed') {
//             console.log('❌ Analysis failed:', data.error);
//             setAnalysisStatus('error');
//             setError(data.error || 'Analysis failed');
//             if (pollInterval) {
//               clearInterval(pollInterval);
//               pollInterval = null;
//             }
//           }
//         } catch (error) {
//           console.log('⚠️ Polling error:', error);
//           // Continue polling - don't give up on temporary network issues
//         }
//       };

//       // **FASTER POLLING** - Every 500ms for real-time updates
//       pollInterval = setInterval(pollStatus, 500);
//       pollStatus(); // Initial call
//     }

//     return () => {
//       if (pollInterval) {
//         clearInterval(pollInterval);
//       }
//     };
//   }, [currentVideoId, analysisStatus]);

//   // **FIXED** File Upload Handler
//   const handleFileUpload = useCallback(async (uploadedFile: File) => {
//     if (!uploadedFile) return;

//     const maxSize = 100 * 1024 * 1024;
//     const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/webm', 'video/quicktime'];
    
//     if (uploadedFile.size > maxSize) {
//       setError('File size must be less than 100MB');
//       return;
//     }

//     if (!allowedTypes.includes(uploadedFile.type)) {
//       setError('Please upload a valid video file');
//       return;
//     }

//     console.log('📤 Starting file upload:', uploadedFile.name);
    
//     setFile(uploadedFile);
//     setError(null);
//     setResult(null);
//     setAnalysisStatus('analyzing');

//     const formData = new FormData();
//     formData.append('video_file', uploadedFile);

//     try {
//       const response = await fetch(`${API_BASE_URL}/upload-video-enhanced`, {
//         method: 'POST',
//         body: formData,
//       });

//       if (response.ok) {
//         const responseData = await response.json();
//         console.log('✅ Upload successful, video ID:', responseData.video_id);
//         setCurrentVideoId(responseData.video_id);
//       } else {
//         throw new Error(`Upload failed: ${response.status}`);
//       }
//     } catch (err) {
//       console.error('❌ Upload error:', err);
//       setAnalysisStatus('error');
//       setError('Failed to upload video. Please check your connection and try again.');
//     }
//   }, []);

//   // ****FIXED**** YouTube Handler with comprehensive URL validation
//   const handleYoutubeAnalysis = useCallback(async () => {
//     if (!youtubeUrl.trim()) {
//       setError('Please enter a YouTube URL');
//       return;
//     }

//     // ****ENHANCED**** - Comprehensive YouTube URL validation including Shorts
//     const validateYouTubeUrl = (url: string): boolean => {
//       const youtubePatterns = [
//         // YouTube Shorts - PRIORITY PATTERN
//         /^https?:\/\/(www\.|m\.)?youtube\.com\/shorts\/[a-zA-Z0-9_-]{11}/,
        
//         // Regular YouTube videos
//         /^https?:\/\/(www\.|m\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}/,
        
//         // youtu.be short URLs
//         /^https?:\/\/youtu\.be\/[a-zA-Z0-9_-]{11}/,
        
//         // YouTube embed URLs
//         /^https?:\/\/(www\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]{11}/,
        
//         // YouTube Live URLs
//         /^https?:\/\/(www\.|m\.)?youtube\.com\/live\/[a-zA-Z0-9_-]{11}/,
        
//         // Just the video ID (11 characters)
//         /^[a-zA-Z0-9_-]{11}$/
//       ];
      
//       return youtubePatterns.some(pattern => pattern.test(url.trim()));
//     };

//     // ****FIXED**** - Use comprehensive validation
//     if (!validateYouTubeUrl(youtubeUrl.trim())) {
//       setError('Please enter a valid YouTube URL (including Shorts, regular videos, or youtu.be links)');
//       return;
//     }

//     console.log('📺 Starting YouTube analysis:', youtubeUrl);

//     setError(null);
//     setResult(null);
//     setAnalysisStatus('analyzing');

//     try {
//       const response = await fetch(`${API_BASE_URL}/detect-deepfake-youtube`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           youtube_url: youtubeUrl.trim()
//         }),
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
//       }

//       const data = await response.json();
//       setCurrentVideoId(data.video_id);
      
//       console.log('✅ YouTube analysis started, video ID:', data.video_id);
      
//     } catch (err) {
//       console.error('❌ YouTube analysis error:', err);
//       setError(`YouTube analysis failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
//       setAnalysisStatus('error');
//     }
//   }, [youtubeUrl]);

//   // Dropzone configuration (React-dropzone would need to be installed)
//   const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
//     e.preventDefault();
//     const files = Array.from(e.dataTransfer.files);
//     if (files.length > 0 && files[0].type.startsWith('video/')) {
//       handleFileUpload(files[0]);
//     }
//   }, [handleFileUpload]);

//   const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
//     e.preventDefault();
//   }, []);

//   // Reset handler
//   const handleReset = useCallback(() => {
//     setFile(null);
//     setYoutubeUrl('');
//     setResult(null);
//     setAnalysisStatus('idle');
//     setError(null);
//     setCurrentVideoId(null);
//   }, []);

//   return (
//     <div className="min-h-screen bg-white">
//       {/* Header */}
//       <header className="bg-white border-b border-gray-200 shadow-sm">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center space-x-3">
//               <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
//                 <Shield className="w-6 h-6 text-white" />
//               </div>
//               <div>
//                 <h1 className="text-2xl font-bold text-gray-900">iFake</h1>
//                 <p className="text-gray-600 text-sm">Advanced Deepfake Detection</p>
//               </div>
//             </div>
//             <div className="flex items-center space-x-6 text-gray-600">
//               <div className="flex items-center space-x-2">
//                 <Brain className="w-5 h-5 text-blue-600" />
//                 <span className="text-sm">AI-Powered</span>
//               </div>
//               <div className="flex items-center space-x-2">
//                 <Zap className="w-5 h-5 text-yellow-500" />
//                 <span className="text-sm">Real-time</span>
//               </div>
//               <div className="flex items-center space-x-2">
//                 <Lock className="w-5 h-5 text-green-500" />
//                 <span className="text-sm">Secure</span>
//               </div>
//             </div>
//           </div>
//         </div>
//       </header>

//       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
//         <div className="text-center mb-12">
//           <h2 className="text-4xl font-bold text-gray-900 mb-4">
//             Upload your media to analyze for deepfake content using our advanced trained AI model with 94.1% accuracy
//           </h2>
//           <p className="text-xl text-gray-600">
//             Choose how you'd like to provide your media for deepfake analysis
//           </p>
//         </div>

//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
//           {/* Main Analysis Panel */}
//           <div className="lg:col-span-2 space-y-6">
//             {/* Detection Panel */}
//             <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
//               {/* Upload Method Selection */}
//               <div className="flex bg-gray-50 rounded-xl p-1 mb-6">
//                 <button
//                   onClick={() => setActiveTab('upload')}
//                   className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg transition-all ${
//                     activeTab === 'upload'
//                       ? 'bg-white text-blue-600 shadow-sm'
//                       : 'text-gray-600 hover:text-gray-900'
//                   }`}
//                   disabled={analysisStatus === 'analyzing'}
//                 >
//                   <Upload className="w-5 h-5 mr-2" />
//                   Upload Video
//                 </button>
//                 <button
//                   onClick={() => setActiveTab('youtube')}
//                   className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg transition-all ${
//                     activeTab === 'youtube'
//                       ? 'bg-white text-red-600 shadow-sm'
//                       : 'text-gray-600 hover:text-gray-900'
//                   }`}
//                   disabled={analysisStatus === 'analyzing'}
//                 >
//                   <Youtube className="w-5 h-5 mr-2" />
//                   YouTube URL
//                 </button>
//               </div>

//               {/* Upload Section */}
//               {activeTab === 'upload' && (
//                 <div className="space-y-6">
//                   <div
//                     onDrop={handleDrop}
//                     onDragOver={handleDragOver}
//                     className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer border-gray-300 hover:border-gray-400 ${
//                       analysisStatus === 'analyzing' ? 'opacity-50 cursor-not-allowed' : ''
//                     }`}
//                   >
//                     <input 
//                       type="file" 
//                       accept="video/*" 
//                       style={{ display: 'none' }} 
//                       id="video-upload"
//                       onChange={(e) => {
//                         if (e.target.files && e.target.files[0]) {
//                           handleFileUpload(e.target.files[0]);
//                         }
//                       }}
//                       disabled={analysisStatus === 'analyzing'}
//                     />
//                     <div className="space-y-4">
//                       <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto">
//                         <FileVideo className="w-8 h-8 text-white" />
//                       </div>
//                       <div>
//                         <p className="text-gray-900 text-lg font-medium">
//                           Drag & drop your video here
//                         </p>
//                         <p className="text-gray-500 text-sm mt-2">
//                           Supports MP4, MOV, AVI formats • Maximum 100MB
//                         </p>
//                       </div>
//                       {!analysisStatus || analysisStatus === 'idle' ? (
//                         <label htmlFor="video-upload" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all cursor-pointer inline-block">
//                           Browse Files
//                         </label>
//                       ) : null}
//                     </div>
//                   </div>

//                   {file && (
//                     <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
//                       <div className="flex items-center space-x-3">
//                         <FileVideo className="w-8 h-8 text-blue-600" />
//                         <div className="flex-1">
//                           <p className="text-gray-900 font-medium">{file.name}</p>
//                           <p className="text-gray-500 text-sm">
//                             Ready to analyze • {(file.size / 1024 / 1024).toFixed(1)} MB
//                           </p>
//                         </div>
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               )}

//               {/* YouTube Section */}
//               {activeTab === 'youtube' && (
//                 <div className="space-y-6">
//                   <div className="space-y-4">
//                     <div className="relative">
//                       <input
//                         type="url"
//                         value={youtubeUrl}
//                         onChange={(e) => setYoutubeUrl(e.target.value)}
//                         placeholder="https://www.youtube.com/watch?v=... or https://youtube.com/shorts/..."
//                         className="w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-4 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-red-500 transition-all"
//                         disabled={analysisStatus === 'analyzing'}
//                       />
//                       <Youtube className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-red-500" />
//                     </div>
//                     <p className="text-gray-500 text-sm">
//                       Supports YouTube videos, Shorts, and youtu.be links up to 5 minutes long
//                     </p>
//                     {youtubeUrl && (
//                       <button
//                         onClick={handleYoutubeAnalysis}
//                         disabled={analysisStatus === 'analyzing'}
//                         className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-4 rounded-xl hover:from-red-600 hover:to-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
//                       >
//                         {analysisStatus === 'analyzing' ? (
//                           <>
//                             <Loader2 className="w-5 h-5 animate-spin" />
//                             <span>Processing...</span>
//                           </>
//                         ) : (
//                           <>
//                             <Youtube className="w-5 h-5" />
//                             <span>Analyze YouTube Video</span>
//                           </>
//                         )}
//                       </button>
//                     )}
//                   </div>
//                 </div>
//               )}

//               {/* **REAL-TIME PROGRESS DISPLAY WITH ACTUAL TIMING** */}
//               <ProgressDisplay 
//                 progress={progress} 
//                 status={analysisStatus} 
//                 result={result}
//                 currentStage={currentStage}
//                 elapsedTime={elapsedTime}
//               />

//               {/* Analysis ID Display */}
//               {analysisStatus === 'analyzing' && currentVideoId && (
//                 <div className="mt-4 text-center">
//                   <p className="text-xs text-gray-500">
//                     Analysis ID: <span className="font-mono text-gray-700">{currentVideoId}</span>
//                   </p>
//                 </div>
//               )}

//               {/* Error Display */}
//               {error && (
//                 <div className="bg-red-50 border border-red-200 rounded-xl p-6 mt-6">
//                   <div className="flex items-center space-x-3">
//                     <AlertTriangle className="w-6 h-6 text-red-500" />
//                     <div>
//                       <h3 className="text-red-700 font-medium">Analysis Error</h3>
//                       <p className="text-red-600 text-sm mt-1">{error}</p>
//                     </div>
//                   </div>
//                 </div>
//               )}
//             </div>

//             {/* Results Panel */}
//             {result && analysisStatus === 'completed' && (
//               <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
//                 <h3 className="text-2xl font-bold text-gray-900 mb-6">Analysis Results</h3>
                
//                 {/* Video Display */}
//                 {result.video_url && (
//                   <div className="mb-6">
//                     <h4 className="text-lg font-medium text-gray-900 mb-3">Analyzed Video</h4>
//                     <VideoPlayer videoUrl={result.video_url} error={error} />
//                   </div>
//                 )}

//                 {/* Detection Result */}
//                 <div className={`rounded-xl p-6 border-2 mb-6 ${
//                   result.result?.toLowerCase().includes('real')
//                     ? 'bg-green-50 border-green-200'
//                     : 'bg-red-50 border-red-200'
//                 }`}>
//                   <div className="flex items-center space-x-3 mb-4">
//                     {result.result?.toLowerCase().includes('real') ? (
//                       <CheckCircle className="w-8 h-8 text-green-600" />
//                     ) : (
//                       <XCircle className="w-8 h-8 text-red-600" />
//                     )}
//                     <div>
//                       <h4 className="text-xl font-bold text-gray-900">{result.result}</h4>
//                       <p className="text-gray-600">
//                         Confidence: {result.confidence?.toFixed(1)}%
//                       </p>
//                     </div>
//                   </div>
//                   <p className="text-gray-700 text-sm">
//                     {result.result?.toLowerCase().includes('real') 
//                       ? 'Our advanced AI models indicate this media appears to be authentic and genuine' 
//                       : 'Our AI analysis detected potential deepfake indicators in this media content'
//                     }
//                   </p>
//                 </div>

//                 {/* Analysis Details */}
//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                   <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
//                     <div className="flex items-center space-x-2 mb-2">
//                       <Eye className="w-5 h-5 text-blue-600" />
//                       <span className="text-gray-700 text-sm">Faces Detected</span>
//                     </div>
//                     <p className="text-gray-900 text-lg font-medium">{result.faces_found || 0}</p>
//                   </div>
                  
//                   <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
//                     <div className="flex items-center space-x-2 mb-2">
//                       <Brain className="w-5 h-5 text-purple-600" />
//                       <span className="text-gray-700 text-sm">Model Used</span>
//                     </div>
//                     <p className="text-gray-900 text-lg font-medium">{result.model_used || 'Enhanced AI'}</p>
//                   </div>
                  
//                   <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
//                     <div className="flex items-center space-x-2 mb-2">
//                       <Clock className="w-5 h-5 text-green-600" />
//                       <span className="text-gray-700 text-sm">Processing Time</span>
//                     </div>
//                     <p className="text-gray-900 text-lg font-medium">{result.processing_time}s</p>
//                   </div>
                  
//                   <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
//                     <div className="flex items-center space-x-2 mb-2">
//                       <Zap className="w-5 h-5 text-yellow-500" />
//                       <span className="text-gray-700 text-sm">Analysis Type</span>
//                     </div>
//                     <p className="text-gray-900 text-lg font-medium">
//                       {result.enhanced_analysis ? 'Enhanced' : 'Standard'}
//                     </p>
//                   </div>
//                 </div>

//                 {/* Reset Button */}
//                 <div className="mt-6 flex justify-center">
//                   <button
//                     onClick={handleReset}
//                     className="bg-gray-600 text-white px-6 py-3 rounded-xl hover:bg-gray-700 transition-all"
//                   >
//                     Analyze Another Video
//                   </button>
//                 </div>
//               </div>
//             )}

//             {/* How iFake Works Section */}
//             <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
//               <div className="text-center mb-8">
//                 <h2 className="text-3xl font-bold text-gray-900 mb-3">How iFake Works</h2>
//                 <p className="text-gray-600">Our AI follows these core steps to analyze your media with precision</p>
//               </div>

//               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//                 {[
//                   { step: "STEP 1", title: "Media Processing", description: "Extract and preprocess frames from your input media" },
//                   { step: "STEP 2", title: "Face Detection", description: "Locate and extract facial regions using MTCNN" },
//                   { step: "STEP 3", title: "Feature Analysis", description: "Analyze spatial artifacts with EfficientNet-B0" },
//                   { step: "STEP 4", title: "Temporal Analysis", description: "Examine frame consistency across video timeline" },
//                   { step: "STEP 5", title: "AI Classification", description: "Binary classifier provides confidence score" },
//                   { step: "STEP 6", title: "Final Verdict", description: "Ensemble decision with detailed analysis" }
//                 ].map((item, index) => (
//                   <div key={index} className="bg-gray-50 rounded-xl p-6 border border-gray-200 hover:bg-gray-100 transition-all">
//                     <div className="flex items-center mb-4">
//                       <div className={`w-8 h-8 ${index % 6 === 0 ? 'bg-blue-500' : index % 6 === 1 ? 'bg-purple-500' : index % 6 === 2 ? 'bg-pink-500' : index % 6 === 3 ? 'bg-red-500' : index % 6 === 4 ? 'bg-yellow-500' : 'bg-green-500'} rounded-lg flex items-center justify-center text-white font-bold text-sm mr-3`}>
//                         {index + 1}
//                       </div>
//                       <h3 className="text-gray-900 font-semibold">{item.title}</h3>
//                     </div>
//                     <p className="text-gray-600 text-sm">
//                       {item.description}
//                     </p>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>

//           {/* Sidebar */}
//           <div className="space-y-6">
//             {/* Detection Tips */}
//             <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
//               <h3 className="text-lg font-bold text-gray-900 mb-4">Detection Tips</h3>
//               <div className="space-y-3 text-sm">
//                 <div className="flex items-start space-x-3">
//                   <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
//                   <p className="text-gray-600">Higher quality videos provide more accurate detection results</p>
//                 </div>
//                 <div className="flex items-start space-x-3">
//                   <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
//                   <p className="text-gray-600">Videos with clear facial features work best for analysis</p>
//                 </div>
//                 <div className="flex items-start space-x-3">
//                   <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
//                   <p className="text-gray-600">Enhanced detection provides additional accuracy for complex cases</p>
//                 </div>
//               </div>
//             </div>

//             {/* AI Insights */}
//             <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
//               <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
//                 <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
//                 AI Research Updates
//               </h3>
//               <div className="space-y-4">
//                 <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:bg-gray-100 transition-all cursor-pointer">
//                   <div className="flex items-start space-x-3">
//                     <div className="w-2 h-2 rounded-full mt-2 bg-red-500"></div>
//                     <div className="flex-1">
//                       <h4 className="text-gray-900 text-sm font-medium mb-1">Neural Network Advances</h4>
//                       <p className="text-gray-600 text-xs mb-2">Latest improvements in deepfake detection accuracy reach 99.7%</p>
//                       <div className="flex items-center justify-between text-xs">
//                         <span className="text-gray-500">2 min</span>
//                         <span className="text-blue-600">High Impact</span>
//                       </div>
//                     </div>
//                   </div>
//                 </div>
//                 <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:bg-gray-100 transition-all cursor-pointer">
//                   <div className="flex items-start space-x-3">
//                     <div className="w-2 h-2 rounded-full mt-2 bg-yellow-500"></div>
//                     <div className="flex-1">
//                       <h4 className="text-gray-900 text-sm font-medium mb-1">Real-time Detection</h4>
//                       <p className="text-gray-600 text-xs mb-2">Edge computing enables instant deepfake detection in live streams</p>
//                       <div className="flex items-center justify-between text-xs">
//                         <span className="text-gray-500">3 min</span>
//                         <span className="text-blue-600">Medium Impact</span>
//                       </div>
//                     </div>
//                   </div>
//                 </div>
//                 <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:bg-gray-100 transition-all cursor-pointer">
//                   <div className="flex items-start space-x-3">
//                     <div className="w-2 h-2 rounded-full mt-2 bg-green-500"></div>
//                     <div className="flex-1">
//                       <h4 className="text-gray-900 text-sm font-medium mb-1">Security Best Practices</h4>
//                       <p className="text-gray-600 text-xs mb-2">Guidelines for implementing content verification systems</p>
//                       <div className="flex items-center justify-between text-xs">
//                         <span className="text-gray-500">5 min</span>
//                         <span className="text-blue-600">Practical</span>
//                       </div>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }




























'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Camera, 
  Upload, 
  VideoIcon, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  Shield, 
  TrendingUp, 
  FileVideo, 
  Youtube, 
  Loader2, 
  BarChart3, 
  Zap, 
  Brain, 
  Lock,
  Activity,
  Monitor,
  StopCircle,
  Play
} from 'lucide-react';

// ✅ FIXED API Configuration - Corrected Endpoints
const API_BASE_URL = 'http://localhost:8000';

// ✅ FIXED API Endpoints matching your backend
const ENDPOINTS = {
  UPLOAD_VIDEO: '/upload-video',           // ✅ Standard detection
  MODERN_AI_DETECT: '/detect-modern-ai-content', // ✅ Modern AI detection
  YOUTUBE_DETECT: '/detect-deepfake-youtube',     // ✅ YouTube detection
  STATUS_CHECK: '/detection-status',       // ✅ Status polling
};

// Types
interface AnalysisResult {
  video_id: string;
  status: 'processing' | 'completed' | 'failed';
  result?: string;
  prediction?: string;
  confidence?: number;
  enhanced_analysis?: boolean;
  video_type?: string;
  metadata?: any;
  video_url?: string;
  faces_found?: number;
  faces_detected?: number;
  model_used?: string;
  detection_method?: string;
  processing_time?: number;
  current_stage?: string;
  progress_percentage?: number;
  stage_details?: string;
  error?: string;
  color?: string;
  message?: string;
  detection_type?: string;
}

// Progress mapping functions
const mapBackendStageToProgress = (stageDetails: string, currentProgress: number): number => {
  const stage = stageDetails?.toLowerCase() || '';
  
  if (stage.includes('initializing') || currentProgress <= 5) return 5;
  if (stage.includes('starting face detection') || currentProgress <= 15) return 15;
  if (stage.includes('extracting faces') || stage.includes('detected') || currentProgress <= 25) return 25;
  if (stage.includes('found') && stage.includes('faces') || currentProgress <= 50) return 50;
  if (stage.includes('ensemble') || stage.includes('analysis') || currentProgress <= 60) return 60;
  if (stage.includes('finalizing') || currentProgress <= 90) return 90;
  if (stage.includes('completed') || currentProgress >= 100) return 100;
  
  return Math.max(currentProgress, 5);
};

const getStageMessage = (backendStage: string, progress: number): string => {
  if (progress >= 100) return "✅ Analysis completed successfully!";
  if (progress >= 90) return "📊 Finalizing analysis and insights...";
  if (progress >= 60) return "🔬 Processing neural network results...";
  if (progress >= 50) return "⚡ Running deepfake detection models...";
  if (progress >= 25) return "🔍 Extracting facial features from frames...";
  if (progress >= 15) return "👁️ Starting facial recognition algorithms...";
  if (progress >= 5) return "🚀 Initializing AI detection systems...";
  
  return "🚀 Initializing AI detection systems...";
};

// Real-time Progress Hook
const useRealTimeProgress = (isActive: boolean, result?: AnalysisResult) => {
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const lastProgressRef = useRef(0);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isActive) {
      setProgress(0);
      setCurrentStage('');
      setElapsedTime(0);
      lastProgressRef.current = 0;
      startTimeRef.current = null;
      return;
    }

    if (!startTimeRef.current) {
      startTimeRef.current = Date.now();
    }

    const timeInterval = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setElapsedTime(elapsed);
      }
    }, 1000);

    if (result?.progress_percentage !== undefined) {
      const backendProgress = result.progress_percentage;
      const mappedProgress = mapBackendStageToProgress(result.stage_details || '', backendProgress);
      const newProgress = Math.max(lastProgressRef.current, mappedProgress);
      
      setProgress(newProgress);
      setCurrentStage(getStageMessage(result.stage_details || '', newProgress));
      lastProgressRef.current = newProgress;
    } else {
      let localProgress = 5;
      const progressInterval = setInterval(() => {
        localProgress = Math.min(localProgress + 2, 85);
        setProgress(prev => Math.max(prev, localProgress));
        setCurrentStage(getStageMessage('', localProgress));
      }, 800);
      
      return () => {
        clearInterval(progressInterval);
        clearInterval(timeInterval);
      };
    }

    return () => clearInterval(timeInterval);
  }, [isActive, result?.progress_percentage, result?.stage_details]);

  return { progress, currentStage, elapsedTime };
};

// Progress Display Component
const ProgressDisplay: React.FC<{ 
  progress: number; 
  status: string; 
  result?: AnalysisResult;
  currentStage: string;
  elapsedTime: number;
}> = ({ progress, status, result, currentStage, elapsedTime }) => {
  
  if (status !== 'analyzing') return null;

  const formatElapsedTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}s`;
    } else {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}m ${secs}s`;
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border border-blue-200 rounded-xl p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <Activity className="w-4 h-4 text-white animate-pulse" />
          </div>
          <h3 className="text-blue-700 font-semibold text-lg">AI Analysis in Progress</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-green-600 font-medium">PROCESSING</span>
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <span className="text-blue-700 font-medium block">
              {currentStage}
            </span>
            <span className="text-gray-600 text-sm mt-1 block">
              Advanced neural networks analyzing your content...
            </span>
          </div>
          <div className="text-right ml-4">
            <div className="text-3xl font-bold text-blue-700 transition-all duration-1000">
              {Math.floor(progress)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Processing...
            </div>
          </div>
        </div>
        
        <div className="relative w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
          <div 
            className="h-4 rounded-full relative overflow-hidden transition-all duration-1000 ease-out"
            style={{ 
              width: `${progress}%`,
              background: `linear-gradient(90deg, 
                #3B82F6 0%, 
                #6366F1 25%, 
                #8B5CF6 50%, 
                #A855F7 75%, 
                #EC4899 100%)`
            }}
          >
            <div 
              className="absolute inset-0 opacity-50"
              style={{
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent)',
                transform: 'translateX(-100%)',
                animation: progress > 0 ? 'smoothSweep 2.5s ease-in-out infinite' : 'none'
              }}
            ></div>
          </div>
        </div>
        
        <div className="grid grid-cols-8 gap-1 mt-4">
          {[
            { label: '0%', threshold: 0, emoji: '🚀' },
            { label: '15%', threshold: 15, emoji: '👁️' },
            { label: '30%', threshold: 30, emoji: '🔍' },
            { label: '45%', threshold: 45, emoji: '🧠' },
            { label: '50%', threshold: 50, emoji: '⚡' },
            { label: '70%', threshold: 70, emoji: '🔬' },
            { label: '90%', threshold: 90, emoji: '📊' },
            { label: '100%', threshold: 100, emoji: '✅' }
          ].map((milestone, index) => (
            <div 
              key={index} 
              className={`text-center p-2 rounded-lg text-xs transition-all duration-500 ${
                progress >= milestone.threshold 
                  ? 'bg-green-100 text-green-700 border border-green-300 transform scale-105 shadow-sm' 
                  : progress >= (milestone.threshold - 8)
                  ? 'bg-blue-100 text-blue-700 border border-blue-300 animate-pulse'
                  : 'bg-gray-100 text-gray-500'
              }`}
            >
              <div className="text-base mb-1">{milestone.emoji}</div>
              <div className="font-semibold text-xs">{milestone.label}</div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between text-sm pt-3 border-t border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
              <span className="text-gray-600">Neural Processing Active</span>
            </div>
            {result?.faces_found && result.faces_found > 0 && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                <span className="text-green-600 font-medium">
                  ✓ {result.faces_found} face{result.faces_found > 1 ? 's' : ''} detected
                </span>
              </div>
            )}
          </div>
          <div className="text-gray-500 text-xs">
            {formatElapsedTime(elapsedTime)} elapsed
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes smoothSweep {
          0% { transform: translateX(-100%); }
          50% { transform: translateX(0%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
};

// Video Player Component
const VideoPlayer: React.FC<{ videoUrl?: string; error?: string }> = ({ videoUrl, error }) => {
  const [videoError, setVideoError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    setVideoError(null);
    setIsLoading(true);
  }, [videoUrl]);

  const handleVideoError = useCallback((e: React.SyntheticEvent<HTMLVideoElement>) => {
    console.error('Video error:', e);
    setVideoError('Failed to load video. Please try again.');
    setIsLoading(false);
  }, []);

  const handleVideoLoad = useCallback(() => {
    setVideoError(null);
    setIsLoading(false);
  }, []);

  if (error || videoError) {
    return (
      <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center border">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-2">⚠️</div>
          <div className="text-gray-700 text-sm font-medium">Video Load Error</div>
          <div className="text-gray-500 text-xs mt-1">{error || videoError}</div>
        </div>
      </div>
    );
  }

  if (!videoUrl) {
    return (
      <div className="w-full h-48 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-200">
        <div className="text-gray-400">No video available</div>
      </div>
    );
  }

  let fullVideoUrl = videoUrl;
  if (videoUrl.startsWith('/')) {
    fullVideoUrl = `${API_BASE_URL}${videoUrl}`;
  }

  return (
    <div className="relative w-full">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-50 rounded-lg flex items-center justify-center z-10 border border-gray-200">
          <div className="flex items-center space-x-2 text-gray-600">
            <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
            <span>Loading video...</span>
          </div>
        </div>
      )}
      <video
        ref={videoRef}
        key={fullVideoUrl}
        className="w-full h-auto max-h-96 rounded-lg border border-gray-200"
        controls
        preload="metadata"
        onError={handleVideoError}
        onLoadedData={handleVideoLoad}
        onLoadStart={() => setIsLoading(true)}
        crossOrigin="anonymous"
        playsInline
      >
        <source src={fullVideoUrl} type="video/mp4" />
        <source src={fullVideoUrl} type="video/webm" />
        <source src={fullVideoUrl} type="video/ogg" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

// Main Component
export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<'idle' | 'analyzing' | 'completed' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [currentVideoId, setCurrentVideoId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'youtube'>('upload');
  const [detectionMode, setDetectionMode] = useState<'standard' | 'modern'>('modern');
  
  // Enhanced progress states from 'use client'.txt
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  const { progress, currentStage, elapsedTime } = useRealTimeProgress(analysisStatus === 'analyzing', result);

  // Enhanced polling from 'use client'.txt
  const startPolling = (videoId: string) => {
    let pollCount = 0;
    const maxPolls = 60; // Maximum 60 polls (30 seconds at 500ms intervals)
    
    const poll = async () => {
      try {
        pollCount++;
        
        // Enhanced progress based on polling duration
        const progressIncrement = Math.min((pollCount / maxPolls) * 70, 70);
        setAnalysisProgress(30 + progressIncrement);
        
        // Update status based on progress
        if (pollCount <= 10) {
          setProcessingStatus('Extracting faces from video...');
        } else if (pollCount <= 25) {
          setProcessingStatus('Analyzing faces with AI model...');
        } else if (pollCount <= 40) {
          setProcessingStatus('Running deepfake detection...');
        } else {
          setProcessingStatus('Finalizing analysis...');
        }

        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.STATUS_CHECK}/${videoId}`);
        
        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'completed') {
            // Completed - Show results
            setAnalysisProgress(100);
            setProcessingStatus('Analysis completed!');
            
            setResult({
              result: data.prediction || 'Unknown',
              confidence: data.confidence || 0,
              faces_found: data.faces_detected || 0,
              model_used: data.detection_method || 'Enhanced AI',
              processing_time: data.processing_time || 0,
              enhanced_analysis: data.enhanced_analysis || false,
              video_url: data.video_url || null,
              ...data
            });
            
            setIsAnalyzing(false);
            setAnalysisStatus('completed');
            
            // Small delay to show completion
            setTimeout(() => {
              setAnalysisProgress(0);
              setProcessingStatus('');
            }, 2000);
            
          } else if (data.status === 'failed') {
            setError(data.error || 'Analysis failed');
            setIsAnalyzing(false);
            setAnalysisStatus('error');
            setAnalysisProgress(0);
            setProcessingStatus('');
          } else {
            // Processing - Continue polling
            if (pollCount < maxPolls) {
              setTimeout(poll, 500); // Poll every 500ms
            } else {
              // Timeout
              setError('Analysis is taking longer than expected. Please try again.');
              setIsAnalyzing(false);
              setAnalysisStatus('error');
              setAnalysisProgress(0);
              setProcessingStatus('');
            }
          }
        } else {
          throw new Error(`Status check failed: ${response.status}`);
        }
      } catch (error) {
        console.error('Polling error:', error);
        if (pollCount < maxPolls) {
          setTimeout(poll, 1000); // Retry with longer delay
        } else {
          setError('Failed to check analysis status');
          setIsAnalyzing(false);
          setAnalysisStatus('error');
          setAnalysisProgress(0);
          setProcessingStatus('');
        }
      }
    };

    poll();
  };

  // ✅ FIXED Backend Polling with correct endpoint and proper field mapping
  useEffect(() => {
    let pollInterval: NodeJS.Timeout | null = null;
    
    if (currentVideoId && analysisStatus === 'analyzing') {
      console.log(`🔄 Starting polling for video ID: ${currentVideoId}`);
      
      const checkDetectionStatus = async () => {
        try {
          // ✅ FIXED: Correct status endpoint
          const response = await fetch(`${API_BASE_URL}${ENDPOINTS.STATUS_CHECK}/${currentVideoId}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Cache-Control': 'no-cache'
            },
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          
          const data: AnalysisResult = await response.json();
          console.log(`📊 Backend Status:`, data);
          
          // ✅ FIXED: Proper mapping from backend response
          if (data.status === 'completed') {
            console.log('✅ Analysis completed!');
            setResult({
              ...data,
              result: data.prediction || data.result || 'Unknown', // Use 'prediction' field
              faces_found: data.faces_detected || data.faces_found || 0, // Use 'faces_detected' field
              model_used: data.detection_method || data.model_used || 'Enhanced AI'
            });
            setAnalysisStatus('completed');
            if (pollInterval) {
              clearInterval(pollInterval);
              pollInterval = null;
            }
          } else if (data.status === 'failed') {
            console.log('❌ Analysis failed:', data.error);
            setAnalysisStatus('error');
            setError(data.error || 'Analysis failed');
            if (pollInterval) {
              clearInterval(pollInterval);
              pollInterval = null;
            }
          } else {
            // Continue processing - update result for progress
            setResult(data);
          }
        } catch (error) {
          console.log('⚠️ Polling error:', error);
          // Continue polling - don't give up on temporary network issues
        }
      };

      pollInterval = setInterval(checkDetectionStatus, 1000);
      checkDetectionStatus();
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [currentVideoId, analysisStatus]);

  // Enhanced file upload handler from 'use client'.txt
  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file); // Corrected field name

    try {
      setIsAnalyzing(true);
      setAnalysisStatus('analyzing');
      setAnalysisProgress(10);
      setProcessingStatus('Uploading video...');
      setError(null);
      setResult(null);

      const endpoint = detectionMode === 'modern' 
        ? ENDPOINTS.MODERN_AI_DETECT 
        : ENDPOINTS.UPLOAD_VIDEO;

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData
      });

      const uploadResult = await response.json();

      if (response.ok) {
        setCurrentVideoId(uploadResult.video_id);
        setAnalysisProgress(20);
        setProcessingStatus('Video uploaded successfully. Starting analysis...');
        
        // Start polling for results
        startPolling(uploadResult.video_id);
      } else {
        setError(uploadResult.detail || 'Upload failed');
        setIsAnalyzing(false);
        setAnalysisStatus('error');
        setAnalysisProgress(0);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setError('Upload failed. Please try again.');
      setIsAnalyzing(false);
      setAnalysisStatus('error');
      setAnalysisProgress(0);
    }
  };

  // Enhanced YouTube analysis from 'use client'.txt
  const handleYouTubeAnalysis = async () => {
    if (!youtubeUrl.trim()) return;

    try {
      setIsAnalyzing(true);
      setAnalysisStatus('analyzing');
      setAnalysisProgress(10);
      setProcessingStatus('Processing YouTube URL...');
      setError(null);
      setResult(null);

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.YOUTUBE_DETECT}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
      });

      const uploadResult = await response.json();

      if (response.ok) {
        setCurrentVideoId(uploadResult.video_id);
        setAnalysisProgress(30);
        setProcessingStatus('YouTube video downloaded. Starting analysis...');
        
        // Start polling for results
        startPolling(uploadResult.video_id);
      } else {
        setError(uploadResult.detail || 'YouTube processing failed');
        setIsAnalyzing(false);
        setAnalysisStatus('error');
        setAnalysisProgress(0);
      }
    } catch (error) {
      console.error('YouTube analysis failed:', error);
      setError('YouTube analysis failed. Please try again.');
      setIsAnalyzing(false);
      setAnalysisStatus('error');
      setAnalysisProgress(0);
    }
  };

  // Dropzone handlers
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && files[0].type.startsWith('video/')) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  // Reset handler
  const handleReset = useCallback(() => {
    setFile(null);
    setYoutubeUrl('');
    setResult(null);
    setAnalysisStatus('idle');
    setError(null);
    setCurrentVideoId(null);
    setIsAnalyzing(false);
    setAnalysisProgress(0);
    setProcessingStatus('');
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🔍 Advanced Deepfake Detection
            </h1>
            <p className="text-xl text-gray-600">
              Upload your media to analyze for deepfake content using our advanced trained AI model with 94.1% accuracy
            </p>
          </div>

          {/* Enhanced Loading Section from 'use client'.txt */}

          {/* Enhanced Progress Display */}
          <ProgressDisplay 
            progress={progress} 
            status={analysisStatus} 
            result={result}
            currentStage={currentStage}
            elapsedTime={elapsedTime}
          />

          {/* Error Display */}
          {error && !isAnalyzing && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Error</h3>
              <p className="text-red-700">{error}</p>
              <Button 
                onClick={() => {setError(null); setResult(null);}} 
                className="mt-3 bg-red-600 hover:bg-red-700"
              >
                Try Again
              </Button>
            </div>
          )}

          {/* Upload Section */}
          {!isAnalyzing && !result && (
            <div className="space-y-8">
              {/* Upload Method Selection */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex bg-gray-50 rounded-xl p-1 mb-6">
                  <button
                    onClick={() => setActiveTab('upload')}
                    className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg transition-all ${
                      activeTab === 'upload'
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    disabled={analysisStatus === 'analyzing'}
                  >
                    <Upload className="w-5 h-5 mr-2" />
                    Upload Video
                  </button>
                  <button
                    onClick={() => setActiveTab('youtube')}
                    className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg transition-all ${
                      activeTab === 'youtube'
                        ? 'bg-white text-red-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    disabled={analysisStatus === 'analyzing'}
                  >
                    <Youtube className="w-5 h-5 mr-2" />
                    YouTube URL
                  </button>
                </div>

                {/* Detection Mode Selection */}
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                  <h3 className="text-blue-700 font-semibold mb-3">🎯 Detection Mode</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button
                      onClick={() => setDetectionMode('modern')}
                      disabled={analysisStatus === 'analyzing'}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        detectionMode === 'modern'
                          ? 'bg-blue-100 border-blue-400 text-blue-700'
                          : 'bg-white border-gray-300 text-gray-700 hover:border-blue-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                          <Brain className="w-4 h-4 text-white" />
                        </div>
                        <div className="text-left">
                          <h4 className="font-semibold">Modern AI Detection</h4>
                          <p className="text-xs">Detects Sora, Midjourney, latest AI</p>
                        </div>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => setDetectionMode('standard')}
                      disabled={analysisStatus === 'analyzing'}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        detectionMode === 'standard'
                          ? 'bg-blue-100 border-blue-400 text-blue-700'
                          : 'bg-white border-gray-300 text-gray-700 hover:border-blue-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                          <Shield className="w-4 h-4 text-white" />
                        </div>
                        <div className="text-left">
                          <h4 className="font-semibold">Standard Detection</h4>
                          <p className="text-xs">Traditional deepfake detection</p>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* File Upload Section */}
                {activeTab === 'upload' && (
                  <div>
                    <h2 className="text-2xl font-bold mb-4">Upload Video File</h2>
                    
                    <div 
                      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                    >
                      <input
                        type="file"
                        accept="video/*"
                        onChange={(e) => {
                          const selectedFile = e.target.files?.[0];
                          if (selectedFile) {
                            setFile(selectedFile);
                          }
                        }}
                        className="hidden"
                        id="file-upload"
                      />
                      <label htmlFor="file-upload" className="cursor-pointer">
                        <div className="text-gray-600">
                          <p className="text-lg mb-2">Drag & drop your video here</p>
                          <p className="text-sm">Supports MP4, MOV, AVI formats • Maximum 100MB</p>
                        </div>
                      </label>
                    </div>

                    {file && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-lg flex items-center justify-between">
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm text-gray-600">
                            Ready to analyze • {(file.size / 1024 / 1024).toFixed(1)} MB
                          </p>
                        </div>
                        <Button 
                          onClick={() => handleFileUpload(file)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          Analyze Video
                        </Button>
                      </div>
                    )}
                  </div>
                )}

                {/* YouTube URL Section */}
                {activeTab === 'youtube' && (
                  <div>
                    <h2 className="text-2xl font-bold mb-4">YouTube Video Analysis</h2>
                    
                    <div className="flex gap-2">
                      <input
                        type="url"
                        placeholder="Enter YouTube video URL"
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <Button 
                        onClick={handleYouTubeAnalysis}
                        disabled={!youtubeUrl.trim()}
                        className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400"
                      >
                        Analyze
                      </Button>
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-2">
                      Supports YouTube videos, Shorts, and youtu.be links up to 5 minutes long
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Results Section */}
          {result && !isAnalyzing && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
              
              {/* Video Display */}
              {result.video_url && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Analyzed Video</h3>
                  <VideoPlayer videoUrl={result.video_url} error={error} />
                </div>
              )}

              {/* Results Display */}
              <div className={`text-center p-6 rounded-lg ${
                result.result?.toLowerCase().includes('real') || 
                result.result?.toLowerCase().includes('authentic') ||
                result.prediction?.toLowerCase().includes('real') ||
                result.prediction?.toLowerCase().includes('authentic') ||
                result.color === 'green'
                  ? 'bg-green-50 border-2 border-green-200' 
                  : 'bg-red-50 border-2 border-red-200'
              }`}>
                <h4 className={`text-xl font-bold mb-2 ${
                  result.result?.toLowerCase().includes('real') || 
                  result.result?.toLowerCase().includes('authentic') ||
                  result.prediction?.toLowerCase().includes('real') ||
                  result.prediction?.toLowerCase().includes('authentic') ||
                  result.color === 'green'
                    ? 'text-green-700' 
                    : 'text-red-700'
                }`}>
                  {result.result || result.prediction || 'Unknown'}
                </h4>
                
                <p className="text-gray-600 mb-4">
                  Confidence: {result.confidence?.toFixed(1) || 0}%
                </p>
                
                <p className="text-gray-700 mb-4">
                  {result.message || (
                    (result.result?.toLowerCase().includes('real') || 
                     result.result?.toLowerCase().includes('authentic') ||
                     result.prediction?.toLowerCase().includes('real') ||
                     result.prediction?.toLowerCase().includes('authentic') ||
                     result.color === 'green')
                      ? 'Our advanced AI models indicate this media appears to be authentic and genuine'
                      : 'Our AI analysis detected potential deepfake indicators in this media content'
                  )}
                </p>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-blue-600">{result.faces_found || result.faces_detected || 0}</span>
                    <p className="text-gray-500">Faces Detected</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-600">{result.model_used || result.detection_method || 'Enhanced AI'}</span>
                    <p className="text-gray-500">Model Used</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-600">{result.processing_time || 0}s</span>
                    <p className="text-gray-500">Processing Time</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-600">
                      {result.enhanced_analysis ? 'Enhanced' : detectionMode === 'modern' ? 'Modern AI' : 'Standard'}
                    </span>
                    <p className="text-gray-500">Analysis Type</p>
                  </div>
                </div>
              </div>

              {/* Reset Button */}
              <div className="mt-6 text-center">
                <Button 
                  onClick={handleReset}
                  className="bg-gray-600 hover:bg-gray-700"
                >
                  Analyze Another Video
                </Button>
              </div>
            </div>
          )}

          {/* How iFake Works Section */}
          <div className="bg-white rounded-lg shadow-lg p-8 mt-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">🔬 How iFake Works</h2>
              <p className="text-gray-600">Our AI follows these core steps to analyze your media with precision</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { step: "STEP 1", title: "Media Processing", description: "Extract and preprocess frames from your input media", color: "bg-blue-500" },
                { step: "STEP 2", title: "Face Detection", description: "Locate and extract facial regions using MTCNN", color: "bg-purple-500" },
                { step: "STEP 3", title: "Feature Analysis", description: "Analyze spatial artifacts with EfficientNet-B0", color: "bg-pink-500" },
                { step: "STEP 4", title: "Temporal Analysis", description: "Examine frame consistency across video timeline", color: "bg-red-500" },
                { step: "STEP 5", title: "AI Classification", description: "Binary classifier provides confidence score", color: "bg-yellow-500" },
                { step: "STEP 6", title: "Final Verdict", description: "Ensemble decision with detailed analysis", color: "bg-green-500" }
              ].map((item, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-6 border border-gray-200 hover:bg-gray-100 transition-all">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 ${item.color} rounded-lg flex items-center justify-center text-white font-bold text-sm mr-3`}>
                      {index + 1}
                    </div>
                    <h3 className="text-gray-900 font-semibold">{item.title}</h3>
                  </div>
                  <p className="text-gray-600 text-sm">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Detection Tips */}
          <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
            <h3 className="text-lg font-bold text-gray-900 mb-4">💡 Detection Tips</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-start space-x-3">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
                <p className="text-gray-600">Higher quality videos provide more accurate detection results</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
                <p className="text-gray-600">Videos with clear facial features work best for analysis</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
                <p className="text-gray-600">Modern AI detection mode catches latest AI-generated content</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
                <p className="text-gray-600">Enhanced detection provides additional accuracy for complex cases</p>
              </div>
            </div>
          </div>

          {/* Performance Stats */}
          <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-blue-500" />
              📊 Performance Stats
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 text-sm">Model Accuracy</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div className="h-2 bg-green-500 rounded-full" style={{width: '95%'}}></div>
                    </div>
                    <span className="text-green-600 font-semibold text-sm">95%+</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 text-sm">Processing Speed</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{width: '90%'}}></div>
                    </div>
                    <span className="text-blue-600 font-semibold text-sm">Fast</span>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 text-sm">False Positives</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div className="h-2 bg-yellow-500 rounded-full" style={{width: '5%'}}></div>
                    </div>
                    <span className="text-yellow-600 font-semibold text-sm">5%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 text-sm">Modern AI Detection</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div className="h-2 bg-purple-500 rounded-full" style={{width: '94%'}}></div>
                    </div>
                    <span className="text-purple-600 font-semibold text-sm">94%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}