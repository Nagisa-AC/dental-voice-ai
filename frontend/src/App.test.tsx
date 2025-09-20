import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the AuthContext
jest.mock('./common/contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="auth-provider">{children}</div>,
  useAuth: () => ({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
  }),
}));

// Mock the components
jest.mock('./features/landing', () => ({
  LandingPage: () => <div data-testid="landing-page">Landing Page</div>,
}));

jest.mock('./features/auth', () => ({
  Login: () => <div data-testid="login-page">Login Page</div>,
}));

jest.mock('./features/dashboard', () => ({
  Dashboard: () => <div data-testid="dashboard-page">Dashboard Page</div>,
}));

jest.mock('./layouts', () => ({
  PublicLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="public-layout">{children}</div>
  ),
  AuthLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="auth-layout">{children}</div>
  ),
  DashboardLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dashboard-layout">{children}</div>
  ),
}));

jest.mock('./common', () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="error-boundary">{children}</div>
  ),
}));

const renderApp = () => {
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
};

describe('App Component', () => {
  test('renders without crashing', () => {
    renderApp();
    expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
  });

  test('renders landing page by default', () => {
    renderApp();
    expect(screen.getByTestId('landing-page')).toBeInTheDocument();
  });

  test('renders error boundary', () => {
    renderApp();
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
  });

  test('has proper routing structure', () => {
    renderApp();
    // Check that the main app container exists
    expect(screen.getByRole('main') || screen.getByTestId('app-container')).toBeInTheDocument();
  });
});
