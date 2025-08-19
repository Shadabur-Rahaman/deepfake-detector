'use client';

import { useState, useEffect } from 'react';
import { Brain, TrendingUp, Shield, Lightbulb, Search, Filter } from 'lucide-react';

interface AIInsight {
  id: string;
  type: 'security' | 'technical' | 'recommendation' | 'trend' | 'research';
  title: string;
  description: string;
  confidence: number;
  category: string;
  date: string;
  source: string;
  featured: boolean;
  tags: string[];
  impact: 'high' | 'medium' | 'low';
  readTime: string;
}

interface AIInsightsResponse {
  success: boolean;
  count: number;
  insights: AIInsight[];
  metadata?: {
    lastUpdated: string;
    categories: string[];
    types: string[];
    avgConfidence: number;
  };
}

export default function AIInsights() {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [metadata, setMetadata] = useState<any>(null);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async (filters?: any) => {
    try {
      setLoading(true);
      const url = '/api/ai-insights';
      const response = await fetch(url, {
        method: filters ? 'POST' : 'GET',
        headers: filters ? { 'Content-Type': 'application/json' } : {},
        body: filters ? JSON.stringify({ filters }) : undefined,
      });

      if (response.ok) {
        const data: AIInsightsResponse = await response.json();
        setInsights(data.insights);
        setMetadata(data.metadata);
      }
    } catch (error) {
      console.error('Error fetching AI insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'security': return <Shield className="w-5 h-5" />;
      case 'trend': return <TrendingUp className="w-5 h-5" />;
      case 'recommendation': return <Lightbulb className="w-5 h-5" />;
      case 'technical': return <Brain className="w-5 h-5" />;
      case 'research': return <Search className="w-5 h-5" />;
      default: return <Brain className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'security': return 'text-red-600 bg-red-100';
      case 'trend': return 'text-green-600 bg-green-100';
      case 'recommendation': return 'text-yellow-600 bg-yellow-100';
      case 'technical': return 'text-blue-600 bg-blue-100';
      case 'research': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-700 bg-red-100';
      case 'medium': return 'text-yellow-700 bg-yellow-100';
      case 'low': return 'text-green-700 bg-green-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const filteredInsights = insights.filter(insight => {
    const matchesType = selectedType === 'all' || insight.type === selectedType;
    const matchesSearch = searchTerm === '' || 
      insight.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      insight.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      insight.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesType && matchesSearch;
  });

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-64 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">AI Detection Insights</h2>
        
        {metadata && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{insights.length}</div>
              <div className="text-sm text-blue-800">Total Insights</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{metadata.avgConfidence}%</div>
              <div className="text-sm text-green-800">Avg Confidence</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{metadata.categories.length}</div>
              <div className="text-sm text-purple-800">Categories</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">Live</div>
              <div className="text-sm text-orange-800">Real-time Data</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Search insights..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="security">Security</option>
            <option value="trend">Trends</option>
            <option value="technical">Technical</option>
            <option value="research">Research</option>
            <option value="recommendation">Recommendations</option>
          </select>
        </div>
      </div>

      {/* Insights Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredInsights.map((insight) => (
          <div
            key={insight.id}
            className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow border-l-4 ${
              insight.featured ? 'border-blue-500' : 'border-gray-300'
            }`}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className={`p-2 rounded-lg ${getTypeColor(insight.type)}`}>
                  {getTypeIcon(insight.type)}
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImpactColor(insight.impact)}`}>
                    {insight.impact.toUpperCase()}
                  </span>
                  {insight.featured && (
                    <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full">
                      FEATURED
                    </span>
                  )}
                </div>
              </div>

              {/* Content */}
              <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">
                {insight.title}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {insight.description}
              </p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-4">
                {insight.tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 text-xs text-gray-600 bg-gray-100 rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between text-sm text-gray-500 border-t border-gray-100 pt-4">
                <div>
                  <div className="font-medium">{insight.source}</div>
                  <div>{insight.readTime}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-blue-600">{insight.confidence}%</div>
                  <div>Confidence</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredInsights.length === 0 && !loading && (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No insights found</h3>
          <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedType('all');
            }}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
