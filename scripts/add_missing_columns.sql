-- Add missing columns to existing tables
-- This script will add columns that exist in the models but not in the database

-- Add recording_url column to calls table if it doesn't exist
ALTER TABLE calls 
ADD COLUMN IF NOT EXISTS recording_url TEXT;

-- Add deleted_at column to calls table if it doesn't exist
ALTER TABLE calls 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'calls' 
ORDER BY ordinal_position;

SELECT 'Missing columns added successfully!' as result;

