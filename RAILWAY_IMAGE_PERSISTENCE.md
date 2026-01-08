# Railway Persistent Storage for Image Uploads

## Problem Identified

Images are being uploaded and database records are being created, but **Railway's filesystem is ephemeral**:
- Files written to disk are deleted when the app restarts
- This is why we see file paths in the database but files don't exist on disk
- The admin dashboard can't display images because the files are gone

## Current Status

✅ **Working:**
- Image upload logic implemented
- WhatsApp media download functional
- Database stores file paths correctly
- Admin dashboard displays file paths
- File serving endpoints created (`/uploads/` and `/files/`)

❌ **Not Persistent:**
- Files are lost after app restart on Railway
- Only works locally where filesystem is persistent

## Solution: Configure Persistent Volume on Railway

### Step-by-Step Instructions

#### 1. Access Railway Dashboard
```
URL: https://railway.app/project/[YOUR_PROJECT_ID]
```

#### 2. Select Your Bot Service
- Click on the "Bot" or "FastAPI" service in your project

#### 3. Go to Settings
- Click "Settings" tab at the bottom left

#### 4. Find Volumes Section
- Look for "Volumes" or "Storage" section
- You may need to scroll down

#### 5. Create New Volume
- Click "Create Volume" or "Add Volume" button
- Fill in the following:

**Configuration:**
```
Mount Path:  /app/uploads
Size:        10GB (or larger if needed)
Label:       homework-uploads (optional)
```

#### 6. Deploy
- Click "Save" or "Deploy"
- Railway will restart your service with the volume attached
- Wait 2-3 minutes for deployment to complete

#### 7. Verify Setup
SSH into your Railway container and run:
```bash
df -h
```

You should see something like:
```
/dev/[volume-name]  10G  0  10G  0% /app/uploads
```

### 8. Test Image Upload

1. **Via WhatsApp:**
   - Send an image homework submission
   - Bot should save it to `/app/uploads/homework/{student_id}/`

2. **Verify on Dashboard:**
   - Go to: https://nurturing-exploration-production.up.railway.app/homework
   - Click "View Homework" on an image submission
   - Image should display in the modal

3. **Test Persistence:**
   - Upload an image
   - Restart the Railway service
   - Image should still exist and display

### Alternative: Use Cloud Storage (S3, Cloudinary, etc.)

If you prefer not to manage volumes, use cloud storage:

1. **AWS S3:**
   - Upload images directly to S3
   - Store S3 URL in database
   - Images persist automatically
   - No volume management needed

2. **Cloudinary or similar:**
   - Free tier available
   - Built-in image optimization
   - Global CDN delivery

### Current Code

**Image Upload Handler:**
- File: `api/routes/whatsapp.py` (lines 219-260)
- Saves to: `/app/uploads/homework/{student_id}/homework_{phone}_{timestamp}.jpg`
- Stores path in database as: `homework/{student_id}/homework_*.jpg`

**File Serving:**
- File: `main.py`
- Endpoints:
  - Static mount: `/uploads/{file_path}`
  - Secure endpoint: `/files/{file_path}`

**Frontend Display:**
- File: `admin-ui/pages/homework.tsx`
- URL construction: `/uploads/{file_path}`

## Troubleshooting

### Files show in database but not on disk after restart

**Solution:** Configure persistent volume (see above)

### Can't see images in admin dashboard

**Check:**
1. Visit `https://nurturing-exploration-production.up.railway.app/homework`
2. Open browser DevTools (F12)
3. Check Console for image loading errors
4. Check Network tab to see if `/uploads/` requests return 404

**If getting 404:**
- Volume may not be mounted
- App may have restarted and lost files
- Configure persistent volume

### Images display locally but not on Railway

**Solution:** Same as above - configure persistent volume on Railway

## Verification Script

Run locally to see which images exist:
```bash
python verify_image_paths.py
```

Output will show:
- Database records with file paths
- Which files actually exist on disk
- File sizes and locations
- Directory structure

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Image Download | ✅ Working | WhatsApp media download |
| File Storage Code | ✅ Working | Saves to /app/uploads/ |
| Database | ✅ Working | Stores file paths |
| Admin Dashboard | ✅ Working | Displays images (if files exist) |
| File Serving | ✅ Working | /uploads/ and /files/ endpoints |
| **Persistence** | ❌ Not Configured | Need persistent volume on Railway |

**Action Required:** Configure persistent volume on Railway for image uploads to survive app restarts.
