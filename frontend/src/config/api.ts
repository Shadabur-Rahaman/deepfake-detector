/**
 * API Configuration for Deepfake Detection Backend
 * Connects to FastAPI backend for video processing and detection
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000', // Hardcoded to fix connection issues
  WS_URL: 'ws://127.0.0.1:8000/ws/admin', // Fixed WebSocket URL to match backend
  HEALTH_ENDPOINT: '/health'
};

// Get the appropriate API URL based on environment
export const getApiUrl = (): string => {
  return API_CONFIG.BASE_URL;
};

// Get WebSocket URL
export const getWebSocketUrl = (): string => {
  return API_CONFIG.WS_URL;
};

// Export the current API URL
export const API_BASE_URL = getApiUrl();
export const WS_URL = getWebSocketUrl();

// Log the API URL being used (for debugging)
console.log('🔗 Using Backend API:', API_BASE_URL);
console.log('🔗 Using WebSocket:', WS_URL);
console.log('🔍 Environment VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('🔍 Environment VITE_WS_URL:', import.meta.env.VITE_WS_URL);
console.log('🔧 Configuration loaded at:', new Date().toISOString());
