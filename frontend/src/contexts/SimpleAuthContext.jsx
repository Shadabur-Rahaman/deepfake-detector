import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await authService.restore();
        if (currentUser) setUser(currentUser);
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (email, password, phone) => {
    setIsLoading(true);
    try {
      const result = await authService.login(email, password, phone);
      if (result.needs_verification) {
        return result;
      }
      if (result.success) {
        setUser(result.user);
        return { success: true, user: result.user };
      }
      return { success: false, message: result.message };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const verifyLogin = async (payload) => {
    setIsLoading(true);
    try {
      const result = await authService.verifyLogin(payload);
      if (result.success) {
        setUser(result.user);
        return { success: true, user: result.user };
      }
      return { success: false, message: result.message };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    try {
      const result = await authService.register(userData);
      if (result.needs_verification) {
        return result;
      }
      if (result.success) {
        setUser(result.user);
        return { success: true, user: result.user };
      }
      return { success: false, message: result.message };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const verifyRegister = async (payload) => {
    setIsLoading(true);
    try {
      const result = await authService.verifyRegister(payload);
      if (result.success) {
        setUser(result.user);
        return { success: true, user: result.user };
      }
      return { success: false, message: result.message };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      return { success: true };
    } catch (error) {
      setUser(null);
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const isAuthenticated = Boolean(user);

  const value = {
    user,
    isLoading,
    login,
    verifyLogin,
    register,
    verifyRegister,
    logout,
    isAuthenticated,
    getAccessToken: () => authService.accessToken(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
