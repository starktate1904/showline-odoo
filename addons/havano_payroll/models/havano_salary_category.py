from odoo import models, fields


class HavanoSalaryCategory(models.Model):
    _name = 'havano.salary.category'
    _description = 'Salary Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)

    category_type = fields.Selection([
        ('taxable_income', 'Taxable Income'),
        ('non_taxable_income', 'Non-Taxable Income'),
        ('allowable_deduction', 'Allowable Deduction'),
        ('non_allowable_deduction', 'Non-Allowable Deduction'),
        ('tax_credit', 'Tax Credit'),
        ('paye', 'PAYE'),
        ('aids_levy', 'AIDS Levy'),
        ('nssa', 'NSSA'),
        ('nec', 'NEC'),
        ('zimdef', 'ZIMDEF'),
        ('medical_aid', 'Medical Aid'),
        ('funeral_policy', 'Funeral Policy'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    ], string='Category Type', required=True)

    # Tax behavior
    affects_taxable_income = fields.Boolean('Affects Taxable Income', default=False,
        help="If True, amounts in this category are added/subtracted from taxable income")
    is_allowable_deduction = fields.Boolean('Is Allowable Deduction', default=False,
        help="If True, reduces taxable income before PAYE calculation")
    is_tax_credit = fields.Boolean('Is Tax Credit', default=False,
        help="If True, reduces the final PAYE amount")
    tax_credit_percentage = fields.Float('Tax Credit %', default=0,
        help="Percentage of this component that becomes a tax credit (e.g., 50 for Medical Aid)")

    # Calculation order (lower = calculated first)
    calculation_order = fields.Integer('Calculation Order', default=50,
        help="Order in which components of this category are calculated. Lower = first.")

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    description = fields.Text('Description')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Category code must be unique!')
    ]