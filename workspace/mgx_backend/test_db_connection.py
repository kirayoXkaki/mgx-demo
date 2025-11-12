#!/usr/bin/env python3
"""Test database connection and configuration."""

import os
import sys
from mgx_backend.database import get_db_manager, UserCreate

def test_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    print("=" * 60)
    
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
    
    # Mask password in URL for display
    display_url = database_url
    if "@" in display_url:
        parts = display_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user, _ = user_pass.split(":", 1)
                display_url = display_url.replace(f":{user_pass.split(':')[1]}@", f":***@")
    
    print(f"📊 Database URL: {display_url}")
    print()
    
    try:
        # Initialize database
        db = get_db_manager(database_url)
        print("✅ Database connection established")
        
        # Test basic operations
        print("\n📝 Testing basic operations...")
        
        # List users
        users = db.list_users()
        print(f"   Found {len(users)} users")
        
        # List projects
        projects = db.list_projects()
        print(f"   Found {len(projects)} projects")
        
        # Test creating a user (if not exists)
        test_username = "test_user_db_check"
        existing_user = db.get_user_by_username(test_username)
        
        if not existing_user:
            test_user = db.create_user(UserCreate(
                username=test_username,
                email="test@example.com",
                api_key="test_key"
            ))
            print(f"   ✅ Created test user: {test_user.username}")
            
            # Clean up
            db_session = db.get_session()
            try:
                db_session.delete(test_user)
                db_session.commit()
                print(f"   🧹 Cleaned up test user")
            finally:
                db_session.close()
        else:
            print(f"   ℹ️  Test user already exists")
        
        print("\n🎉 Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection test failed!")
        print(f"   Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check DATABASE_URL environment variable")
        print("   2. Verify database server is running")
        print("   3. Check database credentials")
        print("   4. Ensure database exists")
        if "psycopg2" in str(e).lower() or "postgresql" in database_url.lower():
            print("   5. Install PostgreSQL driver: pip install psycopg2-binary")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

