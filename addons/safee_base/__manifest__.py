# -*- coding: utf-8 -*-
{
    'name': 'Safee Analytics Base',
    'version': '1.0.0',
    'category': 'Hidden',
    'summary': 'Base module that installs all required Safee Analytics modules',
    'description': """
Safee Analytics Base Installation
==================================

This module automatically installs all required business modules for Safee Analytics:
- Sales Management (Quotations, Sales Orders, Invoicing)
- CRM (Lead & Opportunity Management)
- Accounting (Full accounting & invoicing)
- Project Management (Projects & Tasks)
- HR (Employee Management)
- Calendar (Events & Meetings)

This module is automatically installed on database creation.
    """,
    'author': 'Safee Analytics',
    'website': 'https://safee.local',
    'depends': [
        'base',
        'sale_management',
        'crm',
        'account',
        'project',
        'hr',
        'calendar',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
