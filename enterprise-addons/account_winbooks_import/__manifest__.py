# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': "Account Winbooks Import",
    'summary': """Import Data From Winbooks""",
    'description': """
Import Data From Winbooks
    """,
    'category': 'Accounting/Accounting',
    'depends': ['account_accountant', 'base_vat', 'account_base_import'],
    'external_dependencies': {
        'python': ['dbfread'],
        'apt': {
            'dbfread': 'python3-dbfread',
        },
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_import_summary_views.xml',
        'wizard/import_wizard_views.xml',
    ],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'account_winbooks_import/static/src/xml/**/*',
        ],
    },
}
