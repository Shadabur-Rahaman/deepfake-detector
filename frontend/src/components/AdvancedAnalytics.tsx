/**
 * Advanced Analytics Dashboard Component
 * =====================================
 * 
 * Comprehensive analytics dashboard with:
 * - Real-time performance metrics
 * - ML-powered insights
 * - Predictive analytics
 * - Trend analysis
 * - User behavior analytics
 * - System health monitoring
 * - Custom reporting
 * 
 * Author: Deepfake Detection System
 * Version: 3.0.0
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert,
  Modal,
  TextInput,
  Switch,
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
  ProgressChart,
} from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Card, Title, Paragraph, Button, Chip, Badge } from 'react-native-paper';
import { LinearGradient } from 'react-native-linear-gradient';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

interface AnalyticsData {
  timestamp: number;
  totalDetections: number;
  deepfakeDetections: number;
  realDetections: number;
  averageConfidence: number;
  processingTime: number;
  systemLoad: number;
  userSessions: number;
  errorRate: number;
}

interface PredictiveInsights {
  trend: 'increasing' | 'decreasing' | 'stable';
  prediction: string;
  confidence: number;
  recommendations: string[];
}

interface UserBehavior {
  sessionDuration: number;
  detectionFrequency: number;
  preferredMode: string;
  accuracyRate: number;
  engagementScore: number;
}

const AdvancedAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [predictiveInsights, setPredictiveInsights] = useState<PredictiveInsights | null>(null);
  const [userBehavior, setUserBehavior] = useState<UserBehavior | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [isRealTime, setIsRealTime] = useState(true);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['detections', 'accuracy', 'performance']);
  const [showCustomReport, setShowCustomReport] = useState(false);
  const [customReportConfig, setCustomReportConfig] = useState({
    title: '',
    metrics: [] as string[],
    timeRange: '24h',
    format: 'pdf' as 'pdf' | 'excel' | 'json',
  });

  const fadeAnim = useSharedValue(0);
  const scaleAnim = useSharedValue(0.8);

  useEffect(() => {
    loadAnalyticsData();
    loadPredictiveInsights();
    loadUserBehavior();
    
    // Start real-time updates
    if (isRealTime) {
      const interval = setInterval(updateRealTimeData, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedTimeRange, isRealTime]);

  useEffect(() => {
    // Animate on mount
    fadeAnim.value = withTiming(1, { duration: 500 });
    scaleAnim.value = withSpring(1, { damping: 15 });
  }, []);

  const loadAnalyticsData = async () => {
    try {
      // Simulate API call
      const mockData = generateMockAnalyticsData(selectedTimeRange);
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    }
  };

  const loadPredictiveInsights = async () => {
    try {
      // Simulate ML-powered insights
      const insights: PredictiveInsights = {
        trend: 'increasing',
        prediction: 'Deepfake detection rate will increase by 15% in the next 24 hours',
        confidence: 0.87,
        recommendations: [
          'Increase server capacity for peak hours',
          'Optimize detection models for better accuracy',
          'Implement additional security measures',
        ],
      };
      setPredictiveInsights(insights);
    } catch (error) {
      console.error('Failed to load predictive insights:', error);
    }
  };

  const loadUserBehavior = async () => {
    try {
      // Simulate user behavior analysis
      const behavior: UserBehavior = {
        sessionDuration: 45.2,
        detectionFrequency: 12.5,
        preferredMode: 'balanced',
        accuracyRate: 0.94,
        engagementScore: 0.87,
      };
      setUserBehavior(behavior);
    } catch (error) {
      console.error('Failed to load user behavior:', error);
    }
  };

  const updateRealTimeData = () => {
    if (isRealTime) {
      loadAnalyticsData();
    }
  };

  const generateMockAnalyticsData = (timeRange: string): AnalyticsData[] => {
    const dataPoints = timeRange === '1h' ? 12 : timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : 30;
    const data: AnalyticsData[] = [];
    
    for (let i = 0; i < dataPoints; i++) {
      data.push({
        timestamp: Date.now() - (dataPoints - i) * (timeRange === '1h' ? 5 * 60 * 1000 : timeRange === '24h' ? 60 * 60 * 1000 : timeRange === '7d' ? 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000),
        totalDetections: Math.floor(Math.random() * 1000) + 500,
        deepfakeDetections: Math.floor(Math.random() * 200) + 50,
        realDetections: Math.floor(Math.random() * 800) + 400,
        averageConfidence: Math.random() * 0.3 + 0.7,
        processingTime: Math.random() * 500 + 100,
        systemLoad: Math.random() * 0.4 + 0.3,
        userSessions: Math.floor(Math.random() * 100) + 50,
        errorRate: Math.random() * 0.05 + 0.01,
      });
    }
    
    return data;
  };

  const getChartData = () => {
    const labels = analyticsData.map((_, index) => {
      if (selectedTimeRange === '1h') return `${index * 5}m`;
      if (selectedTimeRange === '24h') return `${index}h`;
      if (selectedTimeRange === '7d') return `Day ${index + 1}`;
      return `Day ${index + 1}`;
    });

    return {
      labels,
      datasets: [
        {
          data: analyticsData.map(d => d.totalDetections),
          color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
          strokeWidth: 2,
        },
        {
          data: analyticsData.map(d => d.deepfakeDetections),
          color: (opacity = 1) => `rgba(244, 67, 54, ${opacity})`,
          strokeWidth: 2,
        },
      ],
    };
  };

  const getPerformanceData = () => {
    return {
      labels: ['CPU', 'Memory', 'GPU', 'Network'],
      data: [
        analyticsData[analyticsData.length - 1]?.systemLoad || 0.5,
        Math.random() * 0.3 + 0.4,
        Math.random() * 0.2 + 0.3,
        Math.random() * 0.1 + 0.2,
      ],
    };
  };

  const getAccuracyData = () => {
    const totalDetections = analyticsData.reduce((sum, d) => sum + d.totalDetections, 0);
    const correctDetections = analyticsData.reduce((sum, d) => sum + d.realDetections, 0);
    const accuracy = totalDetections > 0 ? correctDetections / totalDetections : 0;
    
    return [
      { name: 'Correct', population: accuracy, color: '#4CAF50', legendFontColor: '#7F7F7F', legendFontSize: 12 },
      { name: 'Incorrect', population: 1 - accuracy, color: '#F44336', legendFontColor: '#7F7F7F', legendFontSize: 12 },
    ];
  };

  const generateCustomReport = async () => {
    try {
      // Simulate report generation
      Alert.alert('Report Generated', 'Your custom report has been generated and saved.');
      setShowCustomReport(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate report. Please try again.');
    }
  };

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: fadeAnim.value,
    transform: [{ scale: scaleAnim.value }],
  }));

  return (
    <Animated.View style={[styles.container, animatedStyle]}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Advanced Analytics</Text>
          <View style={styles.headerControls}>
            <TouchableOpacity
              style={[styles.timeRangeButton, selectedTimeRange === '1h' && styles.timeRangeButtonActive]}
              onPress={() => setSelectedTimeRange('1h')}
            >
              <Text style={styles.timeRangeText}>1H</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.timeRangeButton, selectedTimeRange === '24h' && styles.timeRangeButtonActive]}
              onPress={() => setSelectedTimeRange('24h')}
            >
              <Text style={styles.timeRangeText}>24H</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.timeRangeButton, selectedTimeRange === '7d' && styles.timeRangeButtonActive]}
              onPress={() => setSelectedTimeRange('7d')}
            >
              <Text style={styles.timeRangeText}>7D</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.timeRangeButton, selectedTimeRange === '30d' && styles.timeRangeButtonActive]}
              onPress={() => setSelectedTimeRange('30d')}
            >
              <Text style={styles.timeRangeText}>30D</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Real-time Toggle */}
        <View style={styles.realTimeToggle}>
          <Text style={styles.toggleLabel}>Real-time Updates</Text>
          <Switch
            value={isRealTime}
            onValueChange={setIsRealTime}
            trackColor={{ false: '#767577', true: '#81b0ff' }}
            thumbColor={isRealTime ? '#2196F3' : '#f4f3f4'}
          />
        </View>

        {/* Key Metrics */}
        <View style={styles.metricsGrid}>
          <Card style={styles.metricCard}>
            <Card.Content>
              <Title style={styles.metricTitle}>Total Detections</Title>
              <Text style={styles.metricValue}>
                {analyticsData.reduce((sum, d) => sum + d.totalDetections, 0).toLocaleString()}
              </Text>
              <Text style={styles.metricChange}>+12.5% from last period</Text>
            </Card.Content>
          </Card>

          <Card style={styles.metricCard}>
            <Card.Content>
              <Title style={styles.metricTitle}>Deepfake Rate</Title>
              <Text style={styles.metricValue}>
                {((analyticsData.reduce((sum, d) => sum + d.deepfakeDetections, 0) / 
                  analyticsData.reduce((sum, d) => sum + d.totalDetections, 0)) * 100).toFixed(1)}%
              </Text>
              <Text style={styles.metricChange}>+2.1% from last period</Text>
            </Card.Content>
          </Card>

          <Card style={styles.metricCard}>
            <Card.Content>
              <Title style={styles.metricTitle}>Avg Confidence</Title>
              <Text style={styles.metricValue}>
                {(analyticsData.reduce((sum, d) => sum + d.averageConfidence, 0) / analyticsData.length * 100).toFixed(1)}%
              </Text>
              <Text style={styles.metricChange}>+0.8% from last period</Text>
            </Card.Content>
          </Card>

          <Card style={styles.metricCard}>
            <Card.Content>
              <Title style={styles.metricTitle}>Processing Time</Title>
              <Text style={styles.metricValue}>
                {(analyticsData.reduce((sum, d) => sum + d.processingTime, 0) / analyticsData.length).toFixed(0)}ms
              </Text>
              <Text style={styles.metricChange}>-15ms from last period</Text>
            </Card.Content>
          </Card>
        </View>

        {/* Detection Trends Chart */}
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title style={styles.chartTitle}>Detection Trends</Title>
            <LineChart
              data={getChartData()}
              width={width - 40}
              height={220}
              chartConfig={{
                backgroundColor: '#ffffff',
                backgroundGradientFrom: '#ffffff',
                backgroundGradientTo: '#ffffff',
                decimalPlaces: 0,
                color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                style: {
                  borderRadius: 16,
                },
                propsForDots: {
                  r: '6',
                  strokeWidth: '2',
                  stroke: '#2196F3',
                },
              }}
              bezier
              style={styles.chart}
            />
          </Card.Content>
        </Card>

        {/* Performance Metrics */}
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title style={styles.chartTitle}>System Performance</Title>
            <ProgressChart
              data={getPerformanceData()}
              width={width - 40}
              height={220}
              strokeWidth={16}
              radius={32}
              chartConfig={{
                backgroundGradientFrom: '#ffffff',
                backgroundGradientTo: '#ffffff',
                color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
              }}
              hideLegend={false}
            />
          </Card.Content>
        </Card>

        {/* Accuracy Distribution */}
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title style={styles.chartTitle}>Detection Accuracy</Title>
            <PieChart
              data={getAccuracyData()}
              width={width - 40}
              height={220}
              chartConfig={{
                color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              }}
              accessor="population"
              backgroundColor="transparent"
              paddingLeft="15"
              center={[10, 10]}
              absolute
            />
          </Card.Content>
        </Card>

        {/* Predictive Insights */}
        {predictiveInsights && (
          <Card style={styles.insightsCard}>
            <Card.Content>
              <Title style={styles.insightsTitle}>Predictive Insights</Title>
              <View style={styles.insightItem}>
                <Icon name="trending-up" size={24} color="#4CAF50" />
                <Text style={styles.insightText}>{predictiveInsights.prediction}</Text>
              </View>
              <View style={styles.insightItem}>
                <Icon name="lightbulb" size={24} color="#FF9800" />
                <Text style={styles.insightText}>Confidence: {Math.round(predictiveInsights.confidence * 100)}%</Text>
              </View>
              <Title style={styles.recommendationsTitle}>Recommendations</Title>
              {predictiveInsights.recommendations.map((rec, index) => (
                <View key={index} style={styles.recommendationItem}>
                  <Icon name="check-circle" size={16} color="#4CAF50" />
                  <Text style={styles.recommendationText}>{rec}</Text>
                </View>
              ))}
            </Card.Content>
          </Card>
        )}

        {/* User Behavior Analytics */}
        {userBehavior && (
          <Card style={styles.behaviorCard}>
            <Card.Content>
              <Title style={styles.behaviorTitle}>User Behavior Analytics</Title>
              <View style={styles.behaviorMetrics}>
                <View style={styles.behaviorMetric}>
                  <Text style={styles.behaviorLabel}>Session Duration</Text>
                  <Text style={styles.behaviorValue}>{userBehavior.sessionDuration.toFixed(1)} min</Text>
                </View>
                <View style={styles.behaviorMetric}>
                  <Text style={styles.behaviorLabel}>Detection Frequency</Text>
                  <Text style={styles.behaviorValue}>{userBehavior.detectionFrequency.toFixed(1)}/hour</Text>
                </View>
                <View style={styles.behaviorMetric}>
                  <Text style={styles.behaviorLabel}>Preferred Mode</Text>
                  <Chip style={styles.modeChip}>{userBehavior.preferredMode}</Chip>
                </View>
                <View style={styles.behaviorMetric}>
                  <Text style={styles.behaviorLabel}>Accuracy Rate</Text>
                  <Text style={styles.behaviorValue}>{(userBehavior.accuracyRate * 100).toFixed(1)}%</Text>
                </View>
                <View style={styles.behaviorMetric}>
                  <Text style={styles.behaviorLabel}>Engagement Score</Text>
                  <Text style={styles.behaviorValue}>{(userBehavior.engagementScore * 100).toFixed(1)}%</Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

        {/* Custom Report Button */}
        <TouchableOpacity
          style={styles.customReportButton}
          onPress={() => setShowCustomReport(true)}
        >
          <LinearGradient
            colors={['#2196F3', '#1976D2']}
            style={styles.customReportGradient}
          >
            <Icon name="assessment" size={24} color="white" />
            <Text style={styles.customReportText}>Generate Custom Report</Text>
          </LinearGradient>
        </TouchableOpacity>
      </ScrollView>

      {/* Custom Report Modal */}
      <Modal
        visible={showCustomReport}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowCustomReport(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Custom Report Configuration</Text>
            
            <TextInput
              style={styles.textInput}
              placeholder="Report Title"
              value={customReportConfig.title}
              onChangeText={(text) => setCustomReportConfig({ ...customReportConfig, title: text })}
            />
            
            <Text style={styles.sectionTitle}>Select Metrics</Text>
            {['detections', 'accuracy', 'performance', 'trends', 'predictions'].map((metric) => (
              <TouchableOpacity
                key={metric}
                style={styles.metricOption}
                onPress={() => {
                  const newMetrics = customReportConfig.metrics.includes(metric)
                    ? customReportConfig.metrics.filter(m => m !== metric)
                    : [...customReportConfig.metrics, metric];
                  setCustomReportConfig({ ...customReportConfig, metrics: newMetrics });
                }}
              >
                <Icon
                  name={customReportConfig.metrics.includes(metric) ? 'check-box' : 'check-box-outline-blank'}
                  size={24}
                  color={customReportConfig.metrics.includes(metric) ? '#2196F3' : '#666'}
                />
                <Text style={styles.metricOptionText}>{metric.charAt(0).toUpperCase() + metric.slice(1)}</Text>
              </TouchableOpacity>
            ))}
            
            <View style={styles.modalButtons}>
              <Button
                mode="outlined"
                onPress={() => setShowCustomReport(false)}
                style={styles.modalButton}
              >
                Cancel
              </Button>
              <Button
                mode="contained"
                onPress={generateCustomReport}
                style={styles.modalButton}
              >
                Generate Report
              </Button>
            </View>
          </View>
        </View>
      </Modal>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  headerControls: {
    flexDirection: 'row',
    gap: 8,
  },
  timeRangeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  timeRangeButtonActive: {
    backgroundColor: '#2196F3',
  },
  timeRangeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
  },
  realTimeToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    marginTop: 1,
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 20,
    gap: 10,
  },
  metricCard: {
    width: (width - 50) / 2,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  metricTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  metricChange: {
    fontSize: 12,
    color: '#4CAF50',
  },
  chartCard: {
    margin: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  insightsCard: {
    margin: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  insightsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  insightItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  insightText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
    flex: 1,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
    marginBottom: 12,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
  behaviorCard: {
    margin: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  behaviorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  behaviorMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  behaviorMetric: {
    width: (width - 80) / 2,
    alignItems: 'center',
  },
  behaviorLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  behaviorValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  modeChip: {
    backgroundColor: '#E3F2FD',
  },
  customReportButton: {
    margin: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  customReportGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
  },
  customReportText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    width: width - 40,
    maxHeight: height * 0.8,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    padding: 12,
    marginBottom: 20,
    fontSize: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  metricOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  metricOptionText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    marginHorizontal: 8,
  },
});

export default AdvancedAnalytics;
