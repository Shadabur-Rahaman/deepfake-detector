import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { useTheme } from '@/lib/theme';
import { X, Send, Eye, Zap, Crown, CheckCircle, Users, Shield, Clock } from 'lucide-react';
import { toast } from 'sonner';

interface AccessRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  requestType?: 'try_access' | 'detection_access' | 'premium_upgrade';
}

export const AccessRequestModal: React.FC<AccessRequestModalProps> = ({ 
  isOpen, 
  onClose, 
  requestType = 'try_access' 
}) => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [selectedType, setSelectedType] = useState<'try_access' | 'detection_access' | 'premium_upgrade'>(requestType);
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const requestTypes = [
    {
      value: 'try_access',
      label: 'Try Access',
      description: 'Request access to try deepfake detection features',
      icon: <Eye className="w-5 h-5" />,
      color: 'text-primary',
      gradient: 'from-primary/20 to-accent/20',
      buttonGradient: 'from-primary to-accent'
    },
    {
      value: 'detection_access',
      label: 'Detection Access',
      description: 'Request access to advanced detection capabilities',
      icon: <Zap className="w-5 h-5" />,
      color: 'text-accent',
      gradient: 'from-accent/20 to-primary/20',
      buttonGradient: 'from-accent to-primary'
    },
    {
      value: 'premium_upgrade',
      label: 'Premium Upgrade',
      description: 'Request upgrade to premium features',
      icon: <Crown className="w-5 h-5" />,
      color: 'text-warning',
      gradient: 'from-warning/20 to-accent/20',
      buttonGradient: 'from-warning to-accent'
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${API_BASE_URL}/api/auth/request-access`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('ifake_access_token')}`
        },
        body: JSON.stringify({
          requestType: selectedType,
          message: message
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit request');
      }

      const result = await response.json();
      
      toast.success('Access request submitted successfully!', {
        description: 'An administrator will review your request shortly.'
      });

      setMessage('');
      setIsSubmitted(true);
      
      // Auto-close after 3 seconds
      setTimeout(() => {
        setIsSubmitted(false);
        onClose();
      }, 3000);
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const selectedRequestType = requestTypes.find(type => type.value === selectedType);

  // Success state
  if (isSubmitted) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 30 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="relative w-full max-w-lg"
        >
          <Card className="neural-card border-2 border-success/20 bg-gradient-to-br from-success/5 via-background to-success/5 backdrop-blur-xl shadow-2xl">
            <CardContent className="p-8 text-center">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1, duration: 0.4 }}
                className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-success/20 to-success/30 rounded-full flex items-center justify-center neural-glow"
              >
                <CheckCircle className="w-12 h-12 text-success" />
              </motion.div>
              
              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.4 }}
                className="text-3xl font-bold text-success neural-text mb-4"
              >
                Request Submitted!
              </motion.h2>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
                className="text-muted-foreground neural-text mb-6 text-lg"
              >
                Your access request has been sent successfully. An administrator will review it shortly.
              </motion.p>
              
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
                className="flex items-center justify-center gap-2 text-sm text-muted-foreground neural-text bg-muted/30 rounded-lg p-3"
              >
                <Clock className="w-4 h-4" />
                <span>This window will close automatically in 3 seconds</span>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 30 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden mx-2 sm:mx-0"
      >
        <Card className={`neural-card border-2 ${selectedRequestType?.gradient ? `border-${selectedRequestType.color.split('-')[1]}/20` : 'border-primary/20'} bg-gradient-to-br from-background/95 via-card/95 to-background/95 backdrop-blur-xl shadow-2xl transition-all duration-300`}>
          <CardHeader className="relative text-center pb-6">
            <button
              onClick={onClose}
              className="absolute right-4 top-4 text-muted-foreground hover:text-foreground transition-colors p-2 rounded-full hover:bg-muted/50 z-10"
            >
              <X className="w-5 h-5" />
            </button>
            
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              className={`w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 bg-gradient-to-br ${selectedRequestType?.gradient || 'from-primary/20 to-accent/20'} rounded-full flex items-center justify-center neural-glow`}
            >
              <Shield className={`w-8 h-8 sm:w-10 sm:h-10 ${selectedRequestType?.color || 'text-primary'}`} />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <CardTitle className="text-2xl sm:text-3xl font-bold gradient-text neural-text mb-2">
                Request Access
              </CardTitle>
              <p className="text-muted-foreground neural-text text-base sm:text-lg">
                Submit a request for platform access
              </p>
            </motion.div>
          </CardHeader>
          
          <CardContent className="px-6 md:px-8 pb-8 overflow-y-auto max-h-[60vh]">
            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
              onSubmit={handleSubmit} 
              className="space-y-6"
            >
              {/* User Info */}
              <div className="neural-card p-4 md:p-6 bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center">
                    <Users className="w-4 h-4 text-primary" />
                  </div>
                  <h3 className="font-semibold neural-text">Requesting as:</h3>
                </div>
                <div className="space-y-1">
                  <p className="font-medium neural-text">{user?.full_name}</p>
                  <p className="text-sm text-muted-foreground neural-text">{user?.email}</p>
                </div>
              </div>

              {/* Request Type Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold neural-text">Request Type</Label>
                <Select value={selectedType} onValueChange={(value: 'try_access' | 'detection_access' | 'premium_upgrade') => setSelectedType(value)}>
                  <SelectTrigger className="neural-card border-2 border-primary/20 hover:border-primary/40 transition-colors">
                    <SelectValue placeholder="Select request type" />
                  </SelectTrigger>
                  <SelectContent className="neural-card border-2 border-primary/20">
                    {requestTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value} className="cursor-pointer">
                        <div className="flex items-center gap-3 py-2">
                          <span className={type.color}>{type.icon}</span>
                          <div>
                            <div className="font-medium neural-text">{type.label}</div>
                            <div className="text-xs text-muted-foreground neural-text">
                              {type.description}
                            </div>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Selected Type Info */}
              {selectedRequestType && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className={`neural-card p-4 md:p-6 bg-gradient-to-r ${selectedRequestType.gradient} border ${selectedRequestType.color.replace('text-', 'border-')}/20 rounded-xl`}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className={selectedRequestType.color}>
                      {selectedRequestType.icon}
                    </span>
                    <h4 className="font-semibold neural-text">{selectedRequestType.label}</h4>
                  </div>
                  <p className="text-sm text-muted-foreground neural-text leading-relaxed">
                    {selectedRequestType.description}
                  </p>
                </motion.div>
              )}

              {/* Message */}
              <div className="space-y-3">
                <Label htmlFor="message" className="text-sm font-semibold neural-text">
                  Additional Message (Optional)
                </Label>
                <Textarea
                  id="message"
                  placeholder="Please provide any additional information about your request..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={4}
                  disabled={isSubmitting}
                  className="neural-card border-2 border-primary/20 focus:border-primary/40 transition-colors resize-none"
                />
              </div>

              {/* Submit Button */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
              >
                <Button 
                  type="submit" 
                  size="lg"
                  className={`w-full neural-button hover-lift bg-gradient-to-r ${selectedRequestType?.buttonGradient || 'from-primary to-accent'} text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 py-3`}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Submitting Request...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      Submit Request
                    </>
                  )}
                </Button>
              </motion.div>
            </motion.form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
