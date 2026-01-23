# -*- coding: utf-8 -*-
{
    'name': 'Safee Document Styles',
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': 'Custom document styling fields for Safee integration',
    'description': """
        Safee Document Styles
        =====================

        Extends res.company with document styling fields:
        - Primary/secondary/accent colors
        - Font families and sizes
        - Logo position
        - Show/hide options for various document elements

        These fields are used by QWeb report templates to style:
        - Invoices
        - Quotes
        - Payslips
        - Contracts
        - Other accounting/HR documents
    """,
    'author': 'Safee Analytics',
    'website': 'https://safee.analytics',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/res_company_views.xml',
        'views/report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
