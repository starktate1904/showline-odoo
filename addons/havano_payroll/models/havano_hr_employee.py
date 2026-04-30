from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    currency_id = fields.Many2one('res.currency', string='Primary Currency', default=lambda self: self.env.company.currency_id.id)
    secondary_currency_id = fields.Many2one('res.currency', string='Secondary Currency', compute='_compute_secondary_currency', store=True, readonly=False)
    
    working_hours_per_week = fields.Float(string='Working Hours/Week', default=40.0)
    
    earnings_ids = fields.One2many('havano.earning.line', 'employee_id', string='Earnings')
    deduction_ids = fields.One2many('havano.deduction.line', 'employee_id', string='Deductions')
    
    # Computed Totals
    total_earnings = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    total_deductions = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    net_salary = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    secondary_total_earnings = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    secondary_total_deductions = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    secondary_net_salary = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    
    # Tax Fields
    taxable_income = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='currency_id')
    secondary_taxable_income = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='secondary_currency_id')
    total_allowable_deductions = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='currency_id')
    secondary_allowable_deductions = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='secondary_currency_id')
    total_tax_credits = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='currency_id')
    secondary_total_tax_credits = fields.Monetary(compute='_compute_taxable_income', store=True, currency_field='secondary_currency_id')
    nssa_employer_contribution = fields.Monetary(compute='_compute_employer_contributions', store=True, currency_field='currency_id')
    secondary_nssa_employer = fields.Monetary(compute='_compute_employer_contributions', store=True, currency_field='secondary_currency_id')
    nec_employer_contribution = fields.Monetary(compute='_compute_employer_contributions', store=True, currency_field='currency_id')
    zimdef_employer_contribution = fields.Monetary(compute='_compute_employer_contributions', store=True, currency_field='currency_id')

    # Only keep Encashment (Odoo doesn't have this)
    encashment_ids = fields.One2many('havano.leave.encashment', 'employee_id', string='Encashments')
    
    # Leave days (for display)
    leave_days = fields.Float(string='Leave Days (Annual)', default=24.0)

    # Medical Aid fields
    medical_aid_contribution = fields.Monetary(compute='_compute_medical_aid_info', store=True, currency_field='currency_id')
    medical_aid_tax_credit = fields.Monetary(compute='_compute_medical_aid_info', store=True, currency_field='currency_id')
    secondary_medical_aid_contribution = fields.Monetary(compute='_compute_medical_aid_info', store=True, currency_field='secondary_currency_id')
    secondary_medical_aid_tax_credit = fields.Monetary(compute='_compute_medical_aid_info', store=True, currency_field='secondary_currency_id')
    has_medical_aid = fields.Boolean(compute='_compute_medical_aid_info', store=True)

    @api.depends('deduction_ids.amount', 'deduction_ids.secondary_amount', 'deduction_ids.component_id.category_id')
    def _compute_medical_aid_info(self):
        for emp in self:
            med_primary = sum(d.amount for d in emp.deduction_ids if d.component_id.category_id.code == 'MED_CAT')
            med_secondary = sum(d.secondary_amount for d in emp.deduction_ids if d.component_id.category_id.code == 'MED_CAT')
            credit_pct = float(self.env['ir.config_parameter'].sudo().get_param('havano_payroll.medical_aid_tax_credit_pct', 50.0))
            emp.has_medical_aid = med_primary > 0 or med_secondary > 0
            emp.medical_aid_contribution = med_primary
            emp.medical_aid_tax_credit = med_primary * credit_pct / 100.0
            emp.secondary_medical_aid_contribution = med_secondary
            emp.secondary_medical_aid_tax_credit = med_secondary * credit_pct / 100.0

    def _get_param(self, key, default=0.0):
        return float(self.env['ir.config_parameter'].sudo().get_param(key, default))
    
    def _get_bool_param(self, key, default=False):
        return self.env['ir.config_parameter'].sudo().get_param(key, str(default)).lower() == 'true'
    
    def _get_basic_salary(self, is_primary=True):
        if is_primary:
            return sum(self.earnings_ids.filtered(lambda l: l.component_id.code == 'BS').mapped('amount'))
        return sum(self.earnings_ids.filtered(lambda l: l.component_id.code == 'BS').mapped('secondary_amount'))

    @api.depends('currency_id')
    def _compute_secondary_currency(self):
        secondary_id = self.env['ir.config_parameter'].sudo().get_param('havano_payroll.secondary_currency_id')
        multi = self._get_bool_param('havano_payroll.multi_currency')
        for emp in self:
            if multi and secondary_id:
                emp.secondary_currency_id = int(secondary_id)

    @api.depends('earnings_ids.amount', 'earnings_ids.secondary_amount', 'deduction_ids.amount', 'deduction_ids.secondary_amount')
    def _compute_totals(self):
        for emp in self:
            emp.total_earnings = sum(emp.earnings_ids.mapped('amount'))
            emp.total_deductions = sum(emp.deduction_ids.mapped('amount'))
            emp.net_salary = emp.total_earnings - emp.total_deductions
            emp.secondary_total_earnings = sum(emp.earnings_ids.mapped('secondary_amount'))
            emp.secondary_total_deductions = sum(emp.deduction_ids.mapped('secondary_amount'))
            emp.secondary_net_salary = emp.secondary_total_earnings - emp.secondary_total_deductions

    @api.depends('earnings_ids.amount', 'earnings_ids.secondary_amount', 'deduction_ids.amount', 'deduction_ids.secondary_amount')
    def _compute_taxable_income(self):
        for emp in self:
            gross_taxable = sum(l.amount for l in emp.earnings_ids if l.component_id.category_id.affects_taxable_income)
            allowable = sum(l.amount for l in emp.deduction_ids if l.component_id.category_id.is_allowable_deduction)
            emp.total_allowable_deductions = allowable
            emp.taxable_income = max(gross_taxable - allowable, 0)
            tax_credits = 0.0
            for line in emp.deduction_ids:
                cat = line.component_id.category_id
                if cat.is_tax_credit and cat.tax_credit_percentage > 0:
                    tax_credits += line.amount * cat.tax_credit_percentage / 100.0
            for line in emp.earnings_ids:
                if line.component_id.category_id.is_tax_credit:
                    tax_credits += line.amount
            emp.total_tax_credits = tax_credits
            gross_taxable_sec = sum(l.secondary_amount for l in emp.earnings_ids if l.component_id.category_id.affects_taxable_income)
            allowable_sec = sum(l.secondary_amount for l in emp.deduction_ids if l.component_id.category_id.is_allowable_deduction)
            emp.secondary_allowable_deductions = allowable_sec
            emp.secondary_taxable_income = max(gross_taxable_sec - allowable_sec, 0)
            tax_credits_sec = 0.0
            for line in emp.deduction_ids:
                cat = line.component_id.category_id
                if cat.is_tax_credit and cat.tax_credit_percentage > 0:
                    tax_credits_sec += line.secondary_amount * cat.tax_credit_percentage / 100.0
            for line in emp.earnings_ids:
                if line.component_id.category_id.is_tax_credit:
                    tax_credits_sec += line.secondary_amount
            emp.secondary_total_tax_credits = tax_credits_sec

    @api.depends('earnings_ids.amount', 'earnings_ids.secondary_amount')
    def _compute_employer_contributions(self):
        for emp in self:
            basic_p = emp._get_basic_salary(True)
            basic_s = emp._get_basic_salary(False)
            nssa_emp_pct = emp._get_param('havano_payroll.nssa_employer_pct', 4.5)
            nssa_ceiling_p = emp._get_param('havano_payroll.nssa_ceiling', 700.0)
            insurable = min(basic_p, nssa_ceiling_p) if nssa_ceiling_p > 0 else basic_p
            emp.nssa_employer_contribution = insurable * nssa_emp_pct / 100.0
            nssa_emp_sec = emp._get_param('havano_payroll.nssa_employer_pct_secondary', nssa_emp_pct)
            nssa_ceiling_s = emp._get_param('havano_payroll.nssa_ceiling_secondary', 28000.0)
            insurable_s = min(basic_s, nssa_ceiling_s) if nssa_ceiling_s > 0 else basic_s
            emp.secondary_nssa_employer = insurable_s * nssa_emp_sec / 100.0
            if emp._get_bool_param('havano_payroll.nec_enabled'):
                nec_ceiling = emp._get_param('havano_payroll.nec_ceiling', 0)
                insurable_nec = min(basic_p, nec_ceiling) if nec_ceiling > 0 else basic_p
                emp.nec_employer_contribution = insurable_nec * emp._get_param('havano_payroll.nec_employee_pct', 1.5) / 100.0
            if emp._get_bool_param('havano_payroll.zimdef_enabled'):
                emp.zimdef_employer_contribution = basic_p * emp._get_param('havano_payroll.zimdef_employer_pct', 1.0) / 100.0

    def _calculate_nssa(self):
        self.ensure_one()
        nssa_pct = self._get_param('havano_payroll.nssa_employee_pct', 0)
        if nssa_pct <= 0: return None, None
        basic_p = self._get_basic_salary(True)
        basic_s = self._get_basic_salary(False)
        ceiling_p = self._get_param('havano_payroll.nssa_ceiling', 0)
        ceiling_s = self._get_param('havano_payroll.nssa_ceiling_secondary', 0)
        pct_s = self._get_param('havano_payroll.nssa_employee_pct_secondary', nssa_pct)
        ins_p = min(basic_p, ceiling_p) if ceiling_p > 0 else basic_p
        ins_s = min(basic_s, ceiling_s) if ceiling_s > 0 else basic_s
        return ins_p * nssa_pct / 100.0, ins_s * pct_s / 100.0

    def _calculate_nec(self):
        self.ensure_one()
        if not self._get_bool_param('havano_payroll.nec_enabled'): return None, None
        nec_pct = self._get_param('havano_payroll.nec_employee_pct', 0)
        if nec_pct <= 0: return None, None
        basic_p = self._get_basic_salary(True)
        basic_s = self._get_basic_salary(False)
        ceiling_p = self._get_param('havano_payroll.nec_ceiling', 0)
        ceiling_s = self._get_param('havano_payroll.nec_ceiling_secondary', 0)
        pct_s = self._get_param('havano_payroll.nec_employee_pct_secondary', nec_pct)
        ins_p = min(basic_p, ceiling_p) if ceiling_p > 0 else basic_p
        ins_s = min(basic_s, ceiling_s) if ceiling_s > 0 else basic_s
        return ins_p * nec_pct / 100.0, ins_s * pct_s / 100.0

    def action_calculate_component(self, component_code):
        self.ensure_one()
        component = self.env['havano.salary.component'].search([('code', '=', component_code)], limit=1)
        if not component: return False
        primary_amount = 0.0
        secondary_amount = 0.0
        if component_code == 'NSSA':
            result = self._calculate_nssa()
            if result[0] is None: return False
            primary_amount, secondary_amount = result
        elif component_code == 'NEC':
            result = self._calculate_nec()
            if result[0] is None: return False
            primary_amount, secondary_amount = result
        elif component.rule_ids:
            rule = component.rule_ids.filtered(lambda r: r.active)[:1]
            if not rule: return False
            primary_amount = rule.calculate_amount(self, self.currency_id)
            if self.secondary_currency_id:
                secondary_amount = rule.calculate_amount(self, self.secondary_currency_id)
        else:
            return False
        deduction_line = self.deduction_ids.filtered(lambda l: l.component_id.code == component_code)
        if deduction_line:
            deduction_line.write({'amount': primary_amount, 'secondary_amount': secondary_amount})
        else:
            self.env['havano.deduction.line'].create({
                'employee_id': self.id, 'component_id': component.id,
                'amount': primary_amount, 'secondary_amount': secondary_amount,
                'currency_id': self.currency_id.id,
                'secondary_currency_id': self.secondary_currency_id.id if self.secondary_currency_id else False,
            })
        return True

    def action_calculate_all_deductions(self):
        self.ensure_one()
        self.action_calculate_component('NSSA')
        self.action_calculate_component('NEC')
        self.action_calculate_component('PAYE')
        self.action_calculate_component('AIDS')
        return True
