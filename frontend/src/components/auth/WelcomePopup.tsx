import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, User, Sparkles, ArrowRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface WelcomePopupProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string;
  userEmail: string;
}

export const WelcomePopup: React.FC<WelcomePopupProps> = ({
  isOpen,
  onClose,
  userName,
  userEmail
}) => {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Small delay to ensure smooth animation
      const timer = setTimeout(() => setShowContent(true), 100);
      return () => clearTimeout(timer);
    } else {
      setShowContent(false);
    }
  }, [isOpen]);

  // Remove auto-close - user must click proceed button

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.8, opacity: 0, y: 20 }}
          transition={{ 
            type: "spring", 
            stiffness: 300, 
            damping: 30,
            duration: 0.6
          }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md mx-4"
        >
          <Card className="border-0 shadow-2xl bg-gradient-to-br from-green-50 to-emerald-50 overflow-hidden">
            <CardContent className="p-0">
              {/* Header with gradient background */}
              <div className="relative bg-gradient-to-r from-green-500 to-emerald-600 p-6 text-white">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
                
                <div className="relative z-10 flex items-center space-x-4">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm"
                  >
                    <User className="w-8 h-8 text-white" />
                  </motion.div>
                  
                  <div className="flex-1">
                    <motion.h2
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="text-2xl font-bold"
                    >
                      Welcome back!
                    </motion.h2>
                    <motion.p
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 }}
                      className="text-green-100 text-sm"
                    >
                      Great to see you again
                    </motion.p>
                  </div>
                  
                  <motion.div
                    initial={{ rotate: 0 }}
                    animate={{ rotate: 360 }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                    className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center"
                  >
                    <CheckCircle className="w-5 h-5 text-white" />
                  </motion.div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="text-center space-y-4"
                >
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-gray-800">
                      Hello, {userName}! 👋
                    </h3>
                    <p className="text-sm text-gray-600">
                      {userEmail}
                    </p>
                  </div>

                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.8 }}
                    className="flex items-center justify-center space-x-2 text-green-600"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span className="text-sm font-medium">Successfully signed in</span>
                    <Sparkles className="w-4 h-4" />
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.0 }}
                    className="pt-4"
                  >
                    <Button
                      onClick={onClose}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-medium py-2.5 rounded-lg transition-all duration-200 transform hover:scale-105"
                    >
                      <span>Proceed to App</span>
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </motion.div>

                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.2 }}
                    className="text-xs text-gray-500"
                  >
                    Click "Proceed to App" to continue
                  </motion.p>
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default WelcomePopup;
