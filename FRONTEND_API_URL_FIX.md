# Frontend API URL Configuration Fix

## Problem
The frontend (`https://nurturing-exploration-production.up.railway.app`) is unable to connect to the API, returning 500 errors on the `/students` page.

## Root Cause
The `NEXT_PUBLIC_API_URL` environment variable is NOT set in the Railway frontend service during deployment. This causes the frontend to default to `http://localhost:8000`, which is not accessible from production.

## Diagnosis Results

### ✅ Backend API is Working
```
URL: https://edubot-production-cf26.up.railway.app/api/admin/students
Status: 200 OK
Response: Successfully returns student data
```

### ✅ API Code is Correct
- No syntax errors found in `admin/routes/api.py`
- The `/api/admin/students` endpoint is properly implemented
- The recent DELETE endpoint changes (commit dbc7294) did NOT introduce any bugs

### ❌ Frontend Configuration is Missing
- The `NEXT_PUBLIC_API_URL` environment variable is required during build
- Without it, the frontend defaults to `http://localhost:8000`
- This causes all API requests to fail

## Solution

### Step 1: Add Environment Variable to Railway Frontend Service

In the Railway dashboard:
1. Go to the **Frontend Service** (nurturing-exploration-production)
2. Click **Variables**
3. Add a new variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://edubot-production-cf26.up.railway.app`

### Step 2: Trigger a Rebuild

Option A: Manual Rebuild
1. In Railway dashboard, click the **Frontend Service**
2. Click **Deploy** → **Redeploy**
3. Select the latest commit and click **Deploy**

Option B: Push a New Commit
```bash
# Make a minor commit (e.g., update docs, add a comment)
git add .
git commit -m "Trigger frontend rebuild with API URL configuration"
git push origin main
```

This will automatically trigger a rebuild with the new environment variable.

### Step 3: Verify the Fix

After the frontend redeploys:
1. Visit `https://nurturing-exploration-production.up.railway.app`
2. Navigate to the Students page
3. The page should load successfully and display the student list

You can also test the API endpoint directly:
```bash
curl https://nurturing-exploration-production.up.railway.app/api/admin/students
```

This should return student data, not a 404.

## Architecture Clarification

The deployment uses two separate Railway services:

**Frontend Service**
- URL: `https://nurturing-exploration-production.up.railway.app`
- Technology: Next.js (Node.js)
- Dockerfile: `admin-ui/Dockerfile`
- Needs to know the backend URL via `NEXT_PUBLIC_API_URL` environment variable

**Backend Service**
- URL: `https://edubot-production-cf26.up.railway.app`
- Technology: FastAPI (Python)
- Dockerfile: `Dockerfile`
- Provides all API endpoints at `/api/**` routes

The frontend makes requests to the backend at build time and runtime using the configured API URL.

## Files Involved

| File | Purpose |
|------|---------|
| `admin-ui/Dockerfile` | Defines build args for `NEXT_PUBLIC_API_URL` |
| `admin-ui/railway.json` | Passes environment variable as build arg to Docker |
| `admin-ui/lib/api-client.ts` | Uses `NEXT_PUBLIC_API_URL` to configure axios |
| `admin-ui/.env.production` | Documentation of the required variable (not used by Docker build) |
| `admin/routes/api.py` | Backend API endpoints (working correctly ✅) |

## Why This Wasn't Working Before

During previous deployments, the Railway frontend service was built without the `NEXT_PUBLIC_API_URL` environment variable. The default value of `http://localhost:8000` was baked into the build, which is unreachable from the browser.

The `railway.json` and `Dockerfile` are correctly configured to accept the environment variable - it just needs to be set in Railway's service configuration.

## No Code Changes Needed

The recent code changes (commit dbc7294) that removed the duplicate DELETE endpoint are **completely fine**. The bug was never in the code - it was purely an infrastructure/configuration issue with the environment variables.

The `/api/admin/students` endpoint works perfectly:
- ✅ Local testing: Works
- ✅ Backend service testing: Works  
- ✅ Code review: No errors found
- ❌ Frontend integration: Fails due to missing environment variable

