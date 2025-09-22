/**
 * Public Layout Component
 * 
 * Layout for public pages (landing page, login, etc.).
 * Includes navigation and footer for unauthenticated users.
 */

import React from 'react';
import BaseLayout from './BaseLayout';
import './PublicLayout.css';

interface PublicLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const PublicLayout: React.FC<PublicLayoutProps> = ({ children, className = '' }) => {
  return (
    <BaseLayout className={`public-layout ${className}`}>
      <header className="public-layout__header">
        <nav className="public-layout__nav">
          <div className="public-layout__nav-brand">
            <h1>Healthcare Voice AI</h1>
          </div>
          <div className="public-layout__nav-links">
            <a href="#features" className="public-layout__nav-link">Features</a>
            <a href="#pricing" className="public-layout__nav-link">Pricing</a>
            <a href="#contact" className="public-layout__nav-link">Contact</a>
            <a href="/login" className="public-layout__nav-link public-layout__nav-link--primary">Login</a>
          </div>
        </nav>
      </header>
      
      <div className="public-layout__content">
        {children}
      </div>
      
      <footer className="public-layout__footer">
        <div className="public-layout__footer-content">
          <p>&copy; 2024 Healthcare Voice AI. All rights reserved.</p>
          <div className="public-layout__footer-links">
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
            <a href="/security">Security</a>
          </div>
        </div>
      </footer>
    </BaseLayout>
  );
};

export default PublicLayout;


