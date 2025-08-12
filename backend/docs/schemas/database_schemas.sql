-- Dental Voice AI Database Schemas
-- Simplified appointment booking system

-- =============================================
-- 1. TENANTS TABLE (existing)
-- =============================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone_number TEXT UNIQUE,
    hours_json JSONB,
    insurances_json JSONB,
    faq_json JSONB,
    services_json JSONB,
    location_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 2. CALLS TABLE (existing)
-- =============================================
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    caller_number TEXT NOT NULL,
    status TEXT NOT NULL,
    transcript TEXT,
    intent TEXT,
    intent_confidence DECIMAL(3,2),
    faq_matched TEXT,
    response_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 3. APPOINTMENT REQUESTS TABLE
-- =============================================
CREATE TABLE appointment_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    caller_name TEXT,
    caller_number TEXT,
    reason TEXT,
    status TEXT DEFAULT 'new',  -- 'new', 'contacted', 'closed'
    appointment_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT now()
);

-- =============================================
-- 4. APPOINTMENTS TABLE (NEW - for confirmed appointments)
-- =============================================
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    patient_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_datetime TIMESTAMP WITH TIME ZONE,
    reason TEXT DEFAULT 'Dental appointment',
    notes TEXT,
    status TEXT DEFAULT 'scheduled',  -- 'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 5. OFFICE AVAILABILITIES TABLE
-- =============================================
CREATE TABLE office_availabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    date DATE,
    start_time TIME,
    end_time TIME,
    available BOOLEAN DEFAULT TRUE
);

-- =============================================
-- 6. PERFORMANCE INDEXES
-- =============================================

-- Existing indexes
CREATE INDEX idx_tenants_phone_number ON tenants(phone_number);
CREATE INDEX idx_calls_tenant_id ON calls(tenant_id);
CREATE INDEX idx_calls_created_at ON calls(created_at);

-- New indexes for appointment system
CREATE INDEX idx_appointment_requests_tenant_id ON appointment_requests(tenant_id);
CREATE INDEX idx_appointment_requests_status ON appointment_requests(status);
CREATE INDEX idx_appointment_requests_caller_number ON appointment_requests(caller_number);
CREATE INDEX idx_appointment_requests_appointment_time ON appointment_requests(appointment_time);
CREATE INDEX idx_appointment_requests_created_at ON appointment_requests(created_at);

CREATE INDEX idx_appointments_tenant_id ON appointments(tenant_id);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_appointment_datetime ON appointments(appointment_datetime);

CREATE INDEX idx_office_availabilities_tenant_id ON office_availabilities(tenant_id);
CREATE INDEX idx_office_availabilities_date ON office_availabilities(date);
CREATE INDEX idx_office_availabilities_available ON office_availabilities(available);
CREATE INDEX idx_office_availabilities_date_time ON office_availabilities(date, start_time);

-- =============================================
-- 7. SAMPLE DATA FOR TESTING
-- =============================================

-- Sample availability slots (replace YOUR_TENANT_ID with actual ID)
/*
INSERT INTO office_availabilities (tenant_id, date, start_time, end_time, available)
VALUES 
    ('YOUR_TENANT_ID', '2024-08-15', '09:00', '10:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-15', '10:00', '11:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-15', '11:00', '12:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-15', '14:00', '15:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-15', '15:00', '16:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-16', '09:00', '10:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-16', '10:00', '11:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-16', '11:00', '12:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-16', '14:00', '15:00', TRUE),
    ('YOUR_TENANT_ID', '2024-08-16', '15:00', '16:00', TRUE);
*/

-- =============================================
-- 8. USEFUL QUERIES
-- =============================================

-- Get all available slots for a practice
/*
SELECT oa.*, t.name as practice_name
FROM office_availabilities oa
JOIN tenants t ON oa.tenant_id = t.id
WHERE oa.tenant_id = 'YOUR_TENANT_ID'
AND oa.available = TRUE
AND oa.date >= CURRENT_DATE
ORDER BY oa.date, oa.start_time;
*/

-- Get recent appointment requests
/*
SELECT ar.*, t.name as practice_name
FROM appointment_requests ar
JOIN tenants t ON ar.tenant_id = t.id
WHERE ar.tenant_id = 'YOUR_TENANT_ID'
ORDER BY ar.created_at DESC
LIMIT 10;
*/

-- Get confirmed appointments for a practice
/*
SELECT a.*, t.name as practice_name
FROM appointments a
JOIN tenants t ON a.tenant_id = t.id
WHERE a.tenant_id = 'YOUR_TENANT_ID'
AND a.status IN ('scheduled', 'confirmed')
AND a.appointment_datetime >= NOW()
ORDER BY a.appointment_datetime ASC;
*/

-- Get today's appointments
/*
SELECT a.*, t.name as practice_name
FROM appointments a
JOIN tenants t ON a.tenant_id = t.id
WHERE a.tenant_id = 'YOUR_TENANT_ID'
AND a.appointment_date = CURRENT_DATE
ORDER BY a.appointment_time ASC;
*/

-- Check appointment conflicts
/*
SELECT ar.*, oa.date, oa.start_time, oa.end_time
FROM appointment_requests ar
LEFT JOIN office_availabilities oa ON 
    ar.tenant_id = oa.tenant_id 
    AND DATE(ar.appointment_time) = oa.date 
    AND TIME(ar.appointment_time) BETWEEN oa.start_time AND oa.end_time
WHERE ar.status = 'new'
ORDER BY ar.created_at DESC;
*/
