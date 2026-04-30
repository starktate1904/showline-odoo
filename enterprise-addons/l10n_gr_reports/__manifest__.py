# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Greece - Accounting Reports',
    'version': '1.0',
    'description': """
Accounting reports for Greece
================================

    """,
    'category': 'Accounting/Localizations/Reporting',
    'depends': [
        'l10n_gr',
        'account_reports',
    ],
    'data': [
        'data/account_return_data.xml',
        'data/balance_sheet-gr.xml',
        'data/profit_and_loss-gr.xml',
        'data/ec_sales_list_report-gr.xml',
    ],
    'post_init_hook': '_l10n_gr_reports_post_init',
    'installable': True,
    'auto_install': ['l10n_gr', 'account_reports'],
    'website': 'https://dev.erpsys.top/app/accounting',
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
