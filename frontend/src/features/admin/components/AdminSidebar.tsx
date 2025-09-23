/**
 * Admin Sidebar Component
 * 
 * Elegant sidebar navigation inspired by ngrok dashboard.
 * Features collapsible design, smooth animations, and professional styling.
 */

import React from 'react';
import './AdminSidebar.css';

type AdminView = 
  | 'overview'
  | 'tenants'
  | 'users'
  | 'assistants'
  | 'monitoring'
  | 'billing'
  | 'security'
  | 'analytics'
  | 'settings';

interface AdminSidebarProps {
  activeView: AdminView;
  onViewChange: (view: AdminView) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

interface NavigationItem {
  id: AdminView;
  label: string;
  icon: string;
  description: string;
  badge?: string;
  badgeColor?: 'success' | 'warning' | 'danger' | 'info';
}

const navigationItems: NavigationItem[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: 'dashboard',
    description: 'Dashboard overview and key metrics'
  },
  {
    id: 'tenants',
    label: 'Tenants',
    icon: 'business',
    description: 'Manage tenants and organizations',
    badge: '12',
    badgeColor: 'info'
  },
  {
    id: 'users',
    label: 'Users',
    icon: 'people',
    description: 'User management and permissions'
  },
  {
    id: 'assistants',
    label: 'Assistants',
    icon: 'smart_toy',
    description: 'Voice AI assistant management',
    badge: '8',
    badgeColor: 'success'
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: 'monitoring',
    description: 'System health and performance'
  },
  {
    id: 'billing',
    label: 'Billing',
    icon: 'account_balance_wallet',
    description: 'Subscription and payment management'
  },
  {
    id: 'security',
    label: 'Security',
    icon: 'security',
    description: 'Security controls and audit logs'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: 'analytics',
    description: 'Usage analytics and reporting'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'settings',
    description: 'System configuration and preferences'
  }
];

