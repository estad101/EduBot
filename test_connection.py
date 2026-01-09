import os
import sys

os.environ['DATABASE_URL'] = 'mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway'

print("[1] Testing database URL...")
from config.settings import settings
print(f"[✓] DATABASE_URL loaded: {settings.database_url[:50]}...")

print("\n[2] Testing database engine creation...")
try:
    from config.database import engine
    print("[✓] Engine created successfully")
except Exception as e:
    print(f"[✗] Engine creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[3] Testing database connection...")
try:
    from config.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    result = db.execute(text("SELECT 1"))
    print(f"[✓] Database connection successful: {result.fetchone()}")
    db.close()
except Exception as e:
    print(f"[✗] Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4] Testing main.py import...")
try:
    import main
    print("[✓] main.py imported successfully")
except Exception as e:
    print(f"[✗] main.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[✓] ALL TESTS PASSED")
