import sys
import odoo

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'showline_odoo'])

registry = odoo.registry('showline_odoo')
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    
    # Try to render NSSA report
    run = env['hr.payslip.run'].search([], limit=1)
    if run:
        print(f"Generating NSSA report for run {run.id}...")
        try:
            report = env.ref("zimbabwe_payroll.action_report_nssa")
            data = {"data": {"nssa": {"employees": [], "totals": {}, "report_date": "2026-05-05"}}}
            pdf_content, _ = env["ir.actions.report"]._render_qweb_pdf(report.report_name, [run.id], data=data)
            print("NSSA Report generated successfully!")
        except Exception as e:
            print("ERROR generating NSSA report:")
            import traceback
            traceback.print_exc()

    # Try to render Payslip report
    payslip = env['hr.payslip'].search([], limit=1)
    if payslip:
        print(f"\nGenerating Payslip report for payslip {payslip.id}...")
        try:
            report = env.ref("hr_payroll.action_report_payslip")
            if not report:
                print("hr_payroll.action_report_payslip not found")
            else:
                pdf_content, _ = env["ir.actions.report"]._render_qweb_pdf(report.report_name, [payslip.id])
                print("Payslip Report generated successfully!")
        except Exception as e:
            print("ERROR generating Payslip report:")
            import traceback
            traceback.print_exc()
