#!/bin/bash
# Script to install base Safee Analytics modules on an Odoo database

set -e

# Check if database name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <database_name>"
    echo "Example: $0 odoo_safee_demo"
    exit 1
fi

DB_NAME="$1"
echo "Installing Safee Analytics base modules on database: $DB_NAME"

# Install safee_base module which will pull in all dependencies
# This includes: sale_management, crm, account, project, hr, calendar
/opt/odoo/odoo-bin \
    -c /tmp/odoo.conf \
    -d "$DB_NAME" \
    -i safee_base \
    --stop-after-init \
    --no-http

echo "✅ Base modules installed successfully on database: $DB_NAME"
echo ""
echo "Installed modules:"
echo "  - Sales Management (sale_management)"
echo "  - CRM (crm)"
echo "  - Accounting & Invoicing (account)"
echo "  - Project Management (project)"
echo "  - Employees (hr)"
echo "  - Calendar (calendar)"
echo ""
echo "You can now access your database at: http://localhost:8069"
