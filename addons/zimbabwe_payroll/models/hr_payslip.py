from odoo import models
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_payrun_id_from_context_or_record(self):
        run_id = (
            self.env.context.get("default_payslip_run_id")
            or self.env.context.get("search_default_payslip_run_id")
        )
        if not run_id and self:
            run_id = self[0].payslip_run_id.id
        if not run_id and self.env.context.get("active_model") == "hr.payslip.run":
            run_id = self.env.context.get("active_id")
        return run_id

    def action_open_run_salary_breakdown_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{run_id}/salary_breakdown",
            "target": "new",
        }

    def action_open_run_salary_summary_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/zimbabwe_payroll/payrun/{run_id}/salary_summary",
            "target": "new",
        }

    def action_open_run_nssa_report_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'nssa',
                'pay_run_id': run_id,
            }
        }

    def action_open_run_zimra_itf_report_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'zimra_itf',
                'pay_run_id': run_id,
            }
        }

    def action_open_run_nec_report_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'nec',
                'pay_run_id': run_id,
            }
        }

    def action_open_run_zimdef_report_pdf(self):
        run_id = self._get_payrun_id_from_context_or_record()
        if not run_id:
            raise UserError("Open this action from a Pay Run Payslips screen.")
        return {
            'type': 'ir.actions.client',
            'tag': 'zimbabwe_payroll.export_modal',
            'params': {
                'report_type': 'zimdef',
                'pay_run_id': run_id,
            }
        }
