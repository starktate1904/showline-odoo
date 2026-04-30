{
    'name': 'Havano Payroll',
    'version': '19.0.1.0.0',
    'category': 'Payroll',
    'summary': 'Lightweight Payroll Management for Employees',
    'description': """
        Havano Payroll - Simple Employee Payroll System
        
        Features:
        - Salary Components (Earnings & Deductions)
        - Employee Earnings & Deductions Management
        - Automatic Net Salary Calculation
        - Multi-Currency Support
        - Leave Management & Encashment
        - NSSA, PAYE, AIDS Levy Calculations
        - ZIMRA Tax Tables
        - Payslip Generation & Printing
    """,
    'author': 'havano',
    'website': 'https://www.havano.com',
    'depends': ['base', 'hr', 'hr_holidays'],
    'data': [
    'security/ir.model.access.csv',
    'data/res_currency_data.xml',
    'data/havano_salary_category_data.xml', 
    'data/havano_salary_component_data.xml',
    'data/havano_salary_component_rule_data.xml',
    'data/havano_leave_type_data.xml',
    'data/havano_zimra_tax_table_data.xml',
    'views/havano_salary_category_views.xml', 
    'views/havano_salary_component_views.xml',
    'views/havano_salary_component_rule_views.xml',
    'views/havano_leave_type_views.xml',
    'views/havano_leave_request_views.xml',
    'views/havano_leave_encashment_views.xml',
    'views/havano_payroll_settings_views.xml',
    'views/havano_zimra_tax_table_views.xml',
    
    'views/havano_hr_employee_views.xml',
    'views/havano_payslip_views.xml',
],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}