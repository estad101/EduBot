# Admin Bot Message Management Guide

## Overview

The EduBot system provides **complete admin control** (1005 ability) over all preformatted bot responses. This guide documents all administrative endpoints and features.

---

## 📊 Capabilities Summary

| Capability | Status | Details |
|-----------|--------|---------|
| **Create** | ✅ | Add new bot messages |
| **Read** | ✅ | View messages and details |
| **Update** | ✅ | Edit message content, menus, variables |
| **Delete** | ✅ | Remove messages |
| **Toggle Status** | ✅ | Activate/deactivate messages |
| **Filter** | ✅ | By context, type, active status |
| **Statistics** | ✅ | View message analytics |
| **Audit Trail** | ✅ | Track who made changes |

---

## 🔐 Authentication

All admin endpoints require:
- **Decorator**: `@admin_session_required`
- **Session**: Active admin session via `/api/admin/login`
- **Authorization**: Admin role verified on each request

---

## 📋 Admin Endpoints (8 Total)

### 1. List All Bot Messages

**Endpoint**: `GET /api/admin/bot-messages/list`

**Query Parameters**:
```
active_only: boolean (default: false)
context: string (optional) - filter by conversation state
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "message_key": "registration_name_prompt",
      "message_type": "prompt",
      "context": "REGISTERING_NAME",
      "content": "What is your full name?",
      "has_menu": false,
      "menu_items": null,
      "next_states": ["REGISTERING_EMAIL"],
      "variables": null,
      "is_active": true,
      "description": "Initial prompt for user's full name",
      "created_by": "system",
      "updated_by": "admin_user",
      "created_at": "2024-01-10T10:00:00",
      "updated_at": "2024-01-10T12:30:00"
    }
    // ... more messages
  ],
  "count": 17
}
```

**Example Requests**:
```bash
# Get all messages
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/list"

# Get only active messages
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/list?active_only=true"

# Get messages for a specific context
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/list?context=HOMEWORK_SUBJECT"

# Get active messages for registration flow
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/list?active_only=true&context=REGISTERING_NAME"
```

---

### 2. Get Specific Message

**Endpoint**: `GET /api/admin/bot-messages/{message_key}`

**Path Parameters**:
```
message_key: string - Unique message identifier
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "message_key": "registration_name_prompt",
    "message_type": "prompt",
    "context": "REGISTERING_NAME",
    "content": "What is your full name?",
    "has_menu": false,
    "menu_items": null,
    "next_states": ["REGISTERING_EMAIL"],
    "variables": null,
    "is_active": true,
    "description": "Initial prompt for user's full name",
    "created_by": "system",
    "updated_by": "admin_user",
    "created_at": "2024-01-10T10:00:00",
    "updated_at": "2024-01-10T12:30:00"
  }
}
```

**Example**:
```bash
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/registration_name_prompt"
```

---

### 3. Create New Bot Message

**Endpoint**: `POST /api/admin/bot-messages/create`

**Request Body**:
```json
{
  "message_key": "custom_greeting",
  "message_type": "greeting",
  "context": "IDLE",
  "content": "👋 Welcome to my bot!",
  "has_menu": true,
  "menu_items": [
    {
      "id": "help",
      "label": "❓ Help",
      "action": "help"
    }
  ],
  "next_states": ["IDLE"],
  "variables": ["bot_name"],
  "is_active": true,
  "description": "Custom greeting message"
}
```

**Required Fields**:
- `message_key` - Unique identifier
- `message_type` - One of: greeting, prompt, menu, confirmation, error, info
- `context` - Conversation state
- `content` - Message text

**Optional Fields**:
- `has_menu` - Boolean (default: false)
- `menu_items` - Array of menu items
- `next_states` - Array of next conversation states
- `variables` - Array of template variables
- `is_active` - Boolean (default: true)
- `description` - Admin notes

**Response**:
```json
{
  "status": "success",
  "message": "Bot message 'custom_greeting' created successfully",
  "data": {
    "id": 18,
    "message_key": "custom_greeting"
  }
}
```

