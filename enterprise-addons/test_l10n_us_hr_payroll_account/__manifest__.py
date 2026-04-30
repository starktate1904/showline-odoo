# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Test US Payroll',
    'countries': ['us'],
    'category': 'Human Resources',
    'summary': 'Test US Payroll',
    'depends': [
        'l10n_us_hr_payroll',
        'l10n_us_hr_payroll_account',
    ],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
    'post_init_hook': '_generate_payslips',
}
