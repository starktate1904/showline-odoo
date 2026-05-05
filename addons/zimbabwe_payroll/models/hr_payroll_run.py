from odoo import models


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    def action_open_salary_breakdown_pdf(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{self.id}/salary_breakdown",
            "target": "new",
        }

    def action_open_salary_summary_pdf(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{self.id}/salary_summary",
            "target": "new",
        }

    def action_open_nssa_report_pdf(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{self.id}/nssa_report",
            "target": "new",
        }

    def action_open_zimra_itf_report_pdf(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{self.id}/zimra_itf_report",
            "target": "new",
        }
