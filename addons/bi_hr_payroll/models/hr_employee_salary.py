# # -*- coding: utf-8 -*-
# from odoo import api, fields, models, _
# import json

# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
    
#     # Computed fields for the UI tables
#     earnings_table = fields.Html(
#         string='Earnings Table', 
#         compute='_compute_salary_tables',
#         sanitize=False
#     )
    
#     deductions_table = fields.Html(
#         string='Deductions Table', 
#         compute='_compute_salary_tables',
#         sanitize=False
#     )
    
#     salary_summary_table = fields.Html(
#         string='Salary Summary Table', 
#         compute='_compute_salary_tables',
#         sanitize=False
#     )
    
#     # Summary totals
#     total_earnings_usd = fields.Float(
#         string='Total Earnings (USD)', 
#         compute='_compute_salary_summary',
#         currency_field='company_currency_id'
#     )
    
#     total_deductions_usd = fields.Float(
#         string='Total Deductions (USD)', 
#         compute='_compute_salary_summary',
#         currency_field='company_currency_id'
#     )
    
#     net_salary_usd = fields.Float(
#         string='Net Salary (USD)', 
#         compute='_compute_salary_summary',
#         currency_field='company_currency_id'
#     )
    
#     company_currency_id = fields.Many2one(
#         'res.currency', 
#         related='company_id.currency_id',
#         string='Company Currency'
#     )
    
#     @api.depends('contract_ids', 'contract_ids.struct_id', 'contract_ids.wage')
#     def _compute_salary_tables(self):
#         """Generate HTML tables for earnings, deductions, and summary"""
#         for employee in self:
#             # Get active contract
#             contract = employee._get_active_contract()
            
#             if not contract or not contract.struct_id:
#                 employee.earnings_table = self._get_empty_table_html('earnings')
#                 employee.deductions_table = self._get_empty_table_html('deductions')
#                 employee.salary_summary_table = self._get_empty_table_html('summary')
#                 continue
            
#             # Get all rules from structure
#             rules = contract.struct_id.rule_ids
            
#             # Categorize rules
#             earnings_rules = rules.filtered(
#                 lambda r: r.category_id.code in ['BASIC', 'ALLOW', 'ALW']
#             )
#             deductions_rules = rules.filtered(
#                 lambda r: r.category_id.code in ['DED', 'TAX', 'NSSA', 'NEC', 'MEDICAL', 'PENSION', 'LOANS']
#             )
            
#             # Generate tables
#             employee.earnings_table = self._generate_earnings_html(earnings_rules, contract, employee)
#             employee.deductions_table = self._generate_deductions_html(deductions_rules, contract, employee)
#             employee.salary_summary_table = self._generate_summary_html(earnings_rules, deductions_rules, contract, employee)
    
#     @api.depends('contract_ids', 'contract_ids.struct_id', 'contract_ids.wage')
#     def _compute_salary_summary(self):
#         """Compute total earnings, deductions, and net salary"""
#         for employee in self:
#             contract = employee._get_active_contract()
            
#             if not contract or not contract.struct_id:
#                 employee.total_earnings_usd = 0.0
#                 employee.total_deductions_usd = 0.0
#                 employee.net_salary_usd = 0.0
#                 continue
            
#             rules = contract.struct_id.rule_ids
            
#             # Calculate totals
#             earnings_rules = rules.filtered(
#                 lambda r: r.category_id.code in ['BASIC', 'ALLOW', 'ALW']
#             )
#             deductions_rules = rules.filtered(
#                 lambda r: r.category_id.code in ['DED', 'TAX', 'NSSA', 'NEC', 'MEDICAL', 'PENSION', 'LOANS']
#             )
            
#             total_earnings = 0.0
#             total_deductions = 0.0
            
#             # Calculate earnings
#             for rule in earnings_rules:
#                 amount = self._calculate_rule_amount(rule, contract)
#                 total_earnings += amount if amount > 0 else 0
            
#             # Calculate deductions
#             for rule in deductions_rules:
#                 amount = self._calculate_rule_amount(rule, contract)
#                 total_deductions += abs(amount) if amount < 0 else amount
            
#             employee.total_earnings_usd = total_earnings
#             employee.total_deductions_usd = total_deductions
#             employee.net_salary_usd = total_earnings - total_deductions
    
