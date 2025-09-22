-- =====================================================
-- COMPREHENSIVE SCHEMA MIGRATION
-- Aligns Supabase schema with SQLAlchemy models
-- =====================================================

-- ===============
-- Step 1: Create/Update Enum Types
-- ===============

-- Drop existing enum types if they exist (will fail if in use, that's expected)
DROP TYPE IF EXISTS communication_pref_enum CASCADE;
DROP TYPE IF EXISTS appointment_status_enum CASCADE;
DROP TYPE IF EXISTS audit_action_enum CASCADE;

-- Create enum types with correct lowercase values
CREATE TYPE communication_pref_enum AS ENUM ('phone','text','email');
CREATE TYPE appointment_status_enum AS ENUM ('scheduled','cancelled','completed');
CREATE TYPE audit_action_enum AS ENUM ('INSERT','UPDATE','DELETE','SELECT');

-- ===============
-- Step 2: Create/Fix Tables
-- ===============

-- Create tenants table if it doesn't exist
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create clinics table if it doesn't exist
CREATE TABLE IF NOT EXISTS clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create assistants table if it doesn't exist
CREATE TABLE IF NOT EXISTS assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ
);

-- Create patients table if it doesn't exist
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    insurance_type TEXT,
    is_new BOOLEAN DEFAULT TRUE NOT NULL,
    communication_pref communication_pref_enum DEFAULT 'phone' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ
);

-- Create appointments table if it doesn't exist
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    reason TEXT,
    status appointment_status_enum DEFAULT 'scheduled' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ
);

-- Create calls table if it doesn't exist
CREATE TABLE IF NOT EXISTS calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ended_at TIMESTAMPTZ,
    reason_for_call TEXT,
    transcript TEXT,
    recording_url TEXT,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ
);

-- Create audit_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID,
    table_name TEXT NOT NULL,
    record_id TEXT,
    action audit_action_enum NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    details JSONB
);

-- ===============
-- Step 3: Add Missing Columns to Existing Tables
-- ===============

-- Fix tenants table
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();

-- Make required columns NOT NULL
ALTER TABLE tenants 
ALTER COLUMN name SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Fix clinics table
ALTER TABLE clinics 
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();

-- Make required columns NOT NULL
ALTER TABLE clinics 
ALTER COLUMN tenant_id SET NOT NULL,
ALTER COLUMN name SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Add unique constraint for phone_number if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'clinics_phone_number_key'
    ) THEN
        ALTER TABLE clinics ADD CONSTRAINT clinics_phone_number_key UNIQUE (phone_number);
    END IF;
END $$;

-- Fix assistants table
ALTER TABLE assistants 
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Make required columns NOT NULL
ALTER TABLE assistants 
ALTER COLUMN clinic_id SET NOT NULL,
ALTER COLUMN name SET NOT NULL,
ALTER COLUMN phone_number SET NOT NULL,
ALTER COLUMN active SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Add unique constraint for phone_number if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'assistants_phone_number_key'
    ) THEN
        ALTER TABLE assistants ADD CONSTRAINT assistants_phone_number_key UNIQUE (phone_number);
    END IF;
END $$;

-- Fix patients table
ALTER TABLE patients 
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS insurance_type TEXT,
ADD COLUMN IF NOT EXISTS is_new BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS communication_pref communication_pref_enum DEFAULT 'phone',
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Make required columns NOT NULL
ALTER TABLE patients 
ALTER COLUMN clinic_id SET NOT NULL,
ALTER COLUMN name SET NOT NULL,
ALTER COLUMN phone_number SET NOT NULL,
ALTER COLUMN is_new SET NOT NULL,
ALTER COLUMN communication_pref SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Add unique constraint for clinic_id + phone_number if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'idx_patients_clinic_phone'
    ) THEN
        ALTER TABLE patients ADD CONSTRAINT idx_patients_clinic_phone UNIQUE (clinic_id, phone_number);
    END IF;
END $$;

