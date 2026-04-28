from odoo import models, fields


class HavanoLeaveSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    working_days_per_month = fields.Float(
        string='Working Days Per Month',
        config_parameter='havano_payroll.working_days_per_month',
        default=22.0
    )
    
    encashment_enabled = fields.Boolean(
        string='Enable Leave Encashment',
        config_parameter='havano_payroll.encashment_enabled',
        default=True
    )
    
    max_encashment_days = fields.Float(
        string='Max Encashment Days Per Year',
        config_parameter='havano_payroll.max_encashment_days',
        default=10.0
    )