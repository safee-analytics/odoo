{
    'name': 'REST API',
    'version': '19.0.1.0.0',
    'category': 'API',
    'license': 'LGPL-3',
    'summary': 'RESTful API for external frontend applications',
    'description': """
        Provides REST API endpoints with JWT authentication for:
        - CRUD operations on any model
        - Custom business logic
        - File uploads/downloads
        - Authentication & Authorization
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
