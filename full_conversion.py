#!/usr/bin/env python3
"""Complete async migration for all endpoints"""
import re

with open('admin/routes/api.py', 'r') as f:
    content = f.read()

# 1. Fix all parameter signatures that still reference db_dependency
content = content.replace(
    'db: Session = Depends(db_dependency)',
    'db: AsyncSession = Depends(get_async_db)'
)

# 2. Replace db.query patterns with select patterns
# This is complex - we'll use a series of targeted replacements

# Pattern: db.query(Model).filter_by(id=x).first()
content = re.sub(
    r'db\.query\((\w+)\)\.filter_by\(id=(\w+)\)\.first\(\)',
    r'(await db.execute(select(\1).where(\1.id == \2))).scalars().first()',
    content
)

# Pattern: db.query(Model).filter_by(status=x).count()
content = re.sub(
    r'db\.query\((\w+)\)\.filter_by\(status=(\w+)\)\.count\(\)',
    r'(await db.execute(select(func.count(\1.id)).where(\1.status == \2))).scalar() or 0',
    content
)

# Pattern: db.query(Model).filter_by(...).first()
content = re.sub(
    r'db\.query\((\w+)\)\.filter_by\((\w+)=(\w+)\)\.first\(\)',
    r'(await db.execute(select(\1).where(\1.\2 == \3))).scalars().first()',
    content
)

# Pattern: db.query(Model).filter_by(...).count()
content = re.sub(
    r'db\.query\((\w+)\)\.filter_by\((\w+)=(\w+)\)\.count\(\)',
    r'(await db.execute(select(func.count(\1.id)).where(\1.\2 == \3))).scalar() or 0',
    content
)

# Pattern: db.query(Model).count()
content = re.sub(
    r'db\.query\((\w+)\)\.count\(\)',
    r'(await db.execute(select(func.count(\1.id)))).scalar() or 0',
    content
)

# Pattern: db.query(Model).offset(...).limit(...).all()
content = re.sub(
    r'db\.query\((\w+)\)\.offset\((\w+)\)\.limit\((\w+)\)\.all\(\)',
    r'(await db.execute(select(\1).offset(\2).limit(\3))).scalars().all()',
    content
)

# Pattern: db.query(Model).filter(...).offset(...).limit(...).all()
# This one is more complex - need to keep the filter content
content = re.sub(
    r'db\.query\((\w+)\)\.filter\(([^)]+)\)\.offset\((\w+)\)\.limit\((\w+)\)\.all\(\)',
    r'(await db.execute(select(\1).where(\2).offset(\3).limit(\4))).scalars().all()',
    content
)

# Pattern: db.query(Model).all()
content = re.sub(
    r'(\s+)students = db\.query\(Student\)\.all\(\)',
    r'\1result = await db.execute(select(Student))\n\1students = result.scalars().all()',
    content
)

# Pattern: db.query(Model).filter_by(...).all()
content = re.sub(
    r'db\.query\((\w+)\)\.filter_by\((\w+)=(\w+)\)\.all\(\)',
    r'(await db.execute(select(\1).where(\1.\2 == \3))).scalars().all()',
    content
)

# 3. Fix commit/rollback
content = content.replace('db.commit()', 'await db.commit()')
content = content.replace('db.rollback()', 'await db.rollback()')

# 4. Fix delete
content = content.replace('db.delete(', 'await db.delete(')

# 5. Ensure select is imported where used
# Add import at top of function bodies if not already there
lines = content.split('\n')
output_lines = []
in_async_def = False
added_select_import = False

for i, line in enumerate(lines):
    output_lines.append(line)
    
    if line.strip().startswith('async def ') and 'db: AsyncSession' in line:
        in_async_def = True
        added_select_import = False
    elif in_async_def and '"""' in line and i > 0 and '"""' not in lines[i-1]:
        # After docstring, check if we need to add select import
        if i+1 < len(lines):
            next_line = lines[i+1]
            if 'from sqlalchemy import select' not in next_line and 'db.execute' in '\n'.join(lines[i:min(i+10, len(lines))]):
                if not added_select_import:
                    output_lines.append('    from sqlalchemy import select')
                    added_select_import = True
    elif in_async_def and line.strip().startswith('return ') or line.strip().startswith('raise '):
        in_async_def = False

content = '\n'.join(output_lines)

with open('admin/routes/api.py', 'w') as f:
    f.write(content)

print("✅ Complete async migration done!")
