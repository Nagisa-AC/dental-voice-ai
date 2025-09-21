/**
 * Base Layout Component
 * 
 * Provides the fundamental layout structure for all pages.
 * Includes common elements like navigation, footer, and error boundaries.
 */

import React from 'react';
import './BaseLayout.css';

interface BaseLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const BaseLayout: React.FC<BaseLayoutProps> = ({ children, className = '' }) => {
  return (
    <div className={`base-layout ${className}`}>
      <main className="base-layout__main">
        {children}
      </main>
    </div>
  );
};

export default BaseLayout;

