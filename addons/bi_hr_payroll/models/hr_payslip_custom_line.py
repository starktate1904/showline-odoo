from odoo import models, fields,api


class HrPayslipCustomLine(models.Model):
    _name = 'hr.payslip.custom.line'
    _description = 'Payslip Custom Line'

    payslip_id = fields.Many2one('hr.payslip', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    amount = fields.Float(required=True)

    type = fields.Selection([
        ('earning', 'Earning'),
        ('deduction', 'Deduction')
    ], required=True)

    active = fields.Boolean(default=True)
   