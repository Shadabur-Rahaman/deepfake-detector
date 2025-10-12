// src/contexts/AuthContext.tsx - Enhanced for iFake
import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  plan: 'free' | 'premium' | 'enterprise';
  detectionsUsed: number;
  detectionsLimit: number;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  canDetect: () => boolean;
  incrementDetection: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication on app start
  useEffect(() => {
    const token = localStorage.getItem('ifake_token');
    const userData = localStorage.getItem('ifake_user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        localStorage.removeItem('ifake_token');
        localStorage.removeItem('ifake_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // In real implementation, call your FastAPI backend
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const { user, token } = await response.json();
        localStorage.setItem('ifake_token', token);
        localStorage.setItem('ifake_user', JSON.stringify(user));
        setUser(user);
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      // For demo - mock authentication
      const mockUsers = JSON.parse(localStorage.getItem('ifake_users') || '[]');
      const foundUser = mockUsers.find((u: any) => u.email === email && u.password === password);
      
      if (foundUser) {
        const userWithPlan = {
          ...foundUser,
          plan: 'free',
          detectionsUsed: 0,
          detectionsLimit: 5
        };
        delete userWithPlan.password;
        
        localStorage.setItem('ifake_token', 'mock-token-' + Date.now());
        localStorage.setItem('ifake_user', JSON.stringify(userWithPlan));
        setUser(userWithPlan);
      } else {
        throw new Error('Invalid email or password');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      // Check if user exists
      const existingUsers = JSON.parse(localStorage.getItem('ifake_users') || '[]');
      const userExists = existingUsers.some((u: any) => u.email === email);
      
      if (userExists) {
        throw new Error('User already exists');
      }

      // Create new user with iFake-specific data
      const newUser: User = {
        id: Date.now().toString(),
        email,
        name,
        plan: 'free',
        detectionsUsed: 0,
        detectionsLimit: 5
      };

      // Save to mock storage
      const userWithPassword = { ...newUser, password };
      existingUsers.push(userWithPassword);
      localStorage.setItem('ifake_users', JSON.stringify(existingUsers));

      // Set current user
      localStorage.setItem('ifake_token', 'mock-token-' + Date.now());
      localStorage.setItem('ifake_user', JSON.stringify(newUser));
      setUser(newUser);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('ifake_token');
    localStorage.removeItem('ifake_user');
    setUser(null);
  };

  const canDetect = () => {
    if (!user) return false;
    if (user.plan === 'premium' || user.plan === 'enterprise') return true;
    return user.detectionsUsed < user.detectionsLimit;
  };

  const incrementDetection = () => {
    if (user && user.plan === 'free') {
      const updatedUser = { ...user, detectionsUsed: user.detectionsUsed + 1 };
      setUser(updatedUser);
      localStorage.setItem('ifake_user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading, canDetect, incrementDetection }}>
      {children}
    </AuthContext.Provider>
  );
};
