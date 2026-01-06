-- Migration: Fix Almaty timezone from UTC+6 to UTC+5
-- Date: 2025-01-06
-- Purpose: Update all "Asia/Almaty" timezones to "Etc/GMT-5" for consistency

-- Update users table
UPDATE users 
SET timezone = 'Etc/GMT-5' 
WHERE timezone = 'Asia/Almaty' 
   OR timezone LIKE '%UTC+6%'
   OR timezone = 'Etc/GMT-6';

-- Update mentor_settings table
UPDATE mentor_settings 
SET timezone = 'Etc/GMT-5' 
WHERE timezone = 'Asia/Almaty' 
   OR timezone LIKE '%UTC+6%'
   OR timezone = 'Etc/GMT-6';

-- Verify changes
SELECT 'Users updated:' as info, COUNT(*) as count FROM users WHERE timezone = 'Etc/GMT-5';
SELECT 'Mentor settings updated:' as info, COUNT(*) as count FROM mentor_settings WHERE timezone = 'Etc/GMT-5';

-- Check if any old timezones remain
SELECT 'Old timezones remaining:' as info, COUNT(*) as count FROM users WHERE timezone LIKE '%Almaty%' OR timezone LIKE '%UTC+6%';

