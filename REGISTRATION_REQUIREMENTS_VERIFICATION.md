## Registration Requirements Verification ✅

### Requirement: For a number to be considered "registered", it must capture:
1. **Phone Number** ✅
2. **Name (do not auto-grab)** ✅
3. **Email Address** ✅
4. **Class** ✅

---

## Current Implementation Status

### 1. Phone Number Capture ✅

**Location**: `models/student.py`, `schemas/student.py`

- Column: `phone_number` (unique index, not nullable)
- Validation: Must be in format `+234901234567` (country code + 10-15 digits)
- Auto-grabbed from: WhatsApp message metadata (this is correct)

```python
phone_number = Column(String(20), unique=True, index=True, nullable=False)
```

**Schema Validation**:
```python
@field_validator("phone_number")
def validate_phone(cls, v: str) -> str:
    v = re.sub(r"[\s\-\(\)]", "", v)
    if not re.match(r"^\+\d{10,15}$", v):
        raise ValueError("Phone number must be in format: +234901234567")
    return v
```

---

### 2. Full Name (NOT Auto-Grabbed) ✅

**Issue Clarification**: 
- WhatsApp provides an optional `sender_name` field that could be auto-filled
- This is **NOT** used as the Student's `full_name`
- User MUST explicitly provide name during registration

**Location**: `services/conversation_service.py` Line 316-318

```python
elif current_state == ConversationState.REGISTERING_NAME:
    ConversationService.set_data(phone_number, "full_name", message_text)
    return ("Great! What is your email address?", ConversationState.REGISTERING_EMAIL)
```

**Separation of Concerns**:
```
WhatsApp Message:
  └─ sender_name (optional, from WhatsApp profile)
       └─ Stored in Lead.sender_name (for reference only)
       └─ NOT used in Student registration

Registration Flow:
  └─ Ask user: "What is your full name?"
       └─ User response stored in conversation state
       └─ Stored in Student.full_name (mandatory, validated)
```

**Schema Validation**:
```python
@field_validator("full_name")
def validate_name(cls, v: str) -> str:
    if len(v.strip()) < 3:
        raise ValueError("Full name must be at least 3 characters")
    if len(v.strip()) > 255:
        raise ValueError("Full name must not exceed 255 characters")
    return v.strip()
```

**Field Definition**:
```python
full_name = Column(String(255), nullable=False, index=True)
```

---

### 3. Email Address (Explicitly Captured) ✅

**Location**: `services/conversation_service.py` Line 320-322

```python
elif current_state == ConversationState.REGISTERING_EMAIL:
    ConversationService.set_data(phone_number, "email", message_text)
    return ("Perfect! What is your class/grade? (e.g., 10A, SS2, Form 4)", ConversationState.REGISTERING_CLASS)
```

**Schema Validation** (Strong validation via EmailStr):
```python
from pydantic import EmailStr

class StudentRegistrationRequest(BaseModel):
    email: EmailStr  # Validates email format strictly
```

**Field Definition**:
```python
email = Column(String(255), nullable=False, index=True)
```

---

### 4. Class/Grade (Explicitly Captured) ✅

**Location**: `services/conversation_service.py` Line 324-326

```python
elif current_state == ConversationState.REGISTERING_CLASS:
    ConversationService.set_data(phone_number, "class_grade", message_text)
    return ("✅ Registration complete! You are now registered as REGISTERED_FREE...", ConversationState.REGISTERED)
```

**Schema Validation**:
```python
@field_validator("class_grade")
def validate_grade(cls, v: str) -> str:
    if len(v.strip()) < 1 or len(v.strip()) > 100:
        raise ValueError("Class/grade must be 1-100 characters")
    return v.strip()
```

**Field Definition**:
```python
class_grade = Column(String(100), nullable=False, index=True)
```

---

## Registration Flow (Chat Route)

### Conversation State Machine

