"""Initialize database and create sample data."""

import asyncio
from database import get_db_manager, UserCreate, ProjectCreate


def init_database():
    """Initialize database with tables and sample data."""
    print("🔧 Initializing MGX Backend Database...")
    
    # Get database manager
    db = get_db_manager()
    
    # Create tables
    print("📊 Creating tables...")
    db.create_tables()
    print("✅ Tables created successfully!")
    
    # Create sample user
    print("\n👤 Creating sample user...")
    try:
        user = db.create_user(UserCreate(
            username="demo_user",
            email="demo@example.com",
            api_key="demo_api_key"
        ))
        print(f"✅ User created: {user.username} (ID: {user.id})")
        
        # Create sample project
        print("\n📁 Creating sample project...")
        project = db.create_project(
            ProjectCreate(
                name="Sample Calculator",
                description="A simple calculator application",
                idea="Create a calculator with basic operations",
                investment=5.0
            ),
            user_id=user.id
        )
        print(f"✅ Project created: {project.name} (ID: {project.id})")
        
    except Exception as e:
        print(f"⚠️  Sample data already exists or error: {e}")
    
    print("\n🎉 Database initialization complete!")
    print(f"📍 Database location: sqlite:///./mgx_backend.db")
    print("\n💡 You can now:")
    print("   1. Use the database in your code")
    print("   2. Run the API server with database support")
    print("   3. View data using SQLite browser or CLI")


def show_database_info():
    """Show database information."""
    db = get_db_manager()
    
    print("\n" + "="*60)
    print("📊 MGX Backend Database Information")
    print("="*60)
    
    # Count users
    users = db.list_users()
    print(f"\n👥 Users: {len(users)}")
    for user in users[:5]:
        print(f"   - {user.username} ({user.email}) - Created: {user.created_at}")
    
    # Count projects
    projects = db.list_projects()
    print(f"\n📁 Projects: {len(projects)}")
    for project in projects[:5]:
        print(f"   - {project.name} ({project.status}) - Cost: ${project.total_cost:.4f}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Show info
    show_database_info()