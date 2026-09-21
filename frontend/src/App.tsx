import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';

// Theme and Context Providers
import { ThemeProvider } from "./components/theme/ThemeProvider";
import { AuthProvider } from "./contexts/SimpleAuthContext";
import { PaymentProvider } from "./contexts/PaymentContext";
import { NavigationProvider } from "./contexts/NavigationContext";
import { WelcomePopupProvider } from "./contexts/WelcomePopupContext";
import { AdminNotificationProvider } from "./contexts/AdminNotificationContext";
import { EnhancedNotificationProvider } from "./contexts/EnhancedNotificationContext";
import { RealtimeProvider } from "./contexts/RealtimeContext";

// UI Components
import { Toaster } from './components/ui/toaster';
import Header from "./components/ui/Header";
import PageLayout from "./components/layout/PageLayout";
import ConnectionStatus from "./components/ConnectionStatus";

// Pages
import Index from "./pages/Index";
import Detection from "./pages/Detection";
import Features from "./pages/Features";
import ApiDocs from "./pages/ApiDocs";
import Blog from "./pages/Blog";
import Contact from "./pages/Contact";
import TryIt from "./pages/TryIt";
import AdminDashboard from "./pages/AdminDashboard";
import AuthTest from "./pages/AuthTest";
import NotFound from "./pages/NotFound";

// Resource Pages
import GettingStarted from "./pages/GettingStarted";
import FastAPIDocs from "./pages/FastAPIDocs";
import PythonSDK from "./pages/PythonSDK";
import SystemStatus from "./pages/SystemStatus";
import WebSocketGuide from "./pages/WebSocketGuide";
import ModelInformation from "./pages/ModelInformation";

import './App.css';
// import SuperAdvancedDetection from './components/SuperAdvancedDetection';

// Error Fallback
const ErrorFallback = ({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
  <div className="min-h-screen flex items-center justify-center bg-background p-4">
    <div className="text-center max-w-md space-y-4">
      <div className="text-red-500 text-6xl mb-4">⚠️</div>
      <h2 className="text-2xl font-bold text-foreground">Something went wrong</h2>
      <p className="text-muted-foreground">{error.message || "An unexpected error occurred"}</p>
      <button
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <ThemeProvider defaultTheme="light" storageKey="ifake-ui-theme">
        <NavigationProvider>
          <WelcomePopupProvider>
            <AuthProvider>
              <RealtimeProvider>
                <AdminNotificationProvider>
                  <EnhancedNotificationProvider>
                    <PaymentProvider>
                  {/* ✅ Add future flags to suppress warnings */}
                  <Router 
                    future={{ 
                      v7_startTransition: true,
                      v7_relativeSplatPath: true 
                    }}
                  >
                    <div className="relative min-h-screen bg-background">
                      <Header />
                      <ConnectionStatus />
                      
                      <main className="pt-16">
                        <Suspense fallback={
                          <div className="min-h-screen flex items-center justify-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                          </div>
                        }>
                          <Routes>
                            <Route path="/" element={<PageLayout><Index /></PageLayout>} />
                            <Route path="/try" element={<PageLayout><TryIt /></PageLayout>} />
                            <Route path="/detection" element={<PageLayout><Detection /></PageLayout>} />
                            {/* <Route path="/super-advanced" element={<PageLayout><SuperAdvancedDetection /></PageLayout>} /> */}
                            <Route path="/admin" element={<AdminDashboard />} />
                            <Route path="/admin/legacy" element={<AdminDashboard />} />
                            <Route path="/auth-test" element={<PageLayout><AuthTest /></PageLayout>} />
                            <Route path="/features" element={<PageLayout><Features /></PageLayout>} />
                            <Route path="/api" element={<PageLayout><ApiDocs /></PageLayout>} />
                            <Route path="/blog" element={<PageLayout><Blog /></PageLayout>} />
                            <Route path="/contact" element={<PageLayout><Contact /></PageLayout>} />
                            
                            {/* Resource Pages */}
                            <Route path="/docs/getting-started" element={<PageLayout><GettingStarted /></PageLayout>} />
                            <Route path="/docs/fastapi" element={<PageLayout><FastAPIDocs /></PageLayout>} />
                            <Route path="/docs/python-sdk" element={<PageLayout><PythonSDK /></PageLayout>} />
                            <Route path="/status" element={<PageLayout><SystemStatus /></PageLayout>} />
                            <Route path="/docs/websocket" element={<PageLayout><WebSocketGuide /></PageLayout>} />
                            <Route path="/docs/model-info" element={<PageLayout><ModelInformation /></PageLayout>} />
                            
                            <Route path="*" element={<PageLayout><NotFound /></PageLayout>} />
                          </Routes>
                        </Suspense>
                      </main>
                      
                      <Toaster />
                    </div>
                  </Router>
                  </PaymentProvider>
                  </EnhancedNotificationProvider>
                </AdminNotificationProvider>
              </RealtimeProvider>
            </AuthProvider>
          </WelcomePopupProvider>
        </NavigationProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