```
User Message: "register"
  ↓
System: "Let's register you! What is your full name?"
State: REGISTERING_NAME
  ↓
User: "John Doe"
Data Stored: full_name = "John Doe"
  ↓
System: "Great! What is your email address?"
State: REGISTERING_EMAIL
  ↓
User: "john@example.com"
Data Stored: email = "john@example.com"
  ↓
System: "Perfect! What is your class/grade? (e.g., 10A, SS2, Form 4)"
State: REGISTERING_CLASS
  ↓
User: "10A"
Data Stored: class_grade = "10A"
  ↓
System: "✅ Registration complete! You are now registered as REGISTERED_FREE..."
State: REGISTERED
  ↓
Webhook Handler Triggers: StudentService.create_student()
  - phone_number: (from WhatsApp message)
  - full_name: "John Doe" (from conversation state)
  - email: "john@example.com" (from conversation state)
  - class_grade: "10A" (from conversation state)
  ↓
Student Created: Inserted into students table
  ↓
Lead Marked as Converted: Lead.converted_to_student = True
```

---

## Registration Flow (API Route)

### Direct API Call: POST `/api/students/register`

```json
{
  "phone_number": "+234901234567",
  "full_name": "John Doe",
  "email": "john@example.com",
  "class_grade": "10A"
}
```

**Required Fields**:
- ✅ All 4 fields are REQUIRED (no defaults, no auto-population)
- ✅ Each field has strict validation

**Backend Processing** (`api/routes/students.py`):
```python
student = StudentService.register_student(
    db,
    phone_number=request.phone_number,      # Required
    full_name=request.full_name,            # Required (NOT auto-grabbed)
    email=request.email,                    # Required
    class_grade=request.class_grade,        # Required
)
```

**No Auto-Population**:
- `full_name` is NOT pulled from WhatsApp sender_name
- `email` must be explicitly provided
- `class_grade` must be explicitly provided

---

## Data Separation: Lead vs Student

### Lead Model (`models/lead.py`)

Used for tracking **unregistered** phone numbers:

```python
class Lead(Base):
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    sender_name = Column(String(255), nullable=True)  # From WhatsApp (optional)
    first_message = Column(Text, nullable=True)
    last_message = Column(Text, nullable=True)
    message_count = Column(Integer, default=1)
    
    converted_to_student = Column(Boolean, default=False)
    student_id = Column(Integer, nullable=True)  # Links to Student after registration
```

**Purpose**: Track engagement before registration
**sender_name**: Optional WhatsApp profile name (NOT used for Student registration)

### Student Model (`models/student.py`)

Used for tracking **registered** users:

```python
class Student(Base):
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False, index=True)      # Explicitly provided
    email = Column(String(255), nullable=False, index=True)          # Explicitly provided
    class_grade = Column(String(100), nullable=False, index=True)    # Explicitly provided
    status = Column(Enum(UserStatus), default=UserStatus.REGISTERED_FREE)
    is_active = Column(Boolean, default=True)
```

**Purpose**: Store registered student data
**All fields**: Required, validated, explicitly provided during registration

---

## Validation Summary

| Field | Required | Auto-Grabbed | Validated | Storage |
|-------|----------|--------------|-----------|---------|
| Phone Number | ✅ | ✅ (from WhatsApp) | ✅ (regex format) | Student.phone_number |
| Full Name | ✅ | ❌ (asked in chat/API) | ✅ (3-255 chars) | Student.full_name |
| Email | ✅ | ❌ (asked in chat/API) | ✅ (EmailStr) | Student.email |
| Class/Grade | ✅ | ❌ (asked in chat/API) | ✅ (1-100 chars) | Student.class_grade |

---

## Conclusion: ✅ FULLY COMPLIANT

The system correctly implements the requirement:

✅ **Number**: Auto-captured from WhatsApp (mandatory)
✅ **Name**: NOT auto-grabbed, explicitly asked from user (mandatory, 3-255 chars)
✅ **Email**: NOT auto-grabbed, explicitly asked from user (mandatory, valid email format)
✅ **Class**: NOT auto-grabbed, explicitly asked from user (mandatory, 1-100 chars)

**No changes needed.** The registration system is working exactly as specified.

A student is NOT considered registered until all 4 fields are provided:
1. Phone number (from WhatsApp)
2. Full name (user input)
3. Email address (user input)
4. Class/grade (user input)

Only then is the Lead marked as "Converted" and Student record created.
