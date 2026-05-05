from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ==================== NSSA ====================
    havano_nssa_employee_pct = fields.Float(
        string='NSSA Employee Contribution (%)',
        config_parameter='havano_payroll.nssa_employee_pct',
        default=4.5,
        help='Percentage of basic salary for NSSA employee contribution'
    )

    havano_nssa_ceiling = fields.Float(
        string='NSSA Ceiling Amount',
        config_parameter='havano_payroll.nssa_ceiling',
        default=700.00,
        help='Maximum pensionable salary for NSSA'
    )

    # ==================== TAX CREDITS ====================
    havano_medical_aid_tax_credit_pct = fields.Float(
        string='Medical Aid Tax Credit (%)',
        config_parameter='havano_payroll.medical_aid_tax_credit_pct',
        default=50.0,
        help='Percentage of Medical Aid contribution that becomes a tax credit (default 50%)'
    )

    havano_medical_aid_credit_ceiling = fields.Float(
        string='Medical Aid Credit Ceiling',
        config_parameter='havano_payroll.medical_aid_credit_ceiling',
        default=1000.00,
        help='Maximum tax credit amount for Medical Aid'
    )

    havano_tax_credit_blind = fields.Float(
        string='Blind Person Tax Credit Amount',
        config_parameter='havano_payroll.tax_credit_blind',
        default=75.00,
        help='Fixed tax credit for blind employees'
    )

    havano_tax_credit_elderly = fields.Float(
        string='Elderly (65+) Tax Credit Amount',
        config_parameter='havano_payroll.tax_credit_elderly',
        default=75.00,
        help='Fixed tax credit for employees 65 years and older'
    )

    havano_tax_credit_disabled = fields.Float(
        string='Disabled Person Tax Credit Amount',
        config_parameter='havano_payroll.tax_credit_disabled',
        default=75.00,
        help='Fixed tax credit for disabled employees'
    )

    # ==================== AIDS LEVY ====================
    havano_aids_levy_pct = fields.Float(
        string='AIDS Levy (%)',
        config_parameter='havano_payroll.aids_levy_pct',
        default=3.0,
        help='Percentage of PAYE for AIDS Levy'
    )