#!/bin/sh
set -e

# Config should be pre-rendered on the host using envsubst before Docker starts
# See setup-odoo.sh and safee-odoo-config.service for the rendering step

CONFIG_FILE="/var/lib/odoo/odoo.conf"

if [ -f "/etc/odoo/odoo.conf" ]; then
  >&2 echo "Using mounted config at /etc/odoo/odoo.conf"
  cp /etc/odoo/odoo.conf "$CONFIG_FILE"
elif [ -f "/etc/odoo/odoo.conf.template" ]; then
  >&2 echo "Generating config from template (fallback)"
  envsubst < /etc/odoo/odoo.conf.template > "$CONFIG_FILE"
else
  >&2 echo "ERROR: No config file found"
  exit 1
fi

# Extract database connection info for health check (handles spaces around =)
DB_HOST=$(awk -F'=' '/^[ \t]*db_host[ \t]*=/ {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit}' "$CONFIG_FILE")
DB_PORT=$(awk -F'=' '/^[ \t]*db_port[ \t]*=/ {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit}' "$CONFIG_FILE")
DB_USER=$(awk -F'=' '/^[ \t]*db_user[ \t]*=/ {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit}' "$CONFIG_FILE")

# Wait for the database to be ready
>&2 echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
export PGSSLMODE=require
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - starting Odoo with config: ${CONFIG_FILE}"

# Start Odoo
exec odoo -c "${CONFIG_FILE}"
