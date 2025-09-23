/**
 * Dashboard Overview Component
 * 
 * Comprehensive overview with key metrics, charts, and system status.
 * Inspired by ngrok dashboard's clean and informative design.
 */

import React, { useState, useEffect } from 'react';
import './DashboardOverview.css';

interface Metric {
  id: string;
  label: string;
  value: string | number;
  change: number;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: string;
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

interface SystemStatus {
  service: string;
  status: 'operational' | 'degraded' | 'outage';
  uptime: string;
  responseTime: string;
}

const DashboardOverview: React.FC = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMetrics([
        {
          id: 'active-tenants',
          label: 'Active Tenants',
          value: 12,
          change: 8.2,
          changeType: 'positive',
          icon: 'business',
          color: 'primary'
        },
        {
          id: 'total-calls',
          label: 'Total Calls Today',
          value: '2,847',
          change: 12.5,
          changeType: 'positive',
          icon: 'phone',
          color: 'success'
        },
        {
          id: 'success-rate',
          label: 'Success Rate',
          value: '94.2%',
          change: -2.1,
          changeType: 'negative',
          icon: 'check_circle',
          color: 'warning'
        },
        {
          id: 'revenue',
          label: 'Monthly Revenue',
          value: '$24,580',
          change: 15.3,
          changeType: 'positive',
          icon: 'account_balance_wallet',
          color: 'success'
        },
        {
          id: 'active-assistants',
          label: 'Active Assistants',
          value: 8,
          change: 0,
          changeType: 'neutral',
          icon: 'smart_toy',
          color: 'info'
        },
        {
          id: 'avg-response-time',
          label: 'Avg Response Time',
          value: '1.2s',
          change: -0.3,
          changeType: 'positive',
          icon: 'speed',
          color: 'primary'
        }
      ]);

      setSystemStatus([
        {
          service: 'API Gateway',
          status: 'operational',
          uptime: '99.9%',
          responseTime: '45ms'
        },
        {
          service: 'Database',
          status: 'operational',
          uptime: '99.8%',
          responseTime: '12ms'
        },
        {
          service: 'Voice AI Service',
          status: 'operational',
          uptime: '99.7%',
          responseTime: '1.2s'
        },
        {
          service: 'Google Calendar API',
          status: 'degraded',
          uptime: '98.5%',
          responseTime: '2.1s'
        },
        {
          service: 'File Storage',
          status: 'operational',
          uptime: '99.9%',
          responseTime: '89ms'
        }
      ]);

