# Frontend Deployment to Railway - Quick Start

## What I've Set Up

✅ Created Dockerfile for Next.js frontend (optimized for production)
✅ Created .dockerignore for efficient builds
✅ Created Railway configuration files
✅ Created deployment guide in `admin-ui/RAILWAY_DEPLOYMENT.md`
✅ Committed and pushed to GitHub

## Deploy in 3 Steps

### Step 1: Go to Your Railway Project
Visit: https://railway.app/project

### Step 2: Create Frontend Service
1. Click **"Create Service"** → **"Deploy from GitHub"**
2. Select **estad101/EduBot** repository
3. **Important:** Set root directory to **`admin-ui/`**
4. Click **"Deploy"**

Railway will auto-detect the Dockerfile and build!

### Step 3: Set Environment Variables
Once the service is created:

1. Click the new **"edubot-admin"** service card
2. Go to the **"Variables"** tab
3. Add this variable:
   ```
   NEXT_PUBLIC_API_URL=https://edubot-production-cf26.up.railway.app
   ```
4. Save

That's it! The frontend will deploy automatically.

## Access Your Dashboard

After deployment (2-3 minutes), you'll get a URL like:
```
https://edubot-admin-<random>.up.railway.app
```

This will be shown in your Railway dashboard.

## What's Happening Behind the Scenes

1. **Dockerfile** builds the Next.js app (multi-stage build for optimization)
2. **Port 3000** is exposed for the frontend
3. **Environment variable** `NEXT_PUBLIC_API_URL` points frontend to backend API
4. **Health checks** ensure the app stays running

## Frontend Features

The admin dashboard includes:
- 📊 Dashboard with metrics
- 👥 Student management
- 📝 Homework tracking
- 💳 Payment processing
- 📱 WhatsApp status
- ⚙️ Settings & configuration

## Troubleshooting

**If deployment fails:**
1. Check Railway logs in dashboard
2. Verify `admin-ui/` is the root directory
3. Ensure Node.js 18+ compatibility

**If frontend can't reach API:**
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check backend at `https://edubot-production-cf26.up.railway.app/api/health`
3. Ensure backend is running

## Next Steps

1. Deploy frontend using steps above
2. Access dashboard at provided Railway URL
3. Log in with admin credentials
4. Test API endpoints from dashboard
5. Configure custom domain (optional)

---

**Already configured:** Backend, Database, API, Webhooks ✅
**Ready to deploy:** Frontend 🚀
