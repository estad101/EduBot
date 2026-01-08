#!/usr/bin/env python3
"""
Connect to Railway MySQL and create the leads table.
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Extract connection details from DATABASE_URL
# Format: mysql+mysqlconnector://user:password@host:port/database
db_url = os.getenv("DATABASE_URL", "")

if not db_url:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

# Parse the URL
try:
    # Remove the mysql+mysqlconnector:// part
    url_parts = db_url.replace("mysql+mysqlconnector://", "")
    
    # Split user:password@host:port/database
    auth_part, rest = url_parts.split("@")
    user, password = auth_part.split(":")
    
    host_port, database = rest.split("/")
    host, port = host_port.split(":")
    port = int(port)
    
    print(f"✓ Parsed connection details:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Database: {database}")
    
except Exception as e:
    print(f"❌ Error parsing DATABASE_URL: {e}")
    exit(1)

# Connect to Railway MySQL
try:
    print(f"\n🔄 Connecting to Railway MySQL at {host}:{port}...")
    
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✓ Connected to MySQL Server version {db_info}")
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()
        print(f"✓ Using database: {result[0]}")
        
        # Create the leads table
        print(f"\n📋 Creating leads table...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS leads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone_number VARCHAR(20) NOT NULL UNIQUE,
            sender_name VARCHAR(255),
            first_message TEXT,
            last_message TEXT,
            message_count INT NOT NULL DEFAULT 1,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            converted_to_student BOOLEAN NOT NULL DEFAULT FALSE,
            student_id INT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_message_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX ix_leads_phone_number (phone_number),
            INDEX ix_leads_created_at (created_at),
            INDEX ix_leads_updated_at (updated_at),
            INDEX ix_leads_student_id (student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        print("✓ Leads table created successfully!")
        
        # Verify the table exists
        cursor.execute("SHOW TABLES LIKE 'leads'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Verified: 'leads' table exists in database")
            
            # Show table structure
            cursor.execute("DESCRIBE leads")
            columns = cursor.fetchall()
            print(f"\n📊 Table structure ({len(columns)} columns):")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("⚠ Warning: 'leads' table not found after creation")
        
        cursor.close()
        
except Error as e:
    print(f"❌ Error connecting to MySQL: {e}")
    exit(1)

finally:
    if connection.is_connected():
        connection.close()
        print(f"\n✓ Connection closed")

print("\n" + "="*60)
print("✓✓✓ SUCCESS: Leads table ready in Railway! ✓✓✓")
print("="*60)