      setIsLoading(false);
    };

    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="dashboard-overview">
        <div className="dashboard-overview__loading">
          <div className="admin-dashboard__loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-overview">
      {/* Header */}
      <div className="dashboard-overview__header">
        <div>
          <h1>Dashboard Overview</h1>
          <p>Welcome back! Here's what's happening with your system today.</p>
        </div>
        <div className="dashboard-overview__header-actions">
          <button className="admin-btn admin-btn--secondary admin-btn--sm">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M8 0L10.5 5.5L16 8L10.5 10.5L8 16L5.5 10.5L0 8L5.5 5.5L8 0Z"
                stroke="currentColor"
                strokeWidth="2"
              />
            </svg>
            Refresh
          </button>
          <button className="admin-btn admin-btn--primary admin-btn--sm">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M8 0V16M0 8H16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            Export Report
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="dashboard-overview__metrics">
        {metrics.map((metric) => (
          <div key={metric.id} className="admin-metric">
            <div className="admin-metric__icon">
              <span className={`admin-metric__icon-symbol admin-metric__icon-symbol--${metric.color}`}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  {metric.icon === 'business' && (
                    <path d="M12 7V3H2V21H22V7H12ZM6 19H4V17H6V19ZM6 15H4V13H6V15ZM6 11H4V9H6V11ZM6 7H4V5H6V7ZM10 19H8V17H10V19ZM10 15H8V13H10V15ZM10 11H8V9H10V11ZM10 7H8V5H10V7ZM20 19H12V17H14V15H12V13H14V11H12V9H20V19ZM18 11H16V13H18V11ZM18 15H16V17H18V15Z" fill="currentColor"/>
                  )}
                  {metric.icon === 'phone' && (
                    <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="currentColor"/>
                  )}
                  {metric.icon === 'check_circle' && (
                    <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="currentColor"/>
                  )}
                  {metric.icon === 'account_balance_wallet' && (
                    <path d="M21 18V19C21 20.1 20.1 21 19 21H5C3.89 21 3 20.1 3 19V5C3 3.9 3.89 3 5 3H19C20.1 3 21 3.9 21 5V6H12C10.9 6 10 6.9 10 8V16C10 17.1 10.9 18 12 18H21ZM12 16V8H22V16H12ZM16 13.5C15.17 13.5 14.5 12.83 14.5 12S15.17 10.5 16 10.5 17.5 11.17 17.5 12 16.83 13.5 16 13.5Z" fill="currentColor"/>
                  )}
                  {metric.icon === 'smart_toy' && (
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 9H14V4H19V9Z" fill="currentColor"/>
                  )}
                  {metric.icon === 'speed' && (
                    <path d="M20.38 8.57L19.1 7.29C17.9 6.09 16.3 5.5 14.65 5.5C13 5.5 11.4 6.09 10.2 7.29L8.92 8.57C8.53 8.96 8.53 9.59 8.92 9.98C9.31 10.37 9.94 10.37 10.33 9.98L11.61 8.7C12.4 7.91 13.5 7.5 14.65 7.5C15.8 7.5 16.9 7.91 17.69 8.7L18.97 9.98C19.36 10.37 19.99 10.37 20.38 9.98C20.77 9.59 20.77 8.96 20.38 8.57ZM12 18C13.1 18 14 17.1 14 16C14 14.9 13.1 14 12 14C10.9 14 10 14.9 10 16C10 17.1 10.9 18 12 18ZM12 20C9.79 20 8 18.21 8 16C8 13.79 9.79 12 12 12C14.21 12 16 13.79 16 16C16 18.21 14.21 20 12 20Z" fill="currentColor"/>
                  )}
                </svg>
              </span>
            </div>
            <div className="admin-metric__value">{metric.value}</div>
            <div className="admin-metric__label">{metric.label}</div>
            <div className={`admin-metric__change admin-metric__change--${metric.changeType}`}>
              {metric.change > 0 && '+'}
              {metric.change}%
              <span className="admin-metric__change-period">vs last month</span>
            </div>
          </div>
        ))}
      </div>

      {/* Content Grid */}
      <div className="dashboard-overview__content">
        {/* System Status */}
        <div className="admin-card">
          <div className="admin-card__header">
            <h3 className="admin-card__title">System Status</h3>
            <div className="admin-status admin-status--success">
              All Systems Operational
            </div>
          </div>
          <div className="admin-card__content">
            <div className="system-status">
              {systemStatus.map((service, index) => (
                <div key={index} className="system-status__item">
                  <div className="system-status__service">
                    <div className="system-status__name">{service.service}</div>
                    <div className={`system-status__status system-status__status--${service.status}`}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        {service.status === 'operational' && (
                          <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
                        )}
                        {service.status === 'degraded' && (
                          <path d="M1 21H23L12 2L1 21ZM13 18H11V16H13V18ZM13 14H11V10H13V14Z" fill="currentColor"/>
                        )}
                        {service.status === 'outage' && (
                          <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
                        )}
                      </svg>
                      {service.status}
                    </div>
                  </div>
                  <div className="system-status__metrics">
                    <div className="system-status__metric">
                      <span className="system-status__metric-label">Uptime</span>
                      <span className="system-status__metric-value">{service.uptime}</span>
                    </div>
                    <div className="system-status__metric">
                      <span className="system-status__metric-label">Response</span>
                      <span className="system-status__metric-value">{service.responseTime}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="admin-card">
          <div className="admin-card__header">
            <h3 className="admin-card__title">Recent Activity</h3>
            <button className="admin-btn admin-btn--secondary admin-btn--sm">
              View All
            </button>
          </div>
          <div className="admin-card__content">
            <div className="recent-activity">
              <div className="recent-activity__item">
                <div className="recent-activity__icon recent-activity__icon--success">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="recent-activity__content">
                  <div className="recent-activity__title">New tenant registered</div>
                  <div className="recent-activity__description">
                    Dental Care Plus completed onboarding process
                  </div>
                  <div className="recent-activity__time">2 minutes ago</div>
                </div>
              </div>
              <div className="recent-activity__item">
                <div className="recent-activity__icon recent-activity__icon--warning">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 21H23L12 2L1 21ZM13 18H11V16H13V18ZM13 14H11V10H13V14Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="recent-activity__content">
                  <div className="recent-activity__title">High CPU usage detected</div>
                  <div className="recent-activity__description">
                    Server-03 showing 85% CPU utilization
                  </div>
                  <div className="recent-activity__time">15 minutes ago</div>
                </div>
              </div>
              <div className="recent-activity__item">
                <div className="recent-activity__icon recent-activity__icon--info">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="recent-activity__content">
                  <div className="recent-activity__title">Payment processed</div>
                  <div className="recent-activity__description">
                    Monthly subscription payment received from Smile Dental
                  </div>
                  <div className="recent-activity__time">1 hour ago</div>
                </div>
              </div>
              <div className="recent-activity__item">
                <div className="recent-activity__icon recent-activity__icon--success">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="recent-activity__content">
                  <div className="recent-activity__title">Assistant updated</div>
                  <div className="recent-activity__description">
                    Voice AI assistant configuration updated for City Dental
                  </div>
                  <div className="recent-activity__time">2 hours ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-overview__actions">
        <div className="admin-card">
          <div className="admin-card__header">
            <h3 className="admin-card__title">Quick Actions</h3>
          </div>
          <div className="admin-card__content">
            <div className="quick-actions">
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 7V3H2V21H22V7H12ZM6 19H4V17H6V19ZM6 15H4V13H6V15ZM6 11H4V9H6V11ZM6 7H4V5H6V7ZM10 19H8V17H10V19ZM10 15H8V13H10V15ZM10 11H8V9H10V11ZM10 7H8V5H10V7ZM20 19H12V17H14V15H12V13H14V11H12V9H20V19ZM18 11H16V13H18V11ZM18 15H16V17H18V15Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">Add New Tenant</div>
              </button>
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 4C18.21 4 20 5.79 20 8C20 10.21 18.21 12 16 12C13.79 12 12 10.21 12 8C12 5.79 13.79 4 16 4ZM16 14C18.67 14 24 15.34 24 18V20H8V18C8 15.34 13.33 14 16 14ZM8 4C10.21 4 12 5.79 12 8C12 10.21 10.21 12 8 12C5.79 12 4 10.21 4 8C4 5.79 5.79 4 8 4ZM8 14C10.67 14 16 15.34 16 18V20H0V18C0 15.34 5.33 14 8 14Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">Create User</div>
              </button>
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 9H14V4H19V9Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">Configure Assistant</div>
              </button>
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM9 17H7V10H9V17ZM13 17H11V7H13V17ZM17 17H15V13H17V17Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">View Analytics</div>
              </button>
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,16.6 15.6,17 15,17H9C8.4,17 8,16.6 8,16V13C8,12.4 8.4,11.5 9,11.5V10C9,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.2,9.2 10.2,10V11.5H13.8V10C13.8,9.2 12.8,8.2 12,8.2Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">Security Audit</div>
              </button>
              <button className="quick-actions__item">
                <div className="quick-actions__icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.14,12.94C19.18,12.64 19.2,12.33 19.2,12C19.2,11.67 19.18,11.36 19.14,11.06L21.16,9.48C21.34,9.34 21.39,9.07 21.28,8.87L19.36,5.44C19.24,5.24 18.99,5.17 18.77,5.25L16.38,6.05C16.04,5.66 15.66,5.28 15.27,4.94L15.07,2.47C15.05,2.24 14.87,2.05 14.64,2.05H9.36C9.13,2.05 8.95,2.24 8.93,2.47L8.73,4.94C8.34,5.28 7.96,5.66 7.62,6.05L5.23,5.25C5.01,5.17 4.76,5.24 4.64,5.44L2.72,8.87C2.61,9.07 2.66,9.34 2.84,9.48L4.86,11.06C4.82,11.36 4.8,11.67 4.8,12C4.8,12.33 4.82,12.64 4.86,12.94L2.84,14.52C2.66,14.66 2.61,14.93 2.72,15.13L4.64,18.56C4.76,18.76 5.01,18.83 5.23,18.75L7.62,17.95C7.96,18.34 8.34,18.72 8.73,19.06L8.93,21.53C8.95,21.76 9.13,21.95 9.36,21.95H14.64C14.87,21.95 15.05,21.76 15.07,21.53L15.27,19.06C15.66,18.72 16.04,18.34 16.38,17.95L18.77,18.75C18.99,18.83 19.24,18.76 19.36,18.56L21.28,15.13C21.39,14.93 21.34,14.66 21.16,14.52L19.14,12.94ZM12,15.6C10.02,15.6 8.4,13.98 8.4,12C8.4,10.02 10.02,8.4 12,8.4C13.98,8.4 15.6,10.02 15.6,12C15.6,13.98 13.98,15.6 12,15.6Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="quick-actions__label">System Settings</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