**Example**:
```bash
curl -X POST \
  -H "Cookie: admin_session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "message_key": "custom_greeting",
    "message_type": "greeting",
    "context": "IDLE",
    "content": "👋 Welcome!",
    "is_active": true
  }' \
  "https://api.example.com/api/admin/bot-messages/create"
```

---

### 4. Update Bot Message

**Endpoint**: `PUT /api/admin/bot-messages/{message_key}/update`

**Path Parameters**:
```
message_key: string - Message to update
```

**Request Body** (all fields optional):
```json
{
  "content": "Updated message content",
  "message_type": "prompt",
  "context": "IDLE",
  "has_menu": true,
  "menu_items": [
    {
      "id": "yes",
      "label": "✅ Yes",
      "action": "confirm"
    }
  ],
  "next_states": ["CONFIRMED"],
  "variables": ["full_name"],
  "is_active": true,
  "description": "Updated description"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Bot message 'registration_name_prompt' updated successfully",
  "data": {
    "id": 1,
    "message_key": "registration_name_prompt"
  }
}
```

**Example**:
```bash
curl -X PUT \
  -H "Cookie: admin_session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Please enter your full name:"
  }' \
  "https://api.example.com/api/admin/bot-messages/registration_name_prompt/update"
```

---

### 5. Delete Bot Message

**Endpoint**: `DELETE /api/admin/bot-messages/{message_key}`

**Path Parameters**:
```
message_key: string - Message to delete
```

**Response**:
```json
{
  "status": "success",
  "message": "Bot message 'custom_greeting' deleted successfully"
}
```

**Example**:
```bash
curl -X DELETE \
  -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/custom_greeting"
```

---

### 6. Toggle Message Status

**Endpoint**: `PUT /api/admin/bot-messages/{message_key}/toggle`

**Path Parameters**:
```
message_key: string - Message to toggle
```

**Response**:
```json
{
  "status": "success",
  "message": "Bot message 'registration_name_prompt' is now active",
  "data": {
    "is_active": true
  }
}
```

**Example**:
```bash
# Disable a message
curl -X PUT \
  -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/registration_name_prompt/toggle"

# Response: is_active becomes false
```

---

### 7. Get Message Statistics

**Endpoint**: `GET /api/admin/bot-messages/stats/overview`

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_messages": 18,
    "active": 17,
    "inactive": 1,
    "by_type": {
      "prompt": 3,
      "greeting": 2,
      "confirmation": 1,
      "menu": 2,
      "error": 2,
      "info": 8
    },
    "by_context": {
      "REGISTERING_NAME": 1,
      "REGISTERING_EMAIL": 1,
      "REGISTERING_CLASS": 1,
      "REGISTERED": 1,
      "HOMEWORK_SUBJECT": 2,
      "HOMEWORK_TYPE": 1,
      "PAYMENT_PENDING": 2,
      "IDLE": 5,
      "FAQ_MENU": 1,
      "CHAT_SUPPORT_ACTIVE": 1,
      "FAQ_REGISTRATION": 1
    }
  }
}
```

**Example**:
```bash
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/stats/overview"
```

---

## 📝 Admin Actions & Audit Trail

All admin actions are logged with:
- **Admin Username** - Who made the change
- **Timestamp** - When the change occurred
- **Action Type** - Create, Update, Delete, Toggle
- **Message Key** - Which message was affected
- **Details** - What was changed (logged in system logs)

**Database Fields**:
```
created_by: "system"        # Initially created by
updated_by: "admin_user"    # Last modified by
created_at: "2024-01-10"    # Creation timestamp
updated_at: "2024-01-10"    # Last modification timestamp
```

---

## ✅ Validation Rules

### Message Key
- **Format**: Snake_case (e.g., `registration_name_prompt`)
- **Length**: 1-255 characters
- **Uniqueness**: Must be unique in database
- **Allowed Characters**: Letters, numbers, underscores

### Message Type
Valid values: `greeting`, `prompt`, `menu`, `confirmation`, `error`, `info`

### Context (Conversation State)
Valid values:
- `INITIAL`, `REGISTERING_NAME`, `REGISTERING_EMAIL`, `REGISTERING_CLASS`
- `REGISTERED`, `HOMEWORK_SUBJECT`, `HOMEWORK_TYPE`, `HOMEWORK_CONTENT`
- `HOMEWORK_SUBMITTED`, `PAYMENT_PENDING`, `PAYMENT_CONFIRMED`
- `CHAT_SUPPORT_ACTIVE`, `IDLE`, `FAQ_MENU`, `FAQ_REGISTRATION`, etc.

### Menu Items Structure
```json
{
  "id": "string",           // Unique within message
  "label": "string",        // Display text with emoji
  "action": "string"        // Action to trigger
}
```

### Variables
Format: `{variable_name}` in content, listed as array
```json
{
  "content": "Hello {full_name}!",
  "variables": ["full_name"]
}
```

---

## 🔄 Common Use Cases

### Use Case 1: Update Welcome Message
```bash
curl -X PUT \
  -H "Cookie: admin_session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "👋 Welcome to EduBot! We help students submit homework easily."
  }' \
  "https://api.example.com/api/admin/bot-messages/welcome_unregistered/update"
