# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count', groups="bi_hr_payroll.group_hr_payroll_user")
    address_home_id = fields.Many2one('res.partner', 'Address',groups="hr.group_hr_user",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
     # Zimbabwe-specific fields
    tin_number = fields.Char('TIN Number', help='Tax Identification Number')
    nssa_number = fields.Char('NSSA Number')
    ec_number = fields.Char('EC Number')
    national_id = fields.Char('National ID')
    
    # Tax credit flags
    is_blind = fields.Boolean('Blind', help='Qualifies for blind person tax credit ($75)')
    is_elderly = fields.Boolean('Elderly (65+)', help='Qualifies for elderly tax credit ($75)')
    is_disabled = fields.Boolean('Disabled', help='Qualifies for disabled person tax credit ($75)')
    
    # Medical aid
    medical_aid_contributor = fields.Boolean('Medical Aid Contributor')
    medical_aid_amount = fields.Float('Medical Aid Contribution')
    
    # Computed tax credits
    total_tax_credits = fields.Float('Total Tax Credits', compute='_compute_tax_credits', store=True)
    
    @api.depends('is_blind', 'is_elderly', 'is_disabled', 'medical_aid_contributor', 'medical_aid_amount')
    def _compute_tax_credits(self):
        for emp in self:
            credits = 0.0
            if emp.is_blind:
                credits += 75.0
            if emp.is_elderly:
                credits += 75.0
            if emp.is_disabled:
                credits += 75.0
            if emp.medical_aid_contributor and emp.medical_aid_amount > 0:
                credits += emp.medical_aid_amount * 0.5  # 50% of medical aid
            emp.total_tax_credits = credits

    

    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)
