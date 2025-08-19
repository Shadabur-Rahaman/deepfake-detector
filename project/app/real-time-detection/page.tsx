'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Camera, CameraOff, Activity, AlertTriangle, CheckCircle, Wifi, WifiOff } from 'lucide-react';

interface DetectionResult {
    prediction: string;
    confidence: number;
    faces_detected: number;
    processing_time: string;
    face_coordinates?: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    error?: string;
    status?: string;
}

export default function RealTimeDetection() {
    const [isDetecting, setIsDetecting] = useState(false);
    const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
    const [status, setStatus] = useState('Ready to start');
    const [error, setError] = useState<string | null>(null);
    const [connectionState, setConnectionState] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);
    const frameCountRef = useRef(0);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const WS_URL = API_BASE_URL.replace('http', 'ws') + '/ws/real-time-detection';

    // **FIXED** - Improved sendFrame function with better error handling
    const sendFrame = useCallback(() => {
        console.log('🔄 sendFrame called at:', new Date().toISOString());

        // Check WebSocket connection first
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.log('❌ WebSocket not available or not open');
            return;
        }

        // Check video and canvas refs
        if (!videoRef.current || !canvasRef.current) {
            console.log('❌ Video or canvas ref not available');
            return;
        }

        // Check video readiness
        if (videoRef.current.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
            console.log('❌ Video not ready, readyState:', videoRef.current.readyState);
            return;
        }

        // Check video dimensions
        if (videoRef.current.videoWidth === 0 || videoRef.current.videoHeight === 0) {
            console.log('❌ Video dimensions not available');
            return;
        }

        try {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');

            if (!ctx) {
                console.log('❌ Canvas context not available');
                return;
            }

            // Set canvas dimensions to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Draw current video frame to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // **FIXED** - Convert canvas to blob then to base64
            canvas.toBlob((blob) => {
                if (!blob) {
                    console.log('❌ Failed to create blob from canvas');
                    return;
                }

                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const base64String = reader.result as string;
                        const base64Data = base64String.split(',')[1]; // Remove data:image/jpeg;base64, prefix

                        if (wsRef.current?.readyState === WebSocket.OPEN) {
                            wsRef.current.send(JSON.stringify({ frame: base64Data }));
                            frameCountRef.current++;
                            console.log('✅ Frame sent successfully! Count:', frameCountRef.current);
                        }
                    } catch (e) {
                        console.error('❌ Error processing blob:', e);
                    }
                };
                reader.onerror = () => {
                    console.error('❌ FileReader error');
                };
                reader.readAsDataURL(blob);
            }, 'image/jpeg', 0.8);

        } catch (error: any) {
            console.error('❌ Frame capture error:', error);
            setError(`Frame capture failed: ${error.message}`);
        }
    }, []);

    // **FIXED** - Improved WebSocket connection with proper error handling
    const connectWebSocket = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('📶 WebSocket already connected');
            return;
        }

        console.log('🔗 Connecting to WebSocket:', WS_URL);
        setConnectionState('connecting');
        setError(null);

        try {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            // **FIXED** - Set connection timeout
            const connectionTimeout = setTimeout(() => {
                if (ws.readyState === WebSocket.CONNECTING) {
                    ws.close();
                    setConnectionState('disconnected');
                    setError('Connection timeout - server may be unavailable');
                }
            }, 10000); // 10 second timeout

            ws.onopen = () => {
                console.log('✅ WebSocket connected successfully');
                clearTimeout(connectionTimeout);
                setConnectionState('connected');
                setError(null);
                setStatus('Connected - position your face in frame');

                // **FIXED** - Start frame transmission immediately after connection
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
                intervalRef.current = setInterval(sendFrame, 1000); // Send frame every 1 second
            };

            ws.onmessage = (event) => {
                try {
                    const result = JSON.parse(event.data);
                    console.log('📨 Received from server:', result);

                    if (result.status === 'success') {
                        updateResults(result);
                    } else if (result.error) {
                        console.error('❌ Server error:', result.error);
                        setError(result.error);
                    }
                } catch (err) {
                    console.error('❌ Message parsing error:', err);
                }
            };

            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                clearTimeout(connectionTimeout);
                setConnectionState('disconnected');
                setError('Failed to connect to detection server');
            };

            ws.onclose = (event) => {
                console.log('🔌 WebSocket closed:', event.code, event.reason);
                clearTimeout(connectionTimeout);
                setConnectionState('disconnected');

                // Clear frame transmission
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }

                // **FIXED** - Only attempt reconnection if it wasn't a normal closure
                if (isDetecting && event.code !== 1000) {
                    console.log('🔄 Attempting reconnection in 3 seconds...');
                    setTimeout(() => {
                        if (isDetecting) {
                            connectWebSocket();
                        }
                    }, 3000);
                }
            };

        } catch (err: any) {
            console.error('❌ WebSocket creation failed:', err);
            setConnectionState('disconnected');
            setError(`Connection failed: ${err.message}`);
        }
    }, [sendFrame, isDetecting, WS_URL]);

    // **FIXED** - Improved camera initialization
    const startDetection = async () => {
        try {
            console.log('🚀 Starting detection process...');
            setError(null);
            setStatus('Requesting camera access...');

            // Get camera access with specific constraints
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640, max: 1280 },
                    height: { ideal: 480, max: 720 },
                    frameRate: { ideal: 15, max: 30 },
                    facingMode: 'user' // Front-facing camera
                },
                audio: false
            });

            console.log('✅ Camera access granted');

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                streamRef.current = stream;

                // **FIXED** - Wait for video to be properly loaded
                await new Promise<void>((resolve, reject) => {
                    const video = videoRef.current!;
                    
                    const onLoadedData = () => {
                        console.log('🎥 Video loaded, dimensions:', video.videoWidth, 'x', video.videoHeight);
                        video.removeEventListener('loadeddata', onLoadedData);
                        video.removeEventListener('error', onError);
                        resolve();
                    };

                    const onError = (e: any) => {
                        console.error('❌ Video loading error:', e);
                        video.removeEventListener('loadeddata', onLoadedData);
                        video.removeEventListener('error', onError);
                        reject(new Error('Video failed to load'));
                    };

                    video.addEventListener('loadeddata', onLoadedData);
                    video.addEventListener('error', onError);

                    // Start playing the video
                    video.play().catch(reject);

                    // Timeout fallback
                    setTimeout(() => {
                        if (video.videoWidth > 0 && video.videoHeight > 0) {
                            onLoadedData();
                        } else {
                            onError(new Error('Video dimensions not available after timeout'));
                        }
                    }, 5000);
                });
            }

            // Set detection state and connect WebSocket
            setIsDetecting(true);
            frameCountRef.current = 0;
            connectWebSocket();

        } catch (err: any) {
            console.error('❌ Detection start failed:', err);
            setError(`Failed to start: ${err.message}`);
            cleanup();
        }
    };

    // **FIXED** - Improved cleanup function
    const cleanup = useCallback(() => {
        console.log('🧹 Cleaning up resources...');
        setIsDetecting(false);

        // Clear frame transmission interval
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        // Close WebSocket connection
        if (wsRef.current) {
            if (wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.close(1000, 'User stopped detection');
            }
            wsRef.current = null;
        }

        // Stop camera stream
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => {
                track.stop();
                console.log('📹 Camera track stopped');
            });
            streamRef.current = null;
        }

        // Clear video source
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }

        // Reset states
        setConnectionState('disconnected');
        setDetectionResult(null);
        setError(null);
        setStatus('Detection stopped');
    }, []);

    const stopDetection = useCallback(() => {
        console.log('🛑 Stopping detection...');
        cleanup();
    }, [cleanup]);

    // **FIXED** - Improved result updating
    const updateResults = useCallback((result: DetectionResult) => {
        setDetectionResult(result);

        if (result.faces_detected === 0) {
            setStatus('👤 No face detected - position yourself in frame');
        } else {
            const confidence = result.confidence?.toFixed(1) || '0.0';
            const prediction = result.prediction || 'Analyzing';
            setStatus(`🎯 ${prediction} (${confidence}% confidence)`);
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            cleanup();
        };
    }, [cleanup]);

    // **FIXED** - Improved helper functions
    const getStatusColor = (prediction: string | null | undefined) => {
        if (!prediction) return 'text-gray-600';
        if (prediction.toLowerCase().includes('real')) return 'text-green-600';
        if (prediction.toLowerCase().includes('deepfake')) return 'text-red-600';
        return 'text-yellow-600';
    };

    const getStatusIcon = (prediction: string | null | undefined) => {
        if (!prediction) return <Activity className="w-4 h-4" />;
        if (prediction.toLowerCase().includes('real')) return <CheckCircle className="w-4 h-4" />;
        if (prediction.toLowerCase().includes('deepfake')) return <AlertTriangle className="w-4 h-4" />;
        return <Activity className="w-4 h-4" />;
    };

    const getBadgeVariant = (prediction: string | null | undefined): "default" | "destructive" | "secondary" => {
        if (!prediction) return 'secondary';
        if (prediction.toLowerCase().includes('real')) return 'default';
        if (prediction.toLowerCase().includes('deepfake')) return 'destructive';
        return 'secondary';
    };

    return (
        <div className="container mx-auto px-4 py-8 max-w-6xl">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    🎯 Real-Time Deepfake Detection
                </h1>
                <p className="text-xl text-gray-600 mb-6">
                    Live camera analysis using advanced AI multi-stage detection
                </p>

                {/* **FIXED** - Connection Status Display */}
                <div className="flex justify-center items-center gap-4 mb-6">
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100">
                        <span className="text-sm">Camera:</span>
                        {streamRef.current ? (
                            <span className="text-green-600 flex items-center gap-1">
                                <Wifi className="w-4 h-4" /> Active
                            </span>
                        ) : (
                            <span className="text-gray-500 flex items-center gap-1">
                                <WifiOff className="w-4 h-4" /> Inactive
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100">
                        <span className="text-sm">AI Server:</span>
                        {connectionState === 'connected' ? (
                            <span className="text-green-600 flex items-center gap-1">
                                <Wifi className="w-4 h-4" /> Connected
                            </span>
                        ) : connectionState === 'connecting' ? (
                            <span className="text-yellow-600 flex items-center gap-1">
                                <Activity className="w-4 h-4 animate-spin" /> Connecting
                            </span>
                        ) : (
                            <span className="text-gray-500 flex items-center gap-1">
                                <WifiOff className="w-4 h-4" /> Disconnected
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Camera Section */}
                <Card className="overflow-hidden">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Camera className="w-5 h-5" />
                            Live Camera Feed
                        </CardTitle>
                        <CardDescription>
                            Position your face clearly in the camera frame for optimal detection
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {/* **FIXED** - Video Display with Face Tracking */}
                            <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className="w-full h-full object-cover"
                                />
                                <canvas
                                    ref={canvasRef}
                                    className="hidden"
                                />

                                {/* Face Detection Overlay */}
                                {detectionResult?.face_coordinates && streamRef.current && (
                                    <div
                                        className="absolute border-4 border-green-400 rounded-lg transition-all duration-300 ease-out shadow-lg"
                                        style={{
                                            left: `${(detectionResult.face_coordinates.x / 640) * 100}%`,
                                            top: `${(detectionResult.face_coordinates.y / 480) * 100}%`,
                                            width: `${(detectionResult.face_coordinates.width / 640) * 100}%`,
                                            height: `${(detectionResult.face_coordinates.height / 480) * 100}%`,
                                            borderColor: detectionResult.prediction?.toLowerCase().includes('deepfake') ? '#ef4444' : '#4ade80'
                                        }}
                                    >
                                        <div
                                            className={`absolute -top-8 left-0 px-2 py-1 rounded text-xs font-semibold ${
                                                detectionResult.prediction?.toLowerCase().includes('deepfake')
                                                    ? 'bg-red-500 text-white'
                                                    : 'bg-green-500 text-white'
                                            }`}
                                        >
                                            {detectionResult.prediction || 'Analyzing'} - {detectionResult.confidence?.toFixed(1)}%
                                        </div>
                                    </div>
                                )}

                                {/* Inactive Camera Overlay */}
                                {!streamRef.current && (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-800 text-white">
                                        <CameraOff className="w-16 h-16 mb-4 text-gray-400" />
                                        <p className="text-lg font-medium">Camera Inactive</p>
                                        <p className="text-sm text-gray-400">Click "Start Detection" to begin</p>
                                    </div>
                                )}
                            </div>

                            {/* **FIXED** - Controls */}
                            <div className="flex gap-2">
                                <Button
                                    onClick={startDetection}
                                    disabled={isDetecting}
                                    className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                                >
                                    <Camera className="w-4 h-4 mr-2" />
                                    {isDetecting ? 'Detection Active' : 'Start Detection'}
                                </Button>
                                <Button
                                    onClick={stopDetection}
                                    disabled={!isDetecting}
                                    variant="outline"
                                    className="flex-1 border-red-200 text-red-600 hover:bg-red-50"
                                >
                                    <CameraOff className="w-4 h-4 mr-2" />
                                    Stop
                                </Button>
                            </div>

                            {/* Status Display */}
                            <div className="p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm font-medium text-gray-700 mb-1">Status:</p>
                                <p className="text-lg font-semibold">{status}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Results Section */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="w-5 h-5" />
                            Detection Results
                        </CardTitle>
                        <CardDescription>
                            Real-time analysis results from AI models
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {/* Error Display */}
                            {error && (
                                <Alert variant="destructive">
                                    <AlertTriangle className="h-4 w-4" />
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}

                            {/* Detection Results */}
                            {detectionResult && !error && (
                                <div className="space-y-4">
                                    {/* Prediction */}
                                    <div className="text-center p-4 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100">
                                        <div className="flex items-center justify-center gap-2 mb-2">
                                            {getStatusIcon(detectionResult?.prediction)}
                                            <Badge variant={getBadgeVariant(detectionResult?.prediction)} className="text-lg px-4 py-2">
                                                {detectionResult?.prediction || 'Processing...'}
                                            </Badge>
                                        </div>
                                        <p className={`text-3xl font-bold ${getStatusColor(detectionResult?.prediction)}`}>
                                            {detectionResult?.confidence?.toFixed(1) || '0.0'}%
                                        </p>
                                        <p className="text-sm text-gray-500">Confidence Level</p>
                                    </div>

                                    {/* Detailed Metrics */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                                            <p className="text-2xl font-bold text-blue-600">{detectionResult?.faces_detected || 0}</p>
                                            <p className="text-sm text-gray-600">Faces Detected</p>
                                        </div>
                                        <div className="text-center p-3 bg-purple-50 rounded-lg">
                                            <p className="text-lg font-bold text-purple-600">{frameCountRef.current}</p>
                                            <p className="text-sm text-gray-600">Frames Processed</p>
                                        </div>
                                    </div>

                                    {/* Technical Details */}
                                    <div className="text-sm text-gray-500 space-y-1">
                                        <p><strong>Processing:</strong> {detectionResult?.processing_time || 'real-time'}</p>
                                        {detectionResult?.face_coordinates && (
                                            <p><strong>Face Position:</strong> ({detectionResult.face_coordinates.x}, {detectionResult.face_coordinates.y})</p>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Instructions */}
                            {!detectionResult && !error && (
                                <div className="text-center py-8">
                                    <Activity className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                                    <h3 className="text-lg font-semibold mb-2">Ready for Detection</h3>
                                    <div className="text-sm text-gray-500 space-y-2">
                                        <p className="font-medium">Quick Start Guide:</p>
                                        <ol className="list-decimal list-inside space-y-1 text-left max-w-sm mx-auto">
                                            <li>Click "Start Detection" to begin</li>
                                            <li>Allow camera access when prompted</li>
                                            <li>Position your face clearly in frame</li>
                                            <li>Real-time results will appear instantly</li>
                                        </ol>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Features Section */}
            <Card className="mt-8">
                <CardHeader>
                    <CardTitle>🚀 Advanced Real-Time Detection Features</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div className="text-center">
                            <div className="w-12 h-12 mx-auto mb-3 bg-blue-100 rounded-full flex items-center justify-center">
                                <Activity className="w-6 h-6 text-blue-600" />
                            </div>
                            <h3 className="font-semibold">Live Analysis</h3>
                            <p className="text-sm text-gray-600">Real-time processing</p>
                        </div>
                        <div className="text-center">
                            <div className="w-12 h-12 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                                <CheckCircle className="w-6 h-6 text-green-600" />
                            </div>
                            <h3 className="font-semibold">High Accuracy</h3>
                            <p className="text-sm text-gray-600">Multi-stage AI ensemble</p>
                        </div>
                        <div className="text-center">
                            <div className="w-12 h-12 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
                                <Camera className="w-6 h-6 text-purple-600" />
                            </div>
                            <h3 className="font-semibold">Face Tracking</h3>
                            <p className="text-sm text-gray-600">Automatic detection & overlay</p>
                        </div>
                        <div className="text-center">
                            <div className="w-12 h-12 mx-auto mb-3 bg-orange-100 rounded-full flex items-center justify-center">
                                <Wifi className="w-6 h-6 text-orange-600" />
                            </div>
                            <h3 className="font-semibold">WebSocket Streaming</h3>
                            <p className="text-sm text-gray-600">Low-latency communication</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
