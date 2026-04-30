# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for CRM",
    'version': '1.0',
    'category': 'Productivity/Dashboard',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'crm_enterprise'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['crm_enterprise'],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
