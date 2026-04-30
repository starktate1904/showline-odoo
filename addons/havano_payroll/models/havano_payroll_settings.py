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
    
    # ==================== NSSA - Primary Currency ====================
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
    
    # ==================== NSSA - Secondary Currency ====================
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
    
    # ==================== NEC - Primary Currency ====================
    nec_enabled = fields.Boolean(
        string='Enable NEC',
        config_parameter='havano_payroll.nec_enabled',
        default=False
    )
    
    nec_employee_pct = fields.Float(
        string='NEC Employee Contribution (%)',
        config_parameter='havano_payroll.nec_employee_pct',
        default=1.5
    )
    
    nec_ceiling = fields.Float(
        string='NEC Ceiling (0 = No Cap)',
        config_parameter='havano_payroll.nec_ceiling',
        default=0.0
    )
    
    # ==================== NEC - Secondary Currency ====================
    nec_employee_pct_secondary = fields.Float(
        string='NEC Employee Contribution % (Secondary)',
        config_parameter='havano_payroll.nec_employee_pct_secondary',
        default=1.5
    )
    
    nec_ceiling_secondary = fields.Float(
        string='NEC Ceiling Secondary (0 = No Cap)',
        config_parameter='havano_payroll.nec_ceiling_secondary',
        default=0.0
    )
    
    # ==================== ZIMDEF - Primary Currency ====================
    zimdef_enabled = fields.Boolean(
        string='Enable ZIMDEF',
        config_parameter='havano_payroll.zimdef_enabled',
        default=False
    )
    
    zimdef_employer_pct = fields.Float(
        string='ZIMDEF Employer Contribution (%)',
        config_parameter='havano_payroll.zimdef_employer_pct',
        default=1.0
    )
    
    zimdef_deduct_from_employee = fields.Boolean(
        string='Deduct ZIMDEF from Employee',
        config_parameter='havano_payroll.zimdef_deduct_from_employee',
        default=False,
        help="If checked, ZIMDEF is deducted from employee salary. If unchecked, it's an employer contribution only."
    )
    
    # ==================== ZIMDEF - Secondary Currency ====================
    zimdef_employer_pct_secondary = fields.Float(
        string='ZIMDEF Employer Contribution % (Secondary)',
        config_parameter='havano_payroll.zimdef_employer_pct_secondary',
        default=1.0
    )
    
    # ==================== WCIF ====================
    wcif_enabled = fields.Boolean(
        string='Enable WCIF',
        config_parameter='havano_payroll.wcif_enabled',
        default=False
    )
    
    wcif_pct = fields.Float(
        string='WCIF Contribution (%)',
        config_parameter='havano_payroll.wcif_pct',
        default=1.0
    )
    
    wcif_pct_secondary = fields.Float(
        string='WCIF Contribution % (Secondary)',
        config_parameter='havano_payroll.wcif_pct_secondary',
        default=1.0
    )
    
    # ==================== MEDICAL AID TAX CREDIT ====================
    medical_aid_tax_credit_pct = fields.Float(
        string='Medical Aid Tax Credit (%)',
        config_parameter='havano_payroll.medical_aid_tax_credit_pct',
        default=50.0,
        help="Percentage of Medical Aid contribution that becomes a tax credit (default 50%)"
    )
    
    # ==================== TAX CREDITS (FIXED AMOUNTS) ====================
    tax_credit_blind = fields.Float(
        string='Blind Person Tax Credit',
        config_parameter='havano_payroll.tax_credit_blind',
        default=75.00
    )
    
    tax_credit_elderly = fields.Float(
        string='Elderly (65+) Tax Credit',
        config_parameter='havano_payroll.tax_credit_elderly',
        default=75.00
    )
    
    tax_credit_disabled = fields.Float(
        string='Disabled Person Tax Credit',
        config_parameter='havano_payroll.tax_credit_disabled',
        default=75.00
    )