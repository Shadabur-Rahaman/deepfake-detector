import React from 'react';
import { WelcomePopup } from './WelcomePopup';
import { useWelcomePopup } from '../../contexts/WelcomePopupContext';

interface AuthWithWelcomeProps {
  children: React.ReactNode;
}

export const AuthWithWelcome: React.FC<AuthWithWelcomeProps> = ({ children }) => {
  const { isOpen, hideWelcomePopup, userName, userEmail } = useWelcomePopup();

  return (
    <>
      {children}
      <WelcomePopup
        isOpen={isOpen}
        onClose={hideWelcomePopup}
        userName={userName}
        userEmail={userEmail}
      />
    </>
  );
};

export default AuthWithWelcome;
