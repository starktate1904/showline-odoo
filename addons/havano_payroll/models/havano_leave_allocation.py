from odoo import models, fields, api


class HavanoLeaveAllocation(models.Model):
    _name = 'havano.leave.allocation'
    _description = 'Employee Leave Allocation'
    _order = 'employee_id, leave_type_id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    leave_type_id = fields.Many2one('havano.leave.type', string='Leave Type', required=True)
    
    entitled_days = fields.Float('Entitled Days', default=0)
    taken_days = fields.Float('Taken Days', default=0)
    planned_days = fields.Float('Planned Days', default=0)
    remaining_days = fields.Float('Remaining Days', compute='_compute_remaining', store=True)
    carried_over_days = fields.Float('Carried Over', default=0)
    
    year = fields.Char('Year', default=lambda self: str(fields.Date.today().year))
    
    @api.depends('entitled_days', 'taken_days', 'planned_days', 'carried_over_days')
    def _compute_remaining(self):
        for alloc in self:
            alloc.remaining_days = alloc.entitled_days + alloc.carried_over_days - alloc.taken_days - alloc.planned_days
    
    _sql_constraints = [
        ('unique_employee_leave_type_year', 
         'unique(employee_id, leave_type_id, year)',
         'This employee already has an allocation for this leave type and year!')
    ]