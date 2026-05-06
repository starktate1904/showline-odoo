import traceback

with open('/tmp/debug_output.txt', 'w') as f:
    try:
        f.write("Upgrading module...\n")
        env['ir.module.module'].search([('name', '=', 'zimbabwe_payroll')]).button_immediate_upgrade()
        f.write("Upgrade successful!\n")
    except Exception as e:
        f.write("ERROR upgrading module:\n")
        f.write(traceback.format_exc())

    payslip = env['hr.payslip'].search([], limit=1)
    if payslip:
        f.write(f"\nGenerating Payslip report for payslip {payslip.id}...\n")
        try:
            report = env.ref("hr_payroll.action_report_payslip")
            pdf_content, _ = env["ir.actions.report"]._render_qweb_pdf(report.report_name, [payslip.id])
            f.write("Payslip Report generated successfully!\n")
        except Exception as e:
            f.write("ERROR generating Payslip report:\n")
            f.write(traceback.format_exc())
