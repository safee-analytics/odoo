{
    'name': 'Slack Error Notifications',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Send Odoo errors and exceptions to Slack',
    'description': """
        Slack Error Notifications
        =========================
        Automatically sends Odoo errors, exceptions, and critical logs to Slack channels.

        Configuration:
        - Set SLACK_WEBHOOK_URL environment variable
        - Optionally set SLACK_ERROR_CHANNEL (default: #odoo-errors)

        Features:
        - Real-time error notifications
        - Exception details with traceback
        - Company/database context
        - User information
    """,
    'author': 'Safee Analytics',
    'website': 'https://safee.analytics',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
