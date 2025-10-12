/**
 * Production Authentication Context
 * Enterprise-grade authentication with comprehensive security features.
 * 
 * This context provides:
 * - JWT token management
 * - Automatic token refresh
 * - Role-based access control
 * - Session management
 * - Security monitoring
 * 
 * Author: Senior Backend Engineer
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useWelcomePopup } from './WelcomePopupContext';

// Types
interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_verified: boolean;
  is_2fa_enabled: boolean;
  roles: string[];
  permissions: string[];
  created_at: string;
  last_login?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  csrfToken: string | null;
  
  // Authentication methods
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  
  // Security methods
  getCsrfToken: () => Promise<string>;
  validateSession: () => Promise<boolean>;
  
  // Permission checking
  hasPermission: (permission: string, resource?: string) => boolean;
  hasRole: (role: string) => boolean;
  canAccess: (resource: string, action: string) => boolean;
  
  // User management
  updateUser: (userData: Partial<User>) => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  
  // Detection limits
  canDetect: () => boolean;
  getDetectionStatus: () => DetectionStatus;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

interface DetectionStatus {
  canDetect: boolean;
  permissions: string[];
  roles: string[];
  requiresUpgrade: boolean;
}

// API Configuration
import { API_BASE_URL } from '../config/api';
const TOKEN_STORAGE_KEY = 'ifake_access_token';
const REFRESH_TOKEN_STORAGE_KEY = 'ifake_refresh_token';
const USER_STORAGE_KEY = 'ifake_user';
const CSRF_TOKEN_STORAGE_KEY = 'ifake_csrf_token';

// Create context
const AuthContext = createContext<AuthContextType | null>(null);

// Helper function to normalize user data
const normalizeUserData = (userData: any): User => {
  return {
    ...userData,
    roles: userData.roles || ['user'],
    permissions: userData.permissions || []
  };
};

// Custom hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// API helper functions
class ProductionAPIClient {
  private baseURL: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private csrfToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.loadTokensFromStorage();
  }

  private loadTokensFromStorage() {
    this.accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
    this.csrfToken = localStorage.getItem(CSRF_TOKEN_STORAGE_KEY);
  }

  private saveTokensToStorage(tokens: AuthTokens) {
    localStorage.setItem(TOKEN_STORAGE_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token);
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
  }

  private clearTokens() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
    this.accessToken = null;
    this.refreshToken = null;
    this.csrfToken = null;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add authentication headers
    if (requireAuth && this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }

    // Add CSRF token for state-changing operations
    if (this.csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || 'GET')) {
      headers['X-CSRF-Token'] = this.csrfToken;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });

      // Handle token expiration
      if (response.status === 401 && requireAuth && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry request with new token
          headers.Authorization = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, {
            ...options,
            headers,
            credentials: 'include',
          });
          return await this.handleResponse<T>(retryResponse);
        }
      }

      return await this.handleResponse<T>(response);
    } catch (error) {
      console.error('API request failed:', error);
      throw new Error('Network error occurred');
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        this.saveTokensToStorage(tokens);
        return true;
      } else {
        this.clearTokens();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      return false;
    }
  }

  // Authentication methods
  async login(email: string, password: string, rememberMe: boolean = false): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.makeRequest<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
      user: User;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    }, false);

    // Transform the response to match expected format
    const tokens: AuthTokens = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      token_type: response.token_type,
      expires_in: response.expires_in,
    };

    this.saveTokensToStorage(tokens);
    
    // Ensure user data is properly structured
    const userData = response.user || {} as any;
    const user: User = {
      id: userData.id || '',
      email: userData.email || '',
      username: userData.username || '',
      full_name: userData.full_name || '',
      is_verified: userData.is_verified || false,
      is_2fa_enabled: userData.is_2fa_enabled || false,
      roles: userData.roles || ['user'],
      permissions: userData.permissions || [],
      created_at: userData.created_at || new Date().toISOString(),
      last_login: userData.last_login || null,
    };
    
    return {
      user: user,
      tokens: tokens
    };
  }

  async register(userData: RegisterData): Promise<{ user: User }> {
    return await this.makeRequest<{ user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }, false);
  }

  async logout(): Promise<void> {
    try {
      await this.makeRequest('/auth/logout', { method: 'POST' });
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<User> {
    return await this.makeRequest<User>('/auth/me');
  }

  async getCsrfToken(): Promise<string> {
    const response = await this.makeRequest<{ csrf_token: string }>('/auth/csrf-token');
    this.csrfToken = response.csrf_token;
    localStorage.setItem(CSRF_TOKEN_STORAGE_KEY, response.csrf_token);
    return response.csrf_token;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.makeRequest('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }

  async getDetectionStatus(): Promise<DetectionStatus> {
    const response = await this.makeRequest<DetectionStatus>('/detection/status');
    return response;
  }
}

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const { showWelcomePopup } = useWelcomePopup();

  const apiClient = new ProductionAPIClient(API_BASE_URL);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = localStorage.getItem(USER_STORAGE_KEY);
        const storedCsrfToken = localStorage.getItem(CSRF_TOKEN_STORAGE_KEY);

        if (storedUser && storedCsrfToken) {
          const userData = JSON.parse(storedUser);
          setUser(normalizeUserData(userData));
          setCsrfToken(storedCsrfToken);

          // Validate session with server
          try {
            const currentUser = await apiClient.getCurrentUser();
            const normalizedUser = normalizeUserData(currentUser);
            setUser(normalizedUser);
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));
          } catch (error) {
            // Session invalid, clear local data
            localStorage.removeItem(USER_STORAGE_KEY);
            localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
            setUser(null);
            setCsrfToken(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // Clear potentially corrupted data
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token
  useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(async () => {
      try {
        const refreshed = await apiClient.refreshAccessToken();
        if (!refreshed) {
          // Refresh failed, logout user
          await logout();
        }
      } catch (error) {
        console.error('Auto token refresh failed:', error);
      }
    }, 25 * 60 * 1000); // Refresh every 25 minutes

    return () => clearInterval(refreshInterval);
  }, [user]);

  // Authentication methods
  const login = useCallback(async (email: string, password: string, rememberMe: boolean = false) => {
    setIsLoading(true);
    try {
      const { user: userData, tokens } = await apiClient.login(email, password, rememberMe);
      
      const normalizedUser = normalizeUserData(userData);
      setUser(normalizedUser);
      setCsrfToken(tokens.access_token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));
      
      // Show welcome popup with user's name
      showWelcomePopup(userData.full_name || userData.username || 'User', userData.email);
      
      toast.success('Successfully logged in!');
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [showWelcomePopup]);

  const register = useCallback(async (userData: RegisterData) => {
    setIsLoading(true);
    try {
      const { user: newUser } = await apiClient.register(userData);
      
      const normalizedUser = normalizeUserData(newUser);
      setUser(normalizedUser);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));
      
      toast.success('Account created successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setCsrfToken(null);
      setIsLoading(false);
      toast.success('Successfully logged out');
    }
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      return await apiClient.refreshAccessToken();
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }, []);

  const getCsrfToken = useCallback(async (): Promise<string> => {
    try {
      const token = await apiClient.getCsrfToken();
      setCsrfToken(token);
      return token;
    } catch (error) {
      console.error('CSRF token fetch failed:', error);
      throw error;
    }
  }, []);

  const validateSession = useCallback(async (): Promise<boolean> => {
    try {
      await apiClient.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  // Permission checking methods
  const hasPermission = useCallback((permission: string, resource?: string): boolean => {
    if (!user || !user.permissions || !Array.isArray(user.permissions)) return false;
    
    // Check exact permission
    if (user.permissions.includes(permission)) {
      return true;
    }
    
    // Check resource-specific permission
    if (resource) {
      const resourcePermission = `${permission}:${resource}`;
      if (user.permissions.includes(resourcePermission)) {
        return true;
      }
    }
    
    // Check wildcard permissions
    const permissionParts = permission.split(':');
    if (permissionParts.length >= 2) {
      const category = permissionParts[0];
      const action = permissionParts[1];
      
      if (user.permissions.includes(`${category}:*`) || 
          user.permissions.includes(`*:${action}`)) {
        return true;
      }
    }
    
    return false;
  }, [user]);

  const hasRole = useCallback((role: string): boolean => {
    if (!user || !user.roles || !Array.isArray(user.roles)) return false;
    return user.roles.includes(role);
  }, [user]);

  const canAccess = useCallback((resource: string, action: string): boolean => {
    if (!user) return false;
    
    const permission = `${resource}:${action}`;
    return hasPermission(permission) || hasPermission(`${resource}:*`) || hasPermission(`*:${action}`);
  }, [user, hasPermission]);

  const updateUser = useCallback((userData: Partial<User>) => {
    setUser(prev => prev ? { ...prev, ...userData } : null);
    if (user) {
      const updatedUser = { ...user, ...userData };
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(updatedUser));
    }
  }, [user]);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    try {
      await apiClient.changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Password change failed');
      throw error;
    }
  }, []);

  const canDetect = useCallback((): boolean => {
    if (!user) return false;
    return hasPermission('detection:create');
  }, [user, hasPermission]);

  const getDetectionStatus = useCallback((): DetectionStatus => {
    if (!user) {
      return {
        canDetect: false,
        permissions: [],
        roles: [],
        requiresUpgrade: true
      };
    }

    return {
      canDetect: canDetect(),
      permissions: user.permissions,
      roles: user.roles,
      requiresUpgrade: !canDetect()
    };
  }, [user, canDetect]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    csrfToken,
    login,
    register,
    logout,
    refreshToken,
    getCsrfToken,
    validateSession,
    hasPermission,
    hasRole,
    canAccess,
    updateUser,
    changePassword,
    canDetect,
    getDetectionStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
