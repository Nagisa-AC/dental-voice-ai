/**
 * Dashboard Layout Component
 * 
 * Layout for authenticated dashboard pages.
 * Includes sidebar navigation, header, and main content area.
 */

import React, { useState } from 'react';
import BaseLayout from './BaseLayout';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: React.ReactNode;
  className?: string;
  user?: {
    name: string;
    email: string;
    role: string;
  };
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children, 
  className = '',
  user
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Clinics', href: '/dashboard/clinics', icon: '🏥' },
    { name: 'Assistants', href: '/dashboard/assistants', icon: '🤖' },
    { name: 'Analytics', href: '/dashboard/analytics', icon: '📈' },
    { name: 'Settings', href: '/dashboard/settings', icon: '⚙️' },
  ];

  return (
    <BaseLayout className={`dashboard-layout ${className}`}>
      {/* Sidebar */}
      <aside className={`dashboard-layout__sidebar ${sidebarOpen ? 'dashboard-layout__sidebar--open' : ''}`}>
        <div className="dashboard-layout__sidebar-header">
          <h2 className="dashboard-layout__sidebar-title">Healthcare Voice AI</h2>
          <button 
            className="dashboard-layout__sidebar-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            ×
          </button>
        </div>
        
        <nav className="dashboard-layout__sidebar-nav">
          {navigationItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="dashboard-layout__sidebar-link"
            >
              <span className="dashboard-layout__sidebar-icon">{item.icon}</span>
              {item.name}
            </a>
          ))}
        </nav>
        
        <div className="dashboard-layout__sidebar-footer">
          <div className="dashboard-layout__user-info">
            <div className="dashboard-layout__user-avatar">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div className="dashboard-layout__user-details">
              <div className="dashboard-layout__user-name">{user?.name || 'User'}</div>
              <div className="dashboard-layout__user-role">{user?.role || 'User'}</div>
            </div>
          </div>
          <a href="/logout" className="dashboard-layout__logout-link">Logout</a>
        </div>
      </aside>

      {/* Main Content */}
      <div className="dashboard-layout__main">
        {/* Header */}
        <header className="dashboard-layout__header">
          <button 
            className="dashboard-layout__sidebar-toggle"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            ☰
          </button>
          
          <div className="dashboard-layout__header-actions">
            <button className="dashboard-layout__header-button" aria-label="Notifications">
              🔔
            </button>
            <button className="dashboard-layout__header-button" aria-label="Settings">
              ⚙️
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="dashboard-layout__content">
          {children}
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="dashboard-layout__overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </BaseLayout>
  );
};

export default DashboardLayout;


