import sys
import odoo

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'showline_odoo'])
odoo.cli.server.report_configuration()

registry = odoo.registry('showline_odoo')
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    run = env['hr.payslip.run'].browse(19)
    print(f"Payslip run: {run.name}")
    payslips = env['hr.payslip'].search([('payslip_run_id', '=', 19)])
    print(f"Payslips found: {len(payslips)}")
    
    for payslip in payslips:
        print(f"Slip: {payslip.name}")
