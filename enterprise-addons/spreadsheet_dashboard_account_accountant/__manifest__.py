# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for accounting",
    'version': '1.0',
    'category': 'Productivity/Dashboard',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'accountant'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['accountant'],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
