import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './TenantRegistration.css';

interface TenantRegistrationData {
  name: string;
  admin_email: string;
  admin_password: string;
  admin_first_name: string;
  admin_last_name: string;
  phone_number: string;
  address: string;
  website: string;
}

interface TenantRegistrationResponse {
  id: string;
  name: string;
  created_at: string;
  admin_user_id: string;
  admin_email: string;
}

const TenantRegistration: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<TenantRegistrationData>({
    name: '',
    admin_email: '',
    admin_password: '',
    admin_first_name: '',
    admin_last_name: '',
    phone_number: '',
    address: '',
    website: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Practice name is required');
      return false;
    }
    if (!formData.admin_email.trim()) {
      setError('Admin email is required');
      return false;
    }
    if (!formData.admin_password || formData.admin_password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (!formData.admin_first_name.trim()) {
      setError('Admin first name is required');
      return false;
    }
    if (!formData.admin_last_name.trim()) {
      setError('Admin last name is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/tenants/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create practice');
      }

      const result: TenantRegistrationResponse = await response.json();
      
      setSuccess(`Practice "${result.name}" created successfully! You can now sign in with your admin credentials.`);
      
      // Redirect to login page after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while creating the practice');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tenant-registration">
      <div className="registration-container">
        <div className="registration-header">
          <h1>🏥 Register Your Dental Practice</h1>
          <p>Create your practice account and get started with our AI-powered patient management system.</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-section">
            <h3>Practice Information</h3>
            
            <div className="form-group">
              <label htmlFor="name">Practice Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Bright Smile Dental Care"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone_number">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                placeholder="(555) 123-4567"
              />
            </div>

            <div className="form-group">
              <label htmlFor="address">Business Address</label>
              <textarea
                id="address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="123 Main St, City, State 12345"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="website">Website</label>
              <input
                type="url"
                id="website"
                name="website"
                value={formData.website}
                onChange={handleInputChange}
                placeholder="https://www.yourpractice.com"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Admin Account</h3>
            <p className="section-description">
              This will be your administrator account for managing the practice.
            </p>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="admin_first_name">First Name *</label>
                <input
                  type="text"
                  id="admin_first_name"
                  name="admin_first_name"
                  value={formData.admin_first_name}
                  onChange={handleInputChange}
                  placeholder="John"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="admin_last_name">Last Name *</label>
                <input
                  type="text"
                  id="admin_last_name"
                  name="admin_last_name"
                  value={formData.admin_last_name}
                  onChange={handleInputChange}
                  placeholder="Smith"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="admin_email">Email Address *</label>
              <input
                type="email"
                id="admin_email"
                name="admin_email"
                value={formData.admin_email}
                onChange={handleInputChange}
                placeholder="admin@yourpractice.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="admin_password">Password *</label>
              <input
                type="password"
                id="admin_password"
                name="admin_password"
                value={formData.admin_password}
                onChange={handleInputChange}
                placeholder="Minimum 8 characters"
                required
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">❌</span>
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              <span className="success-icon">✅</span>
              {success}
            </div>
          )}

          <div className="form-actions">
            <button
              type="submit"
              className="submit-button"
              disabled={isLoading}
            >
              {isLoading ? 'Creating Practice...' : 'Create Practice'}
            </button>
          </div>
        </form>

        <div className="registration-footer">
          <p>
            Already have an account?{' '}
            <a href="/login" className="login-link">Sign in here</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default TenantRegistration;
