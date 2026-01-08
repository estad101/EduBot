# Complete WhatsApp Image Upload & Display Guide

## The Complete Flow - What Should Happen

### 1. Student Sends Image via WhatsApp
```
Student: [sends homework photo]
↓
WhatsApp Cloud API receives image
↓
Sends webhook to your bot with:
  - image_id: "wamid.xxx..."
  - from: "+234XXXXXXXXXX"
  - message_type: "image"
```

### 2. Bot Processes Image
```
Bot receives webhook
↓
Checks conversation state: "homework_submitted" ✓
Checks message type: "image" ✓
Checks submission type: "IMAGE" ✓
↓
Calls WhatsAppService.download_media(image_id)
↓
WhatsApp returns media URL
↓
Download actual image bytes from URL
```

### 3. Bot Saves Image
```
IF download successful:
  ├─ Create: /app/uploads/homework/{student_id}/ (on Railway)
  │         or uploads/homework/{student_id}/ (local)
  ├─ Save file: homework_{phone}_{timestamp}.jpg
  ├─ Verify file exists and has content
  └─ Store path in database: homework/{student_id}/filename.jpg
ELSE:
  ├─ Create TEXT submission instead
  ├─ Include image_id in message
  └─ Tell user to try again
```

### 4. Bot Responds to Student
```
IF image saved successfully:
  ┌─────────────────────────────────────┐
  │ ✅ Homework submitted successfully! │
  │ 🎓 A tutor has been assigned        │
  └─────────────────────────────────────┘
ELSE:
  ┌──────────────────────────────────────────┐
  │ ⚠️ Image upload had an issue             │
  │ But homework was submitted as text       │
  │ Please try uploading the image again     │
  └──────────────────────────────────────────┘
```

### 5. Admin Views in Dashboard
```
Admin goes to: /homework
↓
See list of submissions (sorted by latest)
↓
Find IMAGE submission (green "IMAGE" badge)
↓
Click "View Homework" button
↓
Modal opens with image displayed
↓
Can click "Open Image in New Tab"
```

## How Image Paths Work

### Path Format
```
Database stores (relative):  homework/6/homework_2348109508833_1767884474455.jpg
Frontend URL:               /uploads/homework/6/homework_2348109508833_1767884474455.jpg
Local disk:                 C:\xampp\htdocs\bot\uploads\homework\6\...
Railway disk:               /app/uploads/homework/6/...
```

### Path Resolution
```
Frontend requests: GET /uploads/homework/6/filename.jpg
         ↓
Backend StaticFiles mount at /uploads
         ↓
Looks in configured directory:
  - On Railway: /app/uploads/
  - Local: ./uploads/
         ↓
Returns: /app/uploads/homework/6/filename.jpg (or local equivalent)
```

## What Can Go Wrong

### Problem 1: Image Download Timeout
**Symptom**: Submission created as TEXT, not IMAGE  
**Cause**: WhatsApp API took too long to respond  
**Solution**: User resends image, usually works second time  
**Code**: Falls back to TEXT automatically with user notice

### Problem 2: File Not Saved to Disk
**Symptom**: Database has file_path but file doesn't exist  
**Cause**: Permission error, disk full, or path issue  
**Check**: Look in uploads/homework/{student_id}/ directory  
**Fix**: Check directory exists and is writable

### Problem 3: Wrong Path Format
**Symptom**: Database shows "/app/uploads/homework/..." instead of "homework/..."  
**Cause**: Absolute path saved instead of relative  
**Fix**: Already fixed in updated code  
**Verify**: Database should show: `homework/{id}/filename.jpg`

### Problem 4: Image Shows 404 in Modal
**Symptom**: Modal displays "(No image file available)"  
**Cause 1**: Image upload actually failed (fell back to TEXT)  
**Cause 2**: File exists locally but not on Railway volume  
**Cause 3**: Path mismatch between database and disk  
**Check**: 
  - Is submission_type "IMAGE" in database?
  - Does file exist on disk?
  - Is path format correct?

### Problem 5: Works Locally, Fails on Railway
**Symptom**: Local testing works, Railway shows 404  
**Cause**: New uploads saved to ephemeral filesystem  
**Solution**: Fixed in updated code - now uses `/app/uploads` if available  
**Verify**: Check Railway volume is mounted at /app/uploads

