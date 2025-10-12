/**
 * Advanced Authentication Modal Component
 * Unified modal for both sign-up and sign-in with advanced features.
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { AdvancedSignInForm } from './AdvancedSignInForm';
import { AdvancedSignUpForm } from './AdvancedSignUpForm';
import { X, UserPlus, Key } from 'lucide-react';

interface AdvancedAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: 'signin' | 'signup';
}

export const AdvancedAuthModal: React.FC<AdvancedAuthModalProps> = ({
  isOpen,
  onClose,
  defaultTab = 'signin'
}) => {
  const [currentTab, setCurrentTab] = useState<'signin' | 'signup'>(defaultTab);

  const handleSuccess = () => {
    onClose();
  };

  const switchToSignUp = () => {
    setCurrentTab('signup');
  };

  const switchToSignIn = () => {
    setCurrentTab('signin');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onClose();
          }
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative bg-background rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Close Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="absolute top-4 right-4 z-10"
          >
            <X className="h-4 w-4" />
          </Button>

          {/* Tab Navigation */}
          <div className="flex border-b border-border">
            <button
              onClick={() => setCurrentTab('signin')}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 transition-colors ${
                currentTab === 'signin'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent'
              }`}
            >
              <Key className="h-4 w-4" />
              <span>Sign In</span>
            </button>
            <button
              onClick={() => setCurrentTab('signup')}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 transition-colors ${
                currentTab === 'signup'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent'
              }`}
            >
              <UserPlus className="h-4 w-4" />
              <span>Sign Up</span>
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            <AnimatePresence mode="wait">
              {currentTab === 'signin' ? (
                <motion.div
                  key="signin"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.2 }}
                >
                  <AdvancedSignInForm
                    onClose={onClose}
                    onSuccess={handleSuccess}
                    switchToSignUp={switchToSignUp}
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="signup"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  <AdvancedSignUpForm
                    onClose={onClose}
                    onSuccess={handleSuccess}
                    switchToSignIn={switchToSignIn}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AdvancedAuthModal;
