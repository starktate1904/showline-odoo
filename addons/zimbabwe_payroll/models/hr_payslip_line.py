from odoo import api, models


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    @api.onchange("amount", "quantity", "rate")
    def _onchange_manual_amount_fields(self):
        for line in self:
            line.total = (line.quantity or 0.0) * (line.amount or 0.0) * ((line.rate or 0.0) / 100.0)
