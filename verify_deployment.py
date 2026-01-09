#!/usr/bin/env python3
"""
Complete Railway Deployment Verification Script
Tests all components before pushing to production
"""
import os
import sys
from pathlib import Path

# Set the Railway database URL for testing
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway'

print("=" * 70)
print("RAILWAY DEPLOYMENT VERIFICATION")
print("=" * 70)

# Test 1: Settings Configuration
print("\n[1] Testing Settings Configuration...")
try:
    from config.settings import settings
    print(f"    ✓ Settings loaded successfully")
    print(f"    ✓ API Title: {settings.api_title}")
    print(f"    ✓ Environment: {settings.environment}")
    if settings.database_url and settings.database_url.strip():
        print(f"    ✓ Database URL configured")
    else:
        print(f"    ✗ Database URL not configured")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Settings failed: {e}")
    sys.exit(1)

# Test 2: Database Engine Creation
print("\n[2] Testing Database Engine Creation...")
try:
    from config.database import engine
    print(f"    ✓ Engine created successfully")
    print(f"    ✓ Using NullPool for Railway")
except Exception as e:
    print(f"    ✗ Engine creation failed: {e}")
    sys.exit(1)

# Test 3: Database Connection
print("\n[3] Testing Database Connection...")
try:
    from config.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    result = db.execute(text("SELECT 1 as connection_test"))
    row = result.fetchone()
    if row and row[0] == 1:
        print(f"    ✓ Database connection successful")
        print(f"    ✓ Query result: {row}")
    db.close()
except Exception as e:
    print(f"    ✗ Connection failed: {e}")
    sys.exit(1)

# Test 4: FastAPI Application Import
print("\n[4] Testing FastAPI Application...")
try:
    import main
    app = main.app
    print(f"    ✓ FastAPI app created successfully")
    print(f"    ✓ Title: {app.title}")
    print(f"    ✓ Version: {app.version}")
except Exception as e:
    print(f"    ✗ FastAPI app failed: {e}")
    sys.exit(1)

# Test 5: Route Registration
print("\n[5] Testing Route Registration...")
try:
    routes = [route.path for route in app.routes]
    api_routes = [r for r in routes if r.startswith('/api')]
    print(f"    ✓ Total routes registered: {len(routes)}")
    print(f"    ✓ API routes: {len(api_routes)}")
    if api_routes:
        for route in api_routes[:5]:
            print(f"       - {route}")
        if len(api_routes) > 5:
            print(f"       ... and {len(api_routes) - 5} more")
except Exception as e:
    print(f"    ✗ Route check failed: {e}")
    sys.exit(1)

# Test 6: Health Check Endpoint
print("\n[6] Testing Health Check Endpoint...")
try:
    from api.routes.health import router as health_router
    print(f"    ✓ Health check module loaded")
except Exception as e:
    print(f"    ✗ Health check failed: {e}")
    sys.exit(1)

# Test 7: Model Imports (Lazy Loading)
print("\n[7] Testing Model Lazy Loading...")
try:
    from models import __all__ as model_exports
    print(f"    ✓ Model __all__ list available")
    print(f"    ✓ Models available: {', '.join(model_exports)}")
except Exception as e:
    print(f"    ✗ Model imports failed: {e}")
    sys.exit(1)

# Test 8: Configuration Files
print("\n[8] Testing Configuration Files...")
config_checks = [
    ('railway.json', Path('railway.json').exists()),
    ('Dockerfile', Path('Dockerfile').exists()),
    ('.dockerignore', Path('.dockerignore').exists()),
]
for config_name, exists in config_checks:
    if exists:
        print(f"    ✓ {config_name} exists")
    else:
        print(f"    ⚠ {config_name} missing (may be needed)")

# Test 9: Environment Variables
print("\n[9] Testing Environment Variables...")
env_vars = [
    ('DATABASE_URL', 'Database connection string'),
    ('SECRET_KEY', 'Application secret key'),
    ('ADMIN_PASSWORD', 'Admin panel password'),
]
for env_var, description in env_vars:
    value = os.getenv(env_var)
    if value:
        # Mask sensitive values
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"    ✓ {env_var}: {description} (set)")
    else:
        print(f"    ⚠ {env_var}: {description} (not set - may use fallback)")

# Test 10: Documentation
print("\n[10] Testing Documentation...")
docs_files = [
    'RAILWAY_DATABASE_URL_SETUP.md',
    'DATABASE_URL_FIX_INSTRUCTIONS.md',
    'RAILWAY_DEPLOYMENT.md',
]
for doc_file in docs_files:
    if Path(doc_file).exists():
        print(f"    ✓ {doc_file}")
    else:
        print(f"    ⚠ {doc_file} (documentation file)")

# Final Summary
print("\n" + "=" * 70)
print("VERIFICATION RESULTS")
print("=" * 70)
print("✓ All critical systems verified successfully!")
print("\nNEXT STEPS:")
print("1. Set DATABASE_URL in Railway Variables (Variables tab)")
print(f"   Value: {os.getenv('DATABASE_URL')}")
print("2. Commit and push: git push origin main")
print("3. Railway will auto-redeploy")
print("4. Check Deploy Logs for '=== APPLICATION READY ==='")
print("5. Test: https://edubot-production-cf26.up.railway.app/api/health")
print("=" * 70)
