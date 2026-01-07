# RAILWAY EXACT SETUP - STEP BY STEP

## Your Current Setup

| Component | URL |
|-----------|-----|
| Frontend (Admin UI) | `https://nurturing-exploration-production.up.railway.app` |
| Backend (API) | `https://edubot-production-cf26.up.railway.app` |
| Database | Railway MySQL |

---

## EXACT STEPS TO FIX LOGIN (Follow Precisely)

### STEP 1: Go to Railway Admin UI Service Variables

1. Open: https://railway.app
2. Click your project name
3. You'll see multiple services listed
4. **Click the service called "Admin UI"** (NOT Backend)
5. You'll see tabs at the top: Overview, Deploy, Logs, Settings, **Variables**
6. **Click "Variables" tab**

### STEP 2: Add Environment Variable

In the Variables section:

1. Look for a button that says **"Add Variable"** or **"New Variable"**
2. Click it
3. You'll see two input boxes:
   - Left box: **Name**
   - Right box: **Value**

**Enter exactly:**
```
Name:  NEXT_PUBLIC_API_URL
Value: https://edubot-production-cf26.up.railway.app
```

**Verification checklist:**
- [ ] Name is: `NEXT_PUBLIC_API_URL` (exactly, with capitals and underscore)
- [ ] Value starts with: `https://` (not http)
- [ ] Value is: `edubot-production-cf26.up.railway.app`
- [ ] No extra spaces before or after
- [ ] No trailing slash at the end

4. Click **"Add"** or press Enter

### STEP 3: Trigger Build

1. Click **"Deploy"** tab (next to Variables)
2. Look at your deployment history - you'll see past deployments listed
3. Find **"Trigger Deploy"** button (usually at the top right)
4. **Click it**

**You should see:**
```
Building...
```

This means the build started. Wait...

### STEP 4: Wait for Build Complete

**Watch the logs.** You should see messages like:**

```
Building...
[npm install messages...]
[npm build messages...]
Build successful ✅
Deployment successful ✅
```

**How long?** 2-3 minutes usually

**Don't close this tab while building.**

Once you see **"Build successful"**, the deploy is done.

### STEP 5: Clear Browser Cache

1. Go to your login page: `https://nurturing-exploration-production.up.railway.app/login`
2. Press **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
   - This is a "hard refresh" that clears the cache
   - Regular F5 refresh won't work

Wait for page to load fully.

### STEP 6: Verify API URL

1. Press **F12** on your keyboard
   - DevTools window opens at bottom
2. Click **"Console"** tab
3. Look at the logged messages
4. Find this line:
   ```
   [APIClient] Initialized with API_URL: https://edubot-production-cf26.up.railway.app
   ```

**This must show your backend URL, NOT localhost!**

If it shows `http://localhost:8000`, go back to Step 1 and repeat.

### STEP 7: Test Login

1. In the login form, enter:
   - **Username:** `admin`
   - **Password:** `marriage2020!`
2. Click **"Login"** button
3. You should see a brief loading indicator
4. Then redirect to **Dashboard** page

**If Dashboard loads, login works 100%!** ✅

---

## TROUBLESHOOTING

### Problem: Console still shows `http://localhost:8000`

**Solution:**
1. Go back to Admin UI → Variables
2. Check if `NEXT_PUBLIC_API_URL` is there
3. If missing, add it again
4. If present, delete it and re-add carefully
5. Trigger Deploy again
6. Wait for "Build successful"
7. Hard refresh (Ctrl+Shift+R)
8. Check console again

### Problem: Build fails or shows errors

**Solution:**
1. Check the logs carefully for error messages
2. Look for lines starting with "ERROR"
3. Common issues:
   - Wrong variable name (must be exactly `NEXT_PUBLIC_API_URL`)
   - Special characters in value
   - Space at start or end

Try deleting the variable and re-adding it.

### Problem: Still getting "Login failed"

**Solution:**
1. Check Network tab in DevTools (F12)
2. Look for POST request to `/api/admin/login`
3. What status code? (should be 200)
4. Check Response tab - what error message?
5. Verify username is `admin` and password is `marriage2020!`

### Problem: "Build successful" never appears

**Solution:**
1. Wait longer (builds can take 3-5 minutes)
2. Refresh the page (F5)
3. Check if any error messages appeared
4. Try "Trigger Deploy" again
5. Make sure you're in the Admin UI service, not Backend

---

## FINAL VERIFICATION

After login works, verify these are set:

**Admin UI Service → Variables:**
- ✅ `NEXT_PUBLIC_API_URL=https://edubot-production-cf26.up.railway.app`

**Backend Service → Variables:**
- ✅ `DATABASE_URL=mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway`
- ✅ `ADMIN_PASSWORD=marriage2020!`
- ✅ `ALLOW_ORIGINS=https://nurturing-exploration-production.up.railway.app`
- ✅ `ADMIN_ORIGIN=https://nurturing-exploration-production.up.railway.app`

---

## QUICK REFERENCE

| Action | Location |
|--------|----------|
| Set API URL | Admin UI → Variables |
| Trigger build | Admin UI → Deploy → Trigger Deploy |
| Check build | Admin UI → Deploy → Look at logs |
| Test login | Visit login page, press F12, check console |
| Backend settings | Backend → Variables |

---

## EXPECTED BEHAVIOR

### When working correctly:

1. Visit login page
2. Console shows: `[APIClient] Initialized with API_URL: https://edubot-production-cf26.up.railway.app`
3. Enter admin/marriage2020!
4. Click Login
5. POST request sent to backend
6. Backend returns token
7. Redirect to Dashboard
8. Dashboard loads with data
9. ✅ Login 100% working!

---

## TIMELINE

- Step 1-2: 1 minute (set variable)
- Step 3-4: 3 minutes (wait for build)
- Step 5-6: 1 minute (verify)
- Step 7: 1 minute (test)

**Total: ~6 minutes**

---

**DO THIS NOW AND LOGIN WILL WORK 100%** 🚀
