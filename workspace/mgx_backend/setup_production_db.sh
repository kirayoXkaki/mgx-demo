#!/bin/bash
# Production Database Setup Script

set -e

echo "🚀 MGX Backend - Production Database Setup"
echo "=" | head -c 60 && echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo ""
    echo "📦 Installation instructions:"
    echo "   macOS:   brew install postgresql@15"
    echo "   Ubuntu:  sudo apt install postgresql postgresql-contrib"
    echo "   Windows: Download from https://www.postgresql.org/download/windows/"
    exit 1
fi

echo "✅ PostgreSQL found: $(psql --version)"
echo ""

# Get database configuration
read -p "📝 Enter database name [mgx_backend]: " DB_NAME
DB_NAME=${DB_NAME:-mgx_backend}

read -p "📝 Enter database user [mgx_user]: " DB_USER
DB_USER=${DB_USER:-mgx_user}

read -sp "🔐 Enter database password: " DB_PASSWORD
echo ""

read -p "📝 Enter database host [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "📝 Enter database port [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

echo ""
echo "🔧 Creating database and user..."

# Create database and user
sudo -u postgres psql <<EOF
-- Create database
CREATE DATABASE $DB_NAME;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to database and grant schema privileges
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database and user created successfully!"
else
    echo "❌ Failed to create database. You may need to run:"
    echo "   sudo -u postgres psql"
    echo "   Then manually create the database and user."
    exit 1
fi

# Create .env file
ENV_FILE=".env"
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

echo ""
echo "📝 Creating .env file..."
cat > "$ENV_FILE" <<EOF
# Database Configuration
DATABASE_URL=$DATABASE_URL

# Database Connection Pool (optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
EOF

echo "✅ Created $ENV_FILE"
echo ""
echo "📋 Database connection string:"
echo "   $DATABASE_URL" | sed 's/:[^:]*@/:***@/'
echo ""

# Install PostgreSQL driver
echo "📦 Installing PostgreSQL driver..."
pip install psycopg2-binary

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL driver installed"
else
    echo "⚠️  Failed to install driver. Run manually:"
    echo "   pip install psycopg2-binary"
fi

echo ""
echo "🧪 Testing database connection..."
python test_db_connection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Initialize database tables: python init_db.py"
    echo "   2. Start the API server: ./start_api.sh"
    echo "   3. Check PRODUCTION_DATABASE_SETUP.md for more details"
else
    echo ""
    echo "⚠️  Connection test failed. Please check:"
    echo "   1. Database server is running"
    echo "   2. Credentials are correct"
    echo "   3. Firewall allows connections"
fi

