#!/bin/bash
set -e

#######################################
# Local Test Script for init-odoo-template.sh
# Tests template initialization with local Odoo setup
#######################################

echo "🧪 Testing Odoo Template Initialization"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# 1. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✅ Docker is running"

# 2. Check if custom_addons directory exists
if [ ! -d "custom_addons" ]; then
    echo "❌ Custom addons directory not found at custom_addons"
    exit 1
fi
ADDON_COUNT=$(ls -1 custom_addons | wc -l)
echo "✅ Found $ADDON_COUNT custom addons"

# 3. Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable is not set"
    echo ""
    echo "Please set your database connection:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:port/dbname'"
    echo ""
    echo "Or use the gateway .env file:"
    echo "  export \$(grep DATABASE_URL ../gateway/.env | xargs)"
    exit 1
fi
echo "✅ DATABASE_URL is set"

# Parse DATABASE_URL
DB_URL_REGEX="postgresql://([^:]+):([^@]+)@([^:/]+):?([0-9]*)/([^?]+)"
if [[ $DATABASE_URL =~ $DB_URL_REGEX ]]; then
    export DB_USER="${BASH_REMATCH[1]}"
    export DB_PASSWORD="${BASH_REMATCH[2]}"
    export DB_HOST="${BASH_REMATCH[3]}"
    export DB_PORT="${BASH_REMATCH[4]:-5432}"
    export DB_NAME="${BASH_REMATCH[5]}"

    echo "   Host: $DB_HOST"
    echo "   Port: $DB_PORT"
    echo "   Database: $DB_NAME"
else
    echo "❌ Could not parse DATABASE_URL"
    exit 1
fi

# 4. Test database connection
echo ""
echo "🔌 Testing database connection..."
if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Could not connect to database"
    echo "   Make sure PostgreSQL is accessible and credentials are correct"
    exit 1
fi

# 5. Set Odoo admin password
export ODOO_ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD:-admin123}"
echo "✅ Odoo admin password set"

echo ""
echo "=================================================="
echo "🚀 Starting template initialization..."
echo "   This will take 10-15 minutes"
echo "=================================================="
echo ""

# Create temporary modified version of init script for local testing
# (production script uses /opt/odoo/addons, local needs custom_addons)
cd "$(dirname "$0")"

echo "📝 Creating temporary local test script..."
TEMP_SCRIPT=$(mktemp)
cp init-odoo-template.sh "$TEMP_SCRIPT"

# Replace server path with local path for Docker volume mount
CUSTOM_ADDONS_PATH="$(cd custom_addons && pwd)"
sed -i.bak "s|/opt/odoo/addons|$CUSTOM_ADDONS_PATH|g" "$TEMP_SCRIPT"

# Add --network host to docker run command for better local networking
sed -i.bak2 "s|docker run --rm|docker run --rm --network host|g" "$TEMP_SCRIPT"

chmod +x "$TEMP_SCRIPT"

echo "✅ Using custom addons from: $CUSTOM_ADDONS_PATH"
echo "✅ Using host networking for database access"
echo "✅ Forcing TCP connection to 127.0.0.1:$DB_PORT"
echo ""

# Override DB_HOST to force TCP connection (not Unix socket)
# When running locally, Docker containers see "localhost" as Unix socket
export DB_HOST="127.0.0.1"

# Run the modified script with overridden environment
"$TEMP_SCRIPT"

# Cleanup
rm -f "$TEMP_SCRIPT" "$TEMP_SCRIPT.bak"

echo ""
echo "=================================================="
echo "✅ Test complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Verify template exists:"
echo "     psql \$DATABASE_URL -c \"SELECT datname FROM pg_database WHERE datname='odoo_template';\""
echo ""
echo "  2. Check template is marked correctly:"
echo "     psql \$DATABASE_URL -c \"SELECT datname, datistemplate FROM pg_database WHERE datname='odoo_template';\""
echo ""
echo "  3. Test creating a company database:"
echo "     cd infra/scripts"
echo "     ./duplicate-odoo-db.sh test_company 'Test Company'"
echo ""