const AdminSidebar: React.FC<AdminSidebarProps> = ({
  activeView,
  onViewChange,
  collapsed,
  onToggleCollapse
}) => {
  return (
    <aside className={`admin-sidebar ${collapsed ? 'admin-sidebar--collapsed' : ''}`}>
      {/* Header */}
      <div className="admin-sidebar__header">
        <div className="admin-sidebar__logo">
          <div className="admin-sidebar__logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          {!collapsed && (
            <div className="admin-sidebar__logo-text">
              <div className="admin-sidebar__logo-title">Healthcare Voice AI</div>
              <div className="admin-sidebar__logo-subtitle">Admin Dashboard</div>
            </div>
          )}
        </div>
        
        <button
          className="admin-sidebar__toggle"
          onClick={onToggleCollapse}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d={collapsed ? "M6 4L10 8L6 12" : "M10 4L6 8L10 12"}
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {/* Navigation */}
      <nav className="admin-sidebar__nav">
        <div className="admin-sidebar__nav-section">
          <div className="admin-sidebar__nav-title">
            {!collapsed && 'Navigation'}
          </div>
          
          <ul className="admin-sidebar__nav-list">
            {navigationItems.map((item) => (
              <li key={item.id} className="admin-sidebar__nav-item">
                <button
                  className={`admin-sidebar__nav-link ${
                    activeView === item.id ? 'admin-sidebar__nav-link--active' : ''
                  }`}
                  onClick={() => onViewChange(item.id)}
                  title={collapsed ? item.description : undefined}
                >
                  <span className="admin-sidebar__nav-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      {item.icon === 'dashboard' && (
                        <path d="M3 13H11V3H3V13ZM3 21H11V15H3V21ZM13 21H21V11H13V21ZM13 3V9H21V3H13Z" fill="currentColor"/>
                      )}
                      {item.icon === 'business' && (
                        <path d="M12 7V3H2V21H22V7H12ZM6 19H4V17H6V19ZM6 15H4V13H6V15ZM6 11H4V9H6V11ZM6 7H4V5H6V7ZM10 19H8V17H10V19ZM10 15H8V13H10V15ZM10 11H8V9H10V11ZM10 7H8V5H10V7ZM20 19H12V17H14V15H12V13H14V11H12V9H20V19ZM18 11H16V13H18V11ZM18 15H16V17H18V15Z" fill="currentColor"/>
                      )}
                      {item.icon === 'people' && (
                        <path d="M16 4C18.21 4 20 5.79 20 8C20 10.21 18.21 12 16 12C13.79 12 12 10.21 12 8C12 5.79 13.79 4 16 4ZM16 14C18.67 14 24 15.34 24 18V20H8V18C8 15.34 13.33 14 16 14ZM8 4C10.21 4 12 5.79 12 8C12 10.21 10.21 12 8 12C5.79 12 4 10.21 4 8C4 5.79 5.79 4 8 4ZM8 14C10.67 14 16 15.34 16 18V20H0V18C0 15.34 5.33 14 8 14Z" fill="currentColor"/>
                      )}
                      {item.icon === 'smart_toy' && (
                        <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 9H14V4H19V9Z" fill="currentColor"/>
                      )}
                      {item.icon === 'monitoring' && (
                        <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19ZM17 12H15V17H17V12ZM13 7H11V17H13V7ZM9 10H7V17H9V10Z" fill="currentColor"/>
                      )}
                      {item.icon === 'account_balance_wallet' && (
                        <path d="M21 18V19C21 20.1 20.1 21 19 21H5C3.89 21 3 20.1 3 19V5C3 3.9 3.89 3 5 3H19C20.1 3 21 3.9 21 5V6H12C10.9 6 10 6.9 10 8V16C10 17.1 10.9 18 12 18H21ZM12 16V8H22V16H12ZM16 13.5C15.17 13.5 14.5 12.83 14.5 12S15.17 10.5 16 10.5 17.5 11.17 17.5 12 16.83 13.5 16 13.5Z" fill="currentColor"/>
                      )}
                      {item.icon === 'security' && (
                        <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,16.6 15.6,17 15,17H9C8.4,17 8,16.6 8,16V13C8,12.4 8.4,11.5 9,11.5V10C9,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.2,9.2 10.2,10V11.5H13.8V10C13.8,9.2 12.8,8.2 12,8.2Z" fill="currentColor"/>
                      )}
                      {item.icon === 'analytics' && (
                        <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM9 17H7V10H9V17ZM13 17H11V7H13V17ZM17 17H15V13H17V17Z" fill="currentColor"/>
                      )}
                      {item.icon === 'settings' && (
                        <path d="M19.14,12.94C19.18,12.64 19.2,12.33 19.2,12C19.2,11.67 19.18,11.36 19.14,11.06L21.16,9.48C21.34,9.34 21.39,9.07 21.28,8.87L19.36,5.44C19.24,5.24 18.99,5.17 18.77,5.25L16.38,6.05C16.04,5.66 15.66,5.28 15.27,4.94L15.07,2.47C15.05,2.24 14.87,2.05 14.64,2.05H9.36C9.13,2.05 8.95,2.24 8.93,2.47L8.73,4.94C8.34,5.28 7.96,5.66 7.62,6.05L5.23,5.25C5.01,5.17 4.76,5.24 4.64,5.44L2.72,8.87C2.61,9.07 2.66,9.34 2.84,9.48L4.86,11.06C4.82,11.36 4.8,11.67 4.8,12C4.8,12.33 4.82,12.64 4.86,12.94L2.84,14.52C2.66,14.66 2.61,14.93 2.72,15.13L4.64,18.56C4.76,18.76 5.01,18.83 5.23,18.75L7.62,17.95C7.96,18.34 8.34,18.72 8.73,19.06L8.93,21.53C8.95,21.76 9.13,21.95 9.36,21.95H14.64C14.87,21.95 15.05,21.76 15.07,21.53L15.27,19.06C15.66,18.72 16.04,18.34 16.38,17.95L18.77,18.75C18.99,18.83 19.24,18.76 19.36,18.56L21.28,15.13C21.39,14.93 21.34,14.66 21.16,14.52L19.14,12.94ZM12,15.6C10.02,15.6 8.4,13.98 8.4,12C8.4,10.02 10.02,8.4 12,8.4C13.98,8.4 15.6,10.02 15.6,12C15.6,13.98 13.98,15.6 12,15.6Z" fill="currentColor"/>
                      )}
                    </svg>
                  </span>
                  
                  {!collapsed && (
                    <>
                      <span className="admin-sidebar__nav-label">{item.label}</span>
                      {item.badge && (
                        <span className={`admin-sidebar__nav-badge admin-sidebar__nav-badge--${item.badgeColor}`}>
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* Footer */}
      <div className="admin-sidebar__footer">
        {!collapsed && (
          <div className="admin-sidebar__footer-content">
            <div className="admin-sidebar__footer-text">
              <div className="admin-sidebar__footer-title">System Status</div>
              <div className="admin-sidebar__footer-status">
                <span className="admin-sidebar__status-dot admin-sidebar__status-dot--success"></span>
                All Systems Operational
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

export default AdminSidebar;