#     def _calculate_rule_amount(self, rule, contract):
#         """Calculate the amount for a given salary rule"""
#         self.ensure_one()
        
#         if rule.amount_select == 'fix':
#             return rule.amount_fix or 0.0
#         elif rule.amount_select == 'percentage':
#             base = contract.wage
#             if rule.amount_percentage_base:
#                 # Try to evaluate the base
#                 try:
#                     base = float(rule.amount_percentage_base) if rule.amount_percentage_base.replace('.', '').isdigit() else contract.wage
#                 except:
#                     base = contract.wage
#             return base * (rule.amount_percentage or 0.0) / 100.0
#         elif rule.amount_select == 'code':
#             # For code-based rules, return 0 as preview (actual calculation requires payslip context)
#             return 0.0
        
#         return 0.0
    
#     def _get_active_contract(self):
#         """Get the active contract for the employee"""
#         self.ensure_one()
#         today = fields.Date.today()
#         return self.contract_ids.filtered(
#             lambda c: c.date_start <= today and (not c.date_end or c.date_end >= today)
#         )[:1]
    
#     def _generate_earnings_html(self, rules, contract, employee):
#         """Generate HTML table for earnings"""
#         if not rules:
#             return self._get_empty_table_html('earnings')
        
#         html = '''
#         <table class="salary-summary-table">
#             <thead>
#                 <tr>
#                     <th>Component</th>
#                     <th>Category</th>
#                     <th class="text-right">Amount (USD)</th>
#                     <th class="text-right">Amount (ZWL)</th>
#                 </tr>
#             </thead>
#             <tbody>
#         '''
        
#         total_usd = 0.0
#         exchange_rate = 1.0  # Default, should come from currency rate configuration
        
#         for rule in rules.sorted(key=lambda r: r.sequence):
#             amount_usd = self._calculate_rule_amount(rule, contract)
#             amount_zwl = amount_usd * exchange_rate
#             total_usd += amount_usd
            
#             html += f'''
#                 <tr class="earning-row">
#                     <td><strong>{rule.name}</strong></td>
#                     <td>{rule.category_id.name}</td>
#                     <td class="text-right currency-primary">
#                         ${amount_usd:,.2f}
#                     </td>
#                     <td class="text-right currency-secondary">
#                         ZWL {amount_zwl:,.2f}
#                     </td>
#                 </tr>
#             '''
        
#         html += f'''
#                 <tr class="category-header">
#                     <td colspan="2"><strong>Total Earnings</strong></td>
#                     <td class="text-right currency-primary">
#                         <strong>${total_usd:,.2f}</strong>
#                     </td>
#                     <td class="text-right currency-secondary">
#                         <strong>ZWL {total_usd * exchange_rate:,.2f}</strong>
#                     </td>
#                 </tr>
#             </tbody>
#         </table>
#         '''
        
#         return html
    
#     def _generate_deductions_html(self, rules, contract, employee):
#         """Generate HTML table for deductions"""
#         if not rules:
#             return self._get_empty_table_html('deductions')
        
#         html = '''
#         <table class="salary-summary-table">
#             <thead>
#                 <tr>
#                     <th>Component</th>
#                     <th>Category</th>
#                     <th class="text-right">Amount (USD)</th>
#                     <th class="text-right">Amount (ZWL)</th>
#                 </tr>
#             </thead>
#             <tbody>
#         '''
        
#         total_usd = 0.0
#         exchange_rate = 1.0
        
#         for rule in rules.sorted(key=lambda r: r.sequence):
#             amount_usd = abs(self._calculate_rule_amount(rule, contract))
#             amount_zwl = amount_usd * exchange_rate
#             total_usd += amount_usd
            
#             html += f'''
#                 <tr class="deduction-row">
#                     <td><strong>{rule.name}</strong></td>
#                     <td>{rule.category_id.name}</td>
#                     <td class="text-right currency-primary">
#                         ${amount_usd:,.2f}
#                     </td>
#                     <td class="text-right currency-secondary">
#                         ZWL {amount_zwl:,.2f}
#                     </td>
#                 </tr>
#             '''
        
#         html += f'''
#                 <tr class="category-header">
#                     <td colspan="2"><strong>Total Deductions</strong></td>
#                     <td class="text-right currency-primary">
#                         <strong>${total_usd:,.2f}</strong>
#                     </td>
#                     <td class="text-right currency-secondary">
#                         <strong>ZWL {total_usd * exchange_rate:,.2f}</strong>
#                     </td>
#                 </tr>
#             </tbody>
#         </table>
#         '''
        
