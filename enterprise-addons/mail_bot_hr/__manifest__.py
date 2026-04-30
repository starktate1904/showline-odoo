# -*- coding: utf-8 -*-
{
    'name': "ErpBot - HR",
    'summary': """Bridge module between hr and mailbot.""",
    'description': """This module adds the ErpBot state and notifications in the user form modified by hr.""",
    'website': "https://dev.erpsys.top/app/discuss",
    'category': 'Productivity/Discuss',
    'version': '1.0',
    'depends': ['mail_bot', 'hr'],
    'installable': True,
    'auto_install': True,
    'data': [
        'views/res_users_views.xml',
    ],
    'author': 'Erp S.A.',
    'license': 'LGPL-3',
}
