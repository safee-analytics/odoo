#!/bin/bash
set -e

#######################################
# Initialize Odoo Template Database
# This creates odoo_template with all base modules and custom addons pre-installed
# New company databases will be duplicated from this template
#
# Usage:
#   ./init-odoo-template.sh                                    # Create if not exists
#   ./init-odoo-template.sh --force                            # Drop and recreate
#   ./init-odoo-template.sh --add-modules "mod1,mod2"          # Install additional modules
#   ./init-odoo-template.sh --remove-modules "mod1,mod2"       # Uninstall modules
#######################################

# Parse arguments
FORCE_RECREATE=false
ADD_MODULES=""
REMOVE_MODULES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_RECREATE=true
            shift
            ;;
        --add-modules)
            ADD_MODULES="$2"
            shift 2
            ;;
        --remove-modules)
            REMOVE_MODULES="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--add-modules \"mod1,mod2\"] [--remove-modules \"mod1,mod2\"]"
            exit 1
            ;;
    esac
done

# Configuration
TEMPLATE_DB="odoo_template"

# Read from environment (set by Odoo server's .env file)
# When running via Terraform, these come from docker-compose .env
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
if [ "$DB_HOST" = "localhost" ]; then
  DB_USER="${DB_USER:-safee}"
  DB_SSLMODE="${DB_SSLMODE:-disable}"
else
  DB_USER="${DB_USER:-postgres}"
  DB_SSLMODE="${DB_SSLMODE:-require}"
fi
DB_PASSWORD="${DB_PASSWORD}"

# Validate required credentials
if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Error: DB_PASSWORD environment variable is required!"
    echo ""
    echo "Please set DB_PASSWORD before running this script:"
    echo "  export DB_PASSWORD=your-database-password"
    exit 1
fi

# Template admin password (from Odoo config)
ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD:-admin}"

# PostgreSQL connection string with SSL
PGCONN="sslmode=$DB_SSLMODE host=$DB_HOST port=$DB_PORT user=$DB_USER dbname=postgres"

# MINIMAL ESSENTIAL MODULES - Additional modules can be installed on-demand per company
# Reduced from 140+ to ~40 modules for faster initialization (10-15 min vs 2+ hours)
# Core Odoo modules
CORE_MODULES="base,web,website,portal,base_automation,mail_group,rating"
# Core business modules
BUSINESS_MODULES="account,crm,sale,sale_crm,hr,hr_holidays,hr_attendance,hr_expense,hr_recruitment,hr_timesheet,hr_contract,project"
# Custom Safee modules
CUSTOM_MODULES="api_key_service,safee_webhooks,slack_error_notifications"
# Essential OCA modules (security, UX improvements, debranding)
OCA_ESSENTIAL="auditlog,auto_backup,auth_api_key,partner_firstname,password_security,base_name_search_improved,base_technical_user,base_address_extended,base_vat,disable_odoo_online,portal_odoo_debranding,web_responsive,web_m2x_options,web_notify"

ALL_MODULES="$CORE_MODULES,$BUSINESS_MODULES,$CUSTOM_MODULES,$OCA_ESSENTIAL"

# Removed bloat modules (install on-demand when needed):
# - Document management: sign_oca, dms*
# - Specialized reports: report_*, bi_sql_editor, sql_export*
# - Advanced mail: mail_tracking*, mail_debrand, mail_optional_autofollow, mail_activity_board
# - Advanced partner: partner_second_lastname, partner_statement, partner_multi_relation, etc.
# - Contract management: contract*
# - Advanced accounting: account_asset*, account_fiscal_year*, account_invoice_*, account_move_*, etc.
# - Advanced sales: sale_automatic_workflow, sale_exception, sale_global_discount, etc.
# - Advanced project: project_department, project_hr, project_key, etc.
# - Advanced HR: hr_contract_reference, hr_course, hr_employee_*, hr_timesheet_sheet, etc.
# - REST API framework: base_rest*, fastapi*, component*, pydantic, etc.
# - MIS reporting: mis_builder
# - Extra UI: web_timeline, web_environment_ribbon, web_dialog_size

echo "🔧 Initializing Odoo Template Database: $TEMPLATE_DB"
echo "=================================================="

# 1. Check if template database already exists
echo "📋 Checking if template database exists..."
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql "$PGCONN" -tAc "SELECT 1 FROM pg_database WHERE datname='$TEMPLATE_DB'")

if [ "$DB_EXISTS" = "1" ]; then
    # Handle add/remove modules for existing template
    if [ -n "$ADD_MODULES" ]; then
        echo "➕ Adding modules to existing template: $ADD_MODULES"
        TEMP_CONF="/tmp/odoo-add-$$.conf"
        cat > "$TEMP_CONF" << EOF
