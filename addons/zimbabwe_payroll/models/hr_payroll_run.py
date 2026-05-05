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
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'nssa',
                'pay_run_id': self.id,
            }
        }

    def action_open_zimra_itf_report_pdf(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'zimra_itf',
                'pay_run_id': self.id,
            }
        }

    def action_open_nec_report_pdf(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'nec',
                'pay_run_id': self.id,
            }
        }

    def action_open_zimdef_report_pdf(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'zimdef',
                'pay_run_id': self.id,
            }
        }
