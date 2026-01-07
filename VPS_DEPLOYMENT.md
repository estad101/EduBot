# EduBot VPS Deployment Guide

## Prerequisites
- AWS EC2 instance (54.236.6.22) running Ubuntu
- SSH access with EduBot.ppk key
- MySQL 8.0+ installed on VPS

## Step 1: Connect to VPS

### Using SSH (from Windows/Mac/Linux)
```bash
ssh -i EduBot.pem ubuntu@54.236.6.22
```

### Using PuTTY (Windows)
1. Open PuTTY
2. Host: `54.236.6.22`
3. Port: `22`
4. Auth > Private key file: Select `EduBot.pem`
5. Open

## Step 2: Create Database on VPS

Once connected to your VPS:

```bash
# Login to MySQL
mysql -u root -p

# Then paste the following SQL commands:
```

### SQL Setup Commands
```sql
-- Create the database
CREATE DATABASE IF NOT EXISTS whatsapp_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create database user
CREATE USER IF NOT EXISTS 'payroll_user'@'localhost' IDENTIFIED BY 'your_strong_password_here';
CREATE USER IF NOT EXISTS 'payroll_user'@'%' IDENTIFIED BY 'your_strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'localhost';
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SELECT user, host FROM mysql.user WHERE user='payroll_user';
SHOW GRANTS FOR 'payroll_user'@'localhost';
```

## Step 3: Verify Connection

```bash
# Test connection from VPS
mysql -u payroll_user -p -h localhost whatsapp_chatbot -e "SELECT 1;"

# Test from remote (if needed)
mysql -u payroll_user -p -h 54.236.6.22 whatsapp_chatbot -e "SELECT 1;"
```

## Step 4: Update .env Files

After database is created, update your `.env` file:

```bash
# Local development (if MySQL is on VPS)
DATABASE_URL=mysql+mysqlconnector://payroll_user:your_password@54.236.6.22:3306/whatsapp_chatbot

# Or if you have local MySQL for development
DATABASE_URL=mysql+mysqlconnector://payroll_user:your_password@localhost:3306/whatsapp_chatbot
```

## Step 5: Initialize Database Tables

The application will automatically create tables on first run via SQLAlchemy ORM.

```bash
# From your local machine or VPS (in the bot directory)
python main.py

# Or run migrations if using Alembic
alembic upgrade head
```

## Security Checklist

- [ ] Change default MySQL password
- [ ] Use strong password for `payroll_user` (min 16 characters)
- [ ] Restrict MySQL port (3306) to specific IPs only
- [ ] Enable SSL/TLS for MySQL connections
- [ ] Backup database regularly
- [ ] Set up automated backups

## Connecting to VPS MySQL from Your Local Machine

### Option 1: Direct Connection
```bash
mysql -u payroll_user -p -h 54.236.6.22 whatsapp_chatbot
```

### Option 2: SSH Tunnel (More Secure)
```bash
# Open tunnel on port 3307
ssh -i EduBot.pem -L 3307:localhost:3306 ubuntu@54.236.6.22

# In another terminal, connect to localhost:3307
mysql -u payroll_user -p -h localhost -P 3307 whatsapp_chatbot
```

## Database Structure

The application will create these tables automatically:
- `users` - Admin users
- `students` - Student records
- `tutors` - Tutor information
- `homework` - Homework submissions
- `payments` - Payment transactions
- `subscriptions` - Student subscriptions
- `tutor_assignments` - Tutor-student assignments

## Troubleshooting

### Can't connect to MySQL?
```bash
# Check if MySQL is running on VPS
sudo systemctl status mysql

# Start if not running
sudo systemctl start mysql

# Check MySQL is listening on port 3306
sudo netstat -tlnp | grep 3306
```

### Permission denied errors
```sql
-- Check current privileges
SHOW GRANTS FOR 'payroll_user'@'localhost';

-- Re-grant if needed
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'localhost';
FLUSH PRIVILEGES;
```

### Application can't connect
1. Verify database exists: `SHOW DATABASES;`
2. Verify user exists: `SELECT user, host FROM mysql.user;`
3. Check DATABASE_URL in .env is correct
4. Test connection: `mysql -u payroll_user -p whatsapp_chatbot -e "SELECT 1;"`

## Next Steps

1. ✅ Create database and user on VPS
2. ✅ Update `.env` with VPS database credentials
3. Upload bot code to VPS
4. Install dependencies: `pip install -r requirements.txt`
5. Run application: `python main.py`
6. Access admin UI: `http://54.236.6.22:3000`

## Quick Reference

**VPS Details:**
- IP: 54.236.6.22
- User: ubuntu
- Key: EduBot.pem (converted from EduBot.ppk)

**Database Details:**
- Host: localhost (on VPS) or 54.236.6.22 (from remote)
- Database: whatsapp_chatbot
- User: payroll_user
- Port: 3306

**Files:**
- Setup script: `database_setup.sql`
- Configuration: `.env`, `.env.production`
- Backend: `main.py`
- Requirements: `requirements.txt`
