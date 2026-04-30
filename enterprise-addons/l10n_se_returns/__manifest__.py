{
    'name': 'Sweden - Accounting Returns',
    'version': '1.0',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
Accounting returns for Sweden
    """,
    'depends': ['l10n_se_reports'],
    'data': [
        'data/account_return_data.xml',
        'security/ir.model.access.csv',
        'wizard/ec_sales_list_submission_wizard.xml',
        'wizard/vat_return_submission_wizard.xml',
    ],
    'installable': True,
    'auto_install': True,
    'author': 'Erp S.A.',
    'website': 'https://dev.erpsys.top/app/accounting',
    'license': 'OEEL-1',
}
