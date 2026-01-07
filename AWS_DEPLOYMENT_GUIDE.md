# EduBot Production Deployment - Quick Reference

## Files Deployed

✅ `deploy.sh` - Complete deployment script (installed in `/opt/edubot/`)

## Running the Deployment

### Option 1: Direct SSH/PLink Connection
```bash
ssh -i EduBot.pem ubuntu@54.236.6.22
cd /opt/edubot
bash deploy.sh
```

### Option 2: From Windows with PLink
```batch
plink -i EduBot.ppk -l ubuntu 54.236.6.22 "cd /opt/edubot && bash deploy.sh"
```

### Option 3: Using Screen for Persistent Session
```bash
ssh -i EduBot.pem ubuntu@54.236.6.22
cd /opt/edubot
screen -S deploy
bash deploy.sh
# Press Ctrl+A then D to detach
```

## What the Script Does

1. ✅ **System Check** - Verifies/installs Python3, Node.js, npm, git
2. ✅ **Backend Setup** - Creates venv, installs requirements.txt, fixes issues
3. ✅ **Frontend Setup** - Installs npm packages, builds Next.js app
4. ✅ **Environment** - Auto-configures .env files
5. ✅ **Launch Services** - Starts FastAPI (port 8000) + Next.js (port 3000)
6. ✅ **Monitoring** - Shows logs and status checks

## Access After Deployment

- **Admin Dashboard**: http://54.236.6.22:3000
- **API Documentation**: http://54.236.6.22:8000/docs
- **API Swagger UI**: http://54.236.6.22:8000/redoc

## Managing Services (via tmux)

### View Running Sessions
```bash
tmux list-sessions
```

### Backend Session
```bash
# Attach to backend
tmux attach-session -t edubot-api

# View logs
tail -f logs/api_error.log

# Detach (Ctrl+B then D)
```

### Frontend Session
```bash
# Attach to frontend
tmux attach-session -t edubot-ui

# View logs
tail -f logs/ui.log
```

### Stop Services
```bash
# Stop backend
tmux kill-session -t edubot-api

# Stop frontend
tmux kill-session -t edubot-ui

# Stop all
tmux kill-server
```

## Logs Location

All logs stored in `/opt/edubot/logs/`:
- `api_access.log` - Backend HTTP requests
- `api_error.log` - Backend errors
- `ui.log` - Frontend build/runtime logs
- `chatbot.log` - Application logs (if configured)

## Restarting Services

```bash
# Restart backend
tmux kill-session -t edubot-api
cd /opt/edubot
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 main:app

# Restart frontend
tmux kill-session -t edubot-ui
cd /opt/edubot/admin-ui
npm start
```

## Database Configuration

Update `/opt/edubot/.env` with:
```
DATABASE_URL=mysql+mysqlconnector://payroll_user:YOUR_PASSWORD@localhost:3306/whatsapp_chatbot
WHATSAPP_API_KEY=your_key
PAYSTACK_SECRET_KEY=your_key
```

Then restart services:
```bash
tmux kill-session -t edubot-api
cd /opt/edubot && source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## Troubleshooting

### Port Already in Use
Script auto-kills processes on ports 8000/3000

### Dependencies Failed
Script retries with `--no-cache-dir` or `--legacy-peer-deps`

### Database Connection Error
1. Verify MySQL is running: `sudo systemctl status mysql`
2. Check DATABASE_URL in `.env`
3. Test connection: `mysql -u payroll_user -p whatsapp_chatbot`

### Frontend Build Failed
Script auto-retries with increased memory: `NODE_OPTIONS=--max_old_space_size=4096`

### Can't Connect to Services
1. Check firewall: `sudo ufw status`
2. Allow ports: `sudo ufw allow 8000/tcp && sudo ufw allow 3000/tcp`
3. Check if services running: `tmux list-sessions`

## Nginx Reverse Proxy (Optional)

For production with domain:

```bash
sudo apt install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/edubot
```

Paste this config:

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name 54.236.6.22;  # or your domain

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/edubot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Health Check

```bash
# Check if services are running
curl http://localhost:8000/docs
curl http://localhost:3000

# Check process list
ps aux | grep python
ps aux | grep node

# Check ports
netstat -tlnp | grep -E '8000|3000'
```

## Next Steps

1. ✅ Run `bash deploy.sh` on AWS
2. ✅ Configure `.env` with actual credentials
3. ✅ Setup MySQL database
4. ✅ Configure domain/DNS if using custom domain
5. ✅ Setup SSL certificate with Let's Encrypt
6. ✅ Setup Nginx reverse proxy for production
7. ✅ Monitor logs and service health
