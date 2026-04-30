# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': "Project Enterprise HR",
    'summary': """Bridge module for project_enterprise and hr""",
    'description': """
Bridge module for project_enterprise and hr
    """,
    'category': 'Services/Project',
    'version': '1.0',
    'depends': ['project_enterprise', 'hr'],
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
    'data': [
        'data/todo_mail_alias.xml',
    ],
}
