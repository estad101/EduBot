#!/usr/bin/env python3
"""Batch convert remaining query patterns"""
import re

with open('admin/routes/api.py', 'r') as f:
    lines = f.readlines()

# Fix parameter signatures
output = []
for line in lines:
    # Fix db parameter types
    line = line.replace(
        'db: Session = Depends(db_dependency)',
        'db: AsyncSession = Depends(get_async_db)'
    )
    # Fix commit/rollback
    if 'db.commit()' in line:
        line = line.replace('db.commit()', 'await db.commit()')
    if 'db.rollback()' in line:
        line = line.replace('db.rollback()', 'await db.rollback()')
    output.append(line)

with open('admin/routes/api.py', 'w') as f:
    f.writelines(output)

print('✅ Basic conversions done')

# Now handle the complex .query() patterns - we'll do these manually in sections
# This just does the easy wins
