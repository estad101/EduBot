# 📦 Railway Volume Configuration for Image Uploads

## ✅ Volume Status
- **Status:** ✓ Attached to backend
- **Mount Path:** `/app/uploads`
- **Purpose:** Persistent storage for homework images, documents, etc.

---

## 🎯 What This Means

### Before (Without Volume):
- ❌ Uploaded files deleted when container restarts
- ❌ No persistent storage
- ❌ Images lost after deployment
- ❌ Can't recover files

### After (With Volume):
- ✅ Files persist across deployments
- ✅ Files survive container restarts
- ✅ Homework submissions saved permanently
- ✅ Student images safe
- ✅ Can recover files

---

## ⚙️ Configuration Required

### Step 1: Set UPLOADS_DIR Environment Variable

On your backend service (edubot-production-0701):

**Variable Name:** `UPLOADS_DIR`
**Variable Value:** `/app/uploads`

⚠️ **IMPORTANT:** This MUST exactly match the volume mount path!

### Step 2: Verify in Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Select: **marvelous-possibility** project
3. Click: **edubot-production-0701** service
4. Click: **Settings** tab (not Variables)
5. Look for **Storage** or **Volumes** section
6. You should see:
   - Volume Name: (something like `uploads` or `homework`)
   - Mount Path: `/app/uploads`

If you see this, volume is configured correctly! ✓

---

## 📁 How It Works

### Directory Structure
```
/app/uploads/
├── homework/
│   ├── student_001/
│   │   └── submission_1.jpg
│   ├── student_002/
│   │   └── submission_1.jpg
│   └── ...
└── other_uploads/
    └── ...
```

### File Upload Flow

1. **Student submits homework** with image
   ```
   POST /api/homework/upload-image
   ```

2. **Backend receives file**
   ```python
   file_path = f"/app/uploads/homework/{student_id}/{filename}"
   ```

3. **Volume saves file persistently**
   ```
   Railway Volume stores file
   File survives restart/redeploy
   ```

4. **File remains available after deployment**
   ```
   Next deployment can access same files
   No data loss
   ```

---

## ✅ Verification Checklist

- [ ] Volume attached to backend (confirmed)
- [ ] Mount path is `/app/uploads` (confirmed)
- [ ] UPLOADS_DIR environment variable = `/app/uploads` (you set this)
- [ ] Test: Submit homework with image
- [ ] Verify: Image appears in homework list
- [ ] Redeploy backend
- [ ] Verify: Image still appears (file persisted)

---

## 🧪 Testing File Upload

Once backend is running with UPLOADS_DIR set:

1. **Login to admin dashboard**
   ```
   https://nurturing-exploration-production.up.railway.app
   ```

2. **Go to Homework section**
   ```
   Click: Homework in sidebar
   ```

3. **Create test submission with image**
   ```
   Student ID: test_student
   Image: any JPG/PNG file
   Click: Submit
   ```

4. **Verify image saved**
   ```
   Should see "Submission successful"
   Image should appear in list
   ```

5. **Check persistence** (optional)
   ```
   Redeploy backend
   Image should still be there
   This confirms volume is working
   ```

---

## 🔍 Troubleshooting

### Problem: "Upload failed" error
**Solution:** 
- Check UPLOADS_DIR is set to `/app/uploads` on backend
- Check file size < MAX_FILE_SIZE_MB
- Check file type in ALLOWED_IMAGE_TYPES

### Problem: Files disappear after redeploy
**Solution:**
- Verify UPLOADS_DIR is set to `/app/uploads` (exact path)
- Check volume is attached in Railway dashboard
- Restart backend service and try again

### Problem: Can't see uploaded files
**Solution:**
- Check backend logs for upload errors
- Verify path `/app/uploads` exists
- Check file permissions
- Restart container

### Problem: "Permission denied" error
**Solution:**
- Volume should have correct permissions automatically
- If not, contact Railway support
- Provide: service name and mount path

---

## 📊 Storage Limits

- **Default Quota:** Railway volumes usually 1GB free
- **Typical Usage:** 
  - 5MB per image × 100 students = 500MB
  - 100MB of documents = total 600MB
- **You Have:** Plenty of space for typical use

If you need more storage:
- Upgrade Railway plan
- Or delete old submissions after semester ends

---

## 🔐 Security Notes

- Files in volume are private to your backend
- Not accessible from internet directly
- Only accessed through API endpoints with auth
- Volume is encrypted at rest by Railway

---

## 📚 Related Files

- `config/settings.py` - Reads UPLOADS_DIR env var
- `utils/file_handler.py` - Handles file operations
- `api/routes/homework.py` - Image upload endpoint

---

## Next Steps

1. ✓ Volume is attached (done)
2. Set UPLOADS_DIR = `/app/uploads` on backend
3. Redeploy backend
4. Test file upload
5. Verify files persist after redeploy

You're all set! Files will now persist. 🎉
