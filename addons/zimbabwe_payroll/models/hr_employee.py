from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_blind = fields.Boolean(string='Blind', default=False)
    is_disabled = fields.Boolean(string='Disabled (Tax Credit)', default=False)

    @api.depends('birthday')
    def _compute_is_over_65(self):
        for emp in self:
            emp.is_over_65 = False
            if emp.birthday:
                today = fields.Date.today()
                age = today.year - emp.birthday.year
                if (today.month, today.day) < (emp.birthday.month, emp.birthday.day):
                    age -= 1
                emp.is_over_65 = age >= 65

    is_over_65 = fields.Boolean(string='Over 65', compute='_compute_is_over_65', store=True)

    zimbabwe_latest_payslip_id = fields.Many2one(
        'hr.payslip',
        string='Latest payslip',
        compute='_compute_zimbabwe_latest_payslip_breakdown',
        groups='hr_payroll.group_hr_payroll_user',
    )
    zimbabwe_latest_net_wage = fields.Monetary(
        string='Net pay (latest payslip)',
        currency_field='currency_id',
        compute='_compute_zimbabwe_latest_payslip_breakdown',
        groups='hr_payroll.group_hr_payroll_user',
    )
    zimbabwe_latest_earning_line_ids = fields.Many2many(
        comodel_name='hr.payslip.line',
        relation='hr_employee_zw_latest_earn_rel',
        column1='employee_id',
        column2='line_id',
        compute='_compute_zimbabwe_latest_payslip_breakdown',
        string='Latest payslip (earnings)',
        groups='hr_payroll.group_hr_payroll_user',
    )
    zimbabwe_latest_deduction_line_ids = fields.Many2many(
        comodel_name='hr.payslip.line',
        relation='hr_employee_zw_latest_ded_rel',
        column1='employee_id',
        column2='line_id',
        compute='_compute_zimbabwe_latest_payslip_breakdown',
        string='Latest payslip (deductions)',
        groups='hr_payroll.group_hr_payroll_user',
    )

    @api.depends(
        'slip_ids',
        'slip_ids.state',
        'slip_ids.date_to',
        'slip_ids.line_ids',
        'slip_ids.line_ids.total',
        'slip_ids.line_ids.quantity',
        'slip_ids.line_ids.amount',
        'slip_ids.line_ids.rate',
        'slip_ids.net_wage',
    )
    def _compute_zimbabwe_latest_payslip_breakdown(self):
        for emp in self:
            slips = emp.slip_ids.filtered(lambda s: s.state in ('validated', 'paid'))
            if not slips:
                emp.zimbabwe_latest_payslip_id = False
                emp.zimbabwe_latest_net_wage = 0.0
                emp.zimbabwe_latest_earning_line_ids = self.env['hr.payslip.line']
                emp.zimbabwe_latest_deduction_line_ids = self.env['hr.payslip.line']
                continue
            slip = max(slips, key=lambda s: (s.date_to or s.date_from, s.id))
            emp.zimbabwe_latest_payslip_id = slip
            emp.zimbabwe_latest_net_wage = slip.net_wage
            rounding = slip.currency_id.rounding or emp.company_id.currency_id.rounding or 0.01

            def _is_visible_line(line):
                if not line.appears_on_payslip or line.salary_rule_id.title:
                    return False
                return not float_is_zero(line.total, precision_rounding=rounding)

            visible = slip.line_ids.filtered(_is_visible_line)
            emp.zimbabwe_latest_earning_line_ids = visible.filtered(lambda l: l.total > 0)
            emp.zimbabwe_latest_deduction_line_ids = visible.filtered(lambda l: l.total < 0)
