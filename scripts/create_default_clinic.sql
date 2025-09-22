-- Create default clinic for webhook operations
INSERT INTO clinics (
    id,
    tenant_id,
    name,
    address,
    phone,
    email,
    website,
    timezone,
    business_hours,
    services_offered,
    insurance_accepted,
    emergency_contact,
    status,
    created_at,
    updated_at
) VALUES (
    'default_clinic',
    'default_tenant',
    'Default Dental Clinic',
    '123 Main Street, City, State 12345',
    '+1 (555) 123-4567',
    'info@defaultdental.com',
    'https://defaultdental.com',
    'America/New_York',
    '{"monday": {"open": "08:00", "close": "17:00"}, "tuesday": {"open": "08:00", "close": "17:00"}, "wednesday": {"open": "08:00", "close": "17:00"}, "thursday": {"open": "08:00", "close": "17:00"}, "friday": {"open": "08:00", "close": "17:00"}, "saturday": {"open": "09:00", "close": "15:00"}, "sunday": {"closed": true}}',
    '["General Dentistry", "Cosmetic Dentistry", "Orthodontics"]',
    '["Delta Dental", "Blue Cross Blue Shield", "Aetna"]',
    '+1 (555) 123-4568',
    'active',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;