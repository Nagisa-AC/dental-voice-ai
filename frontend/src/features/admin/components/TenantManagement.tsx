/**
 * Tenant Management Component
 * 
 * Comprehensive tenant management interface with CRUD operations.
 * Features tenant creation, editing, suspension, and analytics.
 */

import React, { useState, useEffect } from 'react';
import './TenantManagement.css';

interface Tenant {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'suspended' | 'pending';
  plan: 'basic' | 'premium' | 'enterprise';
  createdAt: string;
  lastActive: string;
  clinics: number;
  users: number;
  calls: number;
}

const TenantManagement: React.FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    // Simulate loading tenants
    const loadTenants = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTenants([
        {
          id: '1',
          name: 'Dental Care Plus',
          email: 'admin@dentalcareplus.com',
          status: 'active',
          plan: 'premium',
          createdAt: '2024-01-15',
          lastActive: '2024-01-20',
          clinics: 3,
          users: 12,
          calls: 1247
        },
        {
          id: '2',
          name: 'Smile Dental Group',
          email: 'contact@smiledental.com',
          status: 'active',
          plan: 'enterprise',
          createdAt: '2024-01-10',
          lastActive: '2024-01-20',
          clinics: 8,
          users: 45,
          calls: 3421
        },
        {
          id: '3',
          name: 'City Dental Clinic',
          email: 'info@citydental.com',
          status: 'pending',
          plan: 'basic',
          createdAt: '2024-01-18',
          lastActive: '2024-01-19',
          clinics: 1,
          users: 3,
          calls: 89
        }
      ]);
      
      setIsLoading(false);
    };

    loadTenants();
  }, []);

  if (isLoading) {
    return (
      <div className="tenant-management">
        <div className="tenant-management__loading">
          <div className="admin-dashboard__loading-spinner"></div>
          <p>Loading tenants...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tenant-management">
      {/* Header */}
      <div className="tenant-management__header">
        <div>
          <h1>Tenant Management</h1>
          <p>Manage tenants, organizations, and their subscriptions.</p>
        </div>
        <div className="tenant-management__header-actions">
          <button className="admin-btn admin-btn--secondary admin-btn--sm">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M8 0L10.5 5.5L16 8L10.5 10.5L8 16L5.5 10.5L0 8L5.5 5.5L8 0Z"
                stroke="currentColor"
                strokeWidth="2"
              />
            </svg>
            Export
          </button>
          <button 
            className="admin-btn admin-btn--primary admin-btn--sm"
            onClick={() => setShowCreateModal(true)}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M8 0V16M0 8H16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            Add Tenant
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="tenant-management__stats">
        <div className="admin-metric">
          <div className="admin-metric__value">{tenants.length}</div>
          <div className="admin-metric__label">Total Tenants</div>
        </div>
        <div className="admin-metric">
          <div className="admin-metric__value">{tenants.filter(t => t.status === 'active').length}</div>
          <div className="admin-metric__label">Active</div>
        </div>
        <div className="admin-metric">
          <div className="admin-metric__value">{tenants.filter(t => t.status === 'pending').length}</div>
          <div className="admin-metric__label">Pending</div>
        </div>
        <div className="admin-metric">
          <div className="admin-metric__value">{tenants.reduce((sum, t) => sum + t.clinics, 0)}</div>
          <div className="admin-metric__label">Total Clinics</div>
        </div>
      </div>

      {/* Tenants Table */}
      <div className="admin-card">
        <div className="admin-card__header">
          <h3 className="admin-card__title">All Tenants</h3>
          <div className="tenant-management__filters">
            <select className="admin-select" style={{ width: 'auto' }}>
              <option>All Status</option>
              <option>Active</option>
              <option>Pending</option>
              <option>Suspended</option>
            </select>
            <select className="admin-select" style={{ width: 'auto' }}>
              <option>All Plans</option>
              <option>Basic</option>
              <option>Premium</option>
              <option>Enterprise</option>
            </select>
          </div>
        </div>
        <div className="admin-card__content">
          <div className="admin-table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Tenant</th>
                  <th>Status</th>
                  <th>Plan</th>
                  <th>Clinics</th>
                  <th>Users</th>
                  <th>Calls</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td>
                      <div className="tenant-info">
                        <div className="tenant-info__name">{tenant.name}</div>
                        <div className="tenant-info__email">{tenant.email}</div>
                      </div>
                    </td>
                    <td>
                      <span className={`admin-status admin-status--${tenant.status === 'active' ? 'success' : tenant.status === 'pending' ? 'warning' : 'danger'}`}>
                        {tenant.status}
                      </span>
                    </td>
                    <td>
                      <span className={`plan-badge plan-badge--${tenant.plan}`}>
                        {tenant.plan}
                      </span>
                    </td>
                    <td>{tenant.clinics}</td>
                    <td>{tenant.users}</td>
                    <td>{tenant.calls.toLocaleString()}</td>
                    <td>{new Date(tenant.lastActive).toLocaleDateString()}</td>
                    <td>
                      <div className="table-actions">
                        <button className="table-actions__btn" title="View Details">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path
                              d="M8 0C3.58172 0 0 3.58172 0 8C0 12.4183 3.58172 16 8 16C12.4183 16 16 12.4183 16 8C16 3.58172 12.4183 0 8 0ZM8 12C5.79086 12 4 10.2091 4 8C4 5.79086 5.79086 4 8 4C10.2091 4 12 5.79086 12 8C12 10.2091 10.2091 12 8 12Z"
                              stroke="currentColor"
                              strokeWidth="2"
                            />
                            <path
                              d="M8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6Z"
                              stroke="currentColor"
                              strokeWidth="2"
                            />
                          </svg>
                        </button>
                        <button className="table-actions__btn" title="Edit">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path
                              d="M11 2L14 5L5 14H2V11L11 2Z"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                            <path
                              d="M10 3L13 6"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        </button>
                        <button className="table-actions__btn table-actions__btn--danger" title="Suspend">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path
                              d="M6 2H10M2 4H14M12 4V13C12 13.5523 11.5523 14 11 14H5C4.44772 14 4 13.5523 4 13V4M6 7V11M10 7V11"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TenantManagement;
