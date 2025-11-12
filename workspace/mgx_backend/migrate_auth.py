"""Database migration script to add authentication fields and conversation history."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database import get_db_manager, Base

def migrate_database():
    """Migrate database to add authentication fields and conversation history table."""
    db_manager = get_db_manager()
    engine = db_manager.engine
    
    with engine.connect() as conn:
        # Check if password_hash column exists
        try:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            # Add password_hash if it doesn't exist
            if 'password_hash' not in columns:
                print("Adding password_hash column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT ''"))
                conn.commit()
                print("✅ Added password_hash column")
            
            # Add avatar_url if it doesn't exist
            if 'avatar_url' not in columns:
                print("Adding avatar_url column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) DEFAULT ''"))
                conn.commit()
                print("✅ Added avatar_url column")
        except Exception as e:
            print(f"⚠️  Error checking/adding columns: {e}")
            # Try to create columns anyway (might be PostgreSQL/MySQL)
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) DEFAULT ''"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500) DEFAULT ''"))
                conn.commit()
            except:
                pass
        
        # Check if conversation_history table exists
        try:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_history'"))
            if result.fetchone() is None:
                print("Creating conversation_history table...")
                # Create the table using SQLAlchemy
                from database import ConversationHistoryModel
                ConversationHistoryModel.__table__.create(engine, checkfirst=True)
                print("✅ Created conversation_history table")
            else:
                print("✅ conversation_history table already exists")
        except Exception as e:
            print(f"⚠️  Error checking conversation_history table: {e}")
            # Try to create using SQLAlchemy
            try:
                from database import ConversationHistoryModel
                ConversationHistoryModel.__table__.create(engine, checkfirst=True)
            except Exception as e2:
                print(f"⚠️  Could not create conversation_history table: {e2}")
    
    # Ensure all tables are created
    Base.metadata.create_all(bind=engine)
    print("✅ Database migration completed!")

if __name__ == "__main__":
    migrate_database()

