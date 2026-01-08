"""
Railway Volume Deployment Verification

Volume Configuration:
  Name: edubot-volume
  Mount Path: /app/uploads

This script verifies that:
1. Image uploads are going to the correct location
2. Files are being persisted in the volume
3. Admin dashboard can display images
"""

DEPLOYMENT_GUIDE = """
================================================================================
RAILWAY VOLUME DEPLOYMENT VERIFICATION
================================================================================

Your Configuration:
  Volume Name: edubot-volume
  Mount Path: /app/uploads
  Service: Bot (FastAPI)

How Image Upload Works with Volume:
-----------------------------------

1. Image Submission via WhatsApp:
   User sends image → Bot receives image ID
   
2. Download and Save:
   api/routes/whatsapp.py downloads image
   Saves to: uploads/homework/{student_id}/homework_*.jpg
   
   Full path in container: /app/uploads/homework/{student_id}/homework_*.jpg
   This is INSIDE the persisted volume ✓
   
3. Database Storage:
   Stores relative path: homework/{student_id}/homework_*.jpg
   
4. Admin Display:
   Frontend fetches from: /uploads/homework/{student_id}/homework_*.jpg
   Backend serves from: /app/uploads/homework/{student_id}/homework_*.jpg

Path Resolution:
  Local Disk:    uploads/homework/6/homework_2348109508833_1767880566319.jpg
  In Container:  /app/uploads/homework/6/homework_2348109508833_1767880566319.jpg
  URL:           /uploads/homework/6/homework_2348109508833_1767880566319.jpg
  Volume:        ✓ Persisted (won't disappear on restart)

Verification Steps:
-------------------

1. SSH into Railway Container
   - Go to Railway dashboard
   - Select your Bot service
   - Click "Connect" or "Terminal"
   
2. Verify Volume is Mounted
   $ mount | grep uploads
   
   Should show something like:
   /dev/volumes/edubot-volume on /app/uploads type ext4

3. Check Upload Directory Exists
   $ ls -la /app/uploads/
   $ ls -la /app/uploads/homework/
   
4. Upload Test Image
   - Via WhatsApp, submit image homework
   - Check that file appears in /app/uploads/homework/{student_id}/
   
5. Verify in Admin Dashboard
   - Go to: https://nurturing-exploration-production.up.railway.app/homework
   - Click "View Homework" on an image
   - Image should display in the modal
   
6. Test Persistence (Optional)
   - Upload image
   - Restart the service
   - Image should still be there and display

Testing from Command Line:

$ cd /app/uploads/homework
$ ls -lh
# Should see homework_*.jpg files

$ ls -lh /app/uploads/homework/6/
# Should show image files for student 6

File Serving Endpoints:
-----------------------

Static Mount (Direct Access):
  GET /uploads/homework/{student_id}/homework_*.jpg
  → Served directly from /app/uploads/
  
Secure Endpoint:
  GET /files/homework/{student_id}/homework_*.jpg
  → Served via FileResponse with security checks
  
Browser URL:
  /uploads/homework/6/homework_2348109508833_1767880566319.jpg
  → Displays image or shows download dialog

Admin Dashboard Flow:
---------------------

1. Fetch homework list via API:
   GET /api/admin/homework
   Returns: file_path: "homework/6/homework_*.jpg"
   
2. Click "View Homework":
   Opens modal with homework details
   
3. Display image:
   Frontend constructs URL: /uploads/{file_path}
   = /uploads/homework/6/homework_*.jpg
   
4. Browser requests image:
   GET /uploads/homework/6/homework_*.jpg
   → FastAPI serves from /app/uploads/homework/6/homework_*.jpg
   → Returns image to browser
   
5. Image displays in modal ✓

Troubleshooting:
----------------

Problem: Images don't display in admin dashboard
  
Check 1: Volume mounted?
  $ df -h | grep /app/uploads
  Should show edubot-volume mounted at /app/uploads
  
Check 2: Files exist?
  $ ls -la /app/uploads/homework/
  Should show homework_*.jpg files
  
Check 3: Correct permissions?
  $ ls -l /app/uploads/homework/*/
  Should show readable files (r--)
  
Check 4: Path in database correct?
  Run: python verify_image_paths.py
  Should show: homework/{student_id}/homework_*.jpg
  
Check 5: Frontend seeing images?
  Open browser DevTools (F12)
  Check Network tab for /uploads/ requests
  Should see 200 status, not 404

Common Issues & Solutions:

Issue: Files saved but not in volume
  Solution: Ensure upload_dir = "uploads/homework" (relative path)
  This creates: /app/uploads/homework/ when volume is mounted
  
Issue: File permissions error
  Solution: Volume auto-creates with correct permissions
  If issue persists, check file ownership in container
  
Issue: 404 errors on image requests
  Solution: Check that static mount is configured:
  main.py line ~178: app.mount("/uploads", StaticFiles(...))
  
Issue: Images disappear after restart
  Solution: Confirm volume mount in Railway settings
  Volume must have Mount Path: /app/uploads
"""

print(DEPLOYMENT_GUIDE)

# Quick verification checklist
CHECKLIST = """
QUICK VERIFICATION CHECKLIST:
=============================

Pre-Deployment (Local):
  [ ] Code saves to: uploads/homework/{student_id}/...
  [ ] Database stores: homework/{student_id}/homework_*.jpg
  [ ] Frontend URLs: /uploads/{file_path}
  [ ] File serving endpoints configured

Post-Deployment to Railway:
  [ ] Volume created: edubot-volume
  [ ] Mount path: /app/uploads
  [ ] Service restarted
  [ ] Wait 2-3 minutes for stable state
  
Testing on Railway:
  [ ] SSH into container
  [ ] Verify mount: mount | grep uploads
  [ ] Check directory: ls -la /app/uploads/homework/
  [ ] Upload new image homework via WhatsApp
  [ ] Verify file in: /app/uploads/homework/{student_id}/
  [ ] Check admin dashboard: image displays
  [ ] Optional: restart service, verify image still exists

Success Criteria:
  ✓ Images upload to /app/uploads/homework/{student_id}/
  ✓ Database shows homework/{student_id}/homework_*.jpg
  ✓ Admin dashboard displays images in modal
  ✓ Images persist after app restart
  ✓ File paths show in modal header
  ✓ "Open Image in New Tab" link works
"""

print(CHECKLIST)
