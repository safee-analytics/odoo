#!/bin/bash
# Host script to install Safee Analytics base modules in Docker container

set -e

CONTAINER_NAME="${1:-safee-odoo-1}"
DB_NAME="${2:-odoo_safee}"

echo "========================================="
echo "Safee Analytics - Module Installation"
echo "========================================="
echo ""
echo "Container: $CONTAINER_NAME"
echo "Database: $DB_NAME"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container '$CONTAINER_NAME' is not running"
    echo ""
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo "📦 Installing base modules..."
echo ""

# Execute installation script inside container
docker exec -it "$CONTAINER_NAME" /bin/bash -c "
    cd /opt/odoo && \
    ./install_base_modules.sh $DB_NAME
"

echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo ""
echo "Access your Odoo instance:"
echo "  URL: http://localhost:8069"
echo "  Database: $DB_NAME"
echo ""
echo "Installed modules:"
echo "  📊 Sales Management"
echo "  🤝 CRM"
echo "  💰 Accounting & Invoicing"
echo "  📋 Project Management"
echo "  👥 Employees (HR)"
echo "  📅 Calendar"
echo ""
