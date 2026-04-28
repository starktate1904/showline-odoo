from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HavanoLeaveEncashment(models.Model):
    _name = 'havano.leave.encashment'
    _description = 'Leave Encashment Request'
    _order = 'date_requested desc'
    
    name = fields.Char('Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_requested = fields.Date('Request Date', default=fields.Date.today, required=True)
    
    # Encashment Details
    number_of_days = fields.Float('Number of Days', required=True)
    daily_rate = fields.Monetary('Daily Rate', compute='_compute_amounts', store=True, currency_field='currency_id')
    total_amount = fields.Monetary('Total Amount', compute='_compute_amounts', store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    
    # Secondary Currency
    secondary_daily_rate = fields.Monetary('Daily Rate (Sec)', compute='_compute_amounts', store=True, currency_field='secondary_currency_id')
    secondary_total_amount = fields.Monetary('Total Amount (Sec)', compute='_compute_amounts', store=True, currency_field='secondary_currency_id')
    secondary_currency_id = fields.Many2one('res.currency', related='employee_id.secondary_currency_id')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft')
    
    payslip_id = fields.Many2one('havano.payslip', string='Payslip', readonly=True)
    notes = fields.Text('Notes')
    
    @api.depends('employee_id', 'date_requested')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id:
                rec.name = f'Encashment - {rec.employee_id.name} ({rec.date_requested})'
            else:
                rec.name = 'New Encashment'
    
    @api.depends('employee_id', 'number_of_days')
    def _compute_amounts(self):
        for rec in self:
            if rec.employee_id and rec.number_of_days > 0:
                # Get working days from settings
                working_days = float(self.env['ir.config_parameter'].sudo().get_param(
                    'havano_payroll.working_days_per_month', 22.0
                ))
                
                # Get basic salary from earnings
                basic_salary = sum(rec.employee_id.earnings_ids.filtered(
                    lambda l: l.component_id.code == 'BS'
                ).mapped('amount'))
                
                basic_salary_sec = sum(rec.employee_id.earnings_ids.filtered(
                    lambda l: l.component_id.code == 'BS'
                ).mapped('secondary_amount'))
                
                # Daily rate
                rec.daily_rate = basic_salary / working_days if working_days > 0 else 0
                rec.total_amount = rec.daily_rate * rec.number_of_days
                
                # Secondary
                rec.secondary_daily_rate = basic_salary_sec / working_days if working_days > 0 else 0
                rec.secondary_total_amount = rec.secondary_daily_rate * rec.number_of_days
            else:
                rec.daily_rate = 0
                rec.total_amount = 0
                rec.secondary_daily_rate = 0
                rec.secondary_total_amount = 0
    
    @api.constrains('number_of_days')
    def _check_days(self):
        for rec in self:
            if rec.number_of_days <= 0:
                raise ValidationError('Number of days must be greater than zero!')
    
    def action_request(self):
        self.write({'state': 'requested'})
    
    def action_approve(self):
        self.write({'state': 'approved'})
    
    def action_paid(self):
        self.write({'state': 'paid'})
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_draft(self):
        self.write({'state': 'draft'})