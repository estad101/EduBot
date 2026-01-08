# URGENT: Fix Frontend API Configuration (5-minute fix)

## What's Wrong
The Students page returns a 500 error because the frontend doesn't know how to reach the backend API.

## Why It Happened
When the frontend was deployed, the `NEXT_PUBLIC_API_URL` environment variable was not set in Railway. The frontend was built with a default value of `http://localhost:8000`, which doesn't work in production.

## How to Fix (Railway Web Dashboard)

### Step 1: Open Railway Dashboard
1. Go to: https://railway.app
2. Log in to your account
3. Click on your project

### Step 2: Select the Frontend Service
1. Look for the service called something like "nurturing-exploration-production" or "admin-ui"
2. Click on it to open the service details

### Step 3: Add Environment Variable
1. Click the **Variables** tab (or **Settings** → **Variables**)
2. Click **Add Variable** or the **+** button
3. Enter:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://edubot-production-cf26.up.railway.app`
4. Click **Add** to save

### Step 4: Redeploy the Frontend
1. Click **Deploy** or **Redeploy** button
2. Select the latest commit (2b8d9aa - "Add: Frontend API URL configuration...")
3. Click **Deploy** or **Confirm**
4. Wait for the build to complete (usually 2-5 minutes)

### Step 5: Test
Once deployed, visit:
- https://nurturing-exploration-production.up.railway.app
- Click on **Students** in the sidebar
- You should see the student list load successfully (no more 500 error)

## What Will Happen
1. Railway will rebuild the frontend with the correct API URL baked in
2. When the frontend runs, the axios client will know to call `https://edubot-production-cf26.up.railway.app/api/...`
3. API calls will succeed and the Students page will display data

## Testing After Fix

You can verify it worked by:

### Option A: Check Debug Endpoint (if pushed)
```
Visit: https://nurturing-exploration-production.up.railway.app/api/debug
Should show: "api_url": "https://edubot-production-cf26.up.railway.app"
```

### Option B: Use Browser DevTools
1. Open https://nurturing-exploration-production.up.railway.app/students
2. Press F12 (Developer Tools)
3. Go to **Network** tab
4. Refresh the page
5. Look for API requests like `/api/admin/students`
6. They should return status 200 (not 404)

### Option C: Simple curl test
```bash
curl https://nurturing-exploration-production.up.railway.app/api/admin/students
# Should return JSON with student data, not HTML 404 page
```

## Why The Backend Works But Frontend Doesn't

- **Backend Service** (`https://edubot-production-cf26.up.railway.app`)
  - ✅ Works perfectly
  - ✅ API endpoints return correct data
  - ✅ No code issues

- **Frontend Service** (`https://nurturing-exploration-production.up.railway.app`)
  - ❌ Can't reach the backend
  - ❌ Trying to call `http://localhost:8000` (hardcoded default)
  - ✅ Code is correct, just needs environment variable

## Key Files in This Fix

| File | What it Does |
|------|-------------|
| `admin-ui/Dockerfile` | Accepts `NEXT_PUBLIC_API_URL` as a build argument |
| `admin-ui/railway.json` | Tells Railway to pass env var as build arg: `${{ env.NEXT_PUBLIC_API_URL }}` |
| `admin-ui/lib/api-client.ts` | Uses the API URL: `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"` |

## If You Can't Access Railway Dashboard

Alternative: Redeploy the frontend service by pushing to GitHub:

```bash
# Add a minor change (like updating a comment)
git add -A
git commit -m "Trigger frontend rebuild"
git push origin main

# But IMPORTANT: First set the env var in Railway dashboard,
# because the push alone won't set the environment variable.
```

The push triggers a build, but without the environment variable set, it will still default to localhost.

## Summary

1. **The problem**: Missing `NEXT_PUBLIC_API_URL` environment variable in Railway
2. **The solution**: Set it to `https://edubot-production-cf26.up.railway.app` and redeploy
3. **Time to fix**: 5 minutes
4. **Code changes needed**: Zero (just environment configuration)
5. **Test after**: Visit /students page - should show student list without errors

