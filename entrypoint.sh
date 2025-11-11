#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD="${ODOO_DB_PASSWORD:-safee}" psql -h "${ODOO_DB_HOST:-postgres}" -p "${ODOO_DB_PORT:-5432}" -U "${ODOO_DB_USER:-safee}" -d postgres -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready!"

# Multi-tenancy mode: Don't auto-initialize any database
# Users will create databases through the web interface or API
# Each client gets their own database

echo "Starting Odoo in multi-tenancy mode..."
echo "Create databases for each client via:"
echo "  - Web UI: http://localhost:8069/web/database/manager"
echo "  - Or via API after container starts"

# Substitute environment variables into config file
# This keeps credentials in environment variables, not in git-tracked files
echo "Database: ${ODOO_DB_USER}@${ODOO_DB_HOST}:${ODOO_DB_PORT}"
echo "Admin password: $([ -n "${ODOO_ADMIN_PASSWD}" ] && echo "configured" || echo "NOT SET - using default")"

# Create a writable config file with substituted values in the data directory
cp /etc/odoo/odoo.conf /var/lib/odoo/odoo.conf
sed -i "s/DB_HOST_PLACEHOLDER/${ODOO_DB_HOST}/g" /var/lib/odoo/odoo.conf
sed -i "s/DB_PORT_PLACEHOLDER/${ODOO_DB_PORT}/g" /var/lib/odoo/odoo.conf
sed -i "s/DB_USER_PLACEHOLDER/${ODOO_DB_USER}/g" /var/lib/odoo/odoo.conf
sed -i "s/DB_PASSWORD_PLACEHOLDER/${ODOO_DB_PASSWORD}/g" /var/lib/odoo/odoo.conf
sed -i "s/ADMIN_PASSWD_PLACEHOLDER/${ODOO_ADMIN_PASSWD}/g" /var/lib/odoo/odoo.conf

# Ensure proper ownership
chown -R odoo:odoo /var/lib/odoo

# Start Odoo as odoo user
exec gosu odoo /opt/odoo/odoo-bin -c /var/lib/odoo/odoo.conf
