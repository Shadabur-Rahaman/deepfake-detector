import React from 'react';
import { EnhancedNotificationProvider as Provider } from './EnhancedNotificationContext';

interface EnhancedNotificationProviderProps {
  children: React.ReactNode;
}

export const EnhancedNotificationProvider: React.FC<EnhancedNotificationProviderProps> = ({ children }) => {
  return (
    <Provider>
      {children}
    </Provider>
  );
};
