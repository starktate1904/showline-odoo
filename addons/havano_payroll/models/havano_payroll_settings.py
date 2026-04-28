from odoo import models, fields


class HavanoPayrollSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    multi_currency = fields.Boolean(
        string='Enable Multi-Currency',
        config_parameter='havano_payroll.multi_currency'
    )
    
    base_currency_id = fields.Many2one(
        'res.currency',
        string='Base Currency',
        config_parameter='havano_payroll.base_currency_id',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    
    secondary_currency_id = fields.Many2one(
        'res.currency',
        string='Secondary Currency',
        config_parameter='havano_payroll.secondary_currency_id'
    )
    
    # NSSA - Primary Currency
    nssa_employee_pct = fields.Float(
        string='NSSA Employee Contribution (%)',
        config_parameter='havano_payroll.nssa_employee_pct',
        default=4.5
    )
    
    nssa_employer_pct = fields.Float(
        string='NSSA Employer Contribution (%)',
        config_parameter='havano_payroll.nssa_employer_pct',
        default=4.5
    )
    
    nssa_ceiling = fields.Float(
        string='NSSA Ceiling (Primary Currency)',
        config_parameter='havano_payroll.nssa_ceiling',
        default=700.00
    )
    
    # NSSA - Secondary Currency
    nssa_employee_pct_secondary = fields.Float(
        string='NSSA Employee Contribution % (Secondary)',
        config_parameter='havano_payroll.nssa_employee_pct_secondary',
        default=4.5
    )
    
    nssa_employer_pct_secondary = fields.Float(
        string='NSSA Employer Contribution % (Secondary)',
        config_parameter='havano_payroll.nssa_employer_pct_secondary',
        default=4.5
    )
    
    nssa_ceiling_secondary = fields.Float(
        string='NSSA Ceiling (Secondary Currency)',
        config_parameter='havano_payroll.nssa_ceiling_secondary',
        default=28000.00
    )
    
    # WCIF
    wcif_pct = fields.Float(
        string='WCIF Contribution (%)',
        config_parameter='havano_payroll.wcif_pct',
        default=1.0
    )