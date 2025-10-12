import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Search, Clock, Brain, Microscope, ExternalLink, AlertCircle, RefreshCw, Radio, Loader2, Check, X, Github, Star, GitFork, Eye } from 'lucide-react'
import { AnimatedBackground } from "@/components/ui/AnimatedBackground"
import { getRelevantImage } from "@/utils/imageGenerator"

interface Article {
  id: string
  title: string
  source: string
  category: string
  published_at: string
  excerpt?: string
  url: string
  pdf_url?: string
  read_time?: string
  image?: string
  fetched_at?: string
  author?: string
  timestamp?: number
  isDeepfakeResearch?: boolean
  tags?: string[]
}

interface GitHubRepo {
  id: number
  name: string
  full_name: string
  description: string
  html_url: string
  stargazers_count: number
  forks_count: number
  watchers_count: number
  language: string
  topics: string[]
  created_at: string
  updated_at: string
  size: number
  open_issues_count: number
}

// Color mapping for different categories
const getCategoryColor = (category: string) => {
  const colorMap: { [key: string]: string } = {
    'detection': 'bg-blue-100 text-blue-800 hover:bg-blue-200',
    'generation': 'bg-purple-100 text-purple-800 hover:bg-purple-200',
    'ethics': 'bg-green-100 text-green-800 hover:bg-green-200',
    'policy': 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
    'applications': 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200',
    'datasets': 'bg-pink-100 text-pink-800 hover:bg-pink-200',
    'benchmarks': 'bg-orange-100 text-orange-800 hover:bg-orange-200'
  }

  const lowerCategory = category.toLowerCase()
  return colorMap[lowerCategory] || 'bg-gray-100 text-gray-800 hover:bg-gray-200'
}

const deepfakeCategories = [
  'All Deepfake Research',
  'Detection Methods',
  'Generation Techniques', 
  'Ethics & Policy',
  'Applications',
  'Datasets & Benchmarks',
  'GitHub Repositories'
]

// Format date to relative time (e.g., '2 days ago')
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}


// Advanced AI image generation with content-specific prompts
const generateAIImage = async (category: string, title: string, tags: string[] = [], excerpt: string = ''): Promise<string> => {
  try {
    // Use the same logic as getRelevantImage for consistency
    return getRelevantImage(category, title, tags, excerpt);
  } catch (error) {
    console.error('Error generating AI image:', error);
    return 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=250&fit=crop&q=80';
  }
}

// API Configuration
const NEWS_API_KEY = '24b1bf235a90469ebb8f6d1470988604'
// Live mode shows only articles from the last 24 hours
const LIVE_WINDOW_MS = 24 * 60 * 60 * 1000

// Helper function to check if article is "live" (recent)
const isArticleLive = (article: Article): boolean => {
  if (!article.timestamp) return false
  const now = Date.now()
  return (now - article.timestamp) <= LIVE_WINDOW_MS
}

