from odoo import models, fields

class HrEmployeeSalaryLine(models.Model):
    _name = 'hr.employee.salary.line'
    _description = 'Employee Salary Line'

    employee_id = fields.Many2one('hr.employee', required=True)
    name = fields.Char(required=True)
    amount = fields.Float(required=True)

    type = fields.Selection([
        ('earning', 'Earning'),
        ('deduction', 'Deduction')
    ], required=True)

    active = fields.Boolean(default=True)