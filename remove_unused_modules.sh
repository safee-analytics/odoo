#!/bin/bash
# Remove unused Odoo modules for Safee Analytics
# Keeps: Hisabiq (Accounting), Kanz (HR+Recruitment), Nisbah (CRM), Marketing, Scheduling

set -e

ODOO_ADDONS="/Users/mahmoudabdelhadi/github/safee/odoo/addons"

echo "🗑️  Removing unused Odoo modules for Safee Analytics..."
echo "⚠️  This will permanently delete modules not needed for your ERP"
echo ""

# Modules to remove - organized by category
REMOVE_MODULES=(
    # E-commerce & Online Store
    "website_sale"
    "website_sale_*"
    "sale_amazon"
    "website_payment"
    "website_payment_*"

    # Payment Processors (not needed for invoicing)
    "payment_paypal"
    "payment_stripe"
    "payment_authorize"
    "payment_adyen"
    "payment_alipay"
    "payment_asiapay"
    "payment_buckaroo"
    "payment_flutterwave"
    "payment_mercado_pago"
    "payment_mollie"
    "payment_ogone"
    "payment_payumoney"
    "payment_razorpay"
    "payment_sips"
    "payment_test"

    # Point of Sale & Restaurant
    "point_of_sale"
    "pos_*"

    # Manufacturing
    "mrp"
    "mrp_*"
    "quality"
    "quality_*"
    "plm"

    # Field Service & Maintenance
    "industry_fsm"
    "maintenance"
    "repair"

    # Helpdesk & Support
    "helpdesk"
    "helpdesk_*"

    # Live Chat
    "im_livechat"
    "im_support"

    # Knowledge Base & Wiki
    "knowledge"

    # E-learning
    "website_slides"
    "website_slides_*"
    "slides"
    "slides_*"

    # Events Management
    "event"
    "event_*"
    "website_event"
    "website_event_*"

    # Blog & Forum
    "website_blog"
    "website_forum"
    "forum"

    # Fleet Management
    "fleet"
    "fleet_*"

    # Lunch
    "lunch"

    # Studio (No-code customization)
    "web_studio"
    "web_studio_*"

    # IoT & Hardware
    "iot"
    "iot_*"
    "hw_*"

    # Barcode (Advanced inventory)
    "stock_barcode"

    # Data Recycle Bin
    "data_recycle"

    # Gamification
    "gamification"

    # To-Do (redundant with Project)
    "project_todo"

    # Themes (using custom frontend)
    "theme_*"

    # Test modules
    "test_*"

    # Delivery carriers
    "delivery"
    "delivery_*"

    # Website extras not needed
    "website_livechat"
    "website_twitter"
    "website_links"
    "website_mass_mailing"
    "website_customer"
    "website_form"
    "website_form_*"
    "website_partner"
    "website_rating"
    "website_crm"
    "website_crm_*"
)

echo "📋 Categories to remove:"
echo "  • E-commerce & Online Store"
echo "  • Payment Processors"
echo "  • Point of Sale & Restaurant"
echo "  • Manufacturing & Quality"
echo "  • Field Service & Maintenance"
echo "  • Helpdesk & Live Chat"
echo "  • Knowledge Base & E-learning"
echo "  • Events & Blog"
echo "  • Fleet, Lunch, IoT, Barcode"
echo ""
echo "✅ Keeping for Safee:"
echo "  • Hisabiq: Accounting, Invoicing, Sales, Purchase, Inventory, Subscriptions"
echo "  • Kanz: HR, Payroll, Time Off, Expenses, Timesheets, Recruitment (with website portal), Appraisal"
echo "  • Nisbah: CRM, Calendar, Contacts, Phone"
echo "  • Marketing: Email, SMS, Automation, Social"
echo "  • Scheduling: Planning, Appointments"
echo "  • Supporting: Project, Sign, Discuss, Surveys, Website (base for recruitment)"
echo ""

# Ask for confirmation
read -p "Continue with removal? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted - No changes made"
    exit 1
fi

echo ""
echo "Starting removal process..."
echo ""

# Count before
TOTAL_BEFORE=$(find "$ODOO_ADDONS" -maxdepth 1 -type d | wc -l)
SIZE_BEFORE=$(du -sh "$ODOO_ADDONS" 2>/dev/null | cut -f1)

echo "📊 Before: $TOTAL_BEFORE modules, $SIZE_BEFORE total size"
echo ""

# Remove each module
REMOVED_COUNT=0

for pattern in "${REMOVE_MODULES[@]}"; do
    # Use find to handle wildcards properly
    while IFS= read -r -d '' module_path; do
        if [ -d "$module_path" ]; then
            module_name=$(basename "$module_path")
            module_size=$(du -sh "$module_path" 2>/dev/null | cut -f1)
            echo "🗑️  Removing: $module_name ($module_size)"
            rm -rf "$module_path"
            ((REMOVED_COUNT++))
        fi
    done < <(find "$ODOO_ADDONS" -maxdepth 1 -type d -name "$pattern" -print0 2>/dev/null)
done

# Count after
TOTAL_AFTER=$(find "$ODOO_ADDONS" -maxdepth 1 -type d | wc -l)
SIZE_AFTER=$(du -sh "$ODOO_ADDONS" 2>/dev/null | cut -f1)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cleanup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Summary:"
echo "  Removed: $REMOVED_COUNT modules"
echo "  Before:  $TOTAL_BEFORE modules ($SIZE_BEFORE)"
echo "  After:   $TOTAL_AFTER modules ($SIZE_AFTER)"
echo ""
echo "🎯 Remaining modules optimized for:"
echo "  ✓ Accounting & Finance (Hisabiq)"
echo "  ✓ HR & Recruitment with web portal (Kanz)"
echo "  ✓ CRM & Sales (Nisbah)"
echo "  ✓ Marketing Automation"
echo "  ✓ Scheduling & Planning"
echo ""
echo "📝 Next steps:"
echo "  1. Rebuild Docker image: docker build -t safee-odoo:latest ."
echo "  2. Check remaining modules: ls $ODOO_ADDONS | wc -l"
echo "  3. Expected image size reduction: ~200-300MB"
echo ""
