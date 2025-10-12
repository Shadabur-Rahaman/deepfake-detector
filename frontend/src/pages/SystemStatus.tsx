import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EnhancedCard } from '@/components/ui/EnhancedCard'
import ScrollToTop from '@/components/ScrollToTop'
import { 
  Globe, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Clock,
  Zap,
  Database,
  Cpu,
  Server,
  Wifi,
  WifiOff,
  RefreshCw,
  TrendingUp,
  Users,
  Shield,
  Brain,
  BarChart3,
  Monitor,
  HardDrive,
  MemoryStick
} from 'lucide-react';
import { Link } from 'react-router-dom';

const SystemStatus: React.FC = () => {
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock data - in real implementation, this would come from API
  const systemStatus = {
    overall: 'operational',
    uptime: '99.9%',
    responseTime: '45ms',
    lastIncident: '2024-01-15T10:30:00Z'
  };

  const services = [
    {
      name: 'API Gateway',
      status: 'operational',
      uptime: '99.9%',
      responseTime: '12ms',
      lastCheck: '2024-01-21T15:30:00Z'
    },
    {
      name: 'MesoNet CNN Engine',
      status: 'operational',
      uptime: '99.8%',
      responseTime: '2.3s',
      lastCheck: '2024-01-21T15:30:00Z'
    },
    {
      name: 'File Processing',
      status: 'operational',
      uptime: '99.7%',
      responseTime: '1.8s',
      lastCheck: '2024-01-21T15:30:00Z'
    },
    {
      name: 'YouTube Downloader',
      status: 'operational',
      uptime: '99.5%',
      responseTime: '3.2s',
      lastCheck: '2024-01-21T15:30:00Z'
    },
    {
      name: 'WebSocket Service',
      status: 'operational',
      uptime: '99.9%',
      responseTime: '8ms',
      lastCheck: '2024-01-21T15:30:00Z'
    },
    {
      name: 'Database',
      status: 'operational',
      uptime: '99.9%',
      responseTime: '5ms',
      lastCheck: '2024-01-21T15:30:00Z'
    }
  ];

  const metrics = [
    {
      title: 'Total Requests',
      value: '2.4M',
      change: '+12.5%',
      trend: 'up',
      icon: <TrendingUp className="w-5 h-5" />
    },
    {
      title: 'Active Users',
      value: '1,247',
      change: '+8.2%',
      trend: 'up',
      icon: <Users className="w-5 h-5" />
    },
    {
      title: 'Success Rate',
      value: '99.7%',
      change: '+0.3%',
      trend: 'up',
      icon: <CheckCircle2 className="w-5 h-5" />
    },
    {
      title: 'Avg Response Time',
      value: '1.2s',
      change: '-15.2%',
      trend: 'down',
      icon: <Clock className="w-5 h-5" />
    }
  ];

  const incidents = [
    {
      id: 'INC-2024-001',
      title: 'Temporary API slowdown',
      status: 'resolved',
      severity: 'minor',
      startTime: '2024-01-15T10:30:00Z',
      endTime: '2024-01-15T11:15:00Z',
      description: 'Brief performance degradation due to high traffic load'
    },
    {
      id: 'INC-2024-002',
      title: 'YouTube processing delays',
      status: 'resolved',
      severity: 'minor',
      startTime: '2024-01-10T14:20:00Z',
      endTime: '2024-01-10T16:45:00Z',
      description: 'Temporary delays in YouTube video processing due to external API rate limits'
    },
    {
      id: 'INC-2024-003',
      title: 'WebSocket connection issues',
      status: 'resolved',
      severity: 'major',
      startTime: '2024-01-05T09:00:00Z',
      endTime: '2024-01-05T12:30:00Z',
      description: 'Intermittent WebSocket disconnections affecting real-time detection'
    }
  ];

  const performanceData = [
    { time: '00:00', requests: 120, responseTime: 1.2 },
    { time: '04:00', requests: 85, responseTime: 0.9 },
    { time: '08:00', requests: 340, responseTime: 1.5 },
    { time: '12:00', requests: 520, responseTime: 1.8 },
    { time: '16:00', requests: 480, responseTime: 1.6 },
    { time: '20:00', requests: 380, responseTime: 1.4 }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-success';
      case 'degraded': return 'text-warning';
      case 'outage': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational': return <CheckCircle2 className="w-5 h-5 text-success" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-warning" />;
      case 'outage': return <WifiOff className="w-5 h-5 text-destructive" />;
      default: return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-destructive text-destructive-foreground';
      case 'major': return 'bg-orange-500 text-white';
      case 'minor': return 'bg-warning text-warning-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const refreshStatus = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLastUpdated(new Date());
    setIsRefreshing(false);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen">
      <ScrollToTop />
      {/* Hero Section */}
      <section className="py-24 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="secondary" className="neural-card mb-6 bg-primary/10 text-primary border-primary/20">
              <Globe className="w-3 h-3 mr-1" />
              Live Status
            </Badge>
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">System Status</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 neural-text">
              Real-time API health monitoring and MesoNet model performance metrics dashboard. 
              Monitor uptime, response times, and service availability.
            </p>
            <div className="flex flex-wrap gap-4 justify-center mb-12">
              <Button 
                className="neural-button" 
                onClick={refreshStatus}
                disabled={isRefreshing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? 'Refreshing...' : 'Refresh Status'}
              </Button>
              <Button variant="outline" className="neural-card neural-button" asChild>
                <Link to="/api">
                  <Activity className="w-4 h-4 mr-2" />
                  API Documentation
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Overall Status */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">System Overview</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Current system status and key performance indicators.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card text-center hover-lift">
                  <div className="flex items-center justify-center mb-3">
                    <div className="text-primary">{metric.icon}</div>
                  </div>
                  <h3 className="text-2xl font-bold mb-2 neural-text">{metric.value}</h3>
                  <p className="text-sm text-muted-foreground mb-2 neural-text">{metric.title}</p>
                  <Badge 
                    variant="outline" 
                    className={`neural-card text-xs ${
                      metric.trend === 'up' ? 'text-success' : 'text-warning'
                    }`}
                  >
                    {metric.change}
                  </Badge>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <EnhancedCard className="neural-card">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  {getStatusIcon(systemStatus.overall)}
                  <div>
                    <h3 className="text-xl font-semibold neural-text">All Systems Operational</h3>
                    <p className="text-muted-foreground neural-text">
                      Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-success neural-text">{systemStatus.uptime}</div>
                  <div className="text-sm text-muted-foreground neural-text">Uptime</div>
                </div>
              </div>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-lg font-semibold neural-text">{systemStatus.responseTime}</div>
                  <div className="text-sm text-muted-foreground neural-text">Avg Response Time</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold neural-text">0</div>
                  <div className="text-sm text-muted-foreground neural-text">Active Incidents</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold neural-text">2 days ago</div>
                  <div className="text-sm text-muted-foreground neural-text">Last Incident</div>
                </div>
              </div>
            </EnhancedCard>
          </motion.div>
        </div>
      </section>

      {/* Service Status */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Service Status</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Individual service health and performance metrics.
            </p>
          </motion.div>

          <div className="space-y-4">
            {services.map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card hover-lift">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {getStatusIcon(service.status)}
                      <div>
                        <h3 className="font-semibold neural-text">{service.name}</h3>
                        <p className="text-sm text-muted-foreground neural-text">
                          Last check: {new Date(service.lastCheck).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-sm font-semibold neural-text">{service.uptime}</div>
                        <div className="text-xs text-muted-foreground neural-text">Uptime</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold neural-text">{service.responseTime}</div>
                        <div className="text-xs text-muted-foreground neural-text">Response Time</div>
                      </div>
                      <Badge 
                        variant="outline" 
                        className={`neural-card text-xs ${getStatusColor(service.status)}`}
                      >
                        {service.status}
                      </Badge>
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Performance Metrics</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Real-time performance data and system resource utilization.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Request Volume (24h)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {performanceData.map((data, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm neural-text">{data.time}</span>
                        <div className="flex items-center gap-4">
                          <div className="w-32 bg-muted rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full" 
                              style={{ width: `${(data.requests / 600) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-semibold neural-text w-12 text-right">
                            {data.requests}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card">
                <CardHeader>
                  <CardTitle className="neural-text flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    Response Time Trend
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {performanceData.map((data, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm neural-text">{data.time}</span>
                        <div className="flex items-center gap-4">
                          <div className="w-32 bg-muted rounded-full h-2">
                            <div 
                              className="bg-accent h-2 rounded-full" 
                              style={{ width: `${(data.responseTime / 2) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-semibold neural-text w-12 text-right">
                            {data.responseTime}s
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </EnhancedCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Recent Incidents */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Recent Incidents</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Historical incident reports and resolution status.
            </p>
          </motion.div>

          <div className="space-y-4">
            {incidents.map((incident, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <EnhancedCard className="neural-card">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold neural-text">{incident.title}</h3>
                        <Badge 
                          variant="outline" 
                          className={`neural-card text-xs ${getSeverityColor(incident.severity)}`}
                        >
                          {incident.severity}
                        </Badge>
                        <Badge 
                          variant="outline" 
                          className="neural-card text-xs text-success"
                        >
                          {incident.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3 neural-text">
                        {incident.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>ID: {incident.id}</span>
                        <span>Started: {new Date(incident.startTime).toLocaleString()}</span>
                        <span>Resolved: {new Date(incident.endTime).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </EnhancedCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* System Resources */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-section font-bold mb-6 neural-text">System Resources</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto neural-text">
              Current system resource utilization and capacity metrics.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <EnhancedCard className="neural-card text-center">
                <Cpu className="w-8 h-8 mx-auto mb-4 text-primary" />
                <h3 className="font-semibold mb-2 neural-text">CPU Usage</h3>
                <div className="text-2xl font-bold text-success mb-2 neural-text">23%</div>
                <div className="w-full bg-muted rounded-full h-2 mb-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '23%' }} />
                </div>
                <p className="text-sm text-muted-foreground neural-text">Normal</p>
              </EnhancedCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <EnhancedCard className="neural-card text-center">
                <MemoryStick className="w-8 h-8 mx-auto mb-4 text-primary" />
                <h3 className="font-semibold mb-2 neural-text">Memory Usage</h3>
                <div className="text-2xl font-bold text-warning mb-2 neural-text">67%</div>
                <div className="w-full bg-muted rounded-full h-2 mb-2">
                  <div className="bg-warning h-2 rounded-full" style={{ width: '67%' }} />
                </div>
                <p className="text-sm text-muted-foreground neural-text">Moderate</p>
              </EnhancedCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <EnhancedCard className="neural-card text-center">
                <HardDrive className="w-8 h-8 mx-auto mb-4 text-primary" />
                <h3 className="font-semibold mb-2 neural-text">Storage Usage</h3>
                <div className="text-2xl font-bold text-success mb-2 neural-text">34%</div>
                <div className="w-full bg-muted rounded-full h-2 mb-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '34%' }} />
                </div>
                <p className="text-sm text-muted-foreground neural-text">Good</p>
              </EnhancedCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Activity className="w-16 h-16 mx-auto mb-8 text-primary" />
            <h2 className="text-section font-bold mb-6 neural-text">System Status Updates</h2>
            <p className="text-lg text-muted-foreground mb-8 neural-text">
              Stay informed about system status and performance. Subscribe to status updates 
              and get notified about incidents and maintenance windows.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button size="lg" className="neural-button" asChild>
                <Link to="/api">
                  <Activity className="w-4 h-4 mr-2" />
                  View API Documentation
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="neural-card neural-button" asChild>
                <Link to="/try">
                  <Zap className="w-4 h-4 mr-2" />
                  Try Live Demo
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default SystemStatus;
