import React, { createContext, useContext, useState, ReactNode } from 'react';

interface NavigationState {
  lastApiDocsSection?: string;
  scrollPosition?: number;
}

interface NavigationContextType {
  navigationState: NavigationState;
  setLastApiDocsSection: (section: string) => void;
  setScrollPosition: (position: number) => void;
  clearNavigationState: () => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};

interface NavigationProviderProps {
  children: ReactNode;
}

export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  const [navigationState, setNavigationState] = useState<NavigationState>({});

  const setLastApiDocsSection = (section: string) => {
    setNavigationState(prev => ({
      ...prev,
      lastApiDocsSection: section
    }));
  };

  const setScrollPosition = (position: number) => {
    setNavigationState(prev => ({
      ...prev,
      scrollPosition: position
    }));
  };

  const clearNavigationState = () => {
    setNavigationState({});
  };

  return (
    <NavigationContext.Provider
      value={{
        navigationState,
        setLastApiDocsSection,
        setScrollPosition,
        clearNavigationState
      }}
    >
      {children}
    </NavigationContext.Provider>
  );
};

export default NavigationProvider;
