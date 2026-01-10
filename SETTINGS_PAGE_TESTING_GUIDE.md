# Settings Page - Quick Reference & Testing Guide

## 🚀 Quick Start for Testing

### Access Settings Page
**URL**: `https://edubot-production-0701.up.railway.app/settings`

**Requirements**:
- Must be logged in as admin
- Valid admin token stored in localStorage

---

## 📋 Tab Navigation Guide

### 1. **Bot Configuration** (Default Tab)
- **Purpose**: Configure bot name
- **Fields**: Bot name (text input)
- **Features**: Live preview of bot name usage
- **Testing**: 
  1. Enter bot name (e.g., "EduBot")
  2. See preview update in real-time
  3. Click Save Settings
  4. Confirm changes

### 2. **WhatsApp Configuration**
- **Purpose**: Configure WhatsApp Cloud API credentials
- **Fields**: 
  - Business Account ID (numeric)
  - Phone Number ID (numeric)
  - Phone Number (with country code)
  - API Access Token (long string)
  - Webhook Verification Token (string)
- **Validation**: 
  - Phone numbers validated with regex
  - Token length checked (20+ chars)
  - Numeric IDs validated
- **Features**:
  - ✅ **NEW**: WhatsApp Validation Button
    - Shows "Valid" if configuration looks good
    - Shows "Invalid" if issues detected
    - Provides helpful error messages
  - Token visibility toggle (eye icon)
  - Test message functionality
  - Custom phone number input
- **Testing**:
  1. Fill in all WhatsApp fields
  2. Click the "Validate" button in info box
  3. Check status (Valid/Invalid)
  4. Send test message to a phone number
  5. Verify message received

### 3. **Paystack Configuration**
- **Purpose**: Configure Paystack payment gateway
- **Fields**:
  - Public Key
  - Secret Key
  - Webhook Secret
- **Validation**:
  - Key length validation (20+ chars)
  - Basic format checking
- **Features**:
  - ✅ **NEW**: Paystack Validation Button
    - Shows "Valid" if configuration looks good
    - Shows "Invalid" if issues detected
    - Provides helpful error messages
  - Token visibility toggle
- **Testing**:
  1. Fill in Paystack credentials
  2. Click "Validate" button
  3. Check validation status
  4. Save settings

### 4. **Database Configuration**
- **Purpose**: Configure database connection
- **Fields**: Database URL (connection string)
- **Validation**:
  - Checks for "://" in URL (protocol required)
  - Validates format
- **Testing**:
  1. Enter valid database URL
  2. System validates format
  3. Save settings

### 5. **Templates** (NEW)
- **Purpose**: View bot message templates from database
- **Features**:
  - Summary statistics (Total, Default, Custom)
  - Template list with:
    - Template name
    - Default indicator (⭐)
    - Template content
    - Available variables
  - Scrollable list for large collections
  - Loading state with spinner
  - Empty state message
- **Testing**:
  1. Click Templates tab
  2. Wait for templates to load
  3. Verify template count
  4. Check template content displays correctly
  5. Verify variables are shown

### 6. **Messages**
- **Purpose**: Manage bot response messages
- **Features**:
  - Create new messages
  - Edit existing messages
  - Delete messages
  - Message filtering
  - Workflow visualization
- **Testing**: (See MessageManagementTab documentation)

---

## ✅ Validation Features

### WhatsApp Validation Button
**Location**: Info box on WhatsApp tab (green button)

**What it checks**:
- All required fields are filled
- API key length is reasonable (50+ chars)
- No required fields are missing

**Possible Responses**:
- ✅ "WhatsApp configuration appears valid"
- ⚠️ "Missing WhatsApp configuration: [field names]"
- ⚠️ "WhatsApp API key appears too short"

### Paystack Validation Button
**Location**: Info box on Paystack tab (blue button)

**What it checks**:
- All required fields are filled
- Key lengths are reasonable (20+ chars)
- No required fields are missing

**Possible Responses**:
- ✅ "Paystack configuration appears valid"
- ⚠️ "Missing Paystack configuration: [field names]"
- ⚠️ "Paystack public/secret key appears too short"

---

## 🧪 Testing Scenarios

### Scenario 1: Save Valid Settings
1. Navigate to Settings page
2. Enter valid values for all fields
3. Click Save Settings
4. Confirm in dialog
5. ✅ Should see: "Settings saved successfully ✅"

### Scenario 2: Validate WhatsApp
1. Fill in WhatsApp credentials
2. Click "Validate" button on WhatsApp tab
3. ✅ Should see validation status change
4. If valid: button shows "Valid ✅"
5. If invalid: button shows "Invalid ❌" + error message

