import React, { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Volume2, VolumeX, Maximize, RotateCcw } from 'lucide-react';

interface ResponsiveVideoPlayerProps {
  src: string;
  className?: string;
  poster?: string;
  controls?: boolean;
  autoPlay?: boolean;
  muted?: boolean;
  loop?: boolean;
  onLoadStart?: () => void;
  onLoadedData?: () => void;
  onError?: (error: any) => void;
}

export function ResponsiveVideoPlayer({
  src,
  className = '',
  poster,
  controls = true,
  autoPlay = false,
  muted = false,
  loop = false,
  onLoadStart,
  onLoadedData,
  onError
}: ResponsiveVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(muted);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadStart = () => {
      setIsLoading(true);
      onLoadStart?.();
    };

    const handleLoadedData = () => {
      setIsLoading(false);
      setDuration(video.duration);
      onLoadedData?.();
    };

    const handleError = (e: any) => {
      console.error('Video error:', e);
      setIsLoading(false);
      onError?.(e);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    const handleVolumeChange = () => {
      setVolume(video.volume);
      setIsMuted(video.muted);
    };

    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    video.addEventListener('loadstart', handleLoadStart);
    video.addEventListener('loadeddata', handleLoadedData);
    video.addEventListener('error', handleError);
    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('volumechange', handleVolumeChange);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      video.removeEventListener('loadstart', handleLoadStart);
      video.removeEventListener('loadeddata', handleLoadedData);
      video.removeEventListener('error', handleError);
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('volumechange', handleVolumeChange);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [onLoadStart, onLoadedData, onError]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
  };

  const toggleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (!document.fullscreenElement) {
      video.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  const restart = () => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = 0;
    video.play();
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`relative w-full ${className}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative aspect-video w-full overflow-hidden rounded-2xl bg-black shadow-2xl group hover:shadow-3xl transition-all duration-500 hover:scale-[1.01]"
      >
        {/* Video Element */}
        <video
          ref={videoRef}
          className="h-full w-full object-cover"
          controls={!controls ? false : undefined}
          autoPlay={autoPlay}
          muted={muted}
          loop={loop}
          poster={poster}
          preload="metadata"
          playsInline
        >
          <source src={src} type="video/mp4" />
          <source src={src} type="video/webm" />
          <source src={src} type="video/ogg" />
          Your browser does not support the video tag.
        </video>
        
        {/* Sophisticated Loading Overlay */}
        {isLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-black/80 via-black/60 to-black/80 backdrop-blur-sm"
          >
            <div className="flex flex-col items-center space-y-6">
              <motion.div 
                className="relative"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <div className="w-12 h-12 rounded-full border-4 border-white/20 border-t-white animate-spin" />
                <div className="absolute inset-0 w-12 h-12 rounded-full border-4 border-transparent border-t-white/60 animate-spin" style={{ animationDelay: '0.5s' }} />
              </motion.div>
              <div className="text-center">
                <p className="text-white text-lg font-medium mb-2">Loading Video</p>
                <p className="text-white/70 text-sm">Preparing your content...</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Sophisticated Center Play Button */}
        {controls && (
          <motion.div 
            className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-500 bg-gradient-to-t from-black/40 via-transparent to-transparent"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
          >
            <motion.button
              onClick={togglePlay}
              className="relative w-20 h-20 rounded-full bg-white/95 hover:bg-white flex items-center justify-center shadow-2xl hover:shadow-3xl transition-all duration-300 group/play"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              {/* Ripple Effect */}
              <div className="absolute inset-0 rounded-full bg-white/30 animate-ping" />
              <div className="absolute inset-0 rounded-full bg-white/20 animate-ping" style={{ animationDelay: '0.5s' }} />
              
              {/* Play/Pause Icon */}
              <div className="relative z-10">
                {isPlaying ? (
                  <Pause className="w-8 h-8 text-black group-hover/play:scale-110 transition-transform duration-200" />
                ) : (
                  <Play className="w-8 h-8 text-black ml-1 group-hover/play:scale-110 transition-transform duration-200" />
                )}
              </div>
            </motion.button>
          </motion.div>
        )}

        {/* Sophisticated Bottom Controls */}
        {controls && (
          <motion.div 
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-6 opacity-0 group-hover:opacity-100 transition-all duration-500 backdrop-blur-sm"
            initial={{ y: 20, opacity: 0 }}
            whileHover={{ y: 0, opacity: 1 }}
          >
            <div className="flex items-center space-x-6">
              {/* Play/Pause Button */}
              <motion.button
                onClick={togglePlay}
                className="text-white hover:text-white/80 transition-colors p-2 rounded-full hover:bg-white/10"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6" />
                ) : (
                  <Play className="w-6 h-6" />
                )}
              </motion.button>

              {/* Time Display */}
              <div className="text-white text-sm font-mono bg-black/30 px-3 py-1 rounded-full backdrop-blur-sm">
                {formatTime(currentTime)} / {formatTime(duration)}
              </div>

              {/* Sophisticated Progress Bar */}
              <div className="flex-1 relative">
                <div className="h-2 bg-white/20 rounded-full overflow-hidden backdrop-blur-sm">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-primary to-accent rounded-full relative"
                    style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                    transition={{ duration: 0.1 }}
                  >
                    <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg" />
                  </motion.div>
                </div>
              </div>

              {/* Volume Control */}
              <motion.button
                onClick={toggleMute}
                className="text-white hover:text-white/80 transition-colors p-2 rounded-full hover:bg-white/10"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                {isMuted || volume === 0 ? (
                  <VolumeX className="w-5 h-5" />
                ) : (
                  <Volume2 className="w-5 h-5" />
                )}
              </motion.button>

              {/* Restart Button */}
              <motion.button
                onClick={restart}
                className="text-white hover:text-white/80 transition-colors p-2 rounded-full hover:bg-white/10"
                title="Restart video"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <RotateCcw className="w-5 h-5" />
              </motion.button>

              {/* Fullscreen Button */}
              <motion.button
                onClick={toggleFullscreen}
                className="text-white hover:text-white/80 transition-colors p-2 rounded-full hover:bg-white/10"
                title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Maximize className="w-5 h-5" />
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* Sophisticated Top Overlay */}
        <div className="absolute top-0 left-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-all duration-500">
          <div className="flex justify-between items-center">
            {/* Quality Badge */}
            <div className="bg-black/60 backdrop-blur-md rounded-full px-4 py-2 text-white text-xs font-medium border border-white/20">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>HD Quality</span>
              </div>
            </div>
            
            {/* Status Indicator */}
            <div className="bg-black/60 backdrop-blur-md rounded-full px-4 py-2 text-white text-xs font-medium border border-white/20">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <span>AI Enhanced</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sophisticated Corner Decorations */}
        <div className="absolute top-2 left-2 w-3 h-3 border-l-2 border-t-2 border-white/30 rounded-tl-lg" />
        <div className="absolute top-2 right-2 w-3 h-3 border-r-2 border-t-2 border-white/30 rounded-tr-lg" />
        <div className="absolute bottom-2 left-2 w-3 h-3 border-l-2 border-b-2 border-white/30 rounded-bl-lg" />
        <div className="absolute bottom-2 right-2 w-3 h-3 border-r-2 border-b-2 border-white/30 rounded-br-lg" />
      </motion.div>
    </div>
  );
}

export default ResponsiveVideoPlayer;
