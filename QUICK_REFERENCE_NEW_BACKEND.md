# ⚡ Quick Reference: New Backend Deployment

## Critical Values - Save These!

```
DATABASE_URL=mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
FRONTEND_URL=https://nurturing-exploration-production.up.railway.app
OLD_BACKEND_URL=https://edubot-production-cf26.up.railway.app (DELETED)
NEW_BACKEND_URL=https://[will-get-after-deployment]
```

## 5-Minute Setup Checklist

- [ ] Create new service in Railway (+ New button)
- [ ] Configure Dockerfile deployment
- [ ] Add DATABASE_URL variable (see value above - CRITICAL!)
- [ ] Add other variables (API config, WhatsApp, etc.)
- [ ] Click Deploy
- [ ] Wait for "APPLICATION READY" in logs
- [ ] Get new backend URL from Domains section
- [ ] Update frontend NEXT_PUBLIC_API_URL with new backend URL
- [ ] Test login page loads
- [ ] Test /api/health endpoint
- [ ] Test status indicators show "Connected"

## Key Variables (Must Set!)

### Required:
```
DATABASE_URL=mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
SECRET_KEY=your-long-random-key-32-chars-minimum
ADMIN_PASSWORD=your_password
```

### Recommended:
```
API_TITLE=EduBot API
ENVIRONMENT=production
DEBUG=False
HTTPS_ONLY=True
```

### For Frontend to Work:
```
NEXT_PUBLIC_API_URL=https://[your-new-backend-url]
```

## Expected Build Log Output

```
Using Detected Dockerfile
Build time: 15-20 seconds
...
[Settings] ✓ Database URL configured: mysql+pymysql://...railway
✓ Database engine created successfully
=== APPLICATION READY ===
```

## Test Endpoints

1. Frontend: https://nurturing-exploration-production.up.railway.app
2. Backend: https://[new-url]/api/health
3. Status check: After login, dashboard should show "Database Connected"

## If Something Breaks

1. Check Deploy Logs for exact error
2. Common issue: DATABASE_URL pointing to localhost (use the value above)
3. If all else fails: Delete service and start fresh (code is stable)

## Support

All code is production-ready and tested locally.
If deployment fails, it's almost always DATABASE_URL issue.
