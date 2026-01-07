# EduBot - WhatsApp AI Chatbot for Education

A comprehensive WhatsApp chatbot platform built with **FastAPI** (backend), **Next.js** (admin UI), and **MySQL** database. EduBot provides intelligent tutoring, homework management, student tracking, and payment processing for educational institutions.

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Node.js](https://img.shields.io/badge/node.js-18%2B-green)

---

## 📋 Features

### Core Functionality
- **WhatsApp Integration** - Direct WhatsApp messaging API integration
- **AI Tutoring** - Intelligent conversational tutoring system
- **Homework Management** - Assignment tracking and grading
- **Student Management** - Complete student profiles and analytics
- **Payment Processing** - Paystack integration for payments
- **Subscription Management** - Flexible subscription plans
- **Real-time Notifications** - Alert system for important events
- **Admin Dashboard** - Comprehensive Next.js admin interface
- **Analytics & Reports** - Detailed performance metrics

### Technical Features
- **RESTful API** - FastAPI with automatic OpenAPI documentation
- **Authentication** - JWT-based user authentication
- **Database Monitoring** - Real-time monitoring service
- **Multi-tenant Support** - Tutor assignment and management
- **File Uploads** - Homework file submission system
- **Rate Limiting** - API rate limiting and throttling
- **Logging** - Comprehensive logging system

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn ASGI server
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Messaging**: WhatsApp Business API

### Frontend
- **Framework**: Next.js 13+ (TypeScript)
- **UI Components**: React
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API Client**: Axios

### DevOps
- **VCS**: Git / GitHub
- **Deployment**: Railway, AWS EC2, or DigitalOcean
- **Database**: MySQL Server
- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: systemd

---

## 📦 Prerequisites

### Local Development
- Python 3.9 or higher
- Node.js 18 or higher
- MySQL 5.7 or higher
- Git
- pip (Python package manager)
- npm (Node package manager)

### Deployment
- VPS/Cloud Server (Railway, AWS, DigitalOcean, etc.)
- Domain name
- SSL Certificate (Let's Encrypt)
- WhatsApp Business Account
- Paystack Account (for payments)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/estad101/EduBot.git
cd EduBot
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# Create database
mysql -u root -p < database_setup.sql

# Run migrations
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd admin-ui

# Install Node dependencies
npm install

# Create .env.local
cp .env.example .env.local
# Edit .env.local with your API endpoint
```

### 5. Run Local Development

**Backend** (in project root):
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

**Frontend** (in admin-ui directory):
```bash
npm run dev
```

Admin UI: http://localhost:3000

---

## 📋 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost/edubot_db

# WhatsApp API
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER=your_phone_number

# Paystack
PAYSTACK_PUBLIC_KEY=your_paystack_public_key
PAYSTACK_SECRET_KEY=your_paystack_secret_key

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_PORT=8000
API_HOST=0.0.0.0

# Environment
ENVIRONMENT=development
DEBUG=True
```

### Frontend Environment (.env.local)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

---

## 🌐 Deployment

### Option 1: Railway (Recommended - Free)

1. **Sign up**: https://railway.app
2. **Connect GitHub**: Link your GitHub account
3. **Create Project**: Select "Create a New Project"
4. **Deploy from GitHub**: Connect the EduBot repository
5. **Configure Environment Variables**: Set all `.env` variables in Railway dashboard
6. **Start Services**: Railway auto-deploys on push

**Estimated Cost**: Free tier with $5/month credit

### Option 2: DigitalOcean Droplet

```bash
# 1. Create Droplet (Ubuntu 22.04)
# 2. SSH into server
ssh root@your_server_ip

# 3. Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3.9 python3-pip nodejs npm mysql-server nginx -y

# 4. Clone and setup
git clone https://github.com/estad101/EduBot.git
cd EduBot

# 5. Follow backend and frontend setup steps
```

**Estimated Cost**: $5-12/month

### Option 3: AWS EC2

```bash
# 1. Launch Ubuntu 22.04 instance
# 2. Configure security groups (ports 80, 443, 8000)
# 3. Connect via SSH
ssh -i your_key.pem ec2-user@your_instance_ip

# 4. Follow DigitalOcean deployment steps
```

---

## 📚 API Documentation

The FastAPI backend provides automatic OpenAPI documentation available at:

```
http://your-server:8000/docs          # Swagger UI
http://your-server:8000/redoc         # ReDoc
```

### Main API Endpoints

```
Authentication
POST   /api/auth/register              # Register user
POST   /api/auth/login                 # Login
POST   /api/auth/refresh               # Refresh token

Students
GET    /api/students                   # List all students
POST   /api/students                   # Create student
GET    /api/students/{id}              # Get student details
PUT    /api/students/{id}              # Update student
DELETE /api/students/{id}              # Delete student

Tutors
GET    /api/tutors                     # List all tutors
POST   /api/tutors                     # Create tutor
POST   /api/tutors/{id}/assign         # Assign students to tutor

Homework
GET    /api/homework                   # List homework
POST   /api/homework                   # Create homework
GET    /api/homework/{id}              # Get homework details
PUT    /api/homework/{id}              # Update homework

Payments
GET    /api/payments                   # List payments
POST   /api/payments                   # Create payment
GET    /api/subscriptions              # List subscriptions

WhatsApp
POST   /api/whatsapp/webhook           # WhatsApp webhook
POST   /api/whatsapp/send              # Send WhatsApp message

Health Check
GET    /api/health                     # API health status
```

---

## 📱 WhatsApp Integration

### Setup Steps

1. **Get WhatsApp Business Account**
   - Visit: https://www.whatsapp.com/business/
   - Create business account

2. **Get API Credentials**
   - API Key
   - Phone Number ID
   - Business Account ID

3. **Configure Webhook**
   - Set webhook URL: `https://your-domain.com/api/whatsapp/webhook`
   - Verify token in settings

4. **Update .env**
   ```env
   WHATSAPP_API_KEY=your_key
   WHATSAPP_PHONE_NUMBER=your_phone
   ```

---

## 💳 Payment Integration (Paystack)

### Setup Steps

1. **Create Paystack Account**: https://paystack.com
2. **Get API Keys**: From dashboard settings
3. **Update .env**:
   ```env
   PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
   PAYSTACK_SECRET_KEY=sk_live_xxxxx
   ```

---

## 🛠 Development

### Project Structure

```
EduBot/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Python dependencies
├── config/                 # Configuration files
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
├── api/routes/             # API endpoints
├── admin/                  # Admin panel logic
├── migrations/             # Database migrations
├── middleware/             # FastAPI middleware
├── utils/                  # Utility functions
├── admin-ui/               # Next.js frontend
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   ├── store/              # State management
│   └── lib/                # Utilities
└── docs/                   # Documentation
```

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. Push and create Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

**Database connection error**:
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Verify DATABASE_URL in .env
```

**Import errors**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use**:
```bash
# Use different port
npm run dev -- -p 3001
```

**Dependencies issues**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📈 Monitoring & Logs

### Backend Logs

**Local Development**:
```bash
# Logs appear in console
python main.py
```

**Production (systemd)**:
```bash
# View logs
journalctl -u edubot -f

# View recent logs
journalctl -u edubot -n 50
```

### Database Monitoring

```bash
# Check database status
mysql -u root -p -e "SHOW DATABASES;"
mysql -u root -p -e "USE edubot_db; SHOW TABLES;"
```

---

## 🚨 Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] SSL certificate installed
- [ ] WhatsApp webhook configured
- [ ] Paystack keys verified
- [ ] Admin credentials changed
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Monitoring alerts set up
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers added

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for detailed guide.

---

## 📞 Support & Contact

- **Issues**: Create GitHub issue
- **Email**: estadenterprise@gmail.com
- **Documentation**: See `/docs` folder

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📊 Status

- **Backend**: ✅ Production Ready
- **Frontend**: ✅ Production Ready
- **Database**: ✅ Optimized
- **WhatsApp Integration**: ✅ Active
- **Payment Processing**: ✅ Live
- **Deployment**: ✅ Automated

---

**Last Updated**: January 2026
**Version**: 1.0.0
