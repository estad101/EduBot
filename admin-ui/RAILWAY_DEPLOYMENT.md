# EduBot Admin Frontend - Railway Deployment Guide

## Overview
This guide covers deploying the Next.js admin dashboard to Railway alongside the backend API.

## Prerequisites
- Railway project already set up with backend
- Next.js app ready in `admin-ui/` folder
- Git repository configured

## Deployment Steps

### 1. Create Frontend Service in Railway

#### Option A: Via Railway Dashboard (Recommended)
1. Go to your Railway project: https://railway.app/project
2. Click **"Create Service"** → **"Deploy from GitHub"**
3. Select your **estad101/EduBot** repository
4. Set the root directory to `admin-ui/`
5. Railway will automatically detect the Dockerfile

#### Option B: Via Railway CLI
```bash
cd admin-ui
railway service create edubot-admin
railway link <your-project-id>
railway up
```

### 2. Configure Environment Variables

Add these Railway variables for the frontend service:

```
NEXT_PUBLIC_API_URL=https://edubot-production-cf26.up.railway.app
NODE_ENV=production
```

**Steps:**
1. Go to your Railway project dashboard
2. Click the new **"edubot-admin"** service
3. Go to **"Variables"** tab
4. Add the variables above

### 3. Configure Port

Railway will automatically set `PORT=3000` for the Next.js app. The Dockerfile is configured to run on port 3000.

### 4. Deploy

Once configured, the app will auto-deploy when you push to GitHub or manually trigger:

```bash
railway up
```

## Access the Dashboard

Once deployed, your admin dashboard will be available at:
```
https://edubot-admin-<random-id>.up.railway.app
```

(Railway will provide the exact URL)

## Environment Variables Reference

| Variable | Value | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://edubot-production-cf26.up.railway.app` | Backend API URL |
| `NODE_ENV` | `production` | Set to production |
| `NEXT_TELEMETRY_DISABLED` | `1` | Optional: disable Next.js telemetry |

## API Configuration

The frontend connects to the backend at the URL specified in `NEXT_PUBLIC_API_URL`. Make sure this points to your deployed backend:

```typescript
// lib/api-client.ts uses this URL for all API calls
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Features Available in Admin Dashboard

- **Dashboard**: Overview of app metrics
- **Students**: Manage student accounts
- **Homework**: View and manage homework submissions
- **Payments**: Track payment transactions
- **Subscriptions**: Manage student subscriptions
- **Reports**: View analytics and reports
- **Settings**: Configure application settings
- **WhatsApp Status**: Monitor WhatsApp connection

## Local Testing

To test locally before deploying:

```bash
cd admin-ui
npm install
npm run build
npm start
```

Then visit: `http://localhost:3000`

## Troubleshooting

### Dashboard not connecting to API
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is running and accessible
- Check CORS settings in backend config

### Build fails
- Ensure `package.json` has all required dependencies
- Check Node.js version compatibility (18+)
- Review build logs in Railway dashboard

### Application crashes on startup
- Check Railway logs: `railway logs`
- Verify environment variables are set
- Ensure Dockerfile and build process are correct

## Next Steps

1. ✅ Deploy admin UI to Railway
2. ✅ Configure environment variables
3. Test dashboard at provided URL
4. Verify all API endpoints work
5. Set up custom domain (optional)

## Support

For Railway-specific issues, check:
- https://docs.railway.app/
- https://railway.app/status

For app-specific issues, check:
- Backend logs at `https://edubot-production-cf26.up.railway.app/api/health`
- Frontend logs in Railway dashboard
