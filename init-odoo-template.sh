#!/bin/bash
set -e

#######################################
# Initialize Odoo Template Database
# This creates odoo_template with all base modules and custom addons pre-installed
# New company databases will be duplicated from this template
#######################################

# Configuration
TEMPLATE_DB="odoo_template"

# Read from environment (set by Odoo server's .env file)
# When running via Terraform, these come from docker-compose .env
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"

# Template admin password (from Odoo config)
ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD:-admin}"

# Modules to install (must match database.service.ts modulesToInstall array)
# This ensures template has ALL modules that companies will need
ALL_MODULES="base,web,account,crm,sale,sale_crm,hr,hr_holidays,hr_attendance,hr_expense,hr_recruitment,hr_timesheet,hr_presence,hr_recruitment_skills,hr_work_entry,hr_hourly_cost,project,project_timesheet_holidays,base_automation,mail_group,rating,base_address_extended,base_vat,portal,base_view_inheritance_extension,api_key_service,safee_webhooks,slack_error_notifications,auditlog,auto_backup,base_name_search_improved,base_technical_user,database_cleanup,module_auto_update,scheduler_error_mailer,queue_job,queue_job_cron,dms,dms_auto_classification,dms_field,report_xlsx,report_xlsx_helper,report_csv,report_qr,report_xml,report_py3o,report_qweb_parameter,report_qweb_encrypt,report_qweb_pdf_watermark,bi_sql_editor,sql_export,sql_export_excel,mail_tracking,mail_tracking_mass_mailing,mail_debrand,mail_optional_autofollow,mail_activity_board,partner_firstname,partner_second_lastname,partner_statement,partner_multi_relation,partner_identification,partner_company_group,partner_external_map,contract,contract_sale,contract_payment_mode,contract_variable_quantity,date_range,account_asset_management,account_asset_number,account_financial_report,account_fiscal_year,account_fiscal_year_auto_create,base_global_discount,account_global_discount,account_invoice_refund_link,account_invoice_section_sale_order,account_invoice_supplier_ref_unique,account_invoice_triple_discount,account_move_line_stock_info,account_move_line_purchase_info,account_move_line_sale_info,account_move_template,account_netting,account_spread_cost_revenue,account_tax_balance,sale_automatic_workflow,sale_exception,sale_global_discount,sale_order_invoicing_grouping_criteria,sale_order_type,sale_product_set,sale_quotation_number,sale_stock_picking_invoicing,sale_tier_validation,project_department,project_hr,project_key,project_task_code,project_task_parent_completion_blocking,project_template,project_timeline,hr_contract_reference,hr_course,hr_department_code,hr_employee_age,hr_employee_calendar_planning,hr_employee_firstname,hr_employee_id,hr_employee_medical_examination,hr_employee_relative,hr_employee_service,hr_expense_analytic_tag,hr_timesheet_analytic_tag,web_widget_x2many_2d_matrix,hr_timesheet_sheet,mis_builder,web_responsive,web_m2x_options,web_notify,web_timeline,web_environment_ribbon,web_dialog_size,component,component_event,extendable,pydantic,base_rest,base_rest_pydantic,base_rest_auth_api_key,rest_log,endpoint_route_handler,fastapi,fastapi_auth_api_key,auth_api_key,password_security,base_user_show_email,disable_odoo_online,portal_odoo_debranding"

echo "🔧 Initializing Odoo Template Database: $TEMPLATE_DB"
echo "=================================================="

# 1. Check if template database already exists
echo "📋 Checking if template database exists..."
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$TEMPLATE_DB'")

if [ "$DB_EXISTS" = "1" ]; then
    echo "✅ Template database '$TEMPLATE_DB' already exists - skipping initialization"
    echo "   (This is expected on redeployments)"
    echo ""
    echo "💡 To recreate the template, manually drop it first:"
    echo "   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c \"DROP DATABASE $TEMPLATE_DB;\""
    exit 0
fi

# 2. Create template database
echo "🏗️  Creating template database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $TEMPLATE_DB;"

# 3. Initialize Odoo with all modules using custom image
# Note: safee-odoo:18.0 has Python dependencies and custom addons pre-installed
echo "📦 Installing Odoo modules (this may take 10-15 minutes)..."
echo "   Using image: safee-odoo:18.0"
echo "   Modules: $ALL_MODULES"
docker run --rm \
  -e HOST=$DB_HOST \
  -e PORT=$DB_PORT \
  -e USER=$DB_USER \
  -e PASSWORD=$DB_PASSWORD \
  -e ADMIN_PASSWD=$ADMIN_PASSWORD \
  -v /opt/odoo/addons:/mnt/extra-addons \
  safee-odoo:18.0 \
  odoo --db_host=\$HOST --db_port=\$PORT --db_user=\$USER --db_password=\$PASSWORD -d $TEMPLATE_DB -i $ALL_MODULES --stop-after-init --without-demo=all --load-language=en_US

# 4. Mark database as template
echo "🏷️  Marking database as template..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "
  UPDATE pg_database SET datistemplate = TRUE WHERE datname = '$TEMPLATE_DB';
  COMMENT ON DATABASE $TEMPLATE_DB IS 'Safee Odoo Template - Do not modify directly';
"

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
