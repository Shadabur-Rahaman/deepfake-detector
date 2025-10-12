// src/components/ProtectedDetection.tsx
import React from 'react';
import { useAuth } from '@/contexts/SimpleAuthContext';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lock, Crown, Zap } from 'lucide-react';

interface ProtectedDetectionProps {
  children: React.ReactNode;
  requiresPremium?: boolean;
}

export const ProtectedDetection: React.FC<ProtectedDetectionProps> = ({ 
  children, 
  requiresPremium = false 
}) => {
  const { user, canDetect } = useAuth();

  // Not logged in
  if (!user) {
    return (
      <Card className="text-center p-8">
        <CardHeader>
          <Lock className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <CardTitle>Sign In Required</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-6">
            Please sign in to use iFake's deepfake detection capabilities.
          </p>
          <Button className="glow-primary">
            Sign In to Detect
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Premium feature but user is on free plan
  if (requiresPremium && user.plan === 'free') {
    return (
      <Card className="text-center p-8 border-yellow-500/20 bg-yellow-500/5">
        <CardHeader>
          <Crown className="w-12 h-12 mx-auto text-yellow-500 mb-4" />
          <CardTitle>Premium Feature</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-6">
            This feature requires a Premium subscription for unlimited detections and advanced analysis.
          </p>
          <Button className="bg-yellow-500 hover:bg-yellow-600">
            Upgrade to Premium
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Free user exceeded detection limit
  if (!canDetect()) {
    return (
      <Card className="text-center p-8 border-orange-500/20 bg-orange-500/5">
        <CardHeader>
          <Zap className="w-12 h-12 mx-auto text-orange-500 mb-4" />
          <CardTitle>Detection Limit Reached</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            You've used {user.detectionsUsed}/{user.detectionsLimit} free detections.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button className="bg-yellow-500 hover:bg-yellow-600">
              <Crown className="w-4 h-4 mr-2" />
              Upgrade to Premium
            </Button>
            <Button variant="outline">
              Wait 24 Hours
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // User can access the feature
  return (
    <div>
      {user.plan === 'free' && (
        <div className="mb-4">
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            Free Plan: {user.detectionsUsed}/{user.detectionsLimit} detections used
          </Badge>
        </div>
      )}
      {children}
    </div>
  );
};
