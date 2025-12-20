#!/bin/bash
set -e

#######################################
# Build and Initialize Complete Odoo Setup
# 1. Builds safee-odoo:18.0 with OCA modules
# 2. Initializes template database with all modules
#######################################

echo "🐳 Building and Testing Custom Odoo Setup"
echo "=================================================="

# Navigate to project root (one level up from odoo/)
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Load environment variables if .env exists
if [ -f "odoo/.env" ]; then
    echo "📋 Loading environment from odoo/.env"
    export $(grep -v '^#' odoo/.env | xargs)
fi

echo "📂 Project root: $PROJECT_ROOT"
echo ""

# 1. Build the Docker image from project root
echo "📦 Building safee-odoo:18.0..."
echo "   Build context: $PROJECT_ROOT"
echo "   Dockerfile: odoo/Dockerfile"
docker build -f odoo/Dockerfile -t safee-odoo:18.0 .

# 2. Verify image was created
if docker images safee-odoo:18.0 | grep -q safee-odoo; then
    echo "✅ Image built successfully"
    echo ""
    docker images safee-odoo:18.0
else
    echo "❌ Image build failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "🚀 Initializing Odoo Template Database"
echo "=================================================="
echo ""

# 3. Run the initialization script
cd odoo
./test-init-template.sh

echo ""
echo "=================================================="
echo "✅ Complete setup finished!"
echo "=================================================="
echo ""
echo "Image: safee-odoo:18.0"
echo "Template database: odoo_template (84 MB, 262 modules)"
echo ""
echo "Next steps:"
echo "  1. Verify template:"
echo "     psql \$DATABASE_URL -c \"SELECT datname, datistemplate FROM pg_database WHERE datname='odoo_template';\""
echo ""
echo "  2. Test the image:"
echo "     docker run --rm safee-odoo:18.0 odoo --version"
echo ""
echo "  3. Start Odoo server:"
echo "     docker run -p 8069:8069 -e HOST=127.0.0.1 -e PASSWORD=\$DB_PASSWORD safee-odoo:18.0"
echo ""