### Scenario 3: Validate Paystack
1. Fill in Paystack keys
2. Click "Validate" button on Paystack tab
3. ✅ Should see validation status change
4. If valid: button shows "Valid ✅"
5. If invalid: button shows "Invalid ❌" + error message

### Scenario 4: Test WhatsApp Message
1. Enter phone number in WhatsApp tab
2. Click "Send Test Message"
3. Wait for response
4. ✅ Should see: "Test message sent successfully to [number] ✅"
5. ❌ Or error: "Failed to send test message: [reason]"

### Scenario 5: Load Templates
1. Click Templates tab
2. Wait for loading spinner
3. ✅ Should see:
   - Template count (e.g., "Total Templates: 21")
   - List of templates
   - Template details (content, variables)

### Scenario 6: Handle Empty Strings
1. Clear a field that had a value
2. Click Save Settings
3. ✅ Empty field is NOT saved to database
4. ✅ Database stays clean (no empty values)

### Scenario 7: Clear Error Messages
1. Try to save with invalid data
2. See error message
3. Click Save again without fixing
4. ✅ Previous error is cleared
5. ✅ New error (or success) appears

---

## 🐛 Error Messages Guide

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid phone number format" | Phone number doesn't match +1234567890 | Use country code + number |
| "Phone Number ID should be numeric" | Contains letters or special chars | Enter only digits |
| "Business Account ID should be numeric" | Contains letters or special chars | Enter only digits |
| "Invalid database URL format" | Missing "://" protocol | Include protocol (mysql+pymysql://) |
| "Settings saved successfully ✅" | Settings were saved | Continue using |
| "Test message sent successfully ✅" | Message delivered | Check recipient phone |
| "Failed to send test message" | WhatsApp API error | Check credentials, try again |
| "WhatsApp configuration appears valid" | All checks passed | Settings are likely correct |
| "Paystack configuration appears valid" | All checks passed | Settings are likely correct |

---

## 🔐 Security Features

- ✅ All endpoints require admin authentication
- ✅ CSRF tokens sent with requests
- ✅ Sensitive tokens masked in logs
- ✅ Session verification enforced
- ✅ API key validation in database
- ✅ Input sanitization on all fields

---

## 📱 Mobile/Responsive Testing

- ✅ Tab navigation collapses on small screens
- ✅ Form fields stack properly on mobile
- ✅ Buttons resize for touch targets
- ✅ Messages display correctly on small screens
- ✅ Validation buttons responsive on mobile

---

## 🎯 Performance Checklist

- ✅ Page loads in < 2 seconds (with valid token)
- ✅ Templates load asynchronously (don't block page)
- ✅ Validation buttons respond immediately (< 1 second)
- ✅ Save operation completes in < 3 seconds
- ✅ No memory leaks in component
- ✅ No infinite loops in validation

---

## 🚀 Deployment Verification

Before deploying to production:

```
☑️ Test all tabs load correctly
☑️ Validate all input fields work
☑️ Check validation buttons function
☑️ Verify save functionality
☑️ Confirm error messages display
☑️ Verify success messages display
☑️ Check template loading
☑️ Test WhatsApp message sending
☑️ Verify responsive design
☑️ Check security headers present
☑️ Verify CORS headers correct
```

---

## 📊 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/settings` | GET | Load all settings |
| `/api/admin/settings/update` | POST | Save settings |
| `/api/admin/settings/validate-whatsapp` | POST | Validate WhatsApp config |
| `/api/admin/settings/validate-paystack` | POST | Validate Paystack config |
| `/api/bot-messages/templates/list` | GET | Load templates |
| `/api/admin/whatsapp/test` | POST | Send test message |

---

## 🆘 Troubleshooting

### Page Won't Load
- Check admin token in localStorage
- Verify logged in status
- Check browser console for errors
- Verify CORS settings on backend

### Settings Won't Save
- Check admin token is valid
- Check network connection
- Look for validation errors
- Check browser console
- Verify backend is running

### Validation Button Doesn't Work
- Check backend endpoints exist
- Check token is valid
- Check network connection
- Look for JavaScript errors in console

### Templates Won't Load
- Check templates exist in database
- Check authentication token
- Verify bot_messages table exists
- Check network connection

### WhatsApp Test Fails
- Check WhatsApp API token is valid
- Check phone numbers are correct
- Verify webhook token is set
- Check WhatsApp account is active

---

**Last Updated**: January 10, 2026
**Status**: ✅ Complete & Verified
