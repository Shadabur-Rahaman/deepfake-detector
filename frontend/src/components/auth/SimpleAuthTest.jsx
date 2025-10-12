import React, { useState } from 'react';
import { useAuth } from '../../contexts/SimpleAuthContext';
import SimpleAuthModal from './SimpleAuthModal';
import SimpleUserDashboard from './SimpleUserDashboard';

const SimpleAuthTest = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
            Simple Authentication Test
          </h1>
          
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
            
            {isAuthenticated && user ? (
              <div className="space-y-4">
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                  ✅ <strong>Authenticated</strong> - Welcome, {user.fullName || user.username}!
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-gray-700">User Information</h3>
                    <div className="mt-2 space-y-1 text-sm">
                      <p><strong>ID:</strong> {user.id}</p>
                      <p><strong>Email:</strong> {user.email}</p>
                      <p><strong>Username:</strong> {user.username}</p>
                      <p><strong>Full Name:</strong> {user.fullName}</p>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-700">Actions</h3>
                    <div className="mt-2 space-y-2">
                      <button
                        onClick={() => setShowAuthModal(true)}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                      >
                        Edit Profile
                      </button>
                      <button
                        onClick={logout}
                        className="w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                  ⚠️ <strong>Not Authenticated</strong> - Please login to continue
                </div>
                
                <div className="text-center">
                  <button
                    onClick={() => setShowAuthModal(true)}
                    className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 text-lg"
                  >
                    Login / Sign Up
                  </button>
                </div>
              </div>
            )}
          </div>

          {isAuthenticated && user && (
            <SimpleUserDashboard />
          )}
        </div>
      </div>

      <SimpleAuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={() => {
          setShowAuthModal(false);
          // User is automatically set in context
        }}
      />
    </div>
  );
};

export default SimpleAuthTest;