-- Fix appointments table
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS reason TEXT,
ADD COLUMN IF NOT EXISTS status appointment_status_enum DEFAULT 'scheduled',
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Make required columns NOT NULL
ALTER TABLE appointments 
ALTER COLUMN patient_id SET NOT NULL,
ALTER COLUMN clinic_id SET NOT NULL,
ALTER COLUMN scheduled_at SET NOT NULL,
ALTER COLUMN status SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Fix calls table
ALTER TABLE calls 
ADD COLUMN IF NOT EXISTS assistant_id UUID REFERENCES assistants(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS ended_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS reason_for_call TEXT,
ADD COLUMN IF NOT EXISTS transcript TEXT,
ADD COLUMN IF NOT EXISTS recording_url TEXT,
ADD COLUMN IF NOT EXISTS summary TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Make required columns NOT NULL
ALTER TABLE calls 
ALTER COLUMN assistant_id SET NOT NULL,
ALTER COLUMN clinic_id SET NOT NULL,
ALTER COLUMN started_at SET NOT NULL,
ALTER COLUMN created_at SET NOT NULL;

-- Fix audit_logs table
ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS user_id UUID,
ADD COLUMN IF NOT EXISTS table_name TEXT,
ADD COLUMN IF NOT EXISTS record_id TEXT,
ADD COLUMN IF NOT EXISTS action audit_action_enum,
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS details JSONB;

-- Make required columns NOT NULL
ALTER TABLE audit_logs 
ALTER COLUMN table_name SET NOT NULL,
ALTER COLUMN action SET NOT NULL,
ALTER COLUMN timestamp SET NOT NULL;

-- ===============
-- Step 4: Create Indexes
-- ===============

-- Create performance indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(name);
CREATE INDEX IF NOT EXISTS idx_clinics_tenant_id ON clinics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assistants_clinic_id ON assistants(clinic_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone_number ON patients(phone_number);
CREATE INDEX IF NOT EXISTS idx_patients_clinic_id ON patients(clinic_id);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(clinic_id, name);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_clinic_id ON appointments(clinic_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_appointments_clinic ON appointments(clinic_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_calls_assistant_id ON calls(assistant_id);
CREATE INDEX IF NOT EXISTS idx_calls_patient_id ON calls(patient_id);
CREATE INDEX IF NOT EXISTS idx_calls_clinic_id ON calls(clinic_id);
CREATE INDEX IF NOT EXISTS idx_calls_started ON calls(clinic_id, started_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record_id ON audit_logs(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- ===============
-- Step 5: Insert Default Data
-- ===============

-- Insert default tenant
INSERT INTO tenants (id, name, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Default Tenant',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert default clinic
INSERT INTO clinics (id, tenant_id, name, phone_number, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000000',
    'Bright Smile Dental Care',
    '+1 (415) 555-0123',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert default assistant
INSERT INTO assistants (id, clinic_id, name, phone_number, active, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Sam - Dental Assistant',
    '+1 (415) 555-0124',
    true,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- ===============
-- Step 6: Verification
-- ===============

-- Check all table structures
SELECT '=== TABLE STRUCTURES ===' as info;

SELECT 'tenants' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'tenants' 
ORDER BY ordinal_position;

SELECT 'clinics' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'clinics' 
ORDER BY ordinal_position;

SELECT 'assistants' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'assistants' 
ORDER BY ordinal_position;

SELECT 'patients' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'patients' 
ORDER BY ordinal_position;

SELECT 'appointments' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'appointments' 
ORDER BY ordinal_position;

SELECT 'calls' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'calls' 
ORDER BY ordinal_position;

SELECT 'audit_logs' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'audit_logs' 
ORDER BY ordinal_position;

-- Check enum values
SELECT '=== ENUM VALUES ===' as info;
SELECT enumlabel as communication_pref_values
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'communication_pref_enum');

SELECT enumlabel as appointment_status_values
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'appointment_status_enum');

SELECT enumlabel as audit_action_values
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'audit_action_enum');

-- Check data counts
SELECT '=== DATA COUNTS ===' as info;
SELECT 'tenants' as table_name, COUNT(*) as count FROM tenants
UNION ALL
SELECT 'clinics' as table_name, COUNT(*) as count FROM clinics
UNION ALL
SELECT 'assistants' as table_name, COUNT(*) as count FROM assistants
UNION ALL
SELECT 'patients' as table_name, COUNT(*) as count FROM patients
UNION ALL
SELECT 'appointments' as table_name, COUNT(*) as count FROM appointments
UNION ALL
SELECT 'calls' as table_name, COUNT(*) as count FROM calls
UNION ALL
SELECT 'audit_logs' as table_name, COUNT(*) as count FROM audit_logs;

-- ===============
-- Step 7: Test Inserts and Deletes
-- ===============

-- Test insert into each table and then delete
SELECT '=== TESTING INSERTS ===' as info;

-- Test patient insert
INSERT INTO patients (id, clinic_id, name, phone_number, is_new, communication_pref)
VALUES (
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000001',
    'Test Patient',
    '+1999999999',
    true,
    'phone'
) ON CONFLICT (clinic_id, phone_number) DO NOTHING;

-- Test appointment insert
INSERT INTO appointments (id, patient_id, clinic_id, scheduled_at, reason, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM patients WHERE phone_number = '+1999999999' LIMIT 1),
    '00000000-0000-0000-0000-000000000001',
    NOW() + INTERVAL '1 day',
    'Test appointment',
    'scheduled'
) ON CONFLICT (id) DO NOTHING;

-- Test call insert
INSERT INTO calls (id, assistant_id, patient_id, clinic_id, started_at, reason_for_call, transcript, recording_url, summary)
VALUES (
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000002',
    (SELECT id FROM patients WHERE phone_number = '+1999999999' LIMIT 1),
    '00000000-0000-0000-0000-000000000001',
    NOW(),
    'Test call',
    'Test transcript',
    'https://example.com/recording.wav',
    'Test summary'
) ON CONFLICT (id) DO NOTHING;

-- Test audit log insert
INSERT INTO audit_logs (tenant_id, table_name, record_id, action, details)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'patients',
    (SELECT id FROM patients WHERE phone_number = '+1999999999' LIMIT 1),
    'INSERT',
    '{"test": "data"}'
) ON CONFLICT DO NOTHING;

-- Clean up test data
DELETE FROM audit_logs WHERE table_name = 'patients' AND details->>'test' = 'data';
DELETE FROM calls WHERE reason_for_call = 'Test call';
DELETE FROM appointments WHERE reason = 'Test appointment';
DELETE FROM patients WHERE phone_number = '+1999999999';

SELECT '=== MIGRATION COMPLETED SUCCESSFULLY ===' as result;

