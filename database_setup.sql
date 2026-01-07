-- EduBot Database Setup Script
-- Run this on your VPS MySQL server to initialize the database

-- Create the database
CREATE DATABASE IF NOT EXISTS whatsapp_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create the database user (replace 'password' with a strong password)
CREATE USER IF NOT EXISTS 'payroll_user'@'localhost' IDENTIFIED BY 'change_me_to_strong_password';
CREATE USER IF NOT EXISTS 'payroll_user'@'%' IDENTIFIED BY 'change_me_to_strong_password';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'localhost';
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SELECT user, host FROM mysql.user WHERE user='payroll_user';
SHOW GRANTS FOR 'payroll_user'@'localhost';

-- You can now connect with:
-- mysql -u payroll_user -p -h localhost
-- OR
-- mysql -u payroll_user -p -h your_vps_ip_address
