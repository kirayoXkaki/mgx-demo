"""Database usage examples."""

from database import get_db_manager, UserCreate, ProjectCreate, CostRecordCreate


def example_user_operations():
    """Example: User operations."""
    print("\n" + "="*60)
    print("📝 Example 1: User Operations")
    print("="*60)
    
    db = get_db_manager()
    
    # Create a new user
    print("\n1. Creating a new user...")
    user = db.create_user(UserCreate(
        username="alice",
        email="alice@example.com",
        api_key="sk-alice-key-123"
    ))
    print(f"✅ Created user: {user.username} (ID: {user.id})")
    
    # Get user by ID
    print("\n2. Getting user by ID...")
    user = db.get_user(user.id)
    print(f"✅ Found user: {user.username} - {user.email}")
    
    # Get user by username
    print("\n3. Getting user by username...")
    user = db.get_user_by_username("alice")
    print(f"✅ Found user: {user.username} - {user.email}")
    
    # List all users
    print("\n4. Listing all users...")
    users = db.list_users()
    print(f"✅ Total users: {len(users)}")
    for u in users:
        print(f"   - {u.username} ({u.email})")


def example_project_operations():
    """Example: Project operations."""
    print("\n" + "="*60)
    print("📝 Example 2: Project Operations")
    print("="*60)
    
    db = get_db_manager()
    
    # Get or create user
    user = db.get_user_by_username("demo_user")
    if not user:
        user = db.create_user(UserCreate(
            username="demo_user",
            email="demo@example.com"
        ))
    
    # Create a project
    print("\n1. Creating a new project...")
    project = db.create_project(
        ProjectCreate(
            name="Todo List App",
            description="A simple todo list application",
            idea="Create a todo list with add, delete, and mark complete features",
            investment=5.0
        ),
        user_id=user.id
    )
    print(f"✅ Created project: {project.name} (ID: {project.id})")
    print(f"   Status: {project.status}")
    print(f"   Investment: ${project.investment}")
    
    # Update project status
    print("\n2. Updating project status to 'running'...")
    db.update_project_status(
        project.id,
        "running",
        project_path="/workspace/projects/todo_list"
    )
    project = db.get_project(project.id)
    print(f"✅ Updated status: {project.status}")
    print(f"   Project path: {project.project_path}")
    
    # Update project cost
    print("\n3. Updating project cost...")
    db.update_project_cost(project.id, 2.5)
    project = db.get_project(project.id)
    print(f"✅ Updated cost: ${project.total_cost}")
    
    # Complete the project
    print("\n4. Completing the project...")
    db.update_project_status(project.id, "completed")
    project = db.get_project(project.id)
    print(f"✅ Project completed at: {project.completed_at}")
    
    # List all projects
    print("\n5. Listing all projects...")
    projects = db.list_projects()
    print(f"✅ Total projects: {len(projects)}")
    for p in projects:
        print(f"   - {p.name} ({p.status}) - Cost: ${p.total_cost:.4f}")
    
    # List user's projects
    print(f"\n6. Listing projects for user '{user.username}'...")
    user_projects = db.list_projects(user_id=user.id)
    print(f"✅ User has {len(user_projects)} project(s)")
    for p in user_projects:
        print(f"   - {p.name} ({p.status})")


def example_cost_tracking():
    """Example: Cost tracking."""
    print("\n" + "="*60)
    print("📝 Example 3: Cost Tracking")
    print("="*60)
    
    db = get_db_manager()
    
    # Get a project
    projects = db.list_projects()
    if not projects:
        print("⚠️  No projects found. Create a project first.")
        return
    
    project = projects[0]
    print(f"\n📁 Tracking costs for project: {project.name}")
    
    # Record costs for different actions
    actions = [
        ("WritePRD", "gpt-4-turbo", 1500, 800, 0.035),
        ("WriteDesign", "gpt-4-turbo", 2000, 1200, 0.048),
        ("WriteCode", "gpt-4o", 3000, 2500, 0.052),
    ]
    
    print("\n1. Recording cost entries...")
    for action_type, model, prompt_tokens, completion_tokens, cost in actions:
        db.create_cost_record(CostRecordCreate(
            project_id=project.id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=cost,
            action_type=action_type
        ))
        print(f"✅ Recorded: {action_type} - ${cost:.4f}")
    
    # Get all cost records
    print("\n2. Getting all cost records...")
    costs = db.get_project_costs(project.id)
    print(f"✅ Total cost records: {len(costs)}")
    for c in costs:
        print(f"   - {c.action_type}: {c.prompt_tokens + c.completion_tokens} tokens - ${c.total_cost:.4f}")
    
    # Get total cost
    print("\n3. Calculating total cost...")
    total = db.get_total_cost(project.id)
    print(f"✅ Total project cost: ${total:.4f}")
    
    # Update project with total cost
    db.update_project_cost(project.id, total)
    project = db.get_project(project.id)
    print(f"✅ Project total cost updated: ${project.total_cost:.4f}")


def example_full_workflow():
    """Example: Full workflow from user creation to project completion."""
    print("\n" + "="*60)
    print("📝 Example 4: Full Workflow")
    print("="*60)
    
    db = get_db_manager()
    
    # Step 1: Create user
    print("\n📍 Step 1: Create user")
    user = db.create_user(UserCreate(
        username="bob",
        email="bob@example.com",
        api_key="sk-bob-key-456"
    ))
    print(f"✅ User created: {user.username}")
    
    # Step 2: Create project
    print("\n📍 Step 2: Create project")
    project = db.create_project(
        ProjectCreate(
            name="Calculator App",
            description="A calculator with basic operations",
            idea="Create a calculator with +, -, *, / operations",
            investment=3.0
        ),
        user_id=user.id
    )
    print(f"✅ Project created: {project.name}")
    print(f"   Status: {project.status}")
    
    # Step 3: Start project (update status)
    print("\n📍 Step 3: Start project")
    db.update_project_status(
        project.id,
        "running",
        project_path="/workspace/projects/calculator"
    )
    print(f"✅ Project status: running")
    
    # Step 4: Track costs during development
    print("\n📍 Step 4: Track costs")
    costs_data = [
        ("WritePRD", "gpt-4-turbo", 1000, 500, 0.025),
        ("WriteDesign", "gpt-4-turbo", 1500, 800, 0.038),
        ("WriteCode", "gpt-4o", 2500, 2000, 0.045),
    ]
    
    for action_type, model, prompt_tokens, completion_tokens, cost in costs_data:
        db.create_cost_record(CostRecordCreate(
            project_id=project.id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=cost,
            action_type=action_type
        ))
    
    total_cost = db.get_total_cost(project.id)
    print(f"✅ Total cost: ${total_cost:.4f}")
    
    # Step 5: Complete project
    print("\n📍 Step 5: Complete project")
    db.update_project_cost(project.id, total_cost)
    db.update_project_status(project.id, "completed")
    
    project = db.get_project(project.id)
    print(f"✅ Project completed!")
    print(f"   Final cost: ${project.total_cost:.4f}")
    print(f"   Completed at: {project.completed_at}")
    
    # Step 6: Summary
    print("\n📍 Step 6: Summary")
    user_projects = db.list_projects(user_id=user.id)
    print(f"✅ User '{user.username}' has {len(user_projects)} project(s)")
    for p in user_projects:
        print(f"   - {p.name}: {p.status} (${p.total_cost:.4f})")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 MGX Backend Database Examples")
    print("="*60)
    
    try:
        # Run examples
        example_user_operations()
        example_project_operations()
        example_cost_tracking()
        example_full_workflow()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()