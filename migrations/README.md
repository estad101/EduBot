# Alembic migrations - for version control of database schema

This directory contains database migrations managed by Alembic.

## Commands

### Create initial migration:
```bash
alembic revision --autogenerate -m "Create initial schema"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

### Check current revision:
```bash
alembic current
```

### View history:
```bash
alembic history
```

### Create empty migration:
```bash
alembic revision -m "Description"
```
