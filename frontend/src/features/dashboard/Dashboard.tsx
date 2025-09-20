import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../common/contexts/AuthContext';
import { Button, Card } from '../../common';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🏥 Healthcare Voice AI Dashboard</h1>
          <div className="user-info">
            <span className="user-role">{user?.role || 'User'}</span>
            <Button 
              onClick={handleLogout} 
              variant="outline" 
              size="sm"
              aria-label="Logout from your account"
            >
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="container">
          {/* Overview Cards */}
          <section className="overview-section">
            <h2>Overview</h2>
            <div className="overview-cards">
              <Card className="overview-card" padding="medium">
                <div className="card-icon" aria-hidden="true">📊</div>
                <div className="card-content">
                  <h3>1,234</h3>
                  <p>Total Appointments</p>
                  <span className="trend positive" aria-label="12% increase this month">+12% this month</span>
                </div>
              </Card>
              
              <Card className="overview-card" padding="medium">
                <div className="card-icon" aria-hidden="true">👥</div>
                <div className="card-content">
                  <h3>856</h3>
                  <p>Active Patients</p>
                  <span className="trend positive" aria-label="8% increase this month">+8% this month</span>
                </div>
              </Card>
              
              <Card className="overview-card" padding="medium">
                <div className="card-icon" aria-hidden="true">💰</div>
                <div className="card-content">
                  <h3>$45,678</h3>
                  <p>Monthly Revenue</p>
                  <span className="trend positive" aria-label="15% increase">+15%</span>
                </div>
              </Card>
              
              <Card className="overview-card" padding="medium">
                <div className="card-icon" aria-hidden="true">🤖</div>
                <div className="card-content">
                  <h3>94.2%</h3>
                  <p>AI Success Rate</p>
                  <span className="trend positive" aria-label="2% increase">+2%</span>
                </div>
              </Card>
            </div>
          </section>

          {/* Charts Section */}
          <section className="charts-section">
            <div className="chart-row">
              <div className="chart-card large">
                <h3>Appointment Trends</h3>
                <div className="chart-placeholder">
                  <p>📈 Line chart showing appointment trends over time</p>
                  <p>Mock data: Daily appointments, cancellations, no-shows</p>
                </div>
              </div>
              
              <div className="chart-card small">
                <h3>System Health</h3>
                <div className="health-status">
                  <div className="health-item">
                    <span className="status-icon healthy">✅</span>
                    <div>
                      <strong>API Server</strong>
                      <p>All systems operational</p>
                    </div>
                  </div>
                  <div className="health-item">
                    <span className="status-icon healthy">✅</span>
                    <div>
                      <strong>Database</strong>
                      <p>Connection stable</p>
                    </div>
                  </div>
                  <div className="health-item">
                    <span className="status-icon warning">⚠️</span>
                    <div>
                      <strong>VAPI Integration</strong>
                      <p>High response time detected</p>
                    </div>
                  </div>
                  <div className="health-item">
                    <span className="status-icon healthy">✅</span>
                    <div>
                      <strong>AI Assistant</strong>
                      <p>Processing requests normally</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="chart-row">
              <div className="chart-card">
                <h3>Patient Engagement</h3>
                <div className="chart-placeholder">
                  <p>🥧 Pie chart showing patient engagement levels</p>
                  <p>Highly Engaged: 45% | Moderately Engaged: 35% | Low Engagement: 20%</p>
                </div>
              </div>
              
              <div className="chart-card">
                <h3>Revenue Analysis</h3>
                <div className="chart-placeholder">
                  <p>📊 Bar chart displaying monthly revenue trends</p>
                  <p>Revenue: $45k-$61k | Expenses: $28k-$35k | Profit: $17k-$26k</p>
                </div>
              </div>
            </div>
            
            <div className="chart-card full-width">
              <h3>AI Performance Metrics</h3>
              <div className="chart-placeholder">
                <p>📈 Line chart tracking AI performance over time</p>
                <p>Success Rate: 91-96% | Response Time: 0.9-1.3s | Satisfaction: 4.4-4.8/5</p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;