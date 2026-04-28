from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    currency_id = fields.Many2one('res.currency', string='Primary Currency', default=lambda self: self.env.company.currency_id.id)

    secondary_currency_id = fields.Many2one(
        'res.currency', 
        string='Secondary Currency',
        compute='_compute_secondary_currency',
        store=True,
        readonly=False
    )
    
    working_hours_per_week = fields.Float(string='Working Hours/Week', default=40.0)
    leave_days = fields.Float(string='Leave Days (Annual)', default=24.0)
    
    earnings_ids = fields.One2many('havano.earning.line', 'employee_id', string='Earnings')
    deduction_ids = fields.One2many('havano.deduction.line', 'employee_id', string='Deductions')
    
    # Computed Totals
    total_earnings = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    total_deductions = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    net_salary = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    
    secondary_total_earnings = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    secondary_total_deductions = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    secondary_net_salary = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')
    
    other_earnings_primary = fields.Monetary(compute='_compute_totals', store=True, currency_field='currency_id')
    other_earnings_secondary = fields.Monetary(compute='_compute_totals', store=True, currency_field='secondary_currency_id')

    # NEW FIELDS
    taxable_income = fields.Monetary(
        'Taxable Income (Primary)', 
        compute='_compute_taxable_income', 
        store=True, 
        currency_field='currency_id',
        help="Basic Salary - NSSA Employee Contribution"
    )
    
    secondary_taxable_income = fields.Monetary(
        'Taxable Income (Secondary)', 
        compute='_compute_taxable_income', 
        store=True, 
        currency_field='secondary_currency_id'
    )
    
    total_allowable_deductions = fields.Monetary(
        'Total Allowable Deductions (Primary)',
        compute='_compute_taxable_income',
        store=True,
        currency_field='currency_id',
        help="NSSA Employee Contribution"
    )
    
    secondary_allowable_deductions = fields.Monetary(
        'Total Allowable Deductions (Secondary)',
        compute='_compute_taxable_income',
        store=True,
        currency_field='secondary_currency_id'
    )
    
    nssa_employer_contribution = fields.Monetary(
        'NSSA Employer Contribution (Primary)',
        compute='_compute_taxable_income',
        store=True,
        currency_field='currency_id',
        help="For reporting - NOT deducted from employee"
    )
    
    secondary_nssa_employer = fields.Monetary(
        'NSSA Employer Contribution (Secondary)',
        compute='_compute_taxable_income',
        store=True,
        currency_field='secondary_currency_id'
    )

    # Leave Management Relations
    leave_allocation_ids = fields.One2many(
        'havano.leave.allocation', 
        'employee_id', 
        string='Leave Allocations'
    )

    leave_request_ids = fields.One2many(
        'havano.leave.request', 
        'employee_id', 
        string='Leave Requests'
    )

    encashment_ids = fields.One2many(
        'havano.leave.encashment', 
        'employee_id', 
        string='Encashments'
    )

    @api.model
    def _cron_accrue_leave(self):
        """Accrue 2.5 leave days monthly for all active employees"""
        days_per_month = float(self.env['ir.config_parameter'].sudo().get_param(
            'havano_payroll.annual_leave_days_per_month', 2.5
        ))
        max_days = float(self.env['ir.config_parameter'].sudo().get_param(
            'havano_payroll.max_annual_leave_days', 30.0
        ))
        
        employees = self.search([('active', '=', True)])
        for emp in employees:
            # Add leave days but cap at max
            emp.leave_days = min(emp.leave_days + days_per_month, max_days)
        
        _logger.info(f'Leave accrued for {len(employees)} employees: {days_per_month} days each')


    @api.depends('currency_id')
    def _compute_secondary_currency(self):
        secondary_currency_id = self.env['ir.config_parameter'].sudo().get_param('havano_payroll.secondary_currency_id')
        multi_currency = self.env['ir.config_parameter'].sudo().get_param('havano_payroll.multi_currency')
        for emp in self:
            if multi_currency and secondary_currency_id:
                emp.secondary_currency_id = int(secondary_currency_id)
            elif not emp.secondary_currency_id:
                emp.secondary_currency_id = False

    @api.depends(
        'earnings_ids.amount', 'earnings_ids.secondary_amount',
        'deduction_ids.amount', 'deduction_ids.secondary_amount'
    )
    def _compute_totals(self):
        for emp in self:
            emp.total_earnings = sum(emp.earnings_ids.mapped('amount'))
            emp.total_deductions = sum(emp.deduction_ids.mapped('amount'))
            emp.net_salary = emp.total_earnings - emp.total_deductions
            
            basic_salary = sum(emp.earnings_ids.filtered(lambda l: l.component_id.code == 'BS').mapped('amount'))
            emp.other_earnings_primary = emp.total_earnings - basic_salary
            
            emp.secondary_total_earnings = sum(emp.earnings_ids.mapped('secondary_amount'))
            emp.secondary_total_deductions = sum(emp.deduction_ids.mapped('secondary_amount'))
            emp.secondary_net_salary = emp.secondary_total_earnings - emp.secondary_total_deductions
            
            basic_salary_sec = sum(emp.earnings_ids.filtered(lambda l: l.component_id.code == 'BS').mapped('secondary_amount'))
            emp.other_earnings_secondary = emp.secondary_total_earnings - basic_salary_sec

    @api.depends('earnings_ids.amount', 'earnings_ids.secondary_amount')
    def _compute_taxable_income(self):
        """Calculate taxable income using categories:
        Taxable Income = Sum of (Taxable Income components) - Sum of (Allowable Deductions)
        """
        for emp in self:
            # Primary currency
            taxable_earnings = sum(
                line.amount for line in emp.earnings_ids
                if line.component_id.category_id.affects_taxable_income
            )
            allowable_deds = sum(
                line.amount for line in emp.deduction_ids
                if line.component_id.category_id.is_allowable_deduction
            )
            emp.taxable_income = max(taxable_earnings - allowable_deds, 0)
            emp.total_allowable_deductions = allowable_deds

            # Secondary currency
            taxable_earnings_sec = sum(
                line.secondary_amount for line in emp.earnings_ids
                if line.component_id.category_id.affects_taxable_income
            )
            allowable_deds_sec = sum(
                line.secondary_amount for line in emp.deduction_ids
                if line.component_id.category_id.is_allowable_deduction
            )
            emp.secondary_taxable_income = max(taxable_earnings_sec - allowable_deds_sec, 0)
            emp.secondary_allowable_deductions = allowable_deds_sec


    def action_calculate_component(self, component_code):
        self.ensure_one()
        
        _logger = logging.getLogger(__name__)
        _logger.info("=" * 50)
        _logger.info(f"ACTION CALCULATE: {component_code} for {self.name}")
        
        component = self.env['havano.salary.component'].search([('code', '=', component_code)], limit=1)
        if not component:
            _logger.info("Component not found!")
            return False
        
        # For NSSA, use the already-computed allowable deductions (from settings with ceiling)
        if component_code == 'NSSA':
            _logger.info(f"Using computed NSSA values:")
            _logger.info(f"  total_allowable_deductions = {self.total_allowable_deductions}")
            _logger.info(f"  secondary_allowable_deductions = {self.secondary_allowable_deductions}")
            primary_amount = self.total_allowable_deductions
            secondary_amount = self.secondary_allowable_deductions
        elif component.rule_ids:
            rule = component.rule_ids.filtered(lambda r: r.active)[:1]
            if not rule:
                _logger.info("No active rule found!")
                return False
            _logger.info(f"Using rule: {rule.name}")
            primary_amount = rule.calculate_amount(self, self.currency_id)
            secondary_amount = 0.0
            if self.secondary_currency_id:
                secondary_amount = rule.calculate_amount(self, self.secondary_currency_id)
        else:
            _logger.info("No rules found for component!")
            return False
        
        _logger.info(f"Final amounts: Primary={primary_amount}, Secondary={secondary_amount}")
        
        deduction_line = self.deduction_ids.filtered(lambda l: l.component_id.code == component_code)
        _logger.info(f"Existing deduction line: {deduction_line}")
        
        if deduction_line:
            deduction_line.write({'amount': primary_amount, 'secondary_amount': secondary_amount})
            _logger.info(f"Updated existing line")
        else:
            self.env['havano.deduction.line'].create({
                'employee_id': self.id,
                'component_id': component.id,
                'amount': primary_amount,
                'secondary_amount': secondary_amount,
                'currency_id': self.currency_id.id,
                'secondary_currency_id': self.secondary_currency_id.id if self.secondary_currency_id else False,
            })
            _logger.info(f"Created new line")
        
        _logger.info("=" * 50)
        return True

  

    def action_calculate_all_deductions(self):
        self.ensure_one()
        # Order: NSSA first, then PAYE (uses taxable income), then AIDS Levy
        calc_order = ['NSSA', 'PAYE', 'AIDS']
        for code in calc_order:
            self.action_calculate_component(code)
        return True