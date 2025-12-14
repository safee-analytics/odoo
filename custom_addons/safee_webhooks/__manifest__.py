# -*- coding: utf-8 -*-
{
    'name': 'Safee Webhooks Integration',
    'version': '1.0.0',
    'category': 'Integration',
    'summary': 'Webhook integration between Odoo and Safee Analytics',
    'description': """
        Safee Webhooks Integration
        ===========================

        Sends webhooks to Safee Analytics when:
        - HR records change (employees, departments, contracts, leave requests)
        - CRM records change (leads, opportunities, contacts)
        - Accounting records change (invoices, payments, journal entries)

        Features:
        - HMAC-SHA256 signature verification
        - Automatic sync on create/write/unlink
        - Configurable webhook endpoints
        - Support for all major Odoo modules
    """,
    'author': 'Safee Analytics',
    'website': 'https://safee.analytics',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'crm',
        'account',
        'hr_holidays',
    ],
    'data': [
        'data/default_config.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
