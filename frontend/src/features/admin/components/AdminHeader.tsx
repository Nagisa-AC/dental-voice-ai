/**
 * Admin Header Component
 * 
 * Professional header with user info, notifications, and system status.
 * Inspired by ngrok dashboard's clean and functional design.
 */

import React, { useState } from 'react';
import './AdminHeader.css';

interface User {
  name?: string;
  email?: string;
  role?: string;
}

interface AdminHeaderProps {
  user?: User | null;
  onToggleSidebar: () => void;
}

const AdminHeader: React.FC<AdminHeaderProps> = ({ user, onToggleSidebar }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    {
      id: 1,
      title: 'New tenant registered',
      message: 'Dental Care Plus has completed onboarding',
      time: '2 minutes ago',
      type: 'success',
      unread: true
    },
    {
      id: 2,
      title: 'System alert',
      message: 'High CPU usage detected on server-03',
      time: '15 minutes ago',
      type: 'warning',
      unread: true
    },
    {
      id: 3,
      title: 'Payment processed',
      message: 'Monthly subscription payment received',
      time: '1 hour ago',
      type: 'info',
      unread: false
    }
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header className="admin-header">
      <div className="admin-header__left">
        <button
          className="admin-header__menu-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M3 5H17M3 10H17M3 15H17"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <div className="admin-header__breadcrumb">
          <span className="admin-header__breadcrumb-item">Admin</span>
          <span className="admin-header__breadcrumb-separator">/</span>
          <span className="admin-header__breadcrumb-current">Dashboard</span>
        </div>
      </div>

      <div className="admin-header__right">
        {/* System Status */}
        <div className="admin-header__status">
          <div className="admin-header__status-indicator admin-header__status-indicator--success"></div>
          <span className="admin-header__status-text">All Systems Operational</span>
        </div>

        {/* Notifications */}
        <div className="admin-header__notifications">
          <button
            className="admin-header__notifications-toggle"
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="Notifications"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M15 17H5C3.89543 17 3 16.1046 3 15V10C3 7.79086 4.79086 6 7 6H13C15.2091 6 17 7.79086 17 10V15C17 16.1046 16.1046 17 15 17Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M7 6V4C7 2.34315 8.34315 1 10 1C11.6569 1 13 2.34315 13 4V6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {unreadCount > 0 && (
              <span className="admin-header__notifications-badge">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="admin-header__notifications-dropdown">
              <div className="admin-header__notifications-header">
                <h3>Notifications</h3>
                <button
                  className="admin-header__notifications-close"
                  onClick={() => setShowNotifications(false)}
                >
                  ×
                </button>
              </div>
              <div className="admin-header__notifications-list">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`admin-header__notification ${
                      notification.unread ? 'admin-header__notification--unread' : ''
                    }`}
                  >
                    <div className={`admin-header__notification-icon admin-header__notification-icon--${notification.type}`}>
                      {notification.type === 'success' && '✓'}
                      {notification.type === 'warning' && '⚠'}
                      {notification.type === 'danger' && '✕'}
                      {notification.type === 'info' && 'ℹ'}
                    </div>
                    <div className="admin-header__notification-content">
                      <div className="admin-header__notification-title">
                        {notification.title}
                      </div>
                      <div className="admin-header__notification-message">
                        {notification.message}
                      </div>
                      <div className="admin-header__notification-time">
                        {notification.time}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="admin-header__notifications-footer">
                <button className="admin-btn admin-btn--secondary admin-btn--sm">
                  View All Notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="admin-header__user">
          <button
            className="admin-header__user-toggle"
            onClick={() => setShowUserMenu(!showUserMenu)}
            aria-label="User menu"
          >
            <div className="admin-header__user-avatar">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'A'}
            </div>
            <div className="admin-header__user-info">
              <div className="admin-header__user-name">
                {user?.name || 'Admin User'}
              </div>
              <div className="admin-header__user-role">
                {user?.role || 'Administrator'}
              </div>
            </div>
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              className={`admin-header__user-chevron ${showUserMenu ? 'admin-header__user-chevron--open' : ''}`}
            >
              <path
                d="M4 6L8 10L12 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>

          {showUserMenu && (
            <div className="admin-header__user-dropdown">
              <div className="admin-header__user-dropdown-header">
                <div className="admin-header__user-dropdown-avatar">
                  {user?.name ? user.name.charAt(0).toUpperCase() : 'A'}
                </div>
                <div className="admin-header__user-dropdown-info">
                  <div className="admin-header__user-dropdown-name">
                    {user?.name || 'Admin User'}
                  </div>
                  <div className="admin-header__user-dropdown-email">
                    {user?.email || 'admin@example.com'}
                  </div>
                </div>
              </div>
              <div className="admin-header__user-dropdown-menu">
                <button className="admin-header__user-dropdown-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M8 8C10.2091 8 12 6.20914 12 4C12 1.79086 10.2091 0 8 0C5.79086 0 4 1.79086 4 4C4 6.20914 5.79086 8 8 8Z"
                      stroke="currentColor"
                      strokeWidth="2"
                    />
                    <path
                      d="M0 16C0 12.6863 2.68629 10 6 10H10C13.3137 10 16 12.6863 16 16"
                      stroke="currentColor"
                      strokeWidth="2"
                    />
                  </svg>
                  Profile Settings
                </button>
                <button className="admin-header__user-dropdown-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M8 0L10.5 5.5L16 8L10.5 10.5L8 16L5.5 10.5L0 8L5.5 5.5L8 0Z"
                      stroke="currentColor"
                      strokeWidth="2"
                    />
                  </svg>
                  Preferences
                </button>
                <button className="admin-header__user-dropdown-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M8 0C3.58172 0 0 3.58172 0 8C0 12.4183 3.58172 16 8 16C12.4183 16 16 12.4183 16 8C16 3.58172 12.4183 0 8 0Z"
                      stroke="currentColor"
                      strokeWidth="2"
                    />
                    <path
                      d="M8 4V8L10 10"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                  Activity Log
                </button>
                <div className="admin-header__user-dropdown-divider"></div>
                <button className="admin-header__user-dropdown-item admin-header__user-dropdown-item--danger">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M6 2H10M2 4H14M12 4V13C12 13.5523 11.5523 14 11 14H5C4.44772 14 4 13.5523 4 13V4M6 7V11M10 7V11"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default AdminHeader;
