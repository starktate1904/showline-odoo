from odoo import models, fields, api

class ZimbabwePayrollReportWizard(models.TransientModel):
    _name = "zimbabwe.payroll.report.wizard"
    _description = "Zimbabwe Payroll Report Wizard"

    pay_run_id = fields.Many2one("hr.payslip.run", string="Pay Run", required=True)
    report_type = fields.Selection([
        ('salary_breakdown', 'Salary Breakdown'),
        ('salary_summary', 'Salary Summary'),
        ('detailed_breakdown', 'Detailed Salary Breakdown'),
        ('summary_breakdown', 'Summary Salary Breakdown'),
        ('nssa', 'NSSA Report'),
        ('nssa_p4', 'NSSA P4 Report'),
        ('zimra_itf', 'ZIMRA ITF Report'),
        ('nec', 'NEC Report'),
        ('zimdef', 'ZIMDEF Report')
    ], string="Report Type", required=True)
    
    format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel')
    ], string="Format", default='pdf', required=True)

    def action_generate(self):
        self.ensure_one()
        url = f"/zimbabwe_payroll/export/{self.report_type}/{self.pay_run_id.id}?format={self.format}"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
