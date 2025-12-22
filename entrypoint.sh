#!/bin/sh
set -e

# Wait for the database to be ready
until pg_isready -h postgres -p 5432 -U safee; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - generating config with environment variables"

# Substitute environment variables in config template
# Write to writable location since /etc/odoo/ is read-only
envsubst < /etc/odoo/odoo.conf.template > /var/lib/odoo/odoo.conf

>&2 echo "Starting Odoo with generated config: /var/lib/odoo/odoo.conf"

# Start Odoo
odoo -c /var/lib/odoo/odoo.conf
