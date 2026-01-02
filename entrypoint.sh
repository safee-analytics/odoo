#!/bin/sh
set -e

# Check if a config file is already mounted (production)
if [ -f "/etc/odoo/odoo.conf" ]; then
  >&2 echo "Using mounted config at /etc/odoo/odoo.conf"
  CONFIG_FILE="/etc/odoo/odoo.conf"

  # Extract database connection info from config for health check
  DB_HOST=$(grep "^db_host" /etc/odoo/odoo.conf | cut -d'=' -f2 | tr -d ' ')
  DB_PORT=$(grep "^db_port" /etc/odoo/odoo.conf | cut -d'=' -f2 | tr -d ' ')
  DB_USER=$(grep "^db_user" /etc/odoo/odoo.conf | cut -d'=' -f2 | tr -d ' ')
else
  >&2 echo "No mounted config found, generating from template"
  # Use environment variables with defaults for local development
  DB_HOST="${HOST:-postgres}"
  DB_PORT="${PORT:-5432}"
  DB_USER="${USER:-odoo}"

  # Generate config from template with environment variable substitution
  envsubst < /etc/odoo/odoo.conf.template > /var/lib/odoo/odoo.conf
  CONFIG_FILE="/var/lib/odoo/odoo.conf"
fi

# Wait for the database to be ready
>&2 echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - starting Odoo with config: ${CONFIG_FILE}"

# Start Odoo
odoo -c "${CONFIG_FILE}"
