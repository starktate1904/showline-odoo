from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HavanoLeaveRequest(models.Model):
    _name = 'havano.leave.request'
    _description = 'Leave Request'
    _order = 'date_from desc'
    
    name = fields.Char('Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    leave_type_id = fields.Many2one('havano.leave.type', string='Leave Type', required=True)
    
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    number_of_days = fields.Float('Number of Days', compute='_compute_days', store=True)
    
    reason = fields.Text('Reason')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Date('Approved Date', readonly=True)
    
    allocation_id = fields.Many2one('havano.leave.allocation', string='Allocation', readonly=True)
    
    @api.depends('employee_id', 'leave_type_id', 'date_from')
    def _compute_name(self):
        for req in self:
            if req.employee_id and req.leave_type_id:
                req.name = f'{req.leave_type_id.name} - {req.employee_id.name} ({req.date_from})'
    
    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for req in self:
            if req.date_from and req.date_to:
                delta = req.date_to - req.date_from
                req.number_of_days = delta.days + 1
    
    def action_request(self):
        self.write({'state': 'requested'})
    
    def action_approve(self):
        """Approve leave and update allocation"""
        self.ensure_one()
        
        # Find or create allocation for this employee, leave type, and year
        year = str(self.date_from.year)
        allocation = self.env['havano.leave.allocation'].search([
            ('employee_id', '=', self.employee_id.id),
            ('leave_type_id', '=', self.leave_type_id.id),
            ('year', '=', year),
        ], limit=1)
        
        if not allocation:
            # Create allocation if doesn't exist
            allocation = self.env['havano.leave.allocation'].create({
                'employee_id': self.employee_id.id,
                'leave_type_id': self.leave_type_id.id,
                'entitled_days': self.leave_type_id.max_days,
                'year': year,
            })
        
        # Update taken days
        allocation.taken_days += self.number_of_days
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Date.today(),
            'allocation_id': allocation.id,
        })
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_cancel(self):
        """Cancel leave and restore allocation"""
        self.ensure_one()
        if self.allocation_id and self.state == 'approved':
            self.allocation_id.taken_days -= self.number_of_days
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})