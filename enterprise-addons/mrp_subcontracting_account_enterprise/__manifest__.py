# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting - MRP Subcontracting',
    'version': '1.0',
    'category': 'Supply Chain/Manufacturing',
    'summary': 'Add Subcontracting information in Cost Analysis Reports and Production Analysis',
    'description': """
Add Subcontracting information in Cost Analysis Report and The Production Analysis
""",
    'website': 'https://dev.erpsys.top/app/manufacturing',
    'depends': ['mrp_account_enterprise', 'mrp_subcontracting'],
    'data': [
        'report/mrp_report_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