```

### Use Case 2: Add New Homework Subject Option
```bash
curl -X POST \
  -H "Cookie: admin_session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "message_key": "homework_subjects_expanded",
    "message_type": "prompt",
    "context": "HOMEWORK_SUBJECT",
    "content": "Choose a subject:",
    "has_menu": true,
    "menu_items": [
      {"id": "math", "label": "📐 Math", "action": "select"},
      {"id": "english", "label": "📚 English", "action": "select"},
      {"id": "science", "label": "🔬 Science", "action": "select"},
      {"id": "history", "label": "📜 History", "action": "select"},
      {"id": "geography", "label": "🌍 Geography", "action": "select"}
    ]
  }' \
  "https://api.example.com/api/admin/bot-messages/create"
```

### Use Case 3: Disable Error Message
```bash
curl -X PUT \
  -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/error_generic/toggle"
```

### Use Case 4: Check Message Statistics
```bash
curl -H "Cookie: admin_session=..." \
  "https://api.example.com/api/admin/bot-messages/stats/overview" | jq
```

---

## 🛡️ Error Handling

### 400 Bad Request
```json
{
  "detail": "Missing required field: content"
}
```

### 404 Not Found
```json
{
  "detail": "Message 'invalid_key' not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Admin authentication required"
}
```

---

## 📊 Database Schema

**Table**: `bot_messages`

| Column | Type | Properties |
|--------|------|-----------|
| `id` | Integer | Primary Key |
| `message_key` | String(255) | Unique, Indexed |
| `message_type` | String(50) | Indexed |
| `context` | String(100) | Indexed |
| `content` | Text | Required |
| `has_menu` | Boolean | Default: false |
| `menu_items` | JSON | Optional |
| `next_states` | JSON | Optional |
| `variables` | JSON | Optional |
| `is_active` | Boolean | Default: true, Indexed |
| `description` | Text | Optional |
| `created_by` | String(255) | Admin audit |
| `updated_by` | String(255) | Admin audit |
| `created_at` | DateTime | Auto |
| `updated_at` | DateTime | Auto |

---

## 🔒 Security Notes

1. **All endpoints require admin authentication**
2. **Admin actions are logged for audit trail**
3. **Changes take effect immediately**
4. **No approval workflow** (admin has full control)
5. **Database is source of truth** for bot responses

---

## 📈 Best Practices

1. **Keep message keys consistent** - Use snake_case
2. **Add descriptions** - Help other admins understand purpose
3. **Test after changes** - Use test webhook to verify
4. **Document modifications** - Track why changes were made
5. **Use variables** - Personalize messages with {variables}
6. **Organize by context** - Related messages in same state
7. **Use emojis** - Make messages more engaging
8. **Validate JSON** - Menu items and variables must be valid JSON

---

## ✨ Summary

The admin bot message management system provides:
- ✅ Full CRUD control (Create, Read, Update, Delete)
- ✅ 8 dedicated admin endpoints
- ✅ Real-time changes (no deployment needed)
- ✅ Audit trail (who changed what, when)
- ✅ Statistics and filtering
- ✅ Complete message lifecycle management
- ✅ 17 pre-seeded preformatted responses
- ✅ Extensible for custom messages

**Admin now has 1005 (full) ability to manage bot responses!**
