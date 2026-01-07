CREATE DATABASE IF NOT EXISTS whatsapp_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'payroll_user'@'localhost' IDENTIFIED BY 'EduBot@2024Secure';
CREATE USER IF NOT EXISTS 'payroll_user'@'%' IDENTIFIED BY 'EduBot@2024Secure';
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'localhost';
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'%';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user='payroll_user';
