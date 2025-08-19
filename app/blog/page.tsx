"use client";

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Calendar, 
  Clock, 
  ArrowRight, 
  ExternalLink,
  Brain,
  RefreshCw,
  Sparkles,
  Globe,
  BookOpen,
  Zap,
  TrendingUp,
  Activity,
  Rss
} from 'lucide-react';

interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  category: string;
  date: string;
  readTime: string;
  image: string;
  aiInsight: string;
  featured: boolean;
  source: string;
  url: string;
  author?: string;
  timestamp?: number;
}

export default function Blog() {
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [isRealTimeFetching, setIsRealTimeFetching] = useState(false);
  const [fetchCount, setFetchCount] = useState(0);
  const [lastFetchTime, setLastFetchTime] = useState<Date | null>(null);
  const [streamingPosts, setStreamingPosts] = useState<BlogPost[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Real-time dynamic Medium blog fetching with timestamp-based uniqueness
  const fetchMediumBlogsRealTime = async (): Promise<BlogPost[]> => {
    try {
      const mediumSources = [
        'towardsdatascience',
        'towardsai', 
        'ai-in-plain-english',
        'syncedreview',
        'the-ai-journal',
        'artificial-intelligence'
      ];
      
      const allBlogs: BlogPost[] = [];
      const currentTime = Date.now();
      
      for (const source of mediumSources) {
        try {
          // Add random cache-busting parameter to get fresh content
          const cacheBreaker = `${currentTime}-${Math.random().toString(36).substr(2, 9)}`;
          const response = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/${source}&count=10&timestamp=${cacheBreaker}`);
          
          if (response.ok) {
            const data = await response.json();
            const blogs = data.items?.slice(0, 3).map((item: any, index: number) => ({
              id: `medium-${source}-${currentTime}-${index}`,
              title: item.title || 'Untitled',
              excerpt: item.description?.replace(/<[^>]*>/g, '').substring(0, 200) + '...' || 'No description available',
              category: 'Technology Deep Dive',
              date: new Date(item.pubDate).toLocaleDateString(),
              readTime: `${Math.ceil((item.description?.length || 1000) / 1000)} min read`,
              image: item.thumbnail || `https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=250&fit=crop&t=${currentTime}`,
              aiInsight: `🔥 FRESH: This ${source} article explores cutting-edge AI concepts. Fetched at ${new Date().toLocaleTimeString()}`,
              featured: index === 0,
              source: `Medium - ${source}`,
              url: item.link || '#',
              author: item.author || 'AI Researcher',
              timestamp: currentTime
            })) || [];
            
            allBlogs.push(...blogs);
          }
        } catch (error) {
          console.error(`Error fetching from ${source}:`, error);
        }
        
        // Add small delay between sources for streaming effect
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      return allBlogs;
    } catch (error) {
      console.error('Error fetching Medium blogs:', error);
      return [];
    }
  };

  // Dynamic AI News with real-time generation
  const fetchAINewsDynamic = async (): Promise<BlogPost[]> => {
    const currentTime = Date.now();
    const aiTopics = [
      'AI Safety Research Breakthrough',
      'GPT-5 Development Updates', 
      'Quantum AI Computing Advances',
      'Autonomous AI Agents Revolution',
      'Neural Network Architecture Innovation',
      'AI Ethics Policy Changes',
      'Machine Learning Democratization',
      'AI in Healthcare Breakthroughs'
    ];
    
    const randomTopic = aiTopics[Math.floor(Math.random() * aiTopics.length)];
    const timeString = new Date().toLocaleTimeString();
    
    return [
      {
        id: `ai-news-${currentTime}`,
        title: `🚀 LIVE: ${randomTopic} - ${timeString}`,
        excerpt: `Breaking: Latest developments in ${randomTopic.toLowerCase()} just announced. Real-time updates from the AI research community.`,
        category: 'Breaking AI News',
        date: new Date().toLocaleDateString(),
        readTime: '3 min read',
        image: `https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=250&fit=crop&t=${currentTime}`,
        aiInsight: `⚡ REAL-TIME: This breaking news could impact the future of AI development. Last updated: ${timeString}`,
        featured: true,
        source: 'AI Live Feed',
        url: 'https://www.anthropic.com/research',
        author: 'AI News Bot',
        timestamp: currentTime
      }
    ];
  };

  // Stream posts one by one for dramatic effect
  const streamPostsOneByOne = async (posts: BlogPost[]) => {
    setStreamingPosts([]);
    
    for (let i = 0; i < posts.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800)); // Delay between each post
      setStreamingPosts(prev => [...prev, posts[i]]);
    }
  };

  // Enhanced fetch with real-time streaming
  const fetchAllBlogsRealTime = async () => {
    setLoading(true);
    setFetchCount(prev => prev + 1);
    setLastFetchTime(new Date());
    
    try {
      // Fetch from multiple sources with real-time data
      const [mediumBlogs, aiNews] = await Promise.all([
        fetchMediumBlogsRealTime(),
        fetchAINewsDynamic()
      ]);

      const allBlogs = [...mediumBlogs, ...aiNews];
      
      // Sort by timestamp for freshest content first
      allBlogs.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
      
      // Stream posts one by one for dramatic effect
      await streamPostsOneByOne(allBlogs);
      setBlogPosts(allBlogs);
      
    } catch (error) {
      console.error('Error fetching real-time blogs:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 30 seconds when real-time mode is enabled
  const toggleRealTimeMode = () => {
    if (isRealTimeFetching) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setIsRealTimeFetching(false);
    } else {
      setIsRealTimeFetching(true);
      intervalRef.current = setInterval(fetchAllBlogsRealTime, 30000); // Fetch every 30 seconds
    }
  };

  useEffect(() => {
    fetchAllBlogsRealTime();
    
    // Cleanup interval on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const categories = ["All", "Technology Deep Dive", "Breaking AI News", "Research", "Technical Implementation", "Ethics in AI", "AI Community"];

  const filteredPosts = streamingPosts.filter(post => {
    const matchesCategory = selectedCategory === "All" || post.category === selectedCategory;
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      "Technology Deep Dive": "bg-blue-100 text-blue-800 border-blue-200",
      "Breaking AI News": "bg-red-100 text-red-800 border-red-200",
      "Research": "bg-purple-100 text-purple-800 border-purple-200", 
      "Technical Implementation": "bg-green-100 text-green-800 border-green-200",
      "Ethics in AI": "bg-orange-100 text-orange-800 border-orange-200",
      "AI Community": "bg-pink-100 text-pink-800 border-pink-200"
    };
    return colors[category] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 relative">
      {/* Real-time indicator */}
      {isRealTimeFetching && (
        <div className="fixed top-20 right-4 z-50 bg-green-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center space-x-2 animate-pulse">
          <Activity className="h-4 w-4" />
          <span className="text-sm font-medium">LIVE</span>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        {/* Enhanced Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-6 mb-16"
        >
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
            <Rss className="h-4 w-4 text-blue-600 mr-2" />
            <span className="text-blue-800 text-sm font-medium">iFake Insights - Real-Time AI Feed</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
            🔴 Live AI Research Feed
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Dynamic real-time blog aggregation with fresh content on every fetch. Get the latest AI insights streamed live!
          </p>

          {/* Enhanced Control Panel */}
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mt-8">
            <Button 
              onClick={fetchAllBlogsRealTime}
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl transition-all duration-300 px-8 py-3"
            >
              {loading ? (
                <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5 mr-2" />
              )}
              {loading ? 'Fetching Fresh Content...' : 'Fetch Latest Blogs'}
            </Button>

            <Button 
              onClick={toggleRealTimeMode}
              variant={isRealTimeFetching ? "destructive" : "outline"}
              className="px-6 py-3"
            >
              {isRealTimeFetching ? (
                <>
                  <Activity className="h-4 w-4 mr-2 animate-pulse" />
                  Stop Live Mode
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Enable Live Mode
                </>
              )}
            </Button>
          </div>

          {/* Fetch Statistics */}
          <div className="flex justify-center items-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Zap className="h-4 w-4 text-blue-500" />
              <span>Fetches: {fetchCount}</span>
            </div>
            {lastFetchTime && (
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4 text-green-500" />
                <span>Last: {lastFetchTime.toLocaleTimeString()}</span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Search and Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-12"
        >
          <Card className="border-gray-200 bg-white shadow-sm">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search live AI articles and research..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-12"
                  />
                </div>
                <div className="flex gap-2 flex-wrap">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant={selectedCategory === category ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCategory(category)}
                      className={selectedCategory === category ? 
                        "bg-blue-600 text-white" : 
                        "border-gray-300 text-gray-600 hover:bg-gray-50"
                      }
                    >
                      {category}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Live Feed Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900 flex items-center">
              🔴 Live AI Feed
              {isRealTimeFetching && <span className="ml-2 text-red-500 animate-pulse">●</span>}
            </h2>
            <Badge className="bg-green-100 text-green-800 border-green-200">
              {filteredPosts.length} Live Articles
            </Badge>
          </div>
        </motion.div>

        {/* Dynamic Blog Posts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <AnimatePresence mode="popLayout">
            {loading ? (
              // Enhanced loading animations
              [...Array(6)].map((_, i) => (
                <motion.div
                  key={`skeleton-${i}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: i * 0.1 }}
                >
                  <Card className="border-gray-200 bg-white shadow-sm animate-pulse">
                    <div className="h-48 bg-gradient-to-r from-blue-200 to-purple-200 rounded-t-lg animate-pulse"></div>
                    <CardContent className="p-6">
                      <div className="h-4 bg-gray-200 rounded mb-2 w-3/4 animate-pulse"></div>
                      <div className="h-6 bg-gray-200 rounded mb-4 animate-pulse"></div>
                      <div className="h-16 bg-gray-200 rounded mb-4 animate-pulse"></div>
                      <div className="h-8 bg-gray-100 rounded animate-pulse"></div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            ) : filteredPosts.length > 0 ? (
              filteredPosts.map((post, index) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 30, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -30, scale: 0.9 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  layout
                >
                  <Card className="border-gray-200 bg-white shadow-sm hover:shadow-lg transition-all duration-300 h-full group relative overflow-hidden">
                    {/* Streaming indicator */}
                    <div className="absolute top-2 left-2 w-3 h-3 bg-red-500 rounded-full animate-pulse z-10"></div>
                    
                    <div className="relative overflow-hidden rounded-t-lg">
                      <img 
                        src={post.image} 
                        alt={post.title}
                        className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      {post.featured && (
                        <Badge className="absolute top-3 right-3 bg-gradient-to-r from-red-500 to-pink-500 text-white animate-pulse">
                          🔴 LIVE
                        </Badge>
                      )}
                      <Badge className="absolute bottom-3 right-3 bg-white/90 text-gray-800">
                        {post.source}
                      </Badge>
                    </div>
                    <CardContent className="p-6 flex flex-col flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Badge variant="outline" className={getCategoryColor(post.category)}>
                          {post.category}
                        </Badge>
                        <div className="flex items-center text-gray-500 text-sm">
                          <Calendar className="h-3 w-3 mr-1" />
                          {post.date}
                        </div>
                      </div>
                      
                      <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      
                      <p className="text-gray-600 mb-4 flex-1 line-clamp-3">
                        {post.excerpt}
                      </p>
                      
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-blue-500 p-3 mb-4">
                        <div className="flex items-start space-x-2">
                          <Brain className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs font-semibold text-blue-800 mb-1">🤖 AI Live Insight</p>
                            <p className="text-sm text-blue-700">{post.aiInsight}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center text-gray-500 text-sm">
                          <Clock className="h-3 w-3 mr-1" />
                          {post.readTime}
                        </div>
                        <Button 
                          asChild
                          variant="ghost" 
                          size="sm" 
                          className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                        >
                          <a href={post.url} target="_blank" rel="noopener noreferrer">
                            Read Live <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <Globe className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No live articles found</h3>
                <p className="text-gray-600 mb-6">Try fetching fresh content or adjust your filters</p>
                <Button onClick={fetchAllBlogsRealTime} className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Fetch Live Content
                </Button>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
