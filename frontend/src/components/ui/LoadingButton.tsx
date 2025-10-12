import React from 'react';
import { Button } from './button';
import { Loader2, Play, Zap, Brain, Stars } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/lib/theme';

interface LoadingButtonProps extends React.ComponentProps<typeof Button> {
  loading?: boolean;
  loadingText?: string;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  showIcon?: boolean;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  children,
  disabled,
  className,
  variant = 'default',
  showIcon = true,
  ...props
}) => {
  const { theme } = useTheme();
  
  // Get appropriate icon based on theme and context
  const getIcon = () => {
    if (loading) return <Loader2 className="mr-2 h-4 w-4 animate-spin" />;
    if (!showIcon) return null;
    
    // Different icons for different themes
    switch (theme) {
      case 'neon':
        return <Zap className="mr-2 h-4 w-4" />;
      case 'deep-space':
        return <Stars className="mr-2 h-4 w-4" />;
      case 'minimal':
        return <Play className="mr-2 h-4 w-4" />;
      default:
        return <Brain className="mr-2 h-4 w-4" />;
    }
  };

  // Enhanced className with theme-specific styling
  const enhancedClassName = cn(
    // Base neural button styling
    "neural-button neural-glow hover-lift",
    // Theme-specific enhancements
    {
      // Light theme
      "bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg hover:shadow-xl": theme === 'light',
      // Dark theme
      "bg-gradient-to-r from-primary/90 to-accent/90 text-primary-foreground shadow-glow hover:shadow-glow/80": theme === 'dark',
      // Neon theme
      "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-neon hover:shadow-neon/80 animate-pulse-slow": theme === 'neon',
      // Deep Space theme
      "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-deep-space hover:shadow-deep-space/80 animate-glow": theme === 'deep-space',
      // Minimal theme
      "bg-foreground text-background hover:bg-foreground/90 shadow-elegant": theme === 'minimal',
    },
    // Size-specific adjustments
    {
      "text-base font-semibold px-6 py-3": props.size === 'lg',
      "text-sm font-medium px-4 py-2": props.size === 'default',
      "text-xs font-medium px-3 py-1.5": props.size === 'sm',
    },
    // Loading state styling
    {
      "opacity-75 cursor-not-allowed": loading,
      "transform hover:scale-105 active:scale-95": !loading,
    },
    className
  );

  return (
    <Button
      disabled={loading || disabled}
      variant={variant}
      className={enhancedClassName}
      {...props}
    >
      {getIcon()}
      {loading ? (loadingText || 'Loading...') : children}
    </Button>
  );
};
