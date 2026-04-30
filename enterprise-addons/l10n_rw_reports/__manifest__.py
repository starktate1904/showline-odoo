{
    'name': 'Rwanda - Accounting Reports',
    'version': '1.0',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
Accounting reports for Rwanda
    """,
    'depends': [
        'l10n_rw', 'account_reports'
    ],
    'data': [
        "data/account_return_data.xml",
        "data/balance_sheet.xml",
        "data/profit_loss.xml",
    ],
    'installable': True,
    'auto_install': True,
    'website': 'https://dev.erpsys.top/app/accounting',
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
