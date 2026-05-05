from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ZimraTaxTable(models.Model):
    _name = 'zimra.tax.table'
    _description = 'ZIMRA Tax Table'
    _order = 'currency_id, frequency, min_income'

    name = fields.Char(string='Description', compute='_compute_name', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    frequency = fields.Selection([
        ('daily', 'Daily'), ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'), ('monthly', 'Monthly'),
    ], string='Pay Frequency', required=True, default='monthly')
    min_income = fields.Monetary(string='Income From', required=True, currency_field='currency_id')
    max_income = fields.Monetary(string='Income To', required=True, default=0.0, currency_field='currency_id')
    rate = fields.Float(string='Tax Rate (%)', required=True)
    deduction = fields.Monetary(string='Deduction', currency_field='currency_id', default=0.0)
    effective_date = fields.Date(string='Effective Date', required=True, default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('currency_id', 'frequency', 'min_income', 'max_income')
    def _compute_name(self):
        for r in self:
            if r.max_income > 0:
                r.name = f'{r.currency_id.name} {r.frequency}: {r.min_income:.2f} - {r.max_income:.2f}'
            else:
                r.name = f'{r.currency_id.name} {r.frequency}: {r.min_income:.2f}+'

    @api.constrains('rate')
    def _check_rate(self):
        for r in self:
            if r.rate < 0 or r.rate > 100:
                raise ValidationError('Tax rate must be between 0 and 100!')
