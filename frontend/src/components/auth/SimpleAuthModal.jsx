import React, { useState } from 'react';
import SimpleLoginForm from './SimpleLoginForm';
import SimpleSignupForm from './SimpleSignupForm';

const SimpleAuthModal = ({ isOpen, onClose, onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  const handleLoginSuccess = (user) => {
    onAuthSuccess(user);
    onClose();
  };

  const handleSignupSuccess = (user) => {
    // After successful signup, show a message and switch to login
    alert('Account created successfully! Please login to continue.');
    setIsLogin(true);
  };

  const handleSwitchToSignup = () => {
    setIsLogin(false);
  };

  const handleSwitchToLogin = () => {
    setIsLogin(true);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">
            {isLogin ? 'Login' : 'Sign Up'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        
        <div className="p-6">
          {isLogin ? (
            <SimpleLoginForm
              onLoginSuccess={handleLoginSuccess}
              onSwitchToSignup={handleSwitchToSignup}
            />
          ) : (
            <SimpleSignupForm
              onSignupSuccess={handleSignupSuccess}
              onSwitchToLogin={handleSwitchToLogin}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default SimpleAuthModal;
