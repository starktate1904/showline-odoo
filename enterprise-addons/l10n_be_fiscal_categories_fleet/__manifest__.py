# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgium - Disallowed Expenses Fleet',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'description': """
Disallowed Expenses Fleet Data for Belgium
    """,
    'depends': [
        'account_fiscal_categories_fleet',
        'l10n_be_fiscal_categories',
        'l10n_be_hr_payroll_fleet',
    ],
    'data': [
        'data/account_fiscal_categories.xml',
        'views/fleet_vehicle_views.xml',
    ],
    'installable': True,
    'website': 'https://dev.erpsys.top/app/accounting',
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
