import React, { useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, ArrowLeft, Search, AlertTriangle } from 'lucide-react';

const NotFound: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  const popularPages = [
    { name: 'Try Detection', path: '/try-it', description: 'Upload and analyze your media' },
    { name: 'Real-time Detection', path: '/detection', description: 'Live camera analysis' },
    { name: 'API Documentation', path: '/api-docs', description: 'Integrate our API' },
    { name: 'Contact Us', path: '/contact', description: 'Get in touch with our team' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center py-8">
      <div className="container mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl mx-auto"
        >
          {/* 404 Illustration */}
          <div className="mb-8">
            <div className="text-8xl font-bold text-blue-600 mb-4">404</div>
            <div className="w-32 h-32 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-16 h-16 text-blue-600" />
            </div>
          </div>

          {/* Error Message */}
          <h1 className="text-4xl font-bold text-slate-800 mb-4">
            Oops! Page not found
          </h1>
          <p className="text-xl text-slate-600 mb-8">
            The page you're looking for doesn't exist or has been moved.
            Let's get you back on track!
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link to="/">
              <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold flex items-center gap-2 hover:bg-blue-700 transition-colors">
                <Home className="w-5 h-5" />
                Return to Home
              </button>
            </Link>
            <button
              onClick={() => window.history.back()}
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold flex items-center gap-2 hover:bg-gray-50 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Go Back
            </button>
          </div>

          {/* Popular Pages */}
          <div className="text-left">
            <h2 className="text-2xl font-semibold text-slate-800 mb-6 text-center">
              Popular Pages
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {popularPages.map((page, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Link
                    to={page.path}
                    className="block bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 group"
                  >
                    <h3 className="font-semibold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">
                      {page.name}
                    </h3>
                    <p className="text-slate-600 text-sm">
                      {page.description}
                    </p>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Search Suggestion */}
          <div className="mt-12 bg-white p-8 rounded-2xl shadow-lg">
            <div className="flex items-center justify-center gap-2 text-blue-600 mb-4">
              <Search className="w-6 h-6" />
              <h3 className="text-lg font-semibold">Can't find what you're looking for?</h3>
            </div>
            <p className="text-slate-600 mb-6">
              Try exploring our main features or contact our support team for assistance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/features">
                <button className="bg-blue-100 text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-200 transition-colors">
                  Explore Features
                </button>
              </Link>
              <Link to="/contact">
                <button className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors">
                  Contact Support
                </button>
              </Link>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-8 text-sm text-slate-500">
            <p>
              Error Code: 404 | Path: <code className="bg-gray-100 px-2 py-1 rounded">{location.pathname}</code>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default NotFound;
