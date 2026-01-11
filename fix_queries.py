#!/usr/bin/env python3
"""
Convert remaining .query() patterns to async select() patterns
"""
import re

with open('admin/routes/api.py', 'r') as f:
    content = f.read()

# Fix patterns like: db.query(Student).filter(...).all()
# Replace with: (await db.execute(select(Student).where(...))).scalars().all()

replacements = [
    # Replace remaining parameter signatures
    (r'db: Session = Depends\(db_dependency\)', 'db: AsyncSession = Depends(get_async_db)'),
    
    # Replace simple db.query().filter_by().first()
    (r'db\.query\((\w+)\)\.filter_by\(id=(\w+)\)\.first\(\)', 
     r'(await db.execute(select(\1).where(\1.id == \2))).scalars().first()'),
    
    # Replace db.query().filter_by().all()
    (r'db\.query\((\w+)\)\.filter_by\((\w+)=(\w+)\)\.all\(\)',
     r'(await db.execute(select(\1).where(\1.\2 == \3))).scalars().all()'),
    
    # Replace db.commit() with await
    (r'(\n\s+)db\.commit\(\)', r'\1await db.commit()'),
    
    # Replace db.rollback() with await
    (r'(\n\s+)db\.rollback\(\)', r'\1await db.rollback()'),
    
    # Replace db.delete() with await
    (r'(\n\s+)db\.delete\(', r'\1await db.delete('),
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open('admin/routes/api.py', 'w') as f:
    f.write(content)

print("✅ Query conversion completed")
