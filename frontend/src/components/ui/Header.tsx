// src/components/ui/Header.tsx - Enhanced with active link highlighting
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { useAuth } from '@/contexts/SimpleAuthContext';
import SimpleAuthModal from '@/components/auth/SimpleAuthModal';
import { AdminNotificationBell } from '@/components/admin/AdminNotificationBell';
import { User, LogOut, Menu, X, Shield } from 'lucide-react';

const navigationItems = [
  { name: 'Home', path: '/', exact: true },
  { name: 'Features', path: '/features' },
  { name: 'Try It', path: '/try' },
  { name: 'Detection', path: '/detection' },
  { name: 'Blog', path: '/blog' },
  { name: 'API Docs', path: '/api' },
  { name: 'Contact', path: '/contact' }
];

const adminNavigationItems = [
  { name: 'Admin', path: '/admin', adminOnly: true }
];

export const Header = () => {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);


  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md border-b border-border/40">
        <div className="container mx-auto px-4 lg:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <NavLink to="/" className="flex items-center">
              <span className="text-2xl font-bold gradient-text">iFake</span>
            </NavLink>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1 xl:space-x-2">
              {navigationItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  end={item.exact}
                  className={({ isActive }) =>
                    `px-2 xl:px-3 py-2 rounded-full text-xs xl:text-sm font-medium transition-all duration-300 hover:bg-primary/10 hover:text-primary ${
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-md'
                        : 'text-muted-foreground'
                    }`
                  }
                >
                  {item.name}
                </NavLink>
              ))}
              
              {/* Admin Navigation - Only show for admin users */}
              {isAuthenticated && user?.roles?.includes('admin') && (
                adminNavigationItems.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.path}
                    className={({ isActive }) =>
                      `px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 hover:bg-purple-100 hover:text-purple-600 ${
                        isActive ? 'bg-purple-100 text-purple-600' : 'text-purple-500'
                      }`
                    }
                  >
                    <Shield className="w-4 h-4 inline mr-1" />
                    {item.name}
                  </NavLink>
                ))
              )}
            </nav>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-2 lg:space-x-4">
              {/* Theme Toggle */}
              <ThemeToggle />

              {/* Auth Section */}
              {isAuthenticated && user ? (
                <div className="flex items-center space-x-2 lg:space-x-3">
                  {/* Admin Notification Bell */}
                  {user.roles?.includes('admin') && (
                    <AdminNotificationBell />
                  )}

                  {/* User Info - Desktop */}
                  <div className="hidden lg:flex items-center space-x-2">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-blue-500" />
                      <span className="text-sm font-medium">{user.fullName || user.username}</span>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={logout}
                    className="flex items-center gap-1 lg:gap-2 text-xs lg:text-sm"
                  >
                    <LogOut className="w-3 h-3 lg:w-4 lg:h-4" />
                    <span className="hidden sm:inline">Sign Out</span>
                  </Button>
                </div>
              ) : (
                <div className="flex items-center space-x-2 lg:space-x-3">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setIsAuthModalOpen(true)}
                    className="hidden lg:flex text-sm"
                  >
                    Sign In
                  </Button>
                  <Button 
                    size="sm"
                    className="glow-primary text-xs lg:text-sm px-3 lg:px-4"
                    onClick={() => setIsAuthModalOpen(true)}
                  >
                    <span className="hidden sm:inline">Get Started</span>
                    <span className="sm:hidden">Start</span>
                  </Button>
                </div>
              )}

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden ml-1"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
              </Button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <div className="lg:hidden border-t border-border/40 py-4">
              <nav className="flex flex-col space-y-2">
                {navigationItems.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.path}
                    end={item.exact}
                    className={({ isActive }) =>
                      `px-4 py-3 rounded-lg text-left transition-colors ${
                        isActive
                          ? 'bg-primary text-primary-foreground font-medium'
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`
                    }
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.name}
                  </NavLink>
                ))}
                
                {/* Mobile Auth */}
                {!isAuthenticated && (
                  <div className="pt-4 border-t border-border/40 mt-4">
                    <Button
                      variant="ghost"
                      onClick={() => {
                        setIsAuthModalOpen(true);
                        setIsMobileMenuOpen(false);
                      }}
                      className="justify-start w-full"
                    >
                      Sign In
                    </Button>
                  </div>
                )}
                
                {/* Mobile User Info */}
                {isAuthenticated && user && (
                  <div className="pt-4 border-t border-border/40 mt-4">
                    <div className="flex items-center space-x-2 px-4 py-2">
                      <User className="w-4 h-4 text-blue-500" />
                      <span className="text-sm font-medium">{user.fullName || user.username}</span>
                    </div>
                  </div>
                )}
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Simple Authentication Modal */}
      <SimpleAuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={(user) => {
          setIsAuthModalOpen(false);
          // User is automatically set in context
        }}
      />
    </>
  );
};

export default Header;