[options]
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_sslmode = $DB_SSLMODE
addons_path = /mnt/extra-addons
admin_passwd = $ADMIN_PASSWORD
EOF
        docker run --rm \
          --network=host \
          -v "$TEMP_CONF:/etc/odoo/odoo.conf:ro" \
          ghcr.io/safee-analytics/safee-odoo:18.0 \
          odoo \
            -d "$TEMPLATE_DB" \
            -i "$ADD_MODULES" \
            --stop-after-init \
            --without-demo=all
        rm -f "$TEMP_CONF"
        echo "✅ Modules added successfully!"
        exit 0
    fi

    if [ -n "$REMOVE_MODULES" ]; then
        echo "➖ Removing modules from existing template: $REMOVE_MODULES"
        TEMP_CONF="/tmp/odoo-remove-$$.conf"
        cat > "$TEMP_CONF" << EOF
[options]
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_sslmode = $DB_SSLMODE
addons_path = /mnt/extra-addons
admin_passwd = $ADMIN_PASSWORD
EOF
        docker run --rm \
          --network=host \
          -v "$TEMP_CONF:/etc/odoo/odoo.conf:ro" \
          ghcr.io/safee-analytics/safee-odoo:18.0 \
          odoo \
            -d "$TEMPLATE_DB" \
            -u "$REMOVE_MODULES" \
            --stop-after-init
        rm -f "$TEMP_CONF"
        echo "✅ Modules removed successfully!"
        exit 0
    fi

    if [ "$FORCE_RECREATE" = true ]; then
        echo "⚠️  Template database exists, dropping due to --force flag..."
        # Terminate connections
        PGPASSWORD=$DB_PASSWORD psql "$PGCONN" -c "
          SELECT pg_terminate_backend(pg_stat_activity.pid)
          FROM pg_stat_activity
          WHERE pg_stat_activity.datname = '$TEMPLATE_DB'
            AND pid <> pg_backend_pid();
        " || true
        # Drop database
        PGPASSWORD=$DB_PASSWORD psql "$PGCONN" -c "DROP DATABASE IF EXISTS $TEMPLATE_DB;"
        echo "✅ Dropped existing template database"
    else
        echo "✅ Template database '$TEMPLATE_DB' already exists - skipping initialization"
        echo "   (This is expected on redeployments)"
        echo ""
        echo "💡 Options:"
        echo "   --force                            # Drop and recreate"
        echo "   --add-modules \"mod1,mod2\"          # Install additional modules"
        echo "   --remove-modules \"mod1,mod2\"       # Uninstall modules"
        exit 0
    fi
fi

# 2. Create template database
echo "🏗️  Creating template database..."
PGPASSWORD=$DB_PASSWORD psql "$PGCONN" -c "CREATE DATABASE $TEMPLATE_DB;"

# 3. Initialize Odoo with all modules using custom image
# Note: ghcr.io/safee-analytics/safee-odoo:18.0 has Python dependencies and custom addons pre-installed
echo "📦 Installing Odoo modules (this may take 10-15 minutes)..."
echo "   Using image: ghcr.io/safee-analytics/safee-odoo:18.0"
echo "   Modules: $ALL_MODULES"

# Create temporary Odoo config
TEMP_CONF="/tmp/odoo-init-$$.conf"
cat > "$TEMP_CONF" << EOF
[options]
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_sslmode = $DB_SSLMODE
addons_path = /mnt/extra-addons
admin_passwd = $ADMIN_PASSWORD
EOF

docker run --rm \
  --network=host \
  -v "$TEMP_CONF:/etc/odoo/odoo.conf:ro" \
  ghcr.io/safee-analytics/safee-odoo:18.0 \
  odoo \
    -d "$TEMPLATE_DB" \
    -i "$ALL_MODULES" \
    --stop-after-init \
    --without-demo=all \
    --load-language=en_US

# Clean up temp config
rm -f "$TEMP_CONF"

# 4. Mark database as template (skip on managed DBs like Neon - requires superuser)
echo "🏷️  Template database ready for duplication..."
# Note: On Neon/managed PostgreSQL, we can't set datistemplate=TRUE (requires superuser)
# But we can still use CREATE DATABASE WITH TEMPLATE or pg_dump/restore for duplication
PGPASSWORD=$DB_PASSWORD psql "$PGCONN" -c "
  COMMENT ON DATABASE $TEMPLATE_DB IS 'Safee Odoo Template - Do not modify directly';
" || echo "⚠️  Note: Could not set database comment (non-critical)"

echo ""
echo "✅ Template database created successfully!"
echo "=================================================="
echo "Database: $TEMPLATE_DB"
echo "Admin login: admin"
echo "Admin password: $ADMIN_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: This is a template database."
echo "   - Do NOT modify it directly"
echo "   - Use duplicate-odoo-db.sh to create new company databases"
echo ""
