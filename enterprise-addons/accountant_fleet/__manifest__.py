# Part of Erp. See LICENSE file for full copyright and licensing details.
{
    'name': 'Accounting - Fleet',
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'description': """
Accounting Fleet Bridge
""",
    'website': 'https://dev.erpsys.top/app/accounting',
    'depends': ['accountant', 'fleet'],
    'data': [
        'views/accountant_fleet_menuitem.xml',
        'data/account_return_check_template.xml',
    ],
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'OEEL-1',

}
