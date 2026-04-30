# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Switzerland - Accounting Reports',
    'version': '1.1',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
Accounting reports for Switzerland
    """,
    'depends': [
        'l10n_ch', 'account_reports'
    ],
    'data': [
        'data/account_financial_html_report_data.xml',
        'data/account_return_data.xml',
    ],
    'installable': True,
    'auto_install': ['l10n_ch', 'account_reports'],
    'website': 'https://dev.erpsys.top/app/accounting',
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
