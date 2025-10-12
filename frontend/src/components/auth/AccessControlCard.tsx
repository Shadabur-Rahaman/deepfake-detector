import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTheme } from '@/lib/theme';
import { Shield, Zap, Eye, Camera, Clock, CheckCircle, Lock, Users, Crown, ArrowRight, Sparkles } from 'lucide-react';

interface AccessControlCardProps {
  feature: 'try' | 'detection';
  onRequestAccess: () => void;
  className?: string;
}

export const AccessControlCard: React.FC<AccessControlCardProps> = ({
  feature,
  onRequestAccess,
  className = ""
}) => {
  const { theme } = useTheme();
  const isTryFeature = feature === 'try';
  
  const config = {
    try: {
      icon: Shield,
      iconColor: 'text-primary',
      gradientFrom: 'from-primary/20',
      gradientTo: 'to-accent/20',
      buttonGradient: 'from-primary to-accent',
      title: 'Authentication Required',
      subtitle: 'Please sign in to access this feature.',
      description: 'You need permission to access the Try Detection features. Please request access from an administrator to start analyzing videos with our advanced deepfake detection technology.',
      buttonText: 'Sign In',
      buttonIcon: Lock,
      secondaryButtonText: 'Retry',
      secondaryButtonIcon: ArrowRight,
      featureText: 'Free analysis available',
      featureIcon: Eye,
      requiredRoles: ['user', 'admin', 'premium'],
      requiredPermissions: ['detection:create'],
      benefits: [
        'Upload video files up to 100MB',
        'YouTube URL analysis support',
        '94.1% accuracy with MesoNet CNN',
        'Multiple detection modes available'
      ]
    },
    detection: {
      icon: Zap,
      iconColor: 'text-accent',
      gradientFrom: 'from-accent/20',
      gradientTo: 'to-primary/20',
      buttonGradient: 'from-accent to-primary',
      title: 'Authentication Required',
      subtitle: 'Please sign in to access this feature.',
      description: 'You need permission to access the Real-Time Detection features. Please request access from an administrator to start live camera analysis with our advanced AI detection system.',
      buttonText: 'Sign In',
      buttonIcon: Lock,
      secondaryButtonText: 'Retry',
      secondaryButtonIcon: ArrowRight,
      featureText: 'Live camera analysis',
      featureIcon: Camera,
      requiredRoles: ['user', 'admin', 'premium'],
      requiredPermissions: ['detection:create', 'detection:read'],
      benefits: [
        'Real-time camera feed analysis',
        'Instant deepfake detection',
        'Advanced AI processing',
        'Live confidence scoring'
      ]
    }
  };

  const currentConfig = config[feature];
  const IconComponent = currentConfig.icon;
  const ButtonIconComponent = currentConfig.buttonIcon;
  const FeatureIconComponent = currentConfig.featureIcon;

  return (
    <section className={`py-8 md:py-16 px-4 ${className}`}>
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Card className={`neural-card border-2 ${isTryFeature ? 'border-primary/20' : 'border-accent/20'} bg-gradient-to-br ${currentConfig.gradientFrom} via-background ${currentConfig.gradientTo} backdrop-blur-sm transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10`}>
            <CardContent className="p-6 md:p-8 lg:p-12">
              {/* Header */}
              <div className="text-center mb-8">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                  className={`w-20 h-20 mx-auto mb-6 bg-gradient-to-br ${currentConfig.gradientFrom} ${currentConfig.gradientTo} rounded-full flex items-center justify-center neural-glow`}
                >
                  <IconComponent className={`w-10 h-10 ${currentConfig.iconColor}`} />
                </motion.div>
                
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="text-3xl font-bold mb-2 gradient-text neural-text"
                >
                  {currentConfig.title}
                </motion.h2>
                
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="text-lg text-muted-foreground mb-6 neural-text"
                >
                  {currentConfig.subtitle}
                </motion.p>

                {/* Required Roles and Permissions */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                  className="space-y-4 mb-8"
                >
                  {/* Required Roles */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground neural-text">Required Roles:</p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {currentConfig.requiredRoles.map((role) => (
                        <Badge 
                          key={role} 
                          variant="secondary" 
                          className="neural-card bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 transition-colors"
                        >
                          <Users className="w-3 h-3 mr-1" />
                          {role}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Required Permissions */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground neural-text">Required Permissions:</p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {currentConfig.requiredPermissions.map((permission) => (
                        <Badge 
                          key={permission} 
                          variant="outline" 
                          className="neural-card bg-accent/10 text-accent border-accent/20 hover:bg-accent/20 transition-colors"
                        >
                          <Shield className="w-3 h-3 mr-1" />
                          {permission}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </motion.div>
                
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6, duration: 0.5 }}
                  className="text-base text-muted-foreground mb-6 neural-text max-w-2xl mx-auto leading-relaxed"
                >
                  {currentConfig.description}
                </motion.p>
              </div>

              {/* Benefits Grid */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.5 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4 mb-6 md:mb-8"
              >
                {currentConfig.benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1, duration: 0.4 }}
                    className="flex items-center gap-3 p-4 neural-card rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                  >
                    <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                    <span className="text-sm neural-text">{benefit}</span>
                  </motion.div>
                ))}
              </motion.div>
              
              {/* Action Section */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7, duration: 0.5 }}
                className="text-center space-y-6"
              >
                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button 
                    onClick={onRequestAccess}
                    size="lg"
                    className={`neural-button hover-lift bg-gradient-to-r ${currentConfig.buttonGradient} text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 px-8 py-3`}
                  >
                    <ButtonIconComponent className="w-5 h-5 mr-2" />
                    {currentConfig.buttonText}
                  </Button>
                  
                  <Button 
                    onClick={() => window.location.reload()}
                    variant="outline"
                    size="lg"
                    className="neural-button hover-lift bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300 px-8 py-3"
                  >
                    <currentConfig.secondaryButtonIcon className="w-5 h-5 mr-2" />
                    {currentConfig.secondaryButtonText}
                  </Button>
                </div>

                {/* Help Text */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8, duration: 0.5 }}
                  className="neural-card p-4 rounded-xl bg-muted/30 border border-border/50"
                >
                  <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground neural-text mb-2">
                    <Sparkles className="w-4 h-4" />
                    <span className="font-medium">Need an account?</span>
                  </div>
                  <p className="text-sm text-muted-foreground neural-text">
                    You can create one for free and start detecting deepfakes immediately.
                  </p>
                </motion.div>
                
                <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-sm text-muted-foreground neural-text">
                  <div className="flex items-center gap-2">
                    <FeatureIconComponent className="w-4 h-4" />
                    <span>{currentConfig.featureText}</span>
                  </div>
                  <span className="hidden sm:inline mx-2">•</span>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Response within 24 hours</span>
                  </div>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};
