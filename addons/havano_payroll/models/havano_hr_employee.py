from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_blind = fields.Boolean(
        string='Blind',
        default=False,
        help='Check if the employee is blind (entitled to ZIMRA tax credit)'
    )

    is_disabled = fields.Boolean(
        string='Disabled',
        default=False,
        help='Check if the employee is disabled (entitled to ZIMRA tax credit)'
    )

    @api.depends('birthday')
    def _compute_is_over_65(self):
        """Compute if employee is over 65 years old"""
        for emp in self:
            emp.is_over_65 = False
            if emp.birthday:
                today = fields.Date.today()
                age = today.year - emp.birthday.year
                if (today.month, today.day) < (emp.birthday.month, emp.birthday.day):
                    age -= 1
                emp.is_over_65 = age >= 65

    is_over_65 = fields.Boolean(
        string='Over 65',
        compute='_compute_is_over_65',
        store=True,
        help='Computed: True if employee is 65 years or older (entitled to ZIMRA tax credit)'
    )