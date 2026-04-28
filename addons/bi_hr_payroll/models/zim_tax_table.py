# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ZimTaxTable(models.Model):
    _name = 'zim.tax.table'
    _description = 'ZIMRA Tax Table'
    _order = 'frequency, currency_id, min_income'
    
    name = fields.Char('Description', compute='_compute_name', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', 
                                  default=lambda self: self.env.ref('base.USD'),
                                  required=True)
    
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], required=True, default='monthly')
    
    min_income = fields.Float('Income From', required=True)
    max_income = fields.Float('Income To', help='Leave empty (0) for "and above"')
    
    rate = fields.Float('Tax Rate (%)', required=True)
    deduction = fields.Float('Deduction', default=0.0)
    
    effective_date = fields.Date('Effective Date', required=True, 
                                 default=fields.Date.today)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('unique_bracket', 
         'unique(currency_id, frequency, min_income, effective_date, company_id)',
         'A tax bracket with these parameters already exists!'),
    ]
    
    @api.depends('currency_id', 'frequency', 'min_income', 'max_income')
    def _compute_name(self):
        for record in self:
            currency = record.currency_id.name
            freq = dict(self._fields['frequency'].selection).get(record.frequency, '')
            if record.max_income:
                record.name = f'{currency} {freq}: {record.min_income:,.2f} - {record.max_income:,.2f}'
            else:
                record.name = f'{currency} {freq}: {record.min_income:,.2f} and above'
    
    @api.constrains('min_income', 'max_income')
    def _check_brackets(self):
        for record in self:
            if record.max_income and record.min_income >= record.max_income:
                raise ValidationError('Minimum income must be less than maximum income!')
    
    @api.constrains('rate')
    def _check_rate(self):
        for record in self:
            if record.rate < 0 or record.rate > 100:
                raise ValidationError('Tax rate must be between 0 and 100!')
    
    def get_tax(self, income):
        """Calculate tax for given income"""
        self.ensure_one()
        if income <= 0:
            return 0.0
        tax = (income * self.rate / 100.0) - self.deduction
        return max(tax, 0.0)