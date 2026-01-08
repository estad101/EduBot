# Image Homework Upload - Testing Guide

## Backend URL
```
https://edubot-production-cf26.up.railway.app
```

## Testing Image Upload Status

After submitting an image homework, verify it was uploaded correctly:

### Check if image file exists
```bash
curl -X GET \
  "https://edubot-production-cf26.up.railway.app/api/homework/1/image-status" \
  -H "Content-Type: application/json"
```

**Success Response (file found):**
```json
{
  "status": "success",
  "message": "Image file found and accessible",
  "data": {
    "homework_id": 1,
    "type": "IMAGE",
    "has_file": true,
    "file_path": "uploads/homework/1/homework_2347001234567_1673081234567.jpg",
    "file_size": 152000,
    "file_exists": true
  }
}
```

**Warning Response (file missing):**
```json
{
  "status": "success",
  "message": "Image file path recorded but file not found",
  "data": {
    "homework_id": 1,
    "type": "IMAGE",
    "has_file": false,
    "file_path": "uploads/homework/1/homework_2347001234567_1673081234567.jpg",
    "file_exists": false,
    "status": "FILE_MISSING"
  }
}
```

## WhatsApp Image Submission Flow

### 1. Student sends image in WhatsApp
- Bot receives webhook with `message_type: "image"`
- WhatsApp provides `media_id`

### 2. Check logs for upload confirmation
Look for these log messages:
```
📸 Starting image download for homework
   Image ID: {media_id}
✓ Downloaded media: {size} bytes
📝 Saving image to: uploads/homework/{student_id}/{filename}
   Written {size} bytes
✓ Image saved successfully
   File size: {size} bytes
📚 Submitting homework with:
   student_id: {id}
   submission_type: IMAGE
   file_path: uploads/homework/{student_id}/{filename}
✅ Homework created: {homework_id}
   Image path: {file_path}
```

### 3. Verify with image-status endpoint
```bash
curl "https://edubot-production-cf26.up.railway.app/api/homework/{homework_id}/image-status"
```

## Text Homework Submission (for comparison)

### Submit text homework via API
```bash
curl -X POST \
  "https://edubot-production-cf26.up.railway.app/api/homework/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "subject": "Mathematics",
    "submission_type": "TEXT",
    "content": "This is my homework solution..."
  }'
```

## Troubleshooting

### If image upload fails

1. **Check logs for error messages:**
   - `❌ Failed to download media - no bytes received`
   - `❌ File not found after write`
   - `❌ Failed to download/save image`

2. **Verify WhatsApp credentials:**
   - Check `WHATSAPP_API_KEY` is set
   - Check `WHATSAPP_PHONE_NUMBER_ID` is correct
   - Verify webhook token is valid

3. **Check file permissions:**
   - Ensure `uploads/` directory exists and is writable
   - Check disk space available

4. **Use image-status endpoint:**
   ```bash
   curl "https://edubot-production-cf26.up.railway.app/api/homework/1/image-status"
   ```
   - If `file_exists: false`, file wasn't saved
   - If no homework found, check homework_id

## Log Monitoring

### View logs in Railway
1. Go to https://railway.app/dashboard
2. Select project → bot-api service
3. Click "Logs" tab
4. Search for "📸" emoji to find image downloads
5. Search for "❌" emoji to find errors

### Or check locally (if running)
```bash
# Tail logs while bot is running
tail -f logs/chatbot.log | grep -E "(📸|✓|❌|Image|image)"
```

## File Storage

### Location of uploaded images
```
uploads/
  homework/
    {student_id}/
      homework_{phone_number}_{timestamp}.jpg
```

### Example
```
uploads/homework/1/homework_2347001234567_1673081234567.jpg
uploads/homework/1/homework_2347001234567_1673081234568.jpg
uploads/homework/2/homework_2348001234567_1673081235000.jpg
```

## Expected Behavior

### ✅ Successful Upload
1. Image received from WhatsApp
2. Downloaded from WhatsApp servers
3. Saved to `uploads/homework/{student_id}/`
4. Verified on disk
5. File path stored in database
6. Homework record created
7. Tutor assigned
8. Bot responds: "✅ Homework submitted successfully!"

### ❌ Failed Upload
1. Image received from WhatsApp
2. Download fails (logs show `❌ Failed to download media`)
3. No file saved
4. Homework may or may not be created depending on error
5. Bot responds with error message

## Important Notes

- **File paths** are relative: `uploads/homework/1/image.jpg`
- **Timestamps** are in milliseconds for uniqueness
- **Student ID** used for folder organization
- **Original filename** not preserved (security)
- **Only JPEGs** are saved (WhatsApp images are JPEG)
- **Large files** may take longer to download

## Support

If images aren't uploading:
1. Check `/api/homework/{id}/image-status` endpoint
2. Review logs for error messages with ❌
3. Verify WhatsApp API credentials
4. Check `uploads/` directory permissions
5. Ensure Railway environment variables are set correctly
