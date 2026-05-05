payslips = env['hr.payslip'].search([], limit=1)
print(f"Payslip: {payslips.name}")
for line in payslips.line_ids:
    print(f"[{line.code}] {line.name} | Cat: {line.category_id.code if line.category_id else 'None'} | Total: {line.total} | Appears: {line.appears_on_payslip}")
