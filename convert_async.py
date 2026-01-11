import re

# Read the file
with open('admin/routes/api.py', 'r') as f:
    content = f.read()

# Replace all remaining db: Session = Depends(db_dependency) with db: AsyncSession = Depends(get_async_db)
content = re.sub(
    r'db: Session = Depends\(db_dependency\)',
    'db: AsyncSession = Depends(get_async_db)',
    content
)

# Replace db.commit() with await db.commit()
content = re.sub(
    r'(\s+)db\.commit\(\)',
    r'\1await db.commit()',
    content
)

# Replace db.rollback() with await db.rollback()
content = re.sub(
    r'(\s+)db\.rollback\(\)',
    r'\1await db.rollback()',
    content
)

# Write back
with open('admin/routes/api.py', 'w') as f:
    f.write(content)

print("✅ Conversion script completed")
