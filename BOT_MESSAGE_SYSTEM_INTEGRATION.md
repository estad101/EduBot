# Bot Message Management System - Integration Guide

## Quick Start

### Step 1: Run Migration
```bash
cd c:\xampp\htdocs\bot
python migrations/create_bot_messages.py
```

This will:
- Create 3 new tables: `bot_messages`, `bot_message_templates`, `bot_message_workflows`
- Seed default messages from current hardcoded responses
- Initialize workflow connections

### Step 2: Register API Routes
Add to `main.py`:
```python
from api.routes import bot_messages
app.include_router(bot_messages.router)
```

### Step 3: Add UI Component
Update `admin-ui/pages/settings.tsx` to include the MessageManagementTab:

```tsx
import MessageManagementTab from '../components/MessageManagementTab';

// In the tab navigation, add:
<button
  onClick={() => setActiveTab('messages')}
  className={`px-4 py-2 ${activeTab === 'messages' ? 'border-b-2 border-blue-500' : ''}`}
>
  💬 Messages
</button>

// In the tab content section, add:
{activeTab === 'messages' && <MessageManagementTab />}
```

### Step 4: Update Conversation Service
Modify `services/conversation_service.py` to fetch messages from database:

```python
from services.bot_message_service import BotMessageService

class MessageRouter:
    @staticmethod
    def get_next_response(
        phone_number: str, 
        message_text: str, 
        student_data: Optional[Dict] = None, 
        db: Any = None
    ) -> tuple[str, Optional[ConversationState]]:
        
        current_state = ConversationService.get_state(phone_number)
        state_value = current_state.get("state")
        
        # Try to fetch message from database first
        if db:
            msg = BotMessageService.get_message_by_key(db, f"{state_value}_message")
            if msg:
                variables = {
                    "full_name": student_data.get("name") if student_data else "",
                    "bot_name": "EduBot"
                }
                content = BotMessageService.render_message(msg, variables)
                return (content, msg.next_states[0] if msg.next_states else state_value)
        
        # Fallback to hardcoded messages
        # ... existing code ...
```

### Step 5: Deploy
```bash
git add -A
git commit -m "Add bot message management system with database and admin UI"
git push origin main
```

## File Structure

```
models/
  └── bot_message.py           # Database models

services/
  └── bot_message_service.py   # Service layer for messages and workflows

api/routes/
  └── bot_messages.py          # API endpoints

migrations/
  └── create_bot_messages.py   # Database migration and seeding

admin-ui/components/
  └── MessageManagementTab.tsx # Admin UI component

admin-ui/pages/
  └── settings.tsx             # Updated to include message management tab
```

## Database Schema

### bot_messages
```sql
CREATE TABLE bot_messages (
  id INTEGER PRIMARY KEY,
  message_key VARCHAR(255) UNIQUE NOT NULL,
  message_type VARCHAR(50) NOT NULL,
  context VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  has_menu BOOLEAN DEFAULT FALSE,
  menu_items JSON,
  next_states JSON,
  is_active BOOLEAN DEFAULT TRUE,
  description TEXT,
  variables JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(255),
  updated_by VARCHAR(255)
);

CREATE INDEX idx_message_key ON bot_messages(message_key);
CREATE INDEX idx_context ON bot_messages(context);
CREATE INDEX idx_is_active ON bot_messages(is_active);
```

### bot_message_workflows
```sql
CREATE TABLE bot_message_workflows (
  id INTEGER PRIMARY KEY,
  workflow_name VARCHAR(255) NOT NULL,
  from_message VARCHAR(255) NOT NULL,
  to_message VARCHAR(255) NOT NULL,
  trigger VARCHAR(50) NOT NULL,
  condition VARCHAR(255),
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_from_message ON bot_message_workflows(from_message);
```

## Admin Interface Walkthrough

### Access Messages
1. Go to Admin Dashboard
2. Navigate to Settings
3. Click on "Messages" tab (if integrated)

### View All Messages
- List shows all messages with preview
- Color-coded by type (Greeting, Prompt, Menu, Error, etc.)
- Shows menu items count if applicable
- Shows context/state

### Create New Message
1. Click "Create Message"
2. Fill in form:
   - **Message Key**: Unique identifier (e.g., "welcome_greeting")
   - **Message Type**: greeting, prompt, confirmation, menu, error, info
   - **Context**: Conversation state (e.g., "REGISTERING_NAME")
   - **Content**: Message text with {variables}
   - **Has Menu**: Toggle to add menu buttons
3. Add menu items if needed:
   - ID: Internal identifier
   - Label: What user sees (e.g., "📝 Homework")
   - Action: What happens when clicked
   - Description: Tooltip text
4. Click "Create Message"

### Edit Message
1. Click "Edit" on any message
2. Update fields as needed
3. Click "Update Message"

### Delete Message
1. Click "Delete" on any message
2. Confirm deletion
- Messages are soft-deleted (marked inactive)

### View Workflow
1. Go to "Workflow Diagram" tab
2. See all messages and their connections
3. Understand message flow

## API Endpoints

### Get All Messages
```bash
GET /api/messages/list?active_only=true&context=REGISTERING_NAME
```

### Get Specific Message
```bash
GET /api/messages/registration_name_prompt
```

### Create Message
```bash
POST /api/messages/create
{
  "message_key": "welcome_greeting",
  "message_type": "greeting",
  "context": "INITIAL",
  "content": "Welcome to {bot_name}!",
  "has_menu": false
}
```

### Update Message
```bash
PUT /api/messages/welcome_greeting/update
{
  "content": "Welcome! Please provide your details.",
  "has_menu": true,
  "menu_items": [...]
}
```

### Delete Message
```bash
DELETE /api/messages/welcome_greeting
```

### Get Workflow Diagram
```bash
GET /api/messages/workflow/diagram
```

### Get Next Messages
```bash
GET /api/messages/workflow/next/registration_name_prompt
```

## Variables Reference

### Available Variables
- `{bot_name}` - From admin settings
- `{full_name}` - User's full name
- `{first_name}` - First name only
- `{email}` - User's email
- `{phone_number}` - User's phone
- `{class_grade}` - User's class/grade
- `{subscription_status}` - Active/Inactive
- `{has_subscription}` - true/false

### Example Message
```
Content: "Hello {first_name}! 👋\n\nWelcome to {bot_name}!\n\nYou're subscribed: {has_subscription}"

Variables: {
  first_name: "John",
  bot_name: "EduBot", 
  has_subscription: "true"
}

Result: "Hello John! 👋\n\nWelcome to EduBot!\n\nYou're subscribed: true"
```

## Testing

### Test Message Rendering
```bash
curl -X POST http://localhost:8000/api/messages/test \
  -H "Content-Type: application/json" \
  -d '{
    "message_key": "welcome_greeting",
    "variables": {
      "bot_name": "TestBot",
      "full_name": "John Doe"
    }
  }'
```

### Verify Database
```bash
# Check messages were created
SELECT COUNT(*) FROM bot_messages;

# Check workflows
SELECT * FROM bot_message_workflows WHERE from_message = 'registration_name_prompt';

# Check specific message
SELECT * FROM bot_messages WHERE message_key = 'welcome_greeting';
```

## Monitoring & Maintenance

### View Message Statistics
```sql
-- Messages by type
SELECT message_type, COUNT(*) as count FROM bot_messages GROUP BY message_type;

-- Messages by context
SELECT context, COUNT(*) as count FROM bot_messages GROUP BY context;

-- Recent updates
SELECT message_key, updated_at, updated_by FROM bot_messages 
ORDER BY updated_at DESC LIMIT 10;
```

### Backup Messages
```bash
# Export to JSON
mysqldump -u user -p database bot_messages > bot_messages_backup.json

# Or use the admin UI export feature (if added)
```

## Troubleshooting

### Messages Not Appearing
1. Check if message is marked `is_active = true`
2. Verify message_key is correct
3. Check context matches conversation state
4. Clear bot cache if using caching

### Variables Not Rendering
1. Ensure variable names match exactly (case-sensitive)
2. Check variable is passed in the variables dict
3. Verify syntax: `{variable_name}`

### Menu Items Not Showing
1. Check `has_menu = true` on message
2. Verify `menu_items` JSON is valid
3. Each menu item needs: id, label, action
4. Test in admin UI preview first

## Future Improvements

1. **Message Versioning** - Track all changes with rollback
2. **Multi-language** - Different messages per language
3. **A/B Testing** - Test message variations
4. **Analytics** - Track message effectiveness
5. **Rich Media** - Support images, videos
6. **Conditionals** - Messages based on user data
7. **Scheduling** - Time-based messages
8. **Templates** - Message template library
9. **Bulk Operations** - Import/export messages
10. **Message Approval** - Workflow approval for messages

## Support

For issues or questions:
1. Check BOT_MESSAGE_SYSTEM_ANALYSIS.md for detailed docs
2. Review example messages in database
3. Test in admin UI before deploying
4. Check logs for errors
