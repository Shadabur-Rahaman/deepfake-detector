import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

interface ConnectionStatusProps {
  className?: string;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ className }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        const response = await fetch('http://127.0.0.1:8000/api/health', {
          signal: controller.signal,
          method: 'GET'
        });
        
        clearTimeout(timeoutId);
        setBackendStatus(response.ok ? 'online' : 'offline');
      } catch (error) {
        setBackendStatus('offline');
      }
    };

    // Check backend status on mount
    checkBackendStatus();

    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000);

    // Listen for online/offline events
    const handleOnline = () => {
      setIsOnline(true);
      checkBackendStatus();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setBackendStatus('offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline && backendStatus === 'online') {
    return null; // Don't show status when everything is working
  }

  return (
    <div className={`fixed top-20 right-4 z-40 ${className}`}>
        <div className={`
        flex items-center gap-1.5 px-2.5 py-1.5 rounded-md shadow-md border backdrop-blur-sm text-xs
        ${!isOnline 
          ? 'bg-red-50/90 border-red-200 text-red-700' 
          : backendStatus === 'offline'
          ? 'bg-yellow-50/90 border-yellow-200 text-yellow-700'
          : 'bg-blue-50/90 border-blue-200 text-blue-700'
        }
      `}>
        {!isOnline ? (
          <>
            <WifiOff className="w-3.5 h-3.5" />
            <span className="font-medium">No Internet</span>
          </>
        ) : backendStatus === 'offline' ? (
          <>
            <AlertCircle className="w-3.5 h-3.5" />
            <span className="font-medium">Server Offline</span>
          </>
        ) : backendStatus === 'checking' ? (
          <>
            <div className="w-3.5 h-3.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="font-medium">Checking...</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-3.5 h-3.5" />
            <span className="font-medium">All Online</span>
          </>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatus;
