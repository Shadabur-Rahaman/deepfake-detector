import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './SimpleAuthContext';
import { toast } from 'sonner';
import { API_BASE_URL } from '@/config/api';

interface UserUsage {
  subscription_plan: string;
  subscription_status: string;
  requests_used: number;
  requests_limit: number;
  subscription_end: string | null;
}

interface PaymentContextType {
  usage: UserUsage | null;
  loading: boolean;
  fetchUsage: () => Promise<void>;
  initializePayment: (planId: string, amount: number) => Promise<void>;
}

const PaymentContext = createContext<PaymentContextType | undefined>(undefined);

export const PaymentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [usage, setUsage] = useState<UserUsage | null>(null);
  const [loading, setLoading] = useState(false);
  const { user, isAuthenticated } = useAuth();

  const fetchUsage = async () => {
    if (!user || !isAuthenticated) return;
    
    setLoading(true);
    try {
      // Get token from localStorage for API calls
      const token = localStorage.getItem('ifake_access_token');
      
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch(`${API_BASE_URL}/user/usage`, {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        setUsage(data);
      } else {
        console.warn('Failed to fetch usage: Server returned', response.status);
      }
    } catch (error) {
      // Handle different types of errors gracefully
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.warn('Backend server is not running. Usage tracking disabled.');
        // Set default usage values when backend is unavailable
        setUsage({
          subscription_plan: 'free',
          subscription_status: 'active',
          requests_used: 0,
          requests_limit: 10,
          subscription_end: null
        });
      } else if (error.name === 'AbortError') {
        console.warn('Usage fetch request timed out');
        // Set default usage values when request times out
        setUsage({
          subscription_plan: 'free',
          subscription_status: 'active',
          requests_used: 0,
          requests_limit: 10,
          subscription_end: null
        });
      } else {
        console.warn('Failed to fetch usage:', error);
        // Set default usage values on other errors too
        setUsage({
          subscription_plan: 'free',
          subscription_status: 'active',
          requests_used: 0,
          requests_limit: 10,
          subscription_end: null
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const initializePayment = async (planId: string, amount: number) => {
    if (!user || !isAuthenticated) return;

    try {
      // Get token from localStorage for API calls
      const token = localStorage.getItem('ifake_access_token');
      // Create order on backend
      const orderResponse = await fetch(`${API_BASE_URL}/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ planId, amount })
      });

      const order = await orderResponse.json();

      // Initialize Razorpay
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_key',
        amount: order.amount,
        currency: order.currency,
        name: 'iFake API',
        description: `Subscription Plan: ${planId}`,
        order_id: order.id,
        handler: async function (response: any) {
          // Verify payment
          const verifyResponse = await fetch(`${API_BASE_URL}/verify-payment`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              planId
            })
          });

          if (verifyResponse.ok) {
            await fetchUsage();
            toast.success('Payment successful! Your plan has been activated.');
          }
        },
        prefill: {
          name: user.full_name || user.username,
          email: user.email,
        },
        theme: {
          color: '#3B82F6'
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();
    } catch (error) {
      console.error('Payment initialization failed:', error);
    }
  };

  useEffect(() => {
    if (user && isAuthenticated) {
      fetchUsage();
    }
  }, [user, isAuthenticated]);

  return (
    <PaymentContext.Provider value={{ usage, loading, fetchUsage, initializePayment }}>
      {children}
    </PaymentContext.Provider>
  );
};

export const usePayment = () => {
  const context = useContext(PaymentContext);
  if (!context) {
    throw new Error('usePayment must be used within a PaymentProvider');
  }
  return context;
};
