# Image Homework Upload Flow - Complete Implementation

## Overview
The image homework submission flow has been completely redesigned to provide a better user experience. Instead of trying to capture images directly in WhatsApp, users now receive a secure link to a dedicated mobile upload page.

## Complete Flow

### 1. User Initiates Homework Submission
```
Student: "I want to submit homework"
Bot: "What's the subject?"
Student: "Mathematics"
Bot: "How would you like to submit? [TEXT] [IMAGE]"
Student: "IMAGE"
```

### 2. Bot Creates Homework Record & Sends Upload Link
**What happens in the backend:**

1. **Create Homework Record** (without file initially)
   - Status: Created but incomplete
   - Type: IMAGE
   - File path: NULL (will be filled after upload)

2. **Generate Secure Upload Token**
   - Hash of: homework_id + student_id + timestamp
   - 32-character hex string
   - Used to validate upload request

3. **Build Upload Link**
   ```
   https://app.url/homework-upload
   ?student_id=123
   &homework_id=456
   &subject=Mathematics
   &token=abc123def456...
   ```

4. **Send WhatsApp Message**
   ```
   📷 Great! Let's upload your homework image for Mathematics!

   🔗 Tap the link below to open the upload page:
   https://...

   ℹ️ Tips:
   ✓ Make sure the image is clear and readable
   ✓ Landscape orientation works best
   ✓ File size must be less than 10MB

   Once you upload, you'll get a confirmation!
   ```

### 3. User Opens Upload Page
**Technology:** Next.js mobile-responsive page

**Features:**
- Clean, minimalist UI
- 📷 Large upload area
- Image preview before upload
- File type validation (images only)
- File size validation (max 10MB)
- Error messages

**URL Parameters Validated:**
- `student_id` - Must be valid student
- `homework_id` - Must exist and belong to student
- `token` - Must match generated token
- `subject` - Display only

### 4. User Selects & Uploads Image
**Steps:**
1. Tap upload area to open file picker
2. Select image from device (phone gallery, camera, etc.)
3. See preview of selected image
4. Tap "Upload Image" button
5. Image uploads to backend

**Validation:**
- Must be image file (MIME type check)
- Must be less than 10MB
- Cannot be empty

### 5. Backend Receives & Processes Upload
**Endpoint:** `POST /api/homework/upload-image`

**Parameters:**
```
FormData:
- file: Binary image data
- student_id: int
- homework_id: int  
- token: string
```

**Processing Steps:**

1. **Validate Token & IDs**
   ```python
   - Check homework exists and belongs to student
   - Verify student_id matches
   - Return error if invalid
   ```

2. **Save Image File**
   ```python
   # Determine upload directory
   if /app/uploads exists (Railway):
       upload_dir = /app/uploads/homework/{student_id}/
   else:
       upload_dir = ./uploads/homework/{student_id}/

   # Create unique filename
   filename = homework_{timestamp}.jpg
   
   # Save file
   with open(file_path, 'wb') as f:
       f.write(image_bytes)
   ```

3. **Update Homework Record**
   ```python
   homework.file_path = "homework/{student_id}/homework_*.jpg"
   homework.content = "Image submission uploaded"
   db.commit()
   ```

4. **Auto-Assign to Tutor**
   ```python
   # Find tutor by subject
   tutor = TutorService.assign_homework_by_subject(homework.id)
   # Tutor notified via backend system
   ```

5. **Send WhatsApp Confirmation**
   ```
   ✅ Homework Submitted!

   📚 Subject: Mathematics
   📷 Type: Image
   ⏱️ Submitted: Jan 08, 2:30 PM

   🎓 A tutor will review your work shortly!
   ```

### 6. Upload Page Closes
- Success message displays for 3 seconds
- Page automatically closes
- JavaScript: `window.close()`
- User back in WhatsApp

### 7. Admin Views Submission
**Location:** `https://app.url/homework` (Admin Dashboard)

**Display:**
- Student Name
- Class
- Subject
- Type: IMAGE (with green badge)
- Action Button: "View Homework"
- Submitted time

**Modal View:**
- Large image display
- File path info
- Download button
- Download/Print option
- Student metadata
- Solution button (coming soon)

## File Structure

```
admin-ui/pages/
  homework-upload.tsx          # 📱 New upload page

api/routes/
  homework.py                  # Added /api/homework/upload-image endpoint

api/routes/
  whatsapp.py                  # Updated homework submission handler

uploads/
  homework/
    {student_id}/
      homework_{timestamp}.jpg
```

