import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LandingPage } from './features/landing';
import { Dashboard } from './features/dashboard';
import { Login } from './features/auth';
import { AuthProvider } from './common/contexts/AuthContext';
import { PublicLayout, AuthLayout, DashboardLayout } from './layouts';
import { ErrorBoundary } from './common';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="App" data-testid="app-container">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={
                <PublicLayout>
                  <ErrorBoundary>
                    <LandingPage />
                  </ErrorBoundary>
                </PublicLayout>
              } />
              
              {/* Auth routes */}
              <Route path="/login" element={
                <AuthLayout title="Welcome Back" subtitle="Sign in to your account">
                  <ErrorBoundary>
                    <Login />
                  </ErrorBoundary>
                </AuthLayout>
              } />
              
              {/* Dashboard routes */}
              <Route path="/dashboard" element={
                <DashboardLayout user={{ name: 'John Doe', email: 'john@example.com', role: 'admin' }}>
                  <ErrorBoundary>
                    <Dashboard />
                  </ErrorBoundary>
                </DashboardLayout>
              } />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;