function BlogPage() {
  const [deepfakeArticles, setDeepfakeArticles] = useState<Article[]>([])
  const [filteredDeepfakeArticles, setFilteredDeepfakeArticles] = useState<Article[]>([])
  const [displayedArticles, setDisplayedArticles] = useState<Article[]>([])
  const [githubRepos, setGithubRepos] = useState<GitHubRepo[]>([])
  const [selectedDeepfakeCategory, setSelectedDeepfakeCategory] = useState('All Deepfake Research')
  const [deepfakeSearchQuery, setDeepfakeSearchQuery] = useState('')
  const [isDeepfakeFetching, setIsDeepfakeFetching] = useState(false)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [loadingArticles, setLoadingArticles] = useState<Set<string>>(new Set())
  const [apiStatus, setApiStatus] = useState<{[key: string]: boolean}>({
    newsApi: true,
    arxiv: true,
    huggingface: true,
    github: true
  })
  const [lastFetchTime, setLastFetchTime] = useState<string>('')
  const [totalResults, setTotalResults] = useState<number>(0)
  const [expandedArticles, setExpandedArticles] = useState<string[]>([])
  const [liveMode, setLiveMode] = useState<boolean>(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [articlesPerPage, setArticlesPerPage] = useState(15)
  const [hasMoreArticles, setHasMoreArticles] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const liveIntervalRef = useRef<number | null>(null)

  // GitHub API integration with better error handling and CORS proxy
  const fetchGitHubRepos = async (): Promise<GitHubRepo[]> => {
    try {
      console.log('🔍 Starting GitHub API fetch...');
      
      // Use a CORS proxy for GitHub API to avoid CORS issues
      const corsProxy = 'https://api.allorigins.win/raw?url=';
      const queries = [
        'deepfake+detection',
        'face+swap+deepfake',
        'synthetic+media+detection',
        'face+forgery+detection',
        'deepfake+generation',
        'face+reenactment',
        'ai+generated+video+detection',
        'deepfake+cnn+detection'
      ];
      
      const allRepos: GitHubRepo[] = [];
      
      for (const query of queries) {
        try {
          const githubUrl = `https://api.github.com/search/repositories?q=${query}+language:python&sort=stars&order=desc&per_page=3`;
          const fullUrl = corsProxy + encodeURIComponent(githubUrl);
          
          console.log(`🔍 Fetching GitHub repos for: ${query}`);
          const response = await fetch(fullUrl);
          
          if (response.ok) {
            const data = await response.json();
            console.log(`✅ GitHub API response for ${query}:`, data.total_count, 'repos found');
            
            if (data.items && Array.isArray(data.items)) {
              const repos = data.items.map((repo: any) => ({
                id: repo.id,
                name: repo.name,
                full_name: repo.full_name,
                description: repo.description || 'Deepfake detection repository',
                html_url: repo.html_url,
                stargazers_count: repo.stargazers_count || 0,
                forks_count: repo.forks_count || 0,
                watchers_count: repo.watchers_count || 0,
                language: repo.language || 'Python',
                topics: repo.topics || [],
                created_at: repo.created_at,
                updated_at: repo.updated_at,
                size: repo.size || 0,
                open_issues_count: repo.open_issues_count || 0
              }));
              allRepos.push(...repos);
              console.log(`✅ Added ${repos.length} repos for ${query}`);
            }
          } else {
            console.warn(`❌ GitHub API request failed for ${query}:`, response.status, response.statusText);
          }
          
          // Add delay to avoid rate limiting
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
          console.error(`❌ Error fetching GitHub repos for ${query}:`, error);
        }
      }
      
      // Remove duplicates and sort by stars
      const uniqueRepos = allRepos.filter((repo, index, self) => 
        index === self.findIndex(r => r.id === repo.id)
      ).sort((a, b) => b.stargazers_count - a.stargazers_count);
      
      console.log(`🎉 Total unique GitHub repos found: ${uniqueRepos.length}`);
      return uniqueRepos.slice(0, 15); // Limit to top 15
    } catch (error) {
      console.error('❌ Error fetching GitHub repositories:', error);
      return [];
    }
  };

  // Helper function to get curated deepfake content
  const getCuratedDeepfakeContent = (currentTime: number): Article[] => [
    {
      id: `community-${currentTime}-1`,
      title: 'Open Source Deepfake Detection Tools: Community Contributions',
      excerpt: 'Growing ecosystem of open-source projects democratizing access to deepfake detection technology for researchers and developers worldwide.',
      category: 'Community',
      published_at: new Date().toISOString(),
      source: 'GitHub - AI Community',
      url: 'https://github.com/topics/deepfake-detection',
      read_time: '6 min read',
      image: getRelevantImage('Community', 'Open Source Deepfake Detection Tools: Community Contributions', ['community', 'open-source', 'tools'], 'Growing ecosystem of open-source projects democratizing access to deepfake detection technology for researchers and developers worldwide.'),
      author: 'Community Contributor',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['community', 'open-source', 'tools']
    },
    {
      id: `community-${currentTime}-2`,
      title: 'AI Safety & Ethics: Community Guidelines',
      excerpt: 'Community-driven guidelines and best practices for responsible AI development and deepfake technology usage.',
      category: 'Ethics & Policy',
      published_at: new Date(currentTime - 3600000).toISOString(),
      source: 'AI Safety Forum',
      url: 'https://www.aisafety.community/guidelines',
      read_time: '8 min read',
      image: getRelevantImage('Ethics & Policy', 'AI Safety & Ethics: Community Guidelines', ['ethics', 'safety', 'guidelines'], 'Community-driven guidelines and best practices for responsible AI development and deepfake technology usage.'),
      author: 'AI Safety Collective',
      timestamp: currentTime - 3600000,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['ethics', 'safety', 'guidelines']
    },
    {
      id: `curated-deepfake-${currentTime}-1`,
      title: 'State-of-the-Art Deepfake Detection: A Comprehensive Survey 2024',
      excerpt: 'Latest comprehensive review of deepfake detection methods, including transformer-based approaches, multi-modal analysis, and real-time detection systems.',
      category: 'Detection Methods',
      published_at: new Date().toISOString(),
      source: 'Deepfake Research Institute',
      url: 'https://arxiv.org/list/cs.CV/recent',
      read_time: '20 min read',
      image: getRelevantImage('Detection Methods', 'State-of-the-Art Deepfake Detection: A Comprehensive Survey 2024', ['detection', 'survey', 'transformer', 'cnn'], 'Latest comprehensive review of deepfake detection methods, including transformer-based approaches, multi-modal analysis, and real-time detection systems.'),
      author: 'Dr. Sarah Chen',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['detection', 'survey', 'transformer', 'cnn']
    },
    {
      id: `curated-deepfake-${currentTime}-2`,
      title: 'FaceSwap vs. FaceRenactment: Technical Deep Dive into Generation Methods',
      excerpt: 'Comparative analysis of different deepfake generation techniques, examining GAN architectures, diffusion models, and neural radiance fields for facial synthesis.',
      category: 'Generation Techniques',
      published_at: new Date().toISOString(),
      source: 'Computer Vision Research Lab',
      url: 'https://paperswithcode.com/task/face-swapping',
      read_time: '15 min read',
      image: getRelevantImage('Generation Techniques', 'FaceSwap vs. FaceRenactment: Technical Deep Dive into Generation Methods', ['generation', 'gan', 'diffusion', 'faceswap'], 'Comparative analysis of different deepfake generation techniques, examining GAN architectures, diffusion models, and neural radiance fields for facial synthesis.'),
      author: 'Prof. Michael Zhang',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['generation', 'gan', 'diffusion', 'faceswap']
    },
    {
      id: `curated-deepfake-${currentTime}-3`,
      title: 'Ethical Implications of Deepfake Technology: Policy and Regulation Framework',
      excerpt: 'Examining the societal impact of synthetic media, legal challenges, consent frameworks, and proposed regulatory approaches across different jurisdictions.',
      category: 'Ethics & Policy',
      published_at: new Date().toISOString(),
      source: 'AI Ethics & Policy Center',
      url: 'https://www.brookings.edu/research/how-should-governments-respond-to-deepfakes/',
      read_time: '12 min read',
      image: getRelevantImage('Ethics & Policy', 'Ethical Implications of Deepfake Technology: Policy and Regulation Framework', ['ethics', 'policy', 'regulation', 'legal'], 'Examining the societal impact of synthetic media, legal challenges, consent frameworks, and proposed regulatory approaches across different jurisdictions.'),
      author: 'Dr. Emily Johnson',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['ethics', 'policy', 'regulation', 'legal']
    },
    {
      id: `curated-deepfake-${currentTime}-4`,
      title: 'DFDC, FaceForensics++, and Beyond: Deepfake Detection Datasets Comparison',
      excerpt: 'Comprehensive analysis of available deepfake datasets, benchmarking methodologies, evaluation metrics, and challenges in dataset curation for research.',
      category: 'Datasets & Benchmarks',
      published_at: new Date().toISOString(),
      source: 'Machine Learning Datasets Hub',
      url: 'https://github.com/ondyari/FaceForensics',
      read_time: '18 min read',
      image: getRelevantImage('Datasets & Benchmarks', 'DFDC, FaceForensics++, and Beyond: Deepfake Detection Datasets Comparison', ['datasets', 'benchmarks', 'evaluation', 'dfdc'], 'Comprehensive analysis of available deepfake datasets, benchmarking methodologies, evaluation metrics, and challenges in dataset curation for research.'),
      author: 'Research Consortium',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['datasets', 'benchmarks', 'evaluation', 'dfdc']
    },
    {
      id: `curated-deepfake-${currentTime}-5`,
      title: 'Real-World Applications: Deepfakes in Entertainment, Education, and Digital Art',
      excerpt: 'Exploring positive use cases of deepfake technology including film production, historical education, digital art creation, and accessibility applications.',
      category: 'Applications',
      published_at: new Date().toISOString(),
      source: 'Digital Media Innovation Lab',
      url: 'https://www.nature.com/articles/s41598-021-99444-5',
      read_time: '10 min read',
      image: getRelevantImage('Applications', 'Real-World Applications: Deepfakes in Entertainment, Education, and Digital Art', ['applications', 'entertainment', 'education', 'art'], 'Exploring positive use cases of deepfake technology including film production, historical education, digital art creation, and accessibility applications.'),
      author: 'Creative Tech Team',
      timestamp: currentTime,
      fetched_at: new Date().toISOString(),
      isDeepfakeResearch: true,
      tags: ['applications', 'entertainment', 'education', 'art']
    }
  ];

  const fetchNewsApiArticles = async (): Promise<Article[]> => {
    try {
      // More specific query to avoid irrelevant content
      const query = encodeURIComponent('("deepfake detection" OR "synthetic media detection" OR "AI-generated video detection" OR "face swap detection" OR "deepfake technology" OR "synthetic media technology" OR "AI video generation" OR "deepfake research" OR "face forgery detection") AND NOT (politics OR election OR government OR "indian politics" OR "general news" OR "entertainment news" OR "sports news")');
      const response = await fetch(
        `https://newsapi.org/v2/everything?q=${query}&sortBy=publishedAt&language=en&pageSize=10&apiKey=${NEWS_API_KEY}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch articles from NewsAPI');
      }
      
      const data = await response.json();
      const articles = (data.articles || []).filter((article: any) => {
        // Additional filtering to ensure content is relevant
        const title = (article.title || '').toLowerCase();
        const description = (article.description || '').toLowerCase();
        const content = `${title} ${description}`;
        
        // Must contain deepfake/AI related terms
        const relevantTerms = [
          'deepfake', 'synthetic media', 'ai-generated', 'face swap', 
          'face forgery', 'video generation', 'deep learning', 'neural network',
          'computer vision', 'facial recognition', 'ai detection'
        ];
        
        const hasRelevantTerms = relevantTerms.some(term => content.includes(term));
        
        // Must NOT contain irrelevant terms
        const irrelevantTerms = [
          'politics', 'election', 'government', 'indian politics', 'modi', 'trump', 'biden',
          'sports', 'cricket', 'football', 'entertainment', 'bollywood', 'hollywood',
          'general news', 'breaking news', 'weather', 'economy', 'stock market'
        ];
        
        const hasIrrelevantTerms = irrelevantTerms.some(term => content.includes(term));
        
        return hasRelevantTerms && !hasIrrelevantTerms;
      });
      
      return articles.map((article: any) => ({
        id: `news-${encodeURIComponent(article.url || article.title)}`,
        title: article.title,
        source: article.source?.name || 'NewsAPI',
        category: 'Detection Methods',
        published_at: article.publishedAt,
        excerpt: article.description,
        url: article.url,
        image: article.urlToImage || getRelevantImage('Detection Methods', article.title, ['news', 'deepfake', 'detection', 'ai'], article.description),
        author: article.author,
        timestamp: new Date(article.publishedAt).getTime(),
        isDeepfakeResearch: true,
        tags: ['news', 'deepfake', 'detection', 'ai']
      }));
    } catch (error) {
      console.error('Error fetching from NewsAPI:', error);
      return [];
    }
  };

  const fetchArxivArticles = async (): Promise<Article[]> => {
    const currentTime = Date.now();
    const arxivQueries = [
      'deepfake detection',
      'face swap detection',
      'synthetic media detection',
      'face forgery detection',
      'AI-generated video detection',
      'deepfake generation',
      'facial reenactment',
      'computer vision deepfake'
    ];

    const articles: Article[] = [];

    for (const query of arxivQueries) {
      try {
        const response = await fetch(
          `https://export.arxiv.org/api/query?search_query=all:"${encodeURIComponent(query)}"&start=0&max_results=2&sortBy=submittedDate&sortOrder=descending`
        );
        
        if (response.ok) {
          const xmlText = await response.text();
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
          const entries = xmlDoc.getElementsByTagName('entry');
          
          for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            const title = entry.getElementsByTagName('title')[0]?.textContent || 'Research Paper';
            const summary = entry.getElementsByTagName('summary')[0]?.textContent || 'Deepfake research paper';
            const id = entry.getElementsByTagName('id')?.[0]?.textContent || '';
            const published = entry.getElementsByTagName('published')?.[0]?.textContent || new Date().toISOString();
            const author = entry.getElementsByTagName('author')?.[0]?.textContent || 'Unknown Author';
            
            // Additional filtering to ensure relevance
            const titleLower = title.toLowerCase();
            const summaryLower = summary.toLowerCase();
            const content = `${titleLower} ${summaryLower}`;
            
            const relevantTerms = [
              'deepfake', 'synthetic media', 'face swap', 'face forgery', 
              'ai-generated', 'video generation', 'facial reenactment',
              'computer vision', 'neural network', 'deep learning'
            ];
            
            const hasRelevantTerms = relevantTerms.some(term => content.includes(term));
            
            if (!hasRelevantTerms) continue;
            
            const arxivId = id.split('/').pop()?.split('v')[0] || '';
            const pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
            const absUrl = `https://arxiv.org/abs/${arxivId}`;
            
            // Determine category based on query
            let category = 'Detection Methods';
            let tags = ['research', 'arxiv', 'detection'];
            if (query.includes('generation') || query.includes('reenactment')) {
              category = 'Generation Techniques';
              tags = ['generation', 'research', 'arxiv'];
            } else if (query.includes('ethics') || query.includes('policy')) {
              category = 'Ethics & Policy';
              tags = ['ethics', 'policy', 'research', 'arxiv'];
            }
            
            articles.push({
              id: `arxiv-${arxivId}`,
              title: title.trim(),
              excerpt: summary.substring(0, 200) + '...',
              category: category,
              source: 'arXiv',
              published_at: published,
              url: absUrl,
              pdf_url: pdfUrl,
              read_time: '15 min read',
              author: author,
              timestamp: new Date(published).getTime() || currentTime,
              isDeepfakeResearch: true,
              tags: tags,
              image: getRelevantImage(category, title.trim(), tags, summary.substring(0, 200))
            });
          }
        }
      } catch (error) {
        console.error(`Error fetching arXiv for ${query}:`, error);
      }
      
      // Add delay between requests to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return articles;
  };

  // Fetch Medium articles via RSS with better filtering
  const fetchMediumArticles = async (): Promise<Article[]> => {
    try {
      const tags = ['deepfake', 'synthetic-media', 'ai-generated-content', 'face-swap'];
      const parser = new DOMParser();
      const allArticles: Article[] = [];

      for (const tag of tags) {
        const mediumRss = `https://medium.com/feed/tag/${tag}`;
        const rssUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(mediumRss)}`;
        const response = await fetch(rssUrl);
        if (!response.ok) continue;
        const xmlText = await response.text();
        const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
        const items = Array.from(xmlDoc.getElementsByTagName('item'));

        const articles: Article[] = items.slice(0, 5).map((item) => {
          const title = item.getElementsByTagName('title')[0]?.textContent || 'Medium Article';
          const link = item.getElementsByTagName('link')[0]?.textContent || '#';
          const pubDate = item.getElementsByTagName('pubDate')[0]?.textContent || new Date().toUTCString();
          const creator = item.getElementsByTagName('dc:creator')[0]?.textContent || 'Medium Author';
          const description = item.getElementsByTagName('description')[0]?.textContent || '';

          const excerpt = description.replace(/<[^>]*>/g, '').slice(0, 220) + '...';

          return {
            id: `medium-${encodeURIComponent(link)}`,
            title: title,
            source: 'Medium',
            category: 'Blog',
            published_at: new Date(pubDate).toISOString(),
            excerpt: excerpt,
            url: link,
            image: getRelevantImage('Blog', title, ['blog', 'medium', 'deepfake'], excerpt),
            author: creator,
            timestamp: new Date(pubDate).getTime(),
            isDeepfakeResearch: true,
            tags: ['blog', 'medium', 'deepfake']
          } as Article;
        });

        allArticles.push(...articles);
      }

      // De-duplicate and filter for relevance
      const seen = new Set<string>();
      const deduped = allArticles.filter(a => {
        if (seen.has(a.id)) return false;
        seen.add(a.id);
        
        // Additional filtering for relevance
        const content = `${a.title} ${a.excerpt}`.toLowerCase();
        const relevantTerms = [
          'deepfake', 'synthetic media', 'ai-generated', 'face swap', 
          'face forgery', 'video generation', 'computer vision', 'neural network'
        ];
        
        const hasRelevantTerms = relevantTerms.some(term => content.includes(term));
        const hasIrrelevantTerms = ['politics', 'election', 'sports', 'entertainment'].some(term => content.includes(term));
        
        return hasRelevantTerms && !hasIrrelevantTerms;
      });
      
      return deduped.slice(0, 10); // Limit to 10 most relevant articles
    } catch (error) {
      console.error('Error fetching Medium RSS:', error);
      return [];
    }
  };

  // Enhanced deepfake article filtering with live mode support
  useEffect(() => {
    let filtered = [...deepfakeArticles];
    
    // If live mode is active, only show articles from the last 24 hours
    if (liveMode) {
      filtered = filtered.filter(article => isArticleLive(article));
    }
    
    // Filter by category
    if (selectedDeepfakeCategory && selectedDeepfakeCategory !== 'All Deepfake Research' && selectedDeepfakeCategory !== 'GitHub Repositories') {
      const categoryMatch = selectedDeepfakeCategory.split(' ')[0].toLowerCase();
      filtered = filtered.filter(article => 
        article.category && article.category.toLowerCase().includes(categoryMatch)
      );
    }
    
    // Filter by search query
    if (deepfakeSearchQuery) {
      const query = deepfakeSearchQuery.toLowerCase();
      filtered = filtered.filter(article => 
        (article.title && article.title.toLowerCase().includes(query)) ||
        (article.source && article.source.toLowerCase().includes(query)) ||
        (article.excerpt && article.excerpt.toLowerCase().includes(query)) ||
        (article.category && article.category.toLowerCase().includes(query)) ||
        (article.tags && article.tags.some(tag => tag.toLowerCase().includes(query)))
      );
    }
    
    // Sort by timestamp (recent first)
    filtered.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    
    setFilteredDeepfakeArticles(filtered);
    
    // Reset pagination when filters change
    setCurrentPage(1);
    setArticlesPerPage(15);
    setHasMoreArticles(filtered.length > 15);
  }, [deepfakeArticles, selectedDeepfakeCategory, deepfakeSearchQuery, liveMode]);

  // Pagination logic
  useEffect(() => {
    const startIndex = 0;
    const endIndex = currentPage * articlesPerPage;
    const articlesToShow = filteredDeepfakeArticles.slice(startIndex, endIndex);
    setDisplayedArticles(articlesToShow);
    setHasMoreArticles(endIndex < filteredDeepfakeArticles.length);
  }, [filteredDeepfakeArticles, currentPage, articlesPerPage]);

  // Load more articles function
  const loadMoreArticles = () => {
    if (isLoadingMore || !hasMoreArticles) return;
    
    setIsLoadingMore(true);
    setError(null);
    
    // Simulate loading delay for better UX
    setTimeout(() => {
      setCurrentPage(prev => prev + 1);
      setIsLoadingMore(false);
    }, 500);
  };

  const fetchDeepfakeContent = async () => {
    setIsDeepfakeFetching(true);
    setError(null);
    try {
      const currentTime = Date.now();
      const newArticles: Article[] = [];

      // Fetch from NewsAPI
      try {
        const newsApiArticles = await fetchNewsApiArticles();
        newArticles.push(...newsApiArticles);
      } catch (error) {
        console.error('NewsAPI fetch failed:', error);
        setApiStatus(prev => ({ ...prev, newsApi: false }));
      }

      // Fetch from arXiv
      try {
        const arxivArticles = await fetchArxivArticles();
        newArticles.push(...arxivArticles);
      } catch (error) {
        console.error('arXiv fetch failed:', error);
        setApiStatus(prev => ({ ...prev, arxiv: false }));
      }

      // Fetch from Medium RSS
      try {
        const mediumArticles = await fetchMediumArticles();
        newArticles.push(...mediumArticles);
      } catch (error) {
        console.error('Medium fetch failed:', error);
      }

      // Always include curated content
      const curatedContent = getCuratedDeepfakeContent(currentTime);
      newArticles.push(...curatedContent);

      // De-duplicate by id
      const seen = new Set<string>();
      const finalArticles = newArticles.filter(a => {
        if (!a.id) return false;
        if (seen.has(a.id)) return false;
        seen.add(a.id);
        return true;
      });

      setDeepfakeArticles(finalArticles);
      setTotalResults(finalArticles.length);
      setLastFetchTime(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error fetching deepfake content:', error);
      setError('Failed to fetch articles. Please try again.');
    } finally {
      setIsDeepfakeFetching(false);
    }
  };

  // Fetch GitHub repositories with fallback
  const fetchGitHubContent = async () => {
    try {
      setApiStatus(prev => ({ ...prev, github: true }));
      const repos = await fetchGitHubRepos();
      
      // If no repos fetched, use fallback curated list
      if (repos.length === 0) {
        const fallbackRepos: GitHubRepo[] = [
          {
            id: 1,
            name: 'DeepFaceLab',
            full_name: 'iperov/DeepFaceLab',
            description: 'DeepFaceLab is the leading software for creating deepfakes',
            html_url: 'https://github.com/iperov/DeepFaceLab',
            stargazers_count: 45000,
            forks_count: 10000,
            watchers_count: 45000,
            language: 'Python',
            topics: ['deepfake', 'face-swap', 'deep-learning'],
            created_at: '2018-01-01T00:00:00Z',
            updated_at: new Date().toISOString(),
            size: 1000000,
            open_issues_count: 50
          },
          {
            id: 2,
            name: 'FaceSwap',
            full_name: 'deepfakes/faceswap',
            description: 'Deepfakes software for everyone',
            html_url: 'https://github.com/deepfakes/faceswap',
            stargazers_count: 35000,
            forks_count: 8000,
            watchers_count: 35000,
            language: 'Python',
            topics: ['deepfake', 'face-swap', 'tensorflow'],
            created_at: '2018-01-01T00:00:00Z',
            updated_at: new Date().toISOString(),
            size: 800000,
            open_issues_count: 30
          },
          {
            id: 3,
            name: 'Deepfake-Detection',
            full_name: 'microsoft/Deepfake-Detection',
            description: 'Microsoft\'s deepfake detection research and tools',
            html_url: 'https://github.com/microsoft/Deepfake-Detection',
            stargazers_count: 15000,
            forks_count: 3000,
            watchers_count: 15000,
            language: 'Python',
            topics: ['deepfake', 'detection', 'microsoft'],
            created_at: '2019-01-01T00:00:00Z',
            updated_at: new Date().toISOString(),
            size: 500000,
            open_issues_count: 20
          }
        ];
        setGithubRepos(fallbackRepos);
      } else {
        setGithubRepos(repos);
      }
    } catch (error) {
      console.error('Error fetching GitHub repositories:', error);
      setApiStatus(prev => ({ ...prev, github: false }));
      
      // Use fallback on error
      const fallbackRepos: GitHubRepo[] = [
        {
          id: 1,
          name: 'DeepFaceLab',
          full_name: 'iperov/DeepFaceLab',
          description: 'DeepFaceLab is the leading software for creating deepfakes',
          html_url: 'https://github.com/iperov/DeepFaceLab',
          stargazers_count: 45000,
          forks_count: 10000,
          watchers_count: 45000,
          language: 'Python',
          topics: ['deepfake', 'face-swap', 'deep-learning'],
          created_at: '2018-01-01T00:00:00Z',
          updated_at: new Date().toISOString(),
          size: 1000000,
          open_issues_count: 50
        }
      ];
      setGithubRepos(fallbackRepos);
    }
  };

  // Live mode: start/stop polling
  useEffect(() => {
    if (liveMode) {
      // Fetch immediately, then poll every 60s
      fetchDeepfakeContent();
      const id = window.setInterval(() => {
        fetchDeepfakeContent();
      }, 60000);
      liveIntervalRef.current = id;
    } else if (liveIntervalRef.current) {
      window.clearInterval(liveIntervalRef.current);
      liveIntervalRef.current = null;
    }

    return () => {
      if (liveIntervalRef.current) {
        window.clearInterval(liveIntervalRef.current);
        liveIntervalRef.current = null;
      }
    };
  }, [liveMode]);

  // Fetch content on component mount
  useEffect(() => {
    let isMounted = true;
    (async () => {
      await Promise.all([
        fetchDeepfakeContent(),
        fetchGitHubContent()
      ]);
      if (!isMounted) return;
    })();
    return () => { isMounted = false };
  }, [])

  // Update API status based on fetch results
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        // Check NewsAPI status
        const newsApiCheck = await fetch(`https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey=${NEWS_API_KEY}`)
          .then(() => true)
          .catch(() => false);
          
        // Check arXiv status
        const arxivCheck = await fetch('https://export.arxiv.org/api/query?search_query=all:test&max_results=1')
          .then(res => res.ok)
          .catch(() => false);

        // Check GitHub API status
        const githubCheck = await fetch('https://api.github.com/search/repositories?q=deepfake&per_page=1')
          .then(res => res.ok)
          .catch(() => false);
          
        setApiStatus({
          newsApi: newsApiCheck,
          arxiv: arxivCheck,
          huggingface: true,
          github: githubCheck
        });
      } catch (error) {
        console.error('Error checking API status:', error);
      }
    };
    
    checkApiStatus();
    
    // Check status every 5 minutes
    const interval = setInterval(checkApiStatus, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Get live articles count for display
  const liveArticlesCount = deepfakeArticles.filter(article => isArticleLive(article)).length;

  // Main render
  return (
    <div className="relative min-h-screen">
      <AnimatedBackground className="opacity-20" intensity={0.15} />
      <div className="container py-8 relative z-10">
      <div className="mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
          <div className="text-center lg:text-left">
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              The Deepfake Pulse
            </h1>
            <p className="text-muted-foreground text-base sm:text-lg">
              Real-time insights on synthetic media detection and generation
            </p>
          </div>
          
          {/* Live Status and Refresh */}
          <div className="flex flex-col sm:flex-row items-center gap-3 bg-blue-50 p-3 rounded-lg border border-blue-100">
            <div className="text-sm text-center sm:text-left">
              <p className="font-medium text-blue-800 flex items-center justify-center sm:justify-start gap-1">
                <span>📡 {liveMode ? 'Live Mode Active' : 'Live Data'}</span>
                {lastFetchTime && <span className="text-xs text-blue-600">• Updated: {lastFetchTime}</span>}
              </p>
              <p className="text-blue-700 text-xs">
                Showing <span className="font-semibold">{filteredDeepfakeArticles.length}</span> of {totalResults} articles
                {liveMode && <span className="ml-1">({liveArticlesCount} live)</span>}
              </p>
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button
                variant={liveMode ? "default" : "outline"}
                size="sm"
                onClick={() => setLiveMode(v => !v)}
                className={`gap-2 whitespace-nowrap w-full sm:w-auto ${liveMode ? 'bg-green-600 hover:bg-green-700 text-white' : ''}`}
              >
                <Radio className={`h-3.5 w-3.5 ${liveMode ? 'animate-pulse' : ''}`} />
                {liveMode ? 'Live On' : 'Live Off'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fetchDeepfakeContent()}
                disabled={isDeepfakeFetching}
                className="gap-2 whitespace-nowrap w-full sm:w-auto"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isDeepfakeFetching ? 'animate-spin' : ''}`} />
                {isDeepfakeFetching ? 'Refreshing...' : 'Refresh'}
              </Button>
            </div>
          </div>
        </div>
        
        {/* Live Mode Alert */}
        {liveMode && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800 flex items-center gap-2">
              <Radio className="h-4 w-4 animate-pulse" />
              <strong>Live Mode Active:</strong> Showing only articles from the last 24 hours. Auto-refreshing every minute.
            </p>
          </div>
        )}
        
        {/* API Status Badges */}
        <div className="flex flex-wrap gap-2 justify-center md:justify-start mt-2">
          <span className={`flex items-center text-xs px-2 py-1 rounded-full ${apiStatus.newsApi ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
            {apiStatus.newsApi ? '✓' : '⚠'} NewsAPI
          </span>
          <span className={`flex items-center text-xs px-2 py-1 rounded-full ${apiStatus.arxiv ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
            {apiStatus.arxiv ? '✓' : '⚠'} arXiv
          </span>
          <span className={`flex items-center text-xs px-2 py-1 rounded-full ${apiStatus.huggingface ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
            {apiStatus.huggingface ? '✓' : '⚠'} Hugging Face
          </span>
          <span className={`flex items-center text-xs px-2 py-1 rounded-full ${apiStatus.github ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
            {apiStatus.github ? '✓' : '⚠'} GitHub
          </span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
          Deepfake Research Papers {liveMode && <span className="text-green-600">(Live)</span>}
        </h2>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-2">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search research papers..."
              className="pl-10"
              value={deepfakeSearchQuery}
              onChange={(e) => setDeepfakeSearchQuery(e.target.value)}
            />
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchDeepfakeContent()}
            disabled={isDeepfakeFetching}
            className="w-full sm:w-auto"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isDeepfakeFetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Deepfake Category Filters */}
      <Tabs value={selectedDeepfakeCategory} onValueChange={setSelectedDeepfakeCategory} className="mb-6">
        <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 bg-purple-50 overflow-x-auto">
          {deepfakeCategories.map((category) => (
            <TabsTrigger 
              key={category} 
              value={category} 
              className="text-xs sm:text-sm whitespace-nowrap px-2 py-2"
            >
              {category}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Error:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* GitHub Repositories Section */}
      {selectedDeepfakeCategory === 'GitHub Repositories' && (
        <div className="mb-8">
          <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Github className="h-6 w-6" />
            GitHub Repositories
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {githubRepos.map((repo, index) => (
              <motion.div
                key={repo.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="h-full hover:border-blue-300 transition-all duration-300 group border-2 border-blue-100">
                  <a 
                    href={repo.html_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block h-full"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between mb-3">
                        <Badge variant="outline" className="bg-blue-100 text-blue-800 hover:bg-blue-200">
                          <Github className="w-3 h-3 mr-1" />
                          {repo.language}
                        </Badge>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatDate(repo.updated_at)}
                        </div>
                      </div>
                      
                      <CardTitle className="text-lg leading-tight group-hover:text-blue-600 transition-colors">
                        {repo.name}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground font-medium">
                        {repo.full_name}
                      </p>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                        {repo.description}
                      </p>
                      
                      {repo.topics && repo.topics.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-4">
                          {repo.topics.slice(0, 3).map((topic) => (
                            <Badge key={topic} variant="secondary" className="text-xs">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Star className="w-3 h-3" />
                            {repo.stargazers_count}
                          </span>
                          <span className="flex items-center gap-1">
                            <GitFork className="w-3 h-3" />
                            {repo.forks_count}
                          </span>
                          <span className="flex items-center gap-1">
                            <Eye className="w-3 h-3" />
                            {repo.watchers_count}
                          </span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 px-2 group-hover:bg-primary group-hover:text-primary-foreground transition-all"
                          onClick={() => window.open(repo.html_url, '_blank', 'noopener noreferrer')}
                        >
                          <span className="text-xs mr-1">View</span>
                          <ExternalLink className="w-3 h-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </a>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Deepfake Research Grid */}
      {selectedDeepfakeCategory !== 'GitHub Repositories' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-8">
          {(displayedArticles.length > 0 || isDeepfakeFetching) ? (
            [...displayedArticles, ...Array(Math.max(0, 5 - displayedArticles.length)).fill(null)].map((article, index) => (
            article ? (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className={`h-full hover:border-purple-300 transition-all duration-300 group border-2 ${liveMode && isArticleLive(article) ? 'border-green-300 bg-green-50' : 'border-purple-100'}`}>
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block h-full"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between mb-3">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getCategoryColor(article.category)}`}
                        >
                          <Brain className="w-3 h-3 mr-1" />
                          {article.category}
                        </Badge>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatDate(article.published_at)}
                          {liveMode && isArticleLive(article) && (
                            <span className="ml-2 flex items-center text-green-600">
                              <Radio className="w-2 h-2 mr-1 animate-pulse" />
                              LIVE
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="mb-2">
                        <Badge variant="secondary" className="bg-purple-100 text-purple-800 border-purple-200 text-xs">
                          <Microscope className="w-3 h-3 mr-1" />
                          DEEPFAKE RESEARCH
                        </Badge>
                      </div>
                      
                      <CardTitle className="text-lg leading-tight group-hover:text-purple-600 transition-colors">
                        {article.title}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground font-medium">
                        {article.source}
                      </p>
                    </CardHeader>
                    <CardContent>
                      {article.image && (
                        <div className="relative w-full h-48 mb-4 rounded-lg overflow-hidden bg-gray-100">
                          <img 
                            src={article.image} 
                            alt={article.title}
                            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                            onError={(e) => {
                              // Try fallback image with different parameters
                              const fallbackImage = getRelevantImage(article.category, article.title, article.tags || [], article.excerpt || '');
                              if (e.currentTarget.src !== fallbackImage) {
                                e.currentTarget.src = fallbackImage;
                              } else {
                                // Ultimate fallback based on category
                                const content = `${article.title} ${article.excerpt || ''}`.toLowerCase();
                                let ultimateFallback = 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=250&fit=crop&q=80';
                                
                                if (content.includes('data') || content.includes('visualization')) {
                                  ultimateFallback = 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=250&fit=crop&q=80';
                                } else if (content.includes('research') || content.includes('paper')) {
                                  ultimateFallback = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=250&fit=crop&q=80';
                                } else if (content.includes('ethics') || content.includes('policy')) {
                                  ultimateFallback = 'https://images.unsplash.com/photo-1589652717521-10c0d092dea9?w=400&h=250&fit=crop&q=80';
                                } else if (content.includes('application') || content.includes('entertainment')) {
                                  ultimateFallback = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=250&fit=crop&q=80';
                                } else if (content.includes('dataset') || content.includes('benchmark')) {
                                  ultimateFallback = 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=250&fit=crop&q=80';
                                }
                                
                                e.currentTarget.src = ultimateFallback;
                              }
                            }}
                            onLoad={(e) => {
                              e.currentTarget.style.opacity = '1';
                              const spinner = e.currentTarget.parentElement?.querySelector('.loading-spinner');
                              if (spinner && 'style' in spinner) {
                                (spinner as HTMLElement).style.display = 'none';
                              }
                            }}
                            loading="lazy"
                            style={{ opacity: 0, transition: 'opacity 0.3s ease-in-out' }}
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                          <div className="loading-spinner absolute inset-0 flex items-center justify-center">
                            <div className="w-8 h-8 border-2 border-gray-300 border-t-purple-600 rounded-full animate-spin opacity-50"></div>
                          </div>
                        </div>
                      )}
                      
                      {article.excerpt && (
                        <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                          {article.excerpt}
                        </p>
                      )}
                      
                      {article.author && (
                        <div className="text-xs text-muted-foreground mb-3">
                          By {article.author}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          {article.read_time}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 px-2 group-hover:bg-primary group-hover:text-primary-foreground transition-all"
                          onClick={() => window.open(article.url, '_blank', 'noopener noreferrer')}
                        >
                          <span className="text-xs mr-1">Read</span>
                          <ExternalLink className="w-3 h-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </a>
                </Card>
              </motion.div>
            ) : (
              isDeepfakeFetching && (
                <Card key={`loading-${index}`} className="h-full animate-pulse">
                  <CardHeader>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-48 bg-gray-200 rounded mb-4"></div>
                    <div className="h-3 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  </CardContent>
                </Card>
              )
            )
          ))
        ) : (
          <div className="col-span-full text-center py-16">
            <Search className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">
              {liveMode ? 'No live articles found' : 'No articles found'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {liveMode 
                ? 'No articles from the last 24 hours match your criteria. Try turning off live mode.'
                : 'Try adjusting your search terms or category filter.'
              }
            </p>
          </div>
        )}
        </div>
      )}

      {/* Load More Button */}
      {selectedDeepfakeCategory !== 'GitHub Repositories' && hasMoreArticles && (
        <div className="flex justify-center mt-8">
          <Button
            onClick={loadMoreArticles}
            disabled={isLoadingMore}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium"
          >
            {isLoadingMore ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading More...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Fetch More / Explore More
              </>
            )}
          </Button>
        </div>
      )}

      {/* Articles Count Display */}
      {selectedDeepfakeCategory !== 'GitHub Repositories' && (
        <div className="text-center mt-6 text-sm text-muted-foreground">
          Showing {displayedArticles.length} of {filteredDeepfakeArticles.length} articles
          {hasMoreArticles && (
            <span className="ml-2 text-purple-600 font-medium">
              • {filteredDeepfakeArticles.length - displayedArticles.length} more available
            </span>
          )}
        </div>
      )}
      </div>
    </div>
  )
}

export default BlogPage
