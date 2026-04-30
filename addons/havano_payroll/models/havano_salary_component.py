from odoo import models, fields


class HavanoSalaryComponent(models.Model):
    _name = 'havano.salary.component'
    _description = 'Salary Component'
    _order = 'component_type, sequence, name'

    name = fields.Char('Component Name', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)

    component_type = fields.Selection([
        ('earning', 'Earning'),
        ('deduction', 'Deduction')
    ], string='Type', required=True, default='earning')

    # NEW: Link to category
    category_id = fields.Many2one(
        'havano.salary.category',
        string='Category',
        required=True,
        help="Determines how this component affects tax calculations"
    )

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Component code must be unique!')
    ]