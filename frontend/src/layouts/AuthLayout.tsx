/**
 * Auth Layout Component
 * 
 * Layout for authentication pages (login, register, etc.).
 * Provides a centered, focused layout for auth forms.
 */

import React from 'react';
import BaseLayout from './BaseLayout';
import './AuthLayout.css';

interface AuthLayoutProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  className = '', 
  title = 'Welcome',
  subtitle = 'Sign in to your account'
}) => {
  return (
    <BaseLayout className={`auth-layout ${className}`}>
      <div className="auth-layout__container">
        <div className="auth-layout__header">
          <div className="auth-layout__logo">
            <h1>Healthcare Voice AI</h1>
          </div>
          <div className="auth-layout__content">
            <h2 className="auth-layout__title">{title}</h2>
            <p className="auth-layout__subtitle">{subtitle}</p>
          </div>
        </div>
        
        <div className="auth-layout__form-container">
          {children}
        </div>
        
        <div className="auth-layout__footer">
          <p className="auth-layout__footer-text">
            Don't have an account? <a href="/register" className="auth-layout__footer-link">Sign up</a>
          </p>
        </div>
      </div>
    </BaseLayout>
  );
};

export default AuthLayout;
