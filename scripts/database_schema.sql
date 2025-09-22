-- Healthcare Voice AI - Complete Database Schema
-- Generated from consolidated SQLAlchemy models
-- This script represents the complete database structure

-- =============================================================================
-- USERS TABLE
-- =============================================================================
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'readonly',
    tenant_id VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Users indexes
CREATE INDEX idx_users_email_active ON users (email, is_active);
CREATE INDEX idx_users_role_active ON users (role, is_active);
CREATE INDEX idx_users_tenant_active ON users (tenant_id, is_active);
CREATE INDEX idx_users_created_at ON users (created_at);
CREATE INDEX idx_users_last_login ON users (last_login);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_role ON users (role);
CREATE INDEX ix_users_tenant_id ON users (tenant_id);

-- =============================================================================
-- REFRESH TOKENS TABLE
-- =============================================================================
CREATE TABLE refresh_tokens (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    revoked_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Refresh tokens indexes
CREATE INDEX idx_refresh_tokens_user_expires ON refresh_tokens (user_id, expires_at);
CREATE INDEX idx_refresh_tokens_expires_revoked ON refresh_tokens (expires_at, is_revoked);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens (token_hash);
CREATE INDEX idx_refresh_tokens_created_at ON refresh_tokens (created_at);
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX ix_refresh_tokens_expires_at ON refresh_tokens (expires_at);
CREATE INDEX ix_refresh_tokens_is_revoked ON refresh_tokens (is_revoked);
CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON refresh_tokens (token_hash);

-- =============================================================================
-- CLINICS TABLE
-- =============================================================================
CREATE TABLE clinics (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    industry_type VARCHAR(50) NOT NULL DEFAULT 'dental',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    website VARCHAR(200),
    business_hours JSON,
    services JSON,
    policies JSON,
    vapi_assistant_id VARCHAR(100),
    assistant_config JSON,
    faq_content TEXT,
    faq_filename VARCHAR(255),
    admin_notes TEXT,
    approved_by VARCHAR,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Clinics indexes
CREATE INDEX idx_clinics_tenant_status ON clinics (tenant_id, status);
CREATE INDEX idx_clinics_industry_status ON clinics (industry_type, status);
CREATE INDEX idx_clinics_phone_email ON clinics (phone, email);
CREATE INDEX idx_clinics_created_status ON clinics (created_at, status);
CREATE INDEX idx_clinics_updated_at ON clinics (updated_at);
CREATE INDEX idx_clinics_approved_by ON clinics (approved_by);
CREATE INDEX idx_clinics_vapi_assistant_id ON clinics (vapi_assistant_id);
CREATE UNIQUE INDEX ix_clinics_tenant_id ON clinics (tenant_id);
CREATE INDEX ix_clinics_name ON clinics (name);
CREATE INDEX ix_clinics_industry_type ON clinics (industry_type);
CREATE INDEX ix_clinics_status ON clinics (status);
CREATE INDEX ix_clinics_phone ON clinics (phone);
CREATE INDEX ix_clinics_email ON clinics (email);
CREATE INDEX ix_clinics_vapi_assistant_id ON clinics (vapi_assistant_id);

-- =============================================================================
-- ASSISTANTS TABLE
-- =============================================================================
CREATE TABLE assistants (
    id VARCHAR PRIMARY KEY,
    clinic_id VARCHAR NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    vapi_assistant_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    model_id VARCHAR(50) NOT NULL,
    voice_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE
);

-- Assistants indexes
CREATE INDEX idx_assistants_clinic_status ON assistants (clinic_id, status);
CREATE INDEX idx_assistants_tenant_status ON assistants (tenant_id, status);
CREATE INDEX idx_assistants_vapi_id ON assistants (vapi_assistant_id);
CREATE INDEX idx_assistants_created ON assistants (created_at);
CREATE INDEX idx_assistants_updated_at ON assistants (updated_at);
CREATE INDEX idx_assistants_name ON assistants (name);
CREATE INDEX ix_assistants_clinic_id ON assistants (clinic_id);
CREATE INDEX ix_assistants_tenant_id ON assistants (tenant_id);
CREATE UNIQUE INDEX ix_assistants_vapi_assistant_id ON assistants (vapi_assistant_id);
CREATE INDEX ix_assistants_name ON assistants (name);
CREATE INDEX ix_assistants_status ON assistants (status);

-- =============================================================================
-- AUDIT LOGS TABLE
-- =============================================================================
CREATE TABLE audit_logs (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    clinic_id VARCHAR,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Audit logs indexes
CREATE INDEX idx_audit_logs_user_action ON audit_logs (user_id, action);
CREATE INDEX idx_audit_logs_clinic_action ON audit_logs (clinic_id, action);
CREATE INDEX idx_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_action ON audit_logs (created_at, action);
CREATE INDEX idx_audit_logs_ip_created ON audit_logs (ip_address, created_at);
CREATE INDEX idx_audit_logs_user_created ON audit_logs (user_id, created_at);
CREATE INDEX idx_audit_logs_clinic_created ON audit_logs (clinic_id, created_at);
CREATE INDEX idx_audit_logs_action_resource ON audit_logs (action, resource_type);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX ix_audit_logs_clinic_id ON audit_logs (clinic_id);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_logs_resource_type ON audit_logs (resource_type);
CREATE INDEX ix_audit_logs_resource_id ON audit_logs (resource_id);
CREATE INDEX ix_audit_logs_ip_address ON audit_logs (ip_address);
CREATE INDEX ix_audit_logs_request_id ON audit_logs (request_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);

-- =============================================================================
-- FILE UPLOADS TABLE
-- =============================================================================
CREATE TABLE file_uploads (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    clinic_id VARCHAR,
    original_filename VARCHAR(255) NOT NULL,
    secure_filename VARCHAR(255) UNIQUE NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded',
    is_quarantined BOOLEAN NOT NULL DEFAULT FALSE,
    quarantine_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- File uploads indexes
CREATE INDEX idx_file_uploads_user_status ON file_uploads (user_id, status);
CREATE INDEX idx_file_uploads_clinic_status ON file_uploads (clinic_id, status);
CREATE INDEX idx_file_uploads_hash ON file_uploads (file_hash);
CREATE INDEX idx_file_uploads_type_status ON file_uploads (file_type, status);
CREATE INDEX idx_file_uploads_quarantined ON file_uploads (is_quarantined, created_at);
CREATE INDEX ix_file_uploads_user_id ON file_uploads (user_id);
CREATE INDEX ix_file_uploads_clinic_id ON file_uploads (clinic_id);
CREATE UNIQUE INDEX ix_file_uploads_secure_filename ON file_uploads (secure_filename);
CREATE INDEX ix_file_uploads_file_hash ON file_uploads (file_hash);
CREATE INDEX ix_file_uploads_file_type ON file_uploads (file_type);
CREATE INDEX ix_file_uploads_status ON file_uploads (status);
CREATE INDEX ix_file_uploads_is_quarantined ON file_uploads (is_quarantined);

-- =============================================================================
-- CSRF TOKENS TABLE
-- =============================================================================
CREATE TABLE csrf_tokens (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    used_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- CSRF tokens indexes
CREATE INDEX idx_csrf_tokens_user_expires ON csrf_tokens (user_id, expires_at);
CREATE INDEX idx_csrf_tokens_expires_used ON csrf_tokens (expires_at, is_used);
CREATE INDEX idx_csrf_tokens_created ON csrf_tokens (created_at);
CREATE INDEX ix_csrf_tokens_user_id ON csrf_tokens (user_id);
CREATE UNIQUE INDEX ix_csrf_tokens_token_hash ON csrf_tokens (token_hash);
CREATE INDEX ix_csrf_tokens_is_used ON csrf_tokens (is_used);
CREATE INDEX ix_csrf_tokens_expires_at ON csrf_tokens (expires_at);

-- =============================================================================
-- RATE LIMITS TABLE
-- =============================================================================
CREATE TABLE rate_limits (
    id VARCHAR PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    window_start DATETIME NOT NULL,
    window_end DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Rate limits indexes
CREATE INDEX idx_rate_limits_key_endpoint ON rate_limits (key, endpoint);
CREATE INDEX idx_rate_limits_window ON rate_limits (window_start, window_end);
CREATE INDEX idx_rate_limits_created ON rate_limits (created_at);
CREATE INDEX ix_rate_limits_key ON rate_limits (key);
CREATE INDEX ix_rate_limits_endpoint ON rate_limits (endpoint);
CREATE INDEX ix_rate_limits_method ON rate_limits (method);
CREATE INDEX ix_rate_limits_window_start ON rate_limits (window_start);
CREATE INDEX ix_rate_limits_window_end ON rate_limits (window_end);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Users table trigger
CREATE TRIGGER users_updated_at 
    AFTER UPDATE ON users
    FOR EACH ROW
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Clinics table trigger
CREATE TRIGGER clinics_updated_at 
    AFTER UPDATE ON clinics
    FOR EACH ROW
    BEGIN
        UPDATE clinics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Assistants table trigger
CREATE TRIGGER assistants_updated_at 
    AFTER UPDATE ON assistants
    FOR EACH ROW
    BEGIN
        UPDATE assistants SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- File uploads table trigger
CREATE TRIGGER file_uploads_updated_at 
    AFTER UPDATE ON file_uploads
    FOR EACH ROW
    BEGIN
        UPDATE file_uploads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Rate limits table trigger
CREATE TRIGGER rate_limits_updated_at 
    AFTER UPDATE ON rate_limits
    FOR EACH ROW
    BEGIN
        UPDATE rate_limits SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================

-- Insert sample admin user
INSERT INTO users (id, username, email, password_hash, role, is_active, is_verified) 
VALUES (
    'admin-001',
    'admin',
    'admin@healthcarevoiceai.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2K', -- 'admin123'
    'super_admin',
    TRUE,
    TRUE
);

-- Insert sample clinic
INSERT INTO clinics (
    id, tenant_id, name, industry_type, status, phone, email, address, website,
    business_hours, services, policies, approved_by, approved_at
) VALUES (
    'clinic-001',
    'test-clinic-001',
    'Test Dental Practice',
    'dental',
    'approved',
    '(555) 123-4567',
    'info@testdental.com',
    '123 Main St, Chicago, IL 60601',
    'https://testdental.com',
    '{"monday": {"open": "09:00", "close": "17:00"}, "tuesday": {"open": "09:00", "close": "17:00"}, "wednesday": {"open": "09:00", "close": "17:00"}, "thursday": {"open": "09:00", "close": "17:00"}, "friday": {"open": "09:00", "close": "15:00"}, "saturday": {"open": "09:00", "close": "12:00"}, "sunday": {"closed": true}}',
    '[{"name": "General Checkup", "duration_minutes": 60, "price": 150.00}, {"name": "Teeth Cleaning", "duration_minutes": 45, "price": 120.00}, {"name": "Cavity Filling", "duration_minutes": 90, "price": 200.00}]',
    '{"cancellation_policy": "24 hours notice required", "no_show_policy": "Fee may apply for missed appointments", "payment_policy": "Payment due at time of service"}',
    'admin-001',
    CURRENT_TIMESTAMP
);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active users view
CREATE VIEW active_users AS
SELECT id, username, email, role, tenant_id, last_login, created_at
FROM users
WHERE is_active = TRUE;

-- Approved clinics view
CREATE VIEW approved_clinics AS
SELECT c.*, u.email as approver_email
FROM clinics c
LEFT JOIN users u ON c.approved_by = u.id
WHERE c.status = 'approved';

-- Recent audit logs view
CREATE VIEW recent_audit_logs AS
SELECT al.*, u.email as user_email, c.name as clinic_name
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
LEFT JOIN clinics c ON al.clinic_id = c.id
WHERE al.created_at >= datetime('now', '-7 days')
ORDER BY al.created_at DESC;

-- =============================================================================
-- SCHEMA SUMMARY
-- =============================================================================

/*
DATABASE SCHEMA SUMMARY:
======================

TABLES (8):
- users: User authentication and authorization
- refresh_tokens: JWT token rotation
- clinics: Healthcare practice management
- assistants: AI assistant configuration
- audit_logs: HIPAA compliance and security monitoring
- file_uploads: Secure file management
- csrf_tokens: CSRF protection
- rate_limits: API rate limiting

KEY FEATURES:
- Multi-tenant architecture with tenant_id fields
- Comprehensive indexing for performance
- Foreign key constraints with proper cascading
- JSON fields for flexible configuration
- Audit logging for HIPAA compliance
- Security features (CSRF, rate limiting)
- File quarantine system
- Automatic timestamp management

INDEXES (50+):
- Performance indexes for common query patterns
- Composite indexes for multi-column queries
- Unique constraints for data integrity
- Foreign key indexes for join performance

TRIGGERS (5):
- Automatic updated_at timestamp management
- Ensures data consistency across all tables

VIEWS (3):
- Active users for user management
- Approved clinics for practice management
- Recent audit logs for monitoring

SAMPLE DATA:
- Admin user for testing
- Sample clinic with complete configuration
- Ready for immediate testing and development
*/

