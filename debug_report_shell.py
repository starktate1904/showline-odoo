import sys
import odoo

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])
registry = odoo.registry('postgres')

with registry.cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    # Render the salary breakdown report
    run = env['hr.payslip.run'].search([], limit=1)
    if run:
        try:
            report = env['ir.actions.report']._render_qweb_html(
                'zimbabwe_payroll.action_report_salary_breakdown', 
                run.ids
            )
            print(report[0].decode('utf-8'))
        except Exception as e:
            print("ERROR:", e)
    else:
        print("No payslip run found")
