from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HavanoDeductionLine(models.Model):
    _name = 'havano.deduction.line'
    _description = 'Employee Deduction Line'
    _order = 'sequence, id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    component_id = fields.Many2one('havano.salary.component', string='Component', domain="[('component_type', '=', 'deduction')]", required=True)
    sequence = fields.Integer('Sequence', default=10)
    amount = fields.Monetary(string='Amount', required=True, default=0.0, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id, required=True)
    secondary_amount = fields.Monetary(string='Secondary Amount', currency_field='secondary_currency_id')
    
    secondary_currency_id = fields.Many2one(
        'res.currency', 
        string='Secondary Currency',
        compute='_compute_secondary_currency',
        store=True,
        readonly=False
    )
    
    # NEW: Display category in list view
    component_category = fields.Char(
        string='Category', 
        related='component_id.category_id.name',
        readonly=True
    )

    @api.depends('currency_id')
    def _compute_secondary_currency(self):
        secondary_currency_id = self.env['ir.config_parameter'].sudo().get_param('havano_payroll.secondary_currency_id')
        multi_currency = self.env['ir.config_parameter'].sudo().get_param('havano_payroll.multi_currency')
        for line in self:
            if multi_currency and secondary_currency_id:
                line.secondary_currency_id = int(secondary_currency_id)

    @api.constrains('employee_id', 'component_id')
    def _check_unique_component(self):
        restricted_codes = ['PAYE', 'AIDS', 'NSSA']
        for line in self:
            if line.component_id.code in restricted_codes:
                existing = self.search([
                    ('employee_id', '=', line.employee_id.id),
                    ('component_id.code', '=', line.component_id.code),
                    ('id', '!=', line.id)
                ])
                if existing:
                    raise ValidationError(
                        f'Deduction "{line.component_id.name}" can only be added once per employee! '
                        f'Use the Calculate button to update the amount.'
                    )