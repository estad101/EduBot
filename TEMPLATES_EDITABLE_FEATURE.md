# Bot Messages Templates - Editable Management Feature

## Feature Overview

The Bot Messages Templates section in the Settings page is now fully editable with a complete management menu.

## Features Implemented

### 1. **Template Display with Management Menu**
- Each template card shows:
  - Template name with default badge (if applicable)
  - Template ID
  - Template content (scrollable, monospace)
  - Variables list (as purple tags)
- Three-dot menu on each template for actions

### 2. **Template Management Menu**
Each template has a dropdown menu with options:

#### 📝 **Edit Template**
Opens an edit modal allowing you to:
- Change template name
- Edit template content
- Manage variables (add/remove)
- Toggle "Default" status
- Save changes to database

#### 📋 **Duplicate** (Coming Soon)
Will allow copying a template to create a new variant

#### 🗑️ **Delete** (Coming Soon)
Will delete the template from the database

### 3. **Edit Modal Interface**
Clean modal for editing templates with:

**Template Name Field**
- Edit the unique template identifier
- Used for referencing templates in code

**Template Content Area**
- Large textarea for editing message content
- Supports multi-line messages
- Help text for variable syntax: `{variable_name}`
- Font: Monospace for better readability

**Variables Manager**
- Add new variables by typing and pressing Enter
- Visual tags showing all variables in template
- Remove variables by clicking the × button
- Variable suggestions (coming soon)

**Default Status Toggle**
- Checkbox to mark template as default
- Visual indication with yellow highlight

### 4. **Real-time Updates**
- Changes save to database immediately
- Success message confirms update
- Templates list updates automatically
- Error handling with user-friendly messages

## Technical Implementation

### Frontend Changes

**File**: `admin-ui/pages/settings.tsx`

**New State Variables**:
```typescript
const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);
const [editingTemplate, setEditingTemplate] = useState<EditingTemplate | null>(null);
const [showEditModal, setShowEditModal] = useState(false);
const [templateMenuId, setTemplateMenuId] = useState<number | null>(null);
```

**New Functions**:
- `openEditModal(template)` - Opens edit form
- `closeEditModal()` - Closes edit form
- `saveTemplateChanges()` - Saves changes via API

**UI Components**:
- Template menu dropdown (three dots)
- Edit modal with form fields
- Variable management with add/remove
- Save/Cancel buttons with loading state

### Backend Changes

**File**: `api/routes/bot_messages.py`

**New Endpoint**:
```
PUT /api/bot-messages/templates/{template_id}
```

**Request Body**:
```json
{
  "template_name": "string",
  "template_content": "string",
  "variables": ["array", "of", "strings"],
  "is_default": boolean
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Template updated successfully",
  "data": {
    "id": 1,
    "template_name": "greeting_welcome_new_user",
    "template_content": "...",
    "variables": ["bot_name"],
    "is_default": true
  }
}
```

### API Client Changes

**File**: `admin-ui/lib/api-client.ts`

**New Method**:
```typescript
async updateTemplate(templateId: number, data: any) {
  const response = await this.client.put(
    `/api/bot-messages/templates/${templateId}`, 
    data
  );
  return response.data;
}
```

## Usage Workflow

### Editing a Template

1. **Open Settings Page**: Navigate to https://edubot-production-0701.up.railway.app/settings
2. **Go to Templates Tab**: Click the "Templates" tab
3. **Find Template**: Locate the template you want to edit
4. **Open Menu**: Click the three-dot menu (⋮) button
5. **Select Edit**: Click "Edit Template"
6. **Modify Content**: 
   - Change name, content, or variables as needed
   - Add new variables by typing and pressing Enter
   - Remove variables by clicking × on the tag
   - Toggle default status with checkbox
7. **Save**: Click "Save Changes" button
8. **Confirmation**: Success message appears, template updates in list

### Adding a Variable

1. Open edit modal for a template
2. In the "Variables" section, find the input field
3. Type variable name (e.g., "user_name")
4. Press Enter
5. Variable appears as a purple tag above
6. Repeat for additional variables

### Removing a Variable

1. In Variables section, click the × on the variable tag
2. Variable is removed immediately
3. Save changes to persist

## Visual Indicators

- **⭐ Default**: Yellow badge on default templates
- **🟣 Variables**: Purple tags showing template variables
- **📝**: Edit icon in menu
- **📋**: Duplicate icon (coming soon)
- **🗑️**: Delete icon (coming soon)

## Status: Production Ready

✅ **Frontend**: Fully implemented
✅ **Backend**: Fully implemented
✅ **Database**: Connected and working
✅ **API Client**: Updated
✅ **Error Handling**: Complete
✅ **User Feedback**: Success/error messages

⏳ **Coming Soon**:
- Duplicate template functionality
- Delete template with confirmation
- Variable suggestions/templates
- Import/export templates
- Bulk edit operations

## Testing

Local Testing (Development):
```bash
cd c:\xampp\htdocs\bot\admin-ui
npm run dev
# Visit http://localhost:3000/settings
# Navigate to Templates tab
# Click edit menu on any template
```

Production Testing:
Visit https://edubot-production-0701.up.railway.app/settings after Railway redeploy

## Deployment

All changes committed and pushed to GitHub:
- Commit: `4362c1d` - Add editable templates with edit modal and management menu
- Status: Ready for Railway auto-deploy

Railway will automatically rebuild and deploy within 2-5 minutes of code push.

## Support & Issues

If templates fail to load:
1. Check network tab in browser DevTools
2. Verify API endpoint: `/api/bot-messages/templates/list` returns 200
3. Check database connection in Railway dashboard
4. Clear browser cache and refresh

If save fails:
1. Check error message in toast notification
2. Verify template has valid name and content
3. Check database connectivity
4. Try again or contact support
