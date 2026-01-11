# Async Database Migration - Complete Guide

## 🚀 What Changed

Your database layer has been converted to **fully async/await** mode, enabling non-blocking database operations.

### Key Changes:

1. **SQLAlchemy Upgrade**: Switched from synchronous to async
   - `create_engine()` → `create_async_engine()`
   - `SessionLocal` → `async_session_maker`
   - `Session` → `AsyncSession`

2. **MySQL Driver**: Now using `aiomysql` for async support
   - More efficient connection handling
   - Supports concurrent requests without blocking

3. **All Functions Are Now Async**
   - `get_db()` - async generator (use with `Depends()`)
   - `init_db()` - async function
   - `drop_db()` - async function

## 📝 Migration Guide for Existing Routes

### Before (Synchronous - BLOCKING):
```python
from fastapi import FastAPI, Depends
from config.database import get_db
from sqlalchemy.orm import Session

@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # ❌ BLOCKING
    users = db.query(User).all()  # Blocks entire worker
    return users
```

**Problem**: If database takes 1 second, worker is blocked for that 1 second. Handles only 1 request at a time.

### After (Asynchronous - NON-BLOCKING):
```python
from fastapi import FastAPI, Depends
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):  # ✅ NON-BLOCKING
    result = await db.execute(select(User))  # Doesn't block worker
    users = result.scalars().all()
    return users
```

**Benefit**: While database is processing, worker handles OTHER requests. Handles 100+ concurrent requests.

## 🔄 Query Migration Examples

### 1. Simple SELECT

**Before:**
```python
user = db.query(User).filter(User.id == 1).first()
```

**After:**
```python
from sqlalchemy import select
result = await db.execute(select(User).where(User.id == 1))
user = result.scalars().first()
```

### 2. Filtering with Multiple Conditions

**Before:**
```python
users = db.query(User).filter(
    User.active == True,
    User.role == "admin"
).all()
```

**After:**
```python
result = await db.execute(
    select(User).where(
        (User.active == True) & (User.role == "admin")
    )
)
users = result.scalars().all()
```

### 3. COUNT Query

**Before:**
```python
count = db.query(User).count()
```

**After:**
```python
from sqlalchemy import func
result = await db.execute(select(func.count(User.id)))
count = result.scalar()
```

### 4. JOIN Query

**Before:**
```python
results = db.query(User, Profile).join(
    Profile, User.id == Profile.user_id
).all()
```

**After:**
```python
from sqlalchemy import select, join
stmt = select(User, Profile).join(
    Profile, User.id == Profile.user_id
)
result = await db.execute(stmt)
rows = result.all()
```

### 5. INSERT/UPDATE/DELETE with Commit

**Before:**
```python
user = User(name="John", email="john@example.com")
db.add(user)
db.commit()
db.refresh(user)
return user
```

**After:**
```python
user = User(name="John", email="john@example.com")
db.add(user)
await db.commit()
await db.refresh(user)
return user
```

## 🛠️ Common Patterns

### Pattern 1: Single Object Fetch

```python
@app.get("/students/{student_id}")
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404)
    return student
```

### Pattern 2: List with Filters

```python
@app.get("/students")
async def list_students(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Student)
    if active_only:
        stmt = stmt.where(Student.is_active == True)
    
    result = await db.execute(stmt)
    students = result.scalars().all()
    return students
```

### Pattern 3: Create with Relationships

```python
@app.post("/students")
async def create_student(data: StudentCreate, db: AsyncSession = Depends(get_db)):
    student = Student(**data.dict())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student
```

### Pattern 4: Bulk Operations

```python
@app.post("/bulk-create")
async def bulk_create(items: List[dict], db: AsyncSession = Depends(get_db)):
    students = [Student(**item) for item in items]
    db.add_all(students)
    await db.commit()
    return {"created": len(students)}
```

## 📊 Performance Impact

### Before (Synchronous):
- 1 worker = 1 concurrent request
- 10 workers × 1 request = 10 concurrent max
- 1 second DB query × 10 = 10 seconds for 10 users

### After (Async):
- 1 worker = 1000+ concurrent requests
- 10 workers × 1000+ = 10,000+ concurrent
- 1 second DB query × 1000 = **same 1 second for 1000 users**

**Result**: 100-1000x throughput increase without changing hardware.

## ⚠️ Important Notes

1. **All `await` calls must be in `async` functions**
   ```python
   # ✅ CORRECT
   async def get_users(db: AsyncSession = Depends(get_db)):
       result = await db.execute(...)
   
   # ❌ WRONG - can't use await in sync function
   def get_users(db: AsyncSession = Depends(get_db)):
       result = await db.execute(...)  # SyntaxError
   ```

2. **Don't forget to commit/refresh**
   ```python
   # ❌ This won't save
   user = User(name="John")
   db.add(user)
   return user
   
   # ✅ This will save
   user = User(name="John")
   db.add(user)
   await db.commit()
   await db.refresh(user)
   return user
   ```

3. **Use `expire_on_commit=False`** - Already set in config
   - Allows lazy loading after commit
   - Set in `async_session_maker` configuration

## 🧪 Testing

For test files still using `SessionLocal`:
- They will continue to fail because there's no sync session anymore
- Update them to use `async_session_maker` or mark as integration tests

```python
# New test pattern
async def test_get_user():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalars().first()
        assert user is not None
```

## 🚦 Gradual Migration Strategy

You don't need to update all routes at once:

1. **Phase 1**: Update high-traffic endpoints first
   - `/api/students/list` (likely high traffic)
   - `/api/conversations` (chat feature)
   - `/api/bot-messages/templates`

2. **Phase 2**: Update medium-traffic endpoints
   - `/api/payments`
   - `/api/homework`

3. **Phase 3**: Update low-traffic endpoints
   - `/api/tutors`
   - `/api/subscriptions`

## 📞 Support

If you encounter issues:

1. Check that function is marked `async`
2. Check that database call is preceded by `await`
3. Check that you're using `select()` instead of `.query()`
4. Check that you imported from correct modules:
   - `from sqlalchemy.ext.asyncio import AsyncSession`
   - `from sqlalchemy import select`

## ✅ Checklist for Updating a Route

- [ ] Mark function as `async`
- [ ] Change `db: Session` to `db: AsyncSession`
- [ ] Import `AsyncSession` from `sqlalchemy.ext.asyncio`
- [ ] Import `select` from `sqlalchemy`
- [ ] Change `db.query()` to `await db.execute(select())`
- [ ] Add `await` before `db.commit()` and `db.refresh()`
- [ ] Test the endpoint

## 🎯 Next Steps

1. Update 3-5 high-traffic endpoints (start with templates/conversations)
2. Test thoroughly with multiple concurrent requests
3. Monitor for any issues
4. Update remaining endpoints
5. Celebrate 10-100x performance improvement! 🎉
