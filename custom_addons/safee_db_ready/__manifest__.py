# -*- coding: utf-8 -*-
{
    'name': 'Safee Database Ready Signal',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Signals when database is ready for use',
    'description': """
        Sends a webhook notification when the database initialization is complete.
        This module should be installed first after database creation.
    """,
    'author': 'Safee Analytics',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
