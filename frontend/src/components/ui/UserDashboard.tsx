import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./card";
import { Button } from "./button";
import { Badge } from "./badge";
import { Progress } from "./progress";
import { usePayment } from '../../contexts/PaymentContext';
import { Calendar, CreditCard, Activity } from 'lucide-react';

const UserDashboard: React.FC = () => {
  const { usage, loading } = usePayment();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!usage) {
    return <div>No usage data available</div>;
  }

  const usagePercentage = (usage.requests_used / usage.requests_limit) * 100;
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            API Usage Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Current Plan:</span>
              <Badge variant={usage.subscription_plan === 'free' ? 'secondary' : 'default'}>
                {usage.subscription_plan.charAt(0).toUpperCase() + usage.subscription_plan.slice(1)}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Requests Used:</span>
                <span>{usage.requests_used} / {usage.requests_limit}</span>
              </div>
              <Progress value={usagePercentage} className="w-full" />
              <div className="text-xs text-muted-foreground">
                {usage.requests_limit - usage.requests_used} requests remaining
              </div>
            </div>
            
            {usage.subscription_end && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="w-4 h-4" />
                <span>Subscription expires: {new Date(usage.subscription_end).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserDashboard;