## Testing Steps

### Test 1: Configuration Check
```bash
python diagnose_upload_flow.py
# Should show:
# - WhatsApp API Key: SET
# - Phone Number ID: SET
# - Upload directory: EXISTS and WRITABLE
```

### Test 2: Manual Image Test
```
1. Open WhatsApp chat with bot
2. Send: "homework"
3. Send: "Math" (or any subject)
4. Send: "image"
5. Send: [actual photo from phone]
6. Wait for bot response
```

**Check logs for**:
```
"Starting image download"
"Downloaded media: XXXXX bytes"  ← Should show > 0
"Image saved successfully"
"Database path: homework/{id}/..."
```

### Test 3: Database Verification
```bash
# Check if IMAGE submission was created
SELECT * FROM homework WHERE submission_type='IMAGE' ORDER BY created_at DESC LIMIT 1;

# Should show:
# - submission_type: IMAGE
# - file_path: homework/{student_id}/homework_*.jpg
# - status: ASSIGNED (or whatever)
```

### Test 4: File Existence
```bash
# Check if actual file exists
ls -la uploads/homework/{student_id}/
# Should show homework_*.jpg files

# Check file size
ls -lh uploads/homework/{student_id}/homework_*.jpg
# Should show > 0 bytes
```

### Test 5: Modal Display
```
1. Go to: https://app.railway.app/homework
2. Find IMAGE submission
3. Click "View Homework"
4. Image should display in modal
   OR
   "(No image file available)" if file missing
5. Click "Open Image in New Tab"
6. Full image should load in new tab
```

## Debugging Checklist

When images don't upload:

- [ ] WhatsApp API key is valid (check .env)
- [ ] Phone number ID is valid (check .env)
- [ ] uploads/homework/ directory exists
- [ ] Directory is writable (check permissions)
- [ ] Submission state is "homework_submitted" when image sent
- [ ] Message type is "image" (actual photo, not text)
- [ ] Logs show "Downloaded media: X bytes" (X > 0)
- [ ] File exists in uploads/homework/{student_id}/
- [ ] Database has file_path (not NULL)
- [ ] Path format is "homework/{id}/filename.jpg" (relative)
- [ ] Frontend requests `/uploads/{db_path}`
- [ ] Backend serves from /app/uploads or ./uploads

## Code Changes Made

### Updated whatsapp.py (Lines 210-240)
**Change**: Now uses Railway volume if available
```python
# Before: upload_dir = "uploads/homework"
# After:
railway_uploads = "/app/uploads/homework"
local_uploads = "uploads/homework"
upload_dir = railway_uploads if os.path.exists("/app/uploads") else local_uploads
```

**Change**: Improved path extraction
```python
# Before: relative_path = os.path.relpath(file_path)
# After: Extract last 2 path components (student_id/filename)
path_parts = file_path.replace('\\', '/').split('/')
relative_path = "{}/{}".format(path_parts[-2], path_parts[-1])
```

### Updated main.py (Lines 183-220)
**Already done**: Path detection for Railway volume
- Checks /app/uploads first
- Falls back to ./uploads
- Updates both StaticFiles mount and /files endpoint

## Expected Results After Fixes

✅ Real WhatsApp images download and save  
✅ Files saved to persistent volume (/app/uploads)  
✅ Database stores correct relative paths  
✅ Admin modal displays images correctly  
✅ Works consistently on Railway  

## If Still Issues

1. **Check Railway logs**: 
   - SSH into container
   - Check /app/uploads directory exists
   - Verify volume is mounted

2. **Check network**:
   - WhatsApp API might be rate limiting
   - Timeout might be too short (currently 30 seconds)
   - Try from different network

3. **Check database**:
   - Verify file_path is being saved
   - Check submission_type is 'IMAGE'
   - Look for error messages in logs

4. **Test with known good image**:
   - Use smaller image first
   - Try a simple JPG
   - Avoid very large files

## Next Steps

1. Push code changes to Railway
2. Test with real WhatsApp upload
3. Monitor logs for download success
4. Verify file appears on disk
5. Check modal displays image
6. Confirm "Open in New Tab" works
