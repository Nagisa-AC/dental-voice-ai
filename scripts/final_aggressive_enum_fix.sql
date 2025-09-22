-- Final Aggressive Enum Fix - Complete Solution
-- This script will fix all enum issues and restore missing columns

-- ===============
-- Step 1: Check current state
-- ===============
SELECT 'Current enum values:' as info;
SELECT enumlabel as communication_pref_values
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'communication_pref_enum');

-- Check if communication_pref column exists
SELECT 'Patients table structure:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'patients' AND column_name = 'communication_pref';

-- ===============
-- Step 2: Drop all foreign key constraints that use enums
-- ===============

-- Drop foreign key constraints temporarily
ALTER TABLE patients DROP CONSTRAINT IF EXISTS patients_clinic_id_fkey;
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_patient_id_fkey;
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_clinic_id_fkey;
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_assistant_id_fkey;
ALTER TABLE audit_logs DROP CONSTRAINT IF EXISTS audit_logs_tenant_id_fkey;

-- ===============
-- Step 3: Drop the enum types completely
-- ===============

DROP TYPE IF EXISTS communication_pref_enum CASCADE;
DROP TYPE IF EXISTS appointment_status_enum CASCADE;
DROP TYPE IF EXISTS audit_action_enum CASCADE;

-- ===============
-- Step 4: Recreate with lowercase values
-- ===============

CREATE TYPE communication_pref_enum AS ENUM ('phone','text','email');
CREATE TYPE appointment_status_enum AS ENUM ('scheduled','cancelled','completed');
CREATE TYPE audit_action_enum AS ENUM ('INSERT','UPDATE','DELETE','SELECT');

-- ===============
-- Step 5: Restore missing columns
-- ===============

-- Restore communication_pref column in patients table
ALTER TABLE patients 
ADD COLUMN IF NOT EXISTS communication_pref communication_pref_enum DEFAULT 'phone' NOT NULL;

-- Restore status column in appointments table if missing
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS status appointment_status_enum DEFAULT 'scheduled' NOT NULL;

-- Restore action column in audit_logs table if missing
ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS action audit_action_enum NOT NULL;

-- ===============
-- Step 6: Recreate foreign key constraints
-- ===============

-- Recreate foreign key constraints
ALTER TABLE patients 
ADD CONSTRAINT patients_clinic_id_fkey 
FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE;

ALTER TABLE appointments 
ADD CONSTRAINT appointments_patient_id_fkey 
FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;

ALTER TABLE appointments 
ADD CONSTRAINT appointments_clinic_id_fkey 
FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE;

ALTER TABLE appointments 
ADD CONSTRAINT appointments_assistant_id_fkey 
FOREIGN KEY (assistant_id) REFERENCES assistants(id) ON DELETE SET NULL;

ALTER TABLE audit_logs 
ADD CONSTRAINT audit_logs_tenant_id_fkey 
FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

-- ===============
-- Step 7: Verify the fix
-- ===============

-- Check enum values
SELECT 'New enum values:' as info;
SELECT enumlabel as communication_pref_values
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'communication_pref_enum');

-- Check patients table structure
SELECT 'Patients table structure after fix:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'patients' AND column_name = 'communication_pref';

-- Check appointments table structure
SELECT 'Appointments table structure after fix:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'appointments' AND column_name = 'status';

-- Check audit_logs table structure
SELECT 'Audit_logs table structure after fix:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'audit_logs' AND column_name = 'action';

-- ===============
-- Step 8: Test inserts
-- ===============

-- Test patient insert
INSERT INTO patients (id, clinic_id, name, phone_number, is_new, communication_pref)
VALUES (
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000001',
    'Test Patient Final Fix',
    '+1999999994',
    true,
    'phone'
) ON CONFLICT (clinic_id, phone_number) DO NOTHING;

-- Test appointment insert
INSERT INTO appointments (id, patient_id, clinic_id, scheduled_at, reason, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM patients WHERE phone_number = '+1999999994' LIMIT 1),
    '00000000-0000-0000-0000-000000000001',
    NOW() + INTERVAL '1 day',
    'Test appointment final fix',
    'scheduled'
) ON CONFLICT (id) DO NOTHING;

-- Test audit log insert
INSERT INTO audit_logs (tenant_id, table_name, record_id, action, details)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'patients',
    (SELECT id FROM patients WHERE phone_number = '+1999999994' LIMIT 1),
    'INSERT',
    '{"test": "final_fix"}'
) ON CONFLICT DO NOTHING;

-- ===============
-- Step 9: Clean up test data
-- ===============

DELETE FROM audit_logs WHERE details->>'test' = 'final_fix';
DELETE FROM appointments WHERE reason = 'Test appointment final fix';
DELETE FROM patients WHERE phone_number = '+1999999994';

-- ===============
-- Step 10: Final verification
-- ===============

SELECT '=== FINAL VERIFICATION ===' as info;

-- Check all enum values
SELECT 'communication_pref_enum values:' as enum_name, enumlabel as values
FROM pg_enum 
WHERE enumtypid = 'communication_pref_enum'::regtype
UNION ALL
SELECT 'appointment_status_enum values:' as enum_name, enumlabel as values
FROM pg_enum 
WHERE enumtypid = 'appointment_status_enum'::regtype
UNION ALL
SELECT 'audit_action_enum values:' as enum_name, enumlabel as values
FROM pg_enum 
WHERE enumtypid = 'audit_action_enum'::regtype;

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

SELECT 'Final aggressive enum fix completed successfully!' as result;

