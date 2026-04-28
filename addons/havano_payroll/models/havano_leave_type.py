from odoo import models, fields


class HavanoLeaveType(models.Model):
    _name = 'havano.leave.type'
    _description = 'Leave Type Configuration'
    _order = 'sequence, name'
    
    name = fields.Char('Leave Type', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)
    
    leave_category = fields.Selection([
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('study', 'Study Leave'),
        ('family', 'Family Responsibility'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ], string='Category', required=True)
    
    accrual_enabled = fields.Boolean('Enable Accrual', default=False)
    accrual_days = fields.Float('Days Per Accrual', default=2.5)
    accrual_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Accrual Frequency', default='monthly')
    
    max_days = fields.Float('Maximum Days', default=30.0)
    gender_restriction = fields.Selection([
        ('none', 'All Employees'),
        ('female', 'Female Only'),
        ('male', 'Male Only'),
    ], string='Gender Restriction', default='none')
    
    allow_carry_over = fields.Boolean('Allow Carry Over', default=False)
    max_carry_over_days = fields.Float('Max Carry Over Days', default=0)
    paid_leave = fields.Boolean('Paid Leave', default=True)
    allow_encashment = fields.Boolean('Allow Encashment', default=False)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Leave type code must be unique!')
    ]