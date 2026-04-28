from odoo import models, fields, api


class HavanoPayslip(models.Model):
    _name = 'havano.payslip'
    _description = 'Employee Payslip'
    _order = 'date_from desc, employee_id'

    name = fields.Char('Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date('Period From', required=True, default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date('Period To', required=True, default=lambda self: fields.Date.today())
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='employee_id.currency_id')
    
    # Salary Data (snapshot at time of creation)
    total_earnings = fields.Monetary(string='Total Earnings', currency_field='currency_id')
    total_deductions = fields.Monetary(string='Total Deductions', currency_field='currency_id')
    net_salary = fields.Monetary(string='Net Salary', currency_field='currency_id')
    taxable_income = fields.Monetary(string='Taxable Income', currency_field='currency_id')
    total_allowable_deductions = fields.Monetary(string='Allowable Deductions', currency_field='currency_id')
    
    # Secondary currency
    secondary_currency_id = fields.Many2one('res.currency', related='employee_id.secondary_currency_id')
    secondary_total_earnings = fields.Monetary(string='Total Earnings (Sec)', currency_field='secondary_currency_id')
    secondary_total_deductions = fields.Monetary(string='Total Deductions (Sec)', currency_field='secondary_currency_id')
    secondary_net_salary = fields.Monetary(string='Net Salary (Sec)', currency_field='secondary_currency_id')
    secondary_taxable_income = fields.Monetary(string='Taxable Income (Sec)', currency_field='secondary_currency_id')
    secondary_allowable_deductions = fields.Monetary(string='Allowable Deductions (Sec)', currency_field='secondary_currency_id')
    
    # Lines
    payslip_earning_ids = fields.One2many('havano.payslip.earning', 'payslip_id', string='Earnings')
    payslip_deduction_ids = fields.One2many('havano.payslip.deduction', 'payslip_id', string='Deductions')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], string='Status', default='draft')
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_name(self):
        for slip in self:
            if slip.employee_id and slip.date_from:
                slip.name = f'Payslip - {slip.employee_id.name} ({slip.date_from} to {slip.date_to})'
            else:
                slip.name = 'New Payslip'
    
    def action_generate_lines(self):
        """Pull current earnings/deductions from employee"""
        self.ensure_one()
        employee = self.employee_id
        
        # Clear old lines
        self.payslip_earning_ids.unlink()
        self.payslip_deduction_ids.unlink()
        
        # Create earning lines
        for earning in employee.earnings_ids:
            self.env['havano.payslip.earning'].create({
                'payslip_id': self.id,
                'component_id': earning.component_id.id,
                'amount': earning.amount,
                'secondary_amount': earning.secondary_amount,
            })
        
        # Create deduction lines
        for deduction in employee.deduction_ids:
            self.env['havano.payslip.deduction'].create({
                'payslip_id': self.id,
                'component_id': deduction.component_id.id,
                'amount': deduction.amount,
                'secondary_amount': deduction.secondary_amount,
            })
        
        # Update totals
        self.write({
            'total_earnings': employee.total_earnings,
            'total_deductions': employee.total_deductions,
            'net_salary': employee.net_salary,
            'taxable_income': employee.taxable_income,
            'total_allowable_deductions': employee.total_allowable_deductions,
            'secondary_total_earnings': employee.secondary_total_earnings,
            'secondary_total_deductions': employee.secondary_total_deductions,
            'secondary_net_salary': employee.secondary_net_salary,
            'secondary_taxable_income': employee.secondary_taxable_income,
            'secondary_allowable_deductions': employee.secondary_allowable_deductions,
        })
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_paid(self):
        self.write({'state': 'paid'})
    
    def action_draft(self):
        self.write({'state': 'draft'})


class HavanoPayslipEarning(models.Model):
    _name = 'havano.payslip.earning'
    _description = 'Payslip Earning Line'
    
    payslip_id = fields.Many2one('havano.payslip', string='Payslip', ondelete='cascade')
    component_id = fields.Many2one('havano.salary.component', string='Component')
    amount = fields.Monetary(string='Amount', currency_field='payslip_currency_id')
    secondary_amount = fields.Monetary(string='Amount (Sec)', currency_field='payslip_secondary_currency_id')
    payslip_currency_id = fields.Many2one('res.currency', related='payslip_id.currency_id')
    payslip_secondary_currency_id = fields.Many2one('res.currency', related='payslip_id.secondary_currency_id')


class HavanoPayslipDeduction(models.Model):
    _name = 'havano.payslip.deduction'
    _description = 'Payslip Deduction Line'
    
    payslip_id = fields.Many2one('havano.payslip', string='Payslip', ondelete='cascade')
    component_id = fields.Many2one('havano.salary.component', string='Component')
    amount = fields.Monetary(string='Amount', currency_field='payslip_currency_id')
    secondary_amount = fields.Monetary(string='Amount (Sec)', currency_field='payslip_secondary_currency_id')
    payslip_currency_id = fields.Many2one('res.currency', related='payslip_id.currency_id')
    payslip_secondary_currency_id = fields.Many2one('res.currency', related='payslip_id.secondary_currency_id')