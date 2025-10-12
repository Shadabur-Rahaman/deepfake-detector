import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './card';
import { cn } from '@/lib/utils';

interface EnhancedCardProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
}

export const EnhancedCard: React.FC<EnhancedCardProps> = ({
  title,
  description,
  children,
  footer,
  className,
  hover = true,
  glow = false
}) => {
  return (
    <Card className={cn(
      'transition-all duration-300',
      hover && 'hover:shadow-lg hover:-translate-y-1',
      glow && 'hover:shadow-primary/20 hover:shadow-2xl',
      className
    )}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      
      <CardContent>
        {children}
      </CardContent>
      
      {footer && (
        <CardFooter>
          {footer}
        </CardFooter>
      )}
    </Card>
  );
};