## Database Structure

**Homework Table:**
```sql
CREATE TABLE homework (
  id INT PRIMARY KEY,
  student_id INT,
  subject VARCHAR(255),
  submission_type ENUM('TEXT', 'IMAGE'),
  content TEXT,           -- "Image submission uploaded"
  file_path VARCHAR(255), -- "homework/123/homework_1234567890.jpg"
  created_at TIMESTAMP,
  ...
);
```

## Security Features

1. **Token-Based Links**
   - Upload token generated for each submission
   - Token includes: homework_id + student_id + timestamp
   - SHA256 hash (32 char hex)
   - Prevents unauthorized uploads

2. **Student ID Verification**
   - Homework must belong to requesting student
   - Prevents student A from uploading for student B

3. **File Type Validation**
   - Client-side: Accept only image/* MIME types
   - Server-side: Check Content-Type header

4. **File Size Limits**
   - Maximum 10MB per image
   - Prevents storage abuse

## Error Handling

**Upload Page Errors:**
```
❌ Invalid upload link. Missing required parameters.
❌ Please select an image file (JPG, PNG, etc.)
❌ Image size must be less than 10MB
```

**Backend Errors:**
```
Error: Homework {id} not found
Error: Student ID mismatch
Error: Student {id} not found
Error: File must be an image
Error: Failed to save image file
```

**WhatsApp Confirmation:**
- If upload fails, user sees error message on page
- Backend logs the failure
- Admin can see homework in "pending" state if needed
- User can retry with new upload link

## Flow Advantages

### vs. Direct WhatsApp Image Upload

| Feature | Before | After |
|---------|--------|-------|
| UX | "Send image to bot" | "Tap secure upload link" |
| File Validation | None | Client-side validation |
| File Size | Unlimited | Max 10MB with clear message |
| Preview | No | Yes, see before upload |
| Mobile Friendly | Basic | Fully responsive |
| Error Handling | Generic WhatsApp | Clear, specific errors |
| Auto-close | No | Yes, 3 second auto-close |
| Security | Media ID only | Token-based access |
| Confirmation | No message | Detailed WhatsApp message |

## Testing Checklist

- [ ] Start WhatsApp conversation with bot
- [ ] Navigate to homework submission
- [ ] Select "IMAGE" type
- [ ] Receive WhatsApp message with upload link
- [ ] Tap link in WhatsApp
- [ ] Upload page opens
- [ ] Select image from device
- [ ] See image preview
- [ ] Click upload button
- [ ] See success message
- [ ] Page auto-closes
- [ ] Receive WhatsApp confirmation
- [ ] Check admin dashboard
- [ ] See submitted homework with image
- [ ] Click "View Homework"
- [ ] See image in modal
- [ ] Verify image is clear and readable

## Environment Variables

Required in Railway:
```
APP_URL=https://nurturing-exploration-production.up.railway.app
WHATSAPP_API_TOKEN=<token>
```

## Deployment Status

✅ **Mobile Upload Page** - Deployed
- Location: `admin-ui/pages/homework-upload.tsx`
- Route: `/homework-upload`
- Build: Successful

✅ **Upload API Endpoint** - Deployed
- Location: `api/routes/homework.py`
- Route: `POST /api/homework/upload-image`
- Accepts: FormData with file + metadata

✅ **WhatsApp Handler** - Updated
- Location: `api/routes/whatsapp.py`
- Creates homework, generates link, sends WhatsApp

✅ **All Code** - Pushed to GitHub/Railway
- Commit: Feature: Replace image homework logic with mobile upload page
- Live on production

## Next Steps

1. **Test Complete Flow**
   - Test with real WhatsApp number
   - Upload actual homework image
   - Verify admin sees image

2. **Monitor Logs**
   - Check Railway logs for errors
   - Verify file paths are correct
   - Check WhatsApp messages sent

3. **Gather Feedback**
   - User experience feedback
   - Mobile responsiveness
   - Success rate of uploads

4. **Future Enhancements**
   - Drag-and-drop upload
   - Multiple image upload
   - Image compression
   - OCR validation

## Support

For issues:
1. Check Railway logs: `railway logs --service nurturing-exploration`
2. Check browser console for errors
3. Check upload directory: `/app/uploads/homework/` on Railway
4. Check database for homework records

---

**Last Updated:** January 8, 2026
**Status:** ✅ Complete and Deployed
