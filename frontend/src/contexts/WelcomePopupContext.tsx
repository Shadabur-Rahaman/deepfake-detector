import React, { createContext, useContext, useState, useCallback } from 'react';

interface WelcomePopupContextType {
  showWelcomePopup: (userName: string, userEmail: string) => void;
  hideWelcomePopup: () => void;
  isOpen: boolean;
  userName: string;
  userEmail: string;
}

const WelcomePopupContext = createContext<WelcomePopupContextType | undefined>(undefined);

export const useWelcomePopup = () => {
  const context = useContext(WelcomePopupContext);
  if (!context) {
    throw new Error('useWelcomePopup must be used within a WelcomePopupProvider');
  }
  return context;
};

interface WelcomePopupProviderProps {
  children: React.ReactNode;
}

export const WelcomePopupProvider: React.FC<WelcomePopupProviderProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');

  const showWelcomePopup = useCallback((name: string, email: string) => {
    setUserName(name);
    setUserEmail(email);
    setIsOpen(true);
  }, []);

  const hideWelcomePopup = useCallback(() => {
    setIsOpen(false);
    // Clear user data after animation completes
    setTimeout(() => {
      setUserName('');
      setUserEmail('');
    }, 300);
  }, []);

  return (
    <WelcomePopupContext.Provider
      value={{
        showWelcomePopup,
        hideWelcomePopup,
        isOpen,
        userName,
        userEmail,
      }}
    >
      {children}
    </WelcomePopupContext.Provider>
  );
};
