#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready!"

# Check if this is first run (no databases exist)
DB_EXISTS=$(psql -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" -lqt | cut -d \| -f 1 | grep -w "${ODOO_DB:-odoo}" | wc -l)

if [ "$DB_EXISTS" -eq "0" ]; then
    echo "First run detected. Initializing database..."
    # Initialize database and install base + api_rest module
    /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf \
        -d "${ODOO_DB:-odoo}" \
        -i base,api_rest \
        --stop-after-init \
        --without-demo=all
    echo "Database initialized with api_rest module!"
fi

# Start Odoo
echo "Starting Odoo..."
exec /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf "$@"
