import React from 'react';
import { HeroCanvas } from '../three/HeroCanvas';

interface PageLayoutProps {
  children: React.ReactNode;
  backgroundOpacity?: number;
  showBackground?: boolean;
  className?: string;
}

const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  backgroundOpacity = 0.6,
  showBackground = true,
  className = ''
}) => {
  return (
    <div className="relative min-h-screen">
      {/* Neural Background with Error Boundary */}
      {showBackground && (
        <div 
          className="fixed inset-0 -z-10 overflow-hidden"
          style={{ opacity: backgroundOpacity }}
        >
          <HeroCanvas className="w-full h-full" />
        </div>
      )}
      
      {/* Content */}
      <div className={`relative z-10 min-h-screen ${className}`}>
        {children}
      </div>
    </div>
  );
};

export default PageLayout;
