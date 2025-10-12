import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./card";
import { Button } from "./button";
import { Badge } from "./badge";
import { X, CheckCircle2 } from 'lucide-react';
import { usePayment } from '../../contexts/PaymentContext';
import toast from 'react-hot-toast';

interface Plan {
  name: string;
  price: string;
  period: string;
  description: string;
  requests: string;
  plan_id: string;
  amount: number; // Amount in paise for Razorpay
  features: string[];
}

interface PaymentModalProps {
  plan: Plan;
  onClose: () => void;
}

const PaymentModal: React.FC<PaymentModalProps> = ({ plan, onClose }) => {
  const [loading, setLoading] = useState(false);
  const { initializePayment } = usePayment();

  const handlePayment = async () => {
    setLoading(true);
    try {
      await initializePayment(plan.plan_id, plan.amount);
      onClose();
    } catch (error) {
      toast.error('Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
        >
          <X className="w-4 h-4" />
        </button>
        
        <CardHeader>
          <CardTitle>Subscribe to {plan.name}</CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">{plan.price}</div>
              <div className="text-muted-foreground">{plan.period}</div>
            </div>
            
            <div className="bg-muted p-4 rounded-lg">
              <div className="font-semibold">{plan.requests}</div>
              <ul className="text-sm text-muted-foreground mt-2 space-y-1">
                {plan.features.slice(0, 4).map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <CheckCircle2 className="w-3 h-3 text-success" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button 
                onClick={handlePayment} 
                disabled={loading}
                className="flex-1"
              >
                {loading ? 'Processing...' : `Pay ${plan.price}`}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentModal;
