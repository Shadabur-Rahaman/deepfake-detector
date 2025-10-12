/**
 * Configuration Test Utility
 * This file helps verify that the API configuration is working correctly
 */

import { API_BASE_URL, WS_URL } from '@/config/api';

export const testApiConfiguration = () => {
  console.log('🧪 API Configuration Test:');
  console.log('  API_BASE_URL:', API_BASE_URL);
  console.log('  WS_URL:', WS_URL);
  console.log('  Expected API:', 'http://127.0.0.1:8000/api');
  console.log('  Expected WS:', 'ws://127.0.0.1:8000/ws/admin');
  
  const apiCorrect = API_BASE_URL === 'http://127.0.0.1:8000/api';
  const wsCorrect = WS_URL === 'ws://127.0.0.1:8000/ws/admin';
  
  console.log('  API URL correct:', apiCorrect);
  console.log('  WS URL correct:', wsCorrect);
  
  if (apiCorrect && wsCorrect) {
    console.log('✅ Configuration is correct!');
    return true;
  } else {
    console.log('❌ Configuration has issues!');
    return false;
  }
};

// Auto-run test when imported
testApiConfiguration();
