{
    'name': 'Havano Payroll - Zimbabwe Localisation',
    'version': '19.0.1.0.0',
    'category': 'Payroll',
    'summary': 'Zimbabwe PAYE, NSSA, AIDS Levy, ZIMRA Tax Tables for Odoo Payroll',
    'description': """
        Havano Payroll - Zimbabwe Payroll Localisation for Odoo 19
        
        Features:
        - Seeds Zimbabwe salary rule categories (Taxable Income, Allowable Deductions, etc.)
        - Seeds salary rules with correct sequence numbers (Basic Salary, NSSA, PAYE, AIDS Levy, etc.)
        - ZIMRA Tax Tables for USD and ZWG (daily, weekly, fortnightly, monthly)
        - Tax Credits: Medical Aid (50%), Blind, Elderly (65+), Disabled
        - AIDS Levy calculation (3% of PAYE)
        - Multi-currency support
        - Extends hr.employee with is_blind, is_disabled fields
        - Configurable via Settings
    """,
    'author': 'Havano',
    'website': 'https://www.havano.com',
    'depends': ['hr_payroll', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/res_currency_data.xml',
        'data/salary_rule_categories.xml',
        'data/salary_rules.xml',
        'data/zimra_tax_table_data.xml',
        'views/zimra_tax_table_views.xml',
        'views/payroll_settings_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}