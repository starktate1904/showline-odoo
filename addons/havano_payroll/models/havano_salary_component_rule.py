from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HavanoSalaryComponentRule(models.Model):
    _name = 'havano.salary.component.rule'
    _description = 'Salary Component Calculation Rule'
    _order = 'sequence, id'

    name = fields.Char('Rule Name', required=True)
    component_id = fields.Many2one(
        'havano.salary.component',
        string='Salary Component',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer('Sequence', default=10)

    rule_type = fields.Selection([
        ('tax_table', 'Tax Table Lookup'),
        ('percentage', 'Percentage Based'),
        ('fixed', 'Fixed Amount'),
    ], string='Rule Type', required=True, default='tax_table')

    percentage = fields.Float('Percentage (%)', digits=(5, 2))
    percentage_base = fields.Selection([
        ('basic_salary', 'Basic Salary'),
        ('gross_salary', 'Gross Salary'),
        ('taxable_income', 'Taxable Income'),
        ('paye_amount', 'PAYE Amount'),
    ], string='Percentage Base')

    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Pay Frequency', default='monthly')

    tax_credit_component_ids = fields.Many2many(
        'havano.salary.component',
        'rule_tax_credit_rel',
        'rule_id',
        'component_id',
        string='Tax Credit Components',
        domain="[('component_type', '=', 'earning')]",
        help="These earnings components reduce the final tax amount"
    )

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')

    def calculate_amount(self, employee, currency):
        """Calculate the amount for this rule"""
        self.ensure_one()

        if self.rule_type == 'percentage':
            return self._calc_percentage(employee, currency)
        elif self.rule_type == 'fixed':
            return self._calc_fixed(employee, currency)
        elif self.rule_type == 'tax_table':
            return self._calc_tax_table(employee, currency)
        return 0.0

    def _calc_tax_table(self, employee, currency):
        """Calculate PAYE using Taxable Income"""
        is_primary = currency.id == employee.currency_id.id
        taxable_income = employee.taxable_income if is_primary else employee.secondary_taxable_income

        tax_table = self.env['zimra.tax.table'].search([
            ('currency_id', '=', currency.id),
            ('frequency', '=', self.frequency),
            ('min_income', '<=', taxable_income),
            '|', ('max_income', '>=', taxable_income), ('max_income', '=', 0),
            ('active', '=', True),
        ], limit=1, order='effective_date desc, min_income desc')

        if not tax_table:
            return 0.0

        tax = max((taxable_income * tax_table.rate / 100.0) - tax_table.deduction, 0)
        
        # Use the pre-computed total_tax_credits from the employee model
        total_credits = employee.total_tax_credits if is_primary else employee.secondary_total_tax_credits

        return max(tax - total_credits, 0)

    def _calc_percentage(self, employee, currency):
        """Calculate percentage-based amount"""
        is_primary = currency.id == employee.currency_id.id

        if self.percentage_base == 'basic_salary':
            basic_earning = employee.earnings_ids.filtered(lambda l: l.component_id.code == 'BS')
            base = basic_earning.amount if is_primary else basic_earning.secondary_amount if basic_earning else 0
        elif self.percentage_base == 'gross_salary':
            base = employee.total_earnings if is_primary else employee.secondary_total_earnings
        elif self.percentage_base == 'taxable_income':
            base = employee.taxable_income if is_primary else employee.secondary_taxable_income
        elif self.percentage_base == 'paye_amount':
            paye_line = employee.deduction_ids.filtered(lambda l: l.component_id.code == 'PAYE')
            base = paye_line.amount if is_primary else paye_line.secondary_amount if paye_line else 0
        else:
            base = 0

        return base * self.percentage / 100.0

    def _calc_fixed(self, employee, currency):
        return 0.0


class HavanoSalaryComponent(models.Model):
    _inherit = 'havano.salary.component'

    rule_ids = fields.One2many(
        'havano.salary.component.rule',
        'component_id',
        string='Calculation Rules'
    )