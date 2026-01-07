# ⏱️ QUICK START - 15 MINUTES TO WORKING LOGIN

## Do This Now (Copy & Paste)

### 🟦 PART 1: Backend Variables (3 minutes)

1. Go to: https://railway.app/dashboard
2. Click: Backend service
3. Click: Variables tab
4. Paste these 4 variables:

```
DATABASE_URL
mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
```

```
SECRET_KEY
edu-bot-secret-key-production-2024-123456789
```

```
ADMIN_PASSWORD
marriage2020!
```

```
DEBUG
False
```

5. Scroll up → Click **Deploy**
6. Click **Trigger Deploy** button
7. ⏳ Wait 3 minutes for "Build successful" message

---

### 🟦 PART 2: Frontend Variables (2 minutes)

1. Go back to dashboard
2. Click: **Admin UI** service
3. Click: **Variables** tab
4. Paste this 1 variable:

```
NEXT_PUBLIC_API_URL
https://edubot-production-cf26.up.railway.app
```

5. Click **Deploy** tab
6. Click **Trigger Deploy** button
7. ⏳ Wait 3 minutes for "Build successful" message

---

### 🟦 PART 3: Test (2 minutes)

1. Open: https://nurturing-exploration-production.up.railway.app/login
2. Hard refresh: **Ctrl+Shift+R** or **Cmd+Shift+R**
3. Open DevTools: **F12** → **Console**
4. Should see: `[APIClient] Initialized with API_URL: https://edubot-production-cf26.up.railway.app`
5. Login: `admin` / `marriage2020!`
6. Should redirect to dashboard ✅

---

## That's It!

| Task | Time | Done? |
|------|------|-------|
| Set 4 Backend variables | 2 min | ☐ |
| Trigger Backend rebuild | 1 min | ☐ |
| Wait for Backend build | 3 min | ☐ |
| Set 1 Frontend variable | 1 min | ☐ |
| Trigger Frontend rebuild | 1 min | ☐ |
| Wait for Frontend build | 3 min | ☐ |
| Test login | 2 min | ☐ |

**TOTAL: ~15 minutes**

---

## If You Get Stuck

### Error: "CORS policy" 
→ Make sure Backend rebuilt (check logs for "Build successful")

### Error: "localhost connection refused"
→ Make sure Frontend rebuilt (console should show backend URL, not localhost)

### Error: "Invalid credentials"
→ Check Backend variables are set correctly

### Error: Database connection error
→ Check DATABASE_URL matches exactly

---

## Success Looks Like

✅ Dashboard loads
✅ Shows student data
✅ All admin features work

---

**Start now! 🚀**
