# Update Frontend with New Backend URL

The new backend URL is: **https://edubot-production-0701.up.railway.app**

## Steps to Update Frontend:

1. Go to: https://railway.app/dashboard
2. Select **marvelous-possibility** project
3. Click **nurturing-exploration** (Frontend) service
4. Click **Variables** tab
5. Find **NEXT_PUBLIC_API_URL**
6. Update the value to:
   ```
   https://edubot-production-0701.up.railway.app
   ```
7. Click **Save**
8. Frontend will auto-redeploy

## After Update:

The frontend will automatically redeploy with the new backend URL. This should take ~30-60 seconds.

## Test:

1. Visit: https://nurturing-exploration-production.up.railway.app
2. You should see the login page
3. After login, dashboard should load with status indicators showing:
   - Database: Connected ✓
   - WhatsApp: Configured ✓
