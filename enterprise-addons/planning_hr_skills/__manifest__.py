# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Planning - Skills',
    'summary': 'Planning Skills',
    'description': """
Search planning slots by skill
    """,
    'category': 'Human Resources/Planning',
    'version': '1.0',
    'depends': ['planning', 'hr_skills'],
    'auto_install': True,
    'data': [
        'views/planning_slot_views.xml',
    ],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
