/**
 * Admin Dashboard Component
 * 
 * Comprehensive admin dashboard inspired by ngrok's elegant design.
 * Features real-time monitoring, tenant management, and system controls.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import AdminSidebar from './components/AdminSidebar';
import AdminHeader from './components/AdminHeader';
import DashboardOverview from './components/DashboardOverview';
import TenantManagement from './components/TenantManagement';
import UserManagement from './components/UserManagement';
import AssistantManagement from './components/AssistantManagement';
import SystemMonitoring from './components/SystemMonitoring';
import BillingManagement from './components/BillingManagement';
import SecurityCenter from './components/SecurityCenter';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SettingsPanel from './components/SettingsPanel';
import './AdminDashboard.css';

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

interface AdminDashboardProps {
  className?: string;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ className = '' }) => {
  const { user, isAuthenticated } = useAuth();
  const [activeView, setActiveView] = useState<AdminView>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  // Check admin permissions
  useEffect(() => {
    if (isAuthenticated && user?.role !== 'admin' && user?.role !== 'super_admin') {
      // Redirect non-admin users
      window.location.href = '/dashboard';
    }
  }, [isAuthenticated, user]);

  if (!isAuthenticated) {
    return (
      <div className="admin-dashboard admin-dashboard--loading">
        <div className="admin-dashboard__loading">
          <div className="admin-dashboard__loading-spinner"></div>
          <p>Authenticating...</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="admin-dashboard admin-dashboard--loading">
        <div className="admin-dashboard__loading">
          <div className="admin-dashboard__loading-spinner"></div>
          <p>Loading Admin Dashboard...</p>
        </div>
      </div>
    );
  }

  const renderActiveView = () => {
    switch (activeView) {
      case 'overview':
        return <DashboardOverview />;
      case 'tenants':
        return <TenantManagement />;
      case 'users':
        return <UserManagement />;
      case 'assistants':
        return <AssistantManagement />;
      case 'monitoring':
        return <SystemMonitoring />;
      case 'billing':
        return <BillingManagement />;
      case 'security':
        return <SecurityCenter />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <DashboardOverview />;
    }
  };

  return (
    <div className={`admin-dashboard ${className}`}>
      {/* Sidebar */}
      <AdminSidebar
        activeView={activeView}
        onViewChange={setActiveView}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div className={`admin-dashboard__main ${sidebarCollapsed ? 'admin-dashboard__main--collapsed' : ''}`}>
        {/* Header */}
        <AdminHeader
          user={user}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Content */}
        <main className="admin-dashboard__content">
          <div className="admin-dashboard__content-inner">
            {renderActiveView()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