#         return html
    
#     def _generate_summary_html(self, earnings_rules, deductions_rules, contract, employee):
#         """Generate HTML table for salary summary"""
#         if not earnings_rules and not deductions_rules:
#             return self._get_empty_table_html('summary')
        
#         exchange_rate = 1.0
        
#         html = '''
#         <table class="salary-summary-table">
#             <thead>
#                 <tr>
#                     <th colspan="4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
#                         Complete Salary Breakdown
#                     </th>
#                 </tr>
#             </thead>
#             <tbody>
#                 <tr class="category-header">
#                     <td colspan="4"><strong>EARNINGS</strong></td>
#                 </tr>
#         '''
        
#         total_earnings_usd = 0.0
        
#         for rule in earnings_rules.sorted(key=lambda r: r.sequence):
#             amount_usd = self._calculate_rule_amount(rule, contract)
#             amount_zwl = amount_usd * exchange_rate
#             total_earnings_usd += amount_usd
            
#             html += f'''
#                 <tr>
#                     <td style="padding-left: 30px;">{rule.name}</td>
#                     <td class="text-center">{rule.category_id.name}</td>
#                     <td class="text-right currency-primary">${amount_usd:,.2f}</td>
#                     <td class="text-right currency-secondary">ZWL {amount_zwl:,.2f}</td>
#                 </tr>
#             '''
        
#         html += f'''
#                 <tr>
#                     <td colspan="2"><strong>Gross Earnings</strong></td>
#                     <td class="text-right currency-primary">
#                         <strong>${total_earnings_usd:,.2f}</strong>
#                     </td>
#                     <td class="text-right currency-secondary">
#                         <strong>ZWL {total_earnings_usd * exchange_rate:,.2f}</strong>
#                     </td>
#                 </tr>
                
#                 <tr class="category-header">
#                     <td colspan="4"><strong>DEDUCTIONS</strong></td>
#                 </tr>
#         '''
        
#         total_deductions_usd = 0.0
        
#         for rule in deductions_rules.sorted(key=lambda r: r.sequence):
#             amount_usd = abs(self._calculate_rule_amount(rule, contract))
#             amount_zwl = amount_usd * exchange_rate
#             total_deductions_usd += amount_usd
            
#             html += f'''
#                 <tr>
#                     <td style="padding-left: 30px;">{rule.name}</td>
#                     <td class="text-center">{rule.category_id.name}</td>
#                     <td class="text-right currency-primary">${amount_usd:,.2f}</td>
#                     <td class="text-right currency-secondary">ZWL {amount_zwl:,.2f}</td>
#                 </tr>
#             '''
        
#         net_salary_usd = total_earnings_usd - total_deductions_usd
        
#         html += f'''
#                 <tr>
#                     <td colspan="2"><strong>Total Deductions</strong></td>
#                     <td class="text-right currency-primary">
#                         <strong>${total_deductions_usd:,.2f}</strong>
#                     </td>
#                     <td class="text-right currency-secondary">
#                         <strong>ZWL {total_deductions_usd * exchange_rate:,.2f}</strong>
#                     </td>
#                 </tr>
                
#                 <tr class="net-row">
#                     <td colspan="2"><strong>NET SALARY</strong></td>
#                     <td class="text-right currency-primary">
#                         <strong style="font-size: 1.2em;">${net_salary_usd:,.2f}</strong>
#                     </td>
#                     <td class="text-right currency-secondary">
#                         <strong style="font-size: 1.2em;">ZWL {net_salary_usd * exchange_rate:,.2f}</strong>
#                     </td>
#                 </tr>
#             </tbody>
#         </table>
#         '''
        
#         return html
    
#     def _get_empty_table_html(self, table_type):
#         """Return HTML for empty table state"""
#         messages = {
#             'earnings': 'No earnings components found. Please assign a salary structure to the employee contract.',
#             'deductions': 'No deduction components found. Please assign a salary structure to the employee contract.',
#             'summary': 'No salary components found. Please assign a salary structure to the employee contract.'
#         }
        
#         return f'''
#         <div class="alert alert-warning text-center" role="alert">
#             <i class="fa fa-info-circle"></i> {messages.get(table_type, 'No data available')}
#         </div>
#         '''