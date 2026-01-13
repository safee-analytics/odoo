#!/bin/sh
set -e

# Set default environment variables
SENTRY_ENABLED="${SENTRY_ENABLED:-true}"
SENTRY_DSN="${SENTRY_DSN:-https://1d96ca4d366bed0dc8d5e2ebd241b454@o4510529722449920.ingest.de.sentry.io/4510637363429456}"
SENTRY_ENVIRONMENT="${SENTRY_ENVIRONMENT:-local}"

# Check if a config file is already mounted (production)
if [ -f "/etc/odoo/odoo.conf" ]; then
  >&2 echo "Using mounted config at /etc/odoo/odoo.conf"

  # Copy config to writable location and substitute environment variables
  cp /etc/odoo/odoo.conf /var/lib/odoo/odoo.conf
  CONFIG_FILE="/var/lib/odoo/odoo.conf"

  # Replace Sentry configuration using sed
  sed -i "s|sentry_enabled = \${SENTRY_ENABLED}|sentry_enabled = ${SENTRY_ENABLED}|g" "$CONFIG_FILE"
  sed -i "s|sentry_dsn = \${SENTRY_DSN}|sentry_dsn = ${SENTRY_DSN}|g" "$CONFIG_FILE"
  sed -i "s|sentry_environment = \${SENTRY_ENVIRONMENT}|sentry_environment = ${SENTRY_ENVIRONMENT}|g" "$CONFIG_FILE"

  # Extract database connection info from config for health check
  DB_HOST=$(grep "^db_host" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
  DB_PORT=$(grep "^db_port" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
  DB_USER=$(grep "^db_user" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
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

>&2 echo "Sentry enabled: ${SENTRY_ENABLED}"
>&2 echo "Sentry DSN configured: $([ -n "$SENTRY_DSN" ] && echo "yes" || echo "no")"
>&2 echo "Sentry environment: ${SENTRY_ENVIRONMENT}"

# Wait for the database to be ready
>&2 echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - starting Odoo with config: ${CONFIG_FILE}"

# Start Odoo
odoo -c "${CONFIG_FILE}"
