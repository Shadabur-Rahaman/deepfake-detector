import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressIndicatorProps {
  value: number; // 0-100
  showPercentage?: boolean;
  className?: string;
  color?: 'primary' | 'success' | 'warning' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  value,
  showPercentage = true,
  className,
  color = 'primary',
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  };

  const colorClasses = {
    primary: 'bg-primary',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    destructive: 'bg-red-500'
  };

  return (
    <div className={cn('w-full', className)}>
      {showPercentage && (
        <div className="flex justify-between text-sm text-muted-foreground mb-2">
          <span>Progress</span>
          <span>{value}%</span>
        </div>
      )}
      
      <div className={cn(
        'w-full bg-muted rounded-full overflow-hidden',
        sizeClasses[size]
      )}>
        <div
          className={cn(
            'h-full transition-all duration-500 ease-out rounded-full',
            colorClasses[color]
          )}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
};
