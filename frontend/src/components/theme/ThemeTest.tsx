import React from 'react';
import { useTheme } from '@/lib/theme';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, Zap, Eye, Crown } from 'lucide-react';

export const ThemeTest: React.FC = () => {
  const { theme, setTheme, themes } = useTheme();

  return (
    <div className="p-8 space-y-6">
      <Card className="neural-card">
        <CardHeader>
          <CardTitle className="neural-text">Theme Consistency Test</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {themes.map((themeName) => (
              <Button
                key={themeName}
                variant={theme === themeName ? 'default' : 'outline'}
                onClick={() => setTheme(themeName)}
                className="neural-button"
              >
                {themeName}
              </Button>
            ))}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="neural-card">
              <CardContent className="p-4">
                <h3 className="neural-text font-semibold mb-2">Access Control Card</h3>
                <div className="space-y-2">
                  <Badge variant="secondary" className="neural-card">
                    <Shield className="w-3 h-3 mr-1" />
                    Try Access
                  </Badge>
                  <Badge variant="secondary" className="neural-card">
                    <Zap className="w-3 h-3 mr-1" />
                    Detection Access
                  </Badge>
                </div>
              </CardContent>
            </Card>
            
            <Card className="neural-card">
              <CardContent className="p-4">
                <h3 className="neural-text font-semibold mb-2">Modal Elements</h3>
                <div className="space-y-2">
                  <Button className="neural-button w-full">
                    <Eye className="w-4 h-4 mr-2" />
                    Request Access
                  </Button>
                  <Button variant="outline" className="neural-button w-full">
                    <Crown className="w-4 h-4 mr-2" />
                    Premium Upgrade
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="text-sm text-muted-foreground neural-text">
            Current theme: <span className="font-semibold">{theme}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
