from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zimbabwe_nssa_employee_pct = fields.Float(
        string="NSSA Employee Contribution (%)",
        config_parameter="zimbabwe_payroll.nssa_employee_pct",
        default=4.5,
    )
    zimbabwe_nssa_employer_pct = fields.Float(
        string="NSSA Employer Contribution (%)",
        config_parameter="zimbabwe_payroll.nssa_employer_pct",
        default=4.5,
    )
    
    zimbabwe_nec_total_pct = fields.Float(
        string="NEC Total Contribution (%)",
        config_parameter="zimbabwe_payroll.nec_total_pct",
        default=2.5,
    )
    
    zimbabwe_nec_employee_split = fields.Float(
        string="NEC Employee Split (%)",
        config_parameter="zimbabwe_payroll.nec_employee_split",
        default=50.0,
    )
    
    zimbabwe_nec_employer_split = fields.Float(
        string="NEC Employer Split (%)",
        config_parameter="zimbabwe_payroll.nec_employer_split",
        default=50.0,
    )

    zimbabwe_zimdef_basic_pct = fields.Float(
        string="ZIMDEF Basic Salary Contribution (%)",
        config_parameter="zimbabwe_payroll.zimdef_basic_pct",
        default=1.0,
    )
    
    zimbabwe_zimdef_contrib_pct = fields.Float(
        string="ZIMDEF Additional Contributions (%)",
        config_parameter="zimbabwe_payroll.zimdef_contrib_pct",
        default=1.0,
    )
    zimbabwe_nssa_ceiling = fields.Float(
        string="NSSA Pensionable Ceiling",
        config_parameter="zimbabwe_payroll.nssa_ceiling",
        default=700.0,
        help="Maximum pensionable income used for NSSA calculation.",
    )
    zimbabwe_nssa_cap = fields.Float(
        string="NSSA Employee Cap Amount",
        config_parameter="zimbabwe_payroll.nssa_employee_cap",
        default=0.0,
        help="Maximum NSSA deduction amount. Set to 0 for no cap.",
    )

    zimbabwe_nec_employee_pct = fields.Float(
        string="NEC Employee Contribution (%)",
        config_parameter="zimbabwe_payroll.nec_employee_pct",
        default=1.5,
    )
    zimbabwe_nec_ceiling = fields.Float(
        string="NEC Pensionable Ceiling",
        config_parameter="zimbabwe_payroll.nec_ceiling",
        default=0.0,
        help="Maximum pensionable income used for NEC calculation. Set to 0 for no ceiling.",
    )
    zimbabwe_nec_cap = fields.Float(
        string="NEC Employee Cap Amount",
        config_parameter="zimbabwe_payroll.nec_employee_cap",
        default=0.0,
        help="Maximum NEC deduction amount. Set to 0 for no cap.",
    )
