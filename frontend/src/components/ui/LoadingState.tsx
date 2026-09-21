import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Brain, Zap } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  progress?: number;
  variant?: 'default' | 'detection' | 'analysis';
  className?: string;
}

export function LoadingState({ 
  message = 'Loading...', 
  progress, 
  variant = 'default',
  className = ''
}: LoadingStateProps) {
  const getIcon = () => {
    switch (variant) {
      case 'detection':
        return <Brain className="w-8 h-8 text-primary" />;
      case 'analysis':
        return <Zap className="w-8 h-8 text-accent" />;
      default:
        return <Loader2 className="w-8 h-8 text-primary animate-spin" />;
    }
  };

  const getMessage = () => {
    switch (variant) {
      case 'detection':
        return message || 'Analyzing video content...';
      case 'analysis':
        return message || 'Processing detection results...';
      default:
        return message;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex flex-col items-center justify-center p-8 ${className}`}
    >
      <motion.div
        animate={{ 
          rotate: variant === 'default' ? 360 : 0,
          scale: [1, 1.1, 1]
        }}
        transition={{ 
          duration: variant === 'default' ? 1 : 2,
          repeat: variant === 'default' ? Infinity : Infinity,
          ease: "easeInOut"
        }}
        className="mb-4"
      >
        {getIcon()}
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-center mb-4 w-full max-w-md"
      >
        <h3 className="text-lg font-semibold mb-2 neural-text px-4">
          {getMessage()}
        </h3>
      </motion.div>
      
      {progress !== undefined && (
        <motion.div
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: 1, width: '100%' }}
          transition={{ delay: 0.4 }}
          className="w-full max-w-md"
        >
          <div className="w-full bg-muted rounded-full h-3 mb-3 overflow-hidden shadow-inner">
            <motion.div
              className="bg-gradient-to-r from-primary to-accent h-3 rounded-full relative overflow-hidden"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              {/* Shimmer effect for active progress */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                animate={{
                  x: ['-100%', '100%'],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            </motion.div>
          </div>
          <div className="flex items-center justify-between text-sm">
            <p className="text-muted-foreground font-medium">
              {progress.toFixed(0)}% complete
            </p>
            {progress > 0 && progress < 100 && (
              <p className="text-muted-foreground/70 text-xs">
                Processing...
              </p>
            )}
          </div>
        </motion.div>
      )}
      
      {variant === 'detection' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-4 text-center"
        >
          <p className="text-sm text-muted-foreground">
            Our AI is analyzing every frame for manipulation patterns
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}

export default LoadingState;
