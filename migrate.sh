#!/bin/bash
# Database migration script
# Run: railway run bash migrate.sh

echo "Starting database migrations..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    if [ -n "$MYSQL_URL" ]; then
        export DATABASE_URL=$MYSQL_URL
    else
        echo "ERROR: DATABASE_URL or MYSQL_URL not set"
        exit 1
    fi
fi

echo "Database URL: ${DATABASE_URL:0:50}..."

# Run migrations
echo "Running alembic upgrade head..."
python -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully!"
else
    echo "✗ Migrations failed"
    exit 1
fi
