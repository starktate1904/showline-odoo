import io
import xlsxwriter
from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import date


class ZimbabwePayrollController(http.Controller):
    @staticmethod
    def _build_pdf_response(pdf_content, filename):
        headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", str(len(pdf_content))),
            ("Content-Disposition", f'inline; filename="{filename}"'),
        ]
        return request.make_response(pdf_content, headers=headers)

    @staticmethod
    def _split_lines(payslip):
        excluded_codes = {"GROSS_TAXABLE", "TAXABLE_INC", "TOT_ALLOW_DED", "TOT_CREDITS", "GROSS", "NET"}
        earning_categories = {"TAXABLE", "BONUS", "NONTAX", "BASIC", "ALW"}
        deduction_categories = {
            "PAYE", "AIDS_LEVY", "NSSA", "MED_AID", "FUNERAL",
            "LOAN", "ALLOW_DED", "NONALLOW_DED", "NEC", "ZIMDEF", "DED",
        }
        display_lines = payslip.line_ids.filtered(
            lambda line: line.appears_on_payslip and line.total and line.code not in excluded_codes
        )

        def is_earning(line):
            cat_code = line.category_id.code if line.category_id else ''
            if cat_code in earning_categories:
                return True
            if cat_code not in deduction_categories and line.total > 0:
                return True
            return False

        def is_deduction(line):
            cat_code = line.category_id.code if line.category_id else ''
            if cat_code in deduction_categories:
                return True
            if cat_code not in earning_categories and line.total < 0:
                return True
            return False

        earnings = display_lines.filtered(is_earning)
        deductions = display_lines.filtered(is_deduction)
        return earnings, deductions

    # ============================================================
    # SALARY BREAKDOWN (aggregated)
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/salary_breakdown", type="http", auth="user")
    def salary_breakdown_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        earnings_totals = defaultdict(float)
        deduction_totals = defaultdict(float)

        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            for line in earnings:
                key = (line.name or line.code or "").strip() or "Earning"
                earnings_totals[key] += float(line.total or 0.0)
            for line in deductions:
                key = (line.name or line.code or "").strip() or "Deduction"
                deduction_totals[key] += abs(float(line.total or 0.0))

        earnings_rows = [
            {"name": key, "amount": amt}
            for key, amt in sorted(earnings_totals.items(), key=lambda kv: kv[0].lower())
            if abs(amt) > 0.00001
        ]
        deduction_rows = [
            {"name": key, "amount": amt}
            for key, amt in sorted(deduction_totals.items(), key=lambda kv: kv[0].lower())
            if abs(amt) > 0.00001
        ]

        total_earnings = sum(r["amount"] for r in earnings_rows)
        total_deductions = sum(r["amount"] for r in deduction_rows)

        report = request.env.ref("zimbabwe_payroll.action_report_salary_breakdown")
        data = {
            "data": {
                "breakdown": {
                    "earnings": earnings_rows,
                    "deductions": deduction_rows,
                    "total_earnings": total_earnings,
                    "total_deductions": total_deductions,
                    "total_employees": len(payslips.mapped("employee_id")),
                    "report_date": date.today().isoformat(),
                }
            }
        }
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_salary_breakdown.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # SALARY SUMMARY
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/salary_summary", type="http", auth="user")
    def salary_summary_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        totals = {
            "basic_salary": 0.0, "gross_wage": 0.0, "net_pay": 0.0,
            "total_earnings": 0.0, "total_deductions": 0.0, "employer_costs": 0.0,
        }

        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            totals["total_earnings"] += sum(earnings.mapped("total"))
            totals["total_deductions"] += abs(sum(deductions.mapped("total")))

            basic_values = payslip.line_ids.filtered(lambda line: line.code == "BASIC").mapped('total')
            if basic_values:
                totals["basic_salary"] += basic_values[0] or 0.0

            gross_wage = payslip.gross_wage if "gross_wage" in payslip._fields else 0.0
            net_wage = payslip.net_wage if "net_wage" in payslip._fields else 0.0
            totals["gross_wage"] += gross_wage or 0.0
            totals["net_pay"] += net_wage or 0.0

            if "employer_cost" in payslip._fields and payslip.employer_cost:
                totals["employer_costs"] += payslip.employer_cost
            else:
                employer_lines = payslip.line_ids.filtered(lambda line: line.category_id.code == "COMP")
                totals["employer_costs"] += sum(employer_lines.mapped("total"))

        report = request.env.ref("zimbabwe_payroll.action_report_salary_summary")
        data = {"data": {"summary": totals}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_salary_summary.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # DETAILED BREAKDOWN (per employee)
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/detailed_breakdown", type="http", auth="user")
    def detailed_breakdown_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        employee_rows = []

        for payslip in payslips:
            earnings_lines, deduction_lines = self._split_lines(payslip)

            earnings = [{"name": (line.name or line.code or "").strip() or "Earning", "amount": float(line.total or 0.0)} for line in earnings_lines]
            deductions = [{"name": (line.name or line.code or "").strip() or "Deduction", "amount": abs(float(line.total or 0.0))} for line in deduction_lines]

            total_earnings = sum(item["amount"] for item in earnings)
            total_deductions = sum(item["amount"] for item in deductions)

            employee_rows.append({
                "employee_name": payslip.employee_id.name,
                "earnings": earnings,
                "deductions": deductions,
                "total_earnings": total_earnings,
                "total_deductions": total_deductions,
                "net_pay": total_earnings - total_deductions,
            })

        report = request.env.ref("zimbabwe_payroll.action_report_detailed_breakdown")
        data = {"data": {"detailed_breakdown": {"employees": employee_rows}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_detailed_salary_breakdown.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # SUMMARY BREAKDOWN (per employee totals only)
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/summary_breakdown", type="http", auth="user")
    def summary_breakdown_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        employee_rows = []
        totals = {"gross_salary": 0.0, "total_earnings": 0.0, "total_deductions": 0.0, "net_pay": 0.0}

        for payslip in payslips:
            earnings_lines, deduction_lines = self._split_lines(payslip)

            total_earnings = sum(float(line.total or 0.0) for line in earnings_lines)
            total_deductions = abs(sum(float(line.total or 0.0) for line in deduction_lines))
            net_pay = total_earnings - total_deductions

            basic_values = payslip.line_ids.filtered(lambda line: line.code == "BASIC").mapped("total")
            gross_salary = float(basic_values[0] or 0.0) if basic_values else 0.0

            employee_rows.append({
                "employee_name": payslip.employee_id.name,
                "gross_salary": gross_salary,
                "total_earnings": total_earnings,
                "total_deductions": total_deductions,
                "net_pay": net_pay,
            })

            totals["gross_salary"] += gross_salary
            totals["total_earnings"] += total_earnings
            totals["total_deductions"] += total_deductions
            totals["net_pay"] += net_pay

        report = request.env.ref("zimbabwe_payroll.action_report_summary_breakdown")
        data = {"data": {"summary_breakdown": {"employees": employee_rows, "totals": totals}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_summary_salary_breakdown.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # NSSA DATA (original - for NSSA Report)
    # ============================================================
    def _get_nssa_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        ceiling = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_ceiling', '700'))
        employer_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employer_pct', '4.5'))
        employee_cap = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employee_cap', '0'))

        employee_rows = []
        for payslip in payslips:
            basic_values = payslip.line_ids.filtered(lambda line: line.code == "BASIC").mapped('total')
            basic = float(basic_values[0] or 0.0) if basic_values else 0.0
            pensionable = min(basic, ceiling) if ceiling > 0 else basic

            nssa_values = payslip.line_ids.filtered(lambda line: line.code == "NSSA").mapped('total')
            employee_nssa = abs(nssa_values[0]) if nssa_values else 0.0
            if employee_cap > 0:
                employee_nssa = min(employee_nssa, employee_cap)

            employer_nssa = pensionable * employer_pct / 100.0

            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''

            employee_rows.append({
                "surname": surname,
                "first_names": first_names,
                "start_date": payslip.date_from,
                "end_date": payslip.date_to,
                "basic_salary": basic,
                "insurable_earnings": basic,
                "employee_nssa": employee_nssa,
                "employer_nssa": employer_nssa,
                "total_nssa": employee_nssa + employer_nssa,
            })

        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {
            "basic_salary": sum(r["basic_salary"] for r in employee_rows),
            "insurable_earnings": sum(r["insurable_earnings"] for r in employee_rows),
            "employee_nssa": sum(r["employee_nssa"] for r in employee_rows),
            "employer_nssa": sum(r["employer_nssa"] for r in employee_rows),
            "total_nssa": sum(r["total_nssa"] for r in employee_rows),
        }
        return employee_rows, totals

    # ============================================================
    # NSSA P4 DATA (for P4 Report - with extra columns)
    # ============================================================
    def _get_nssa_p4_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        ceiling = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_ceiling', '700'))
        employer_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employer_pct', '4.5'))
        employee_cap = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employee_cap', '0'))

        employee_rows = []
        for payslip in payslips:
            basic_values = payslip.line_ids.filtered(lambda line: line.code == "BASIC").mapped('total')
            basic = float(basic_values[0] or 0.0) if basic_values else 0.0
            pensionable = min(basic, ceiling) if ceiling > 0 else basic

            nssa_values = payslip.line_ids.filtered(lambda line: line.code == "NSSA").mapped('total')
            current_contribution = abs(nssa_values[0]) if nssa_values else 0.0
            if employee_cap > 0:
                current_contribution = min(current_contribution, employee_cap)

            employer_payment = pensionable * employer_pct / 100.0
            arrears = 0.0
            prepayments = 0.0
            surcharge = 0.0
            total_payment = current_contribution + arrears + prepayments + surcharge

            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''

            employee_rows.append({
                "surname": surname,
                "first_names": first_names,
                "start_date": payslip.date_from,
                "end_date": payslip.date_to,
                "basic_salary": basic,
                "insurable_earnings": basic,
                "employee_nssa": current_contribution,
                "employer_nssa": employer_payment,
                "total_nssa": current_contribution + employer_payment,
                "total_insurable_earnings": basic,
                "current_contribution": current_contribution,
                "arrears": arrears,
                "prepayments": prepayments,
                "surcharge": surcharge,
                "total_payment": total_payment,
                "employer_payment": employer_payment,
            })

        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {
            "basic_salary": sum(r["basic_salary"] for r in employee_rows),
            "insurable_earnings": sum(r["insurable_earnings"] for r in employee_rows),
            "employee_nssa": sum(r["employee_nssa"] for r in employee_rows),
            "employer_nssa": sum(r["employer_nssa"] for r in employee_rows),
            "total_nssa": sum(r["total_nssa"] for r in employee_rows),
            "total_insurable_earnings": sum(r["total_insurable_earnings"] for r in employee_rows),
            "current_contribution": sum(r["current_contribution"] for r in employee_rows),
            "arrears": sum(r["arrears"] for r in employee_rows),
            "prepayments": sum(r["prepayments"] for r in employee_rows),
            "surcharge": sum(r["surcharge"] for r in employee_rows),
            "total_payment": sum(r["total_payment"] for r in employee_rows),
            "employer_payment": sum(r["employer_payment"] for r in employee_rows),
        }
        return employee_rows, totals

    # ============================================================
    # NSSA REPORT (original)
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/nssa_report", type="http", auth="user")
    def nssa_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        employee_rows, totals = self._get_nssa_data(pay_run)

        report = request.env.ref("zimbabwe_payroll.action_report_nssa")
        data = {"data": {"nssa": {"employees": employee_rows, "totals": totals, "report_date": date.today().isoformat()}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_NSSA_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # NSSA P4 REPORT (new - full columns)
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/nssa_p4_report", type="http", auth="user")
    def nssa_p4_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        employee_rows, totals = self._get_nssa_p4_data(pay_run)

        report = request.env.ref("zimbabwe_payroll.action_report_nssa_p4")
        data = {"data": {"nssa": {"employees": employee_rows, "totals": totals, "report_date": date.today().isoformat()}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_NSSA_P4_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # ZIMRA ITF REPORT
    # ============================================================
    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/zimra_itf_report", type="http", auth="user")
    def zimra_itf_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        employee_rows = []
        for payslip in payslips:
            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''

            basic_values = payslip.line_ids.filtered(lambda line: line.code == "BASIC").mapped('total')
            basic = float(basic_values[0] or 0.0) if basic_values else 0.0

            gross_values = payslip.line_ids.filtered(lambda line: line.code in ("GROSS_TAXABLE", "GROSS", "TAXABLE_INC")).mapped('total')
            gross = float(gross_values[0] or 0.0) if gross_values else 0.0

            paye_values = payslip.line_ids.filtered(lambda line: line.code == "PAYE").mapped('total')
            paye = abs(paye_values[0]) if paye_values else 0.0

            aids_levy_values = payslip.line_ids.filtered(lambda line: line.code == "AIDS_LEVY").mapped('total')
            aids_levy = abs(aids_levy_values[0]) if aids_levy_values else 0.0

            employee_rows.append({
                "employee_id": employee.identification_id or str(employee.id),
                "surname": surname, "first_names": first_names,
                "basic": basic, "gross": gross,
                "paye": paye, "aids_levy": aids_levy,
                "total_tax_due": paye + aids_levy,
            })

        employee_rows.sort(key=lambda x: (x["surname"].lower(), x["first_names"].lower()))
        totals = {
            "basic": sum(r["basic"] for r in employee_rows),
            "gross": sum(r["gross"] for r in employee_rows),
            "paye": sum(r["paye"] for r in employee_rows),
            "aids_levy": sum(r["aids_levy"] for r in employee_rows),
            "total_tax_due": sum(r["total_tax_due"] for r in employee_rows),
        }

        report = request.env.ref("zimbabwe_payroll.action_report_zimra_itf")
        data = {"data": {"zimra": {"employees": employee_rows, "totals": totals, "report_date": date.today().isoformat()}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_ZIMRA_ITF_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    # ============================================================
    # EXPORT ROUTER
    # ============================================================
    @http.route("/zimbabwe_payroll/export/<string:report_type>/<int:pay_run_id>", type="http", auth="user")
    def export_report(self, report_type, pay_run_id, format='pdf', **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        export_format = (format or 'pdf').lower()

        if report_type == 'salary_breakdown':
            return self._export_salary_breakdown_excel(pay_run) if export_format == 'excel' else self.salary_breakdown_pdf(pay_run_id)
        elif report_type == 'salary_summary':
            return self._export_salary_summary_excel(pay_run) if export_format == 'excel' else self.salary_summary_pdf(pay_run_id)
        elif report_type == 'detailed_breakdown':
            return self._export_detailed_breakdown_excel(pay_run) if export_format == 'excel' else self.detailed_breakdown_pdf(pay_run_id)
        elif report_type == 'summary_breakdown':
            return self._export_summary_breakdown_excel(pay_run) if export_format == 'excel' else self.summary_breakdown_pdf(pay_run_id)
        elif report_type == 'nssa':
            return self._export_nssa_excel(pay_run) if export_format == 'excel' else self.nssa_report_pdf(pay_run_id)
        elif report_type == 'nssa_p4':
            return self._export_nssa_p4_excel(pay_run) if export_format == 'excel' else self.nssa_p4_report_pdf(pay_run_id)
        elif report_type == 'zimra_itf':
            return self._export_zimra_itf_excel(pay_run) if export_format == 'excel' else self.zimra_itf_report_pdf(pay_run_id)
        elif report_type == 'nec':
            return self._export_nec_excel(pay_run) if export_format == 'excel' else self.nec_report_pdf(pay_run_id)
        elif report_type == 'zimdef':
            return self._export_zimdef_excel(pay_run) if export_format == 'excel' else self.zimdef_report_pdf(pay_run_id)

        return request.not_found()

    # ============================================================
    # EXCEL EXPORTS
    # ============================================================
    def _export_nssa_excel(self, pay_run):
        employee_rows, totals = self._get_nssa_p4_data(pay_run)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('NSSA P4 Report')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Surname', 'First Names', 'Start Date', 'End Date', 'Total Insurable Earnings', 'Current Contributions', 'Arrears', 'Prepayments', 'Surcharge', 'Total Payment', 'Employer Payment']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 18)
        for row, emp in enumerate(employee_rows, 1):
            sheet.write(row, 0, emp['surname'])
            sheet.write(row, 1, emp['first_names'])
            sheet.write(row, 2, str(emp['start_date']))
            sheet.write(row, 3, str(emp['end_date']))
            sheet.write(row, 4, emp['total_insurable_earnings'], money)
            sheet.write(row, 5, emp['current_contribution'], money)
            sheet.write(row, 6, emp['arrears'], money)
            sheet.write(row, 7, emp['prepayments'], money)
            sheet.write(row, 8, emp['surcharge'], money)
            sheet.write(row, 9, emp['total_payment'], money)
            sheet.write(row, 10, emp['employer_payment'], money)
        row = len(employee_rows) + 1
        sheet.write(row, 0, 'TOTAL', bold)
        sheet.write(row, 4, totals['total_insurable_earnings'], money)
        sheet.write(row, 5, totals['current_contribution'], money)
        sheet.write(row, 6, totals['arrears'], money)
        sheet.write(row, 7, totals['prepayments'], money)
        sheet.write(row, 8, totals['surcharge'], money)
        sheet.write(row, 9, totals['total_payment'], money)
        sheet.write(row, 10, totals['employer_payment'], money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_NSSA_P4_Report.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_nssa_p4_excel(self, pay_run):
        return self._export_nssa_excel(pay_run)

    def _get_nec_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        employee_rows = []
        for payslip in payslips:
            basic = float((payslip.line_ids.filtered(lambda l: l.code == "BASIC").mapped('total') or [0])[0])
            overtime = float((payslip.line_ids.filtered(lambda l: l.code == "OVERTIME").mapped('total') or [0])[0])
            cola = float((payslip.line_ids.filtered(lambda l: l.code == "COLA").mapped('total') or [0])[0])
            backpay = float((payslip.line_ids.filtered(lambda l: l.code == "BACKPAY").mapped('total') or [0])[0])
            earnings_base = basic + overtime + cola + backpay
            employee_nec = abs((payslip.line_ids.filtered(lambda l: l.code == "NEC").mapped('total') or [0])[0])
            employer_nec = abs((payslip.line_ids.filtered(lambda l: l.code == "NEC_ER").mapped('total') or [0])[0])
            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''
            employee_rows.append({"surname": surname, "first_names": first_names, "start_date": payslip.date_from, "end_date": payslip.date_to, "earnings_base": earnings_base, "employee_nec": employee_nec, "employer_nec": employer_nec, "total_nec": employee_nec + employer_nec})
        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {"earnings_base": sum(r["earnings_base"] for r in employee_rows), "employee_nec": sum(r["employee_nec"] for r in employee_rows), "employer_nec": sum(r["employer_nec"] for r in employee_rows), "total_nec": sum(r["total_nec"] for r in employee_rows)}
        return employee_rows, totals

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/nec_report", type="http", auth="user")
    def nec_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()
        employee_rows, totals = self._get_nec_data(pay_run)
        report = request.env.ref("zimbabwe_payroll.action_report_nec")
        data = {"data": {"nec": {"employees": employee_rows, "totals": totals, "report_date": date.today().isoformat()}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_NEC_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    def _export_nec_excel(self, pay_run):
        employee_rows, totals = self._get_nec_data(pay_run)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('NEC Report')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Surname', 'First Name', 'Start Date', 'End Date', 'NEC Earnings Base', 'Employee', 'Employer', 'Total NEC']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 15)
        for row, emp in enumerate(employee_rows, 1):
            sheet.write(row, 0, emp['surname'])
            sheet.write(row, 1, emp['first_names'])
            sheet.write(row, 2, str(emp['start_date']))
            sheet.write(row, 3, str(emp['end_date']))
            sheet.write(row, 4, emp['earnings_base'], money)
            sheet.write(row, 5, emp['employee_nec'], money)
            sheet.write(row, 6, emp['employer_nec'], money)
            sheet.write(row, 7, emp['total_nec'], money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_NEC_Report.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_zimra_itf_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('ZIMRA ITF')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['ID', 'Surname', 'First Name', 'Basic', 'Gross', 'PAYE', 'AIDS Levy', 'Total Tax']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 15)
        for row, payslip in enumerate(payslips, 1):
            emp = payslip.employee_id
            parts = emp.name.rsplit(' ', 1)
            fn = parts[0] if len(parts) > 1 else ''
            sn = parts[-1] if parts else ''
            if not fn:
                fn = sn
                sn = ''
            basic = float((payslip.line_ids.filtered(lambda l: l.code == "BASIC").mapped('total') or [0])[0])
            gross = float((payslip.line_ids.filtered(lambda l: l.code in ("GROSS_TAXABLE","GROSS","TAXABLE_INC")).mapped('total') or [0])[0])
            paye = abs((payslip.line_ids.filtered(lambda l: l.code == "PAYE").mapped('total') or [0])[0])
            aids = abs((payslip.line_ids.filtered(lambda l: l.code == "AIDS_LEVY").mapped('total') or [0])[0])
            sheet.write(row, 0, emp.identification_id or str(emp.id))
            sheet.write(row, 1, sn)
            sheet.write(row, 2, fn)
            sheet.write(row, 3, basic, money)
            sheet.write(row, 4, gross, money)
            sheet.write(row, 5, paye, money)
            sheet.write(row, 6, aids, money)
            sheet.write(row, 7, paye + aids, money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_ZIMRA_ITF.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _get_zimdef_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        basic_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.zimdef_basic_pct', '1.0'))
        employee_rows = []
        for payslip in payslips:
            basic = float((payslip.line_ids.filtered(lambda l: l.code == "BASIC").mapped('total') or [0])[0])
            zimdef_employer = basic * basic_pct / 100.0
            emp = payslip.employee_id
            parts = emp.name.rsplit(' ', 1)
            fn = parts[0] if len(parts) > 1 else ''
            sn = parts[-1] if parts else ''
            if not fn:
                fn = sn
                sn = ''
            employee_rows.append({"surname": sn, "first_names": fn, "basic": basic, "zimdef_employer": zimdef_employer, "total_zimdef": zimdef_employer})
        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {"basic": sum(r["basic"] for r in employee_rows), "zimdef_employer": sum(r["zimdef_employer"] for r in employee_rows), "total_zimdef": sum(r["total_zimdef"] for r in employee_rows)}
        return employee_rows, totals

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/zimdef_report", type="http", auth="user")
    def zimdef_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()
        employee_rows, totals = self._get_zimdef_data(pay_run)
        report = request.env.ref("zimbabwe_payroll.action_report_zimdef")
        data = {"data": {"zimdef": {"employees": employee_rows, "totals": totals, "report_date": date.today().isoformat()}}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_ZIMDEF_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    def _export_zimdef_excel(self, pay_run):
        employee_rows, totals = self._get_zimdef_data(pay_run)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('ZIMDEF')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Surname', 'First Name', 'Basic', 'Employer ZIMDEF', 'Total ZIMDEF']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 15)
        for row, emp in enumerate(employee_rows, 1):
            sheet.write(row, 0, emp['surname'])
            sheet.write(row, 1, emp['first_names'])
            sheet.write(row, 2, emp['basic'], money)
            sheet.write(row, 3, emp['zimdef_employer'], money)
            sheet.write(row, 4, emp['total_zimdef'], money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_ZIMDEF.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_salary_breakdown_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Salary Breakdown')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Employee', 'Earnings', 'Amount', 'Deductions', 'Amount']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 20)
        row = 1
        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            sheet.write(row, 0, payslip.employee_id.name, bold)
            row += 1
            for line in earnings:
                sheet.write(row, 1, line.name)
                sheet.write(row, 2, float(line.total), money)
                row += 1
            for line in deductions:
                sheet.write(row, 3, line.name)
                sheet.write(row, 4, abs(float(line.total)), money)
                row += 1
            row += 1
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_salary_breakdown.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_salary_summary_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Salary Summary')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Description', 'Amount']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 25)
        summaries = defaultdict(float)
        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            for line in earnings:
                summaries[(line.name or line.code or "").strip()] += float(line.total)
            for line in deductions:
                summaries[(line.name or line.code or "").strip()] += abs(float(line.total))
        for row, (name, amt) in enumerate(sorted(summaries.items()), 1):
            sheet.write(row, 0, name)
            sheet.write(row, 1, amt, money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_salary_summary.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_detailed_breakdown_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Detailed Breakdown')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Employee', 'Earnings', 'Amount', 'Deductions', 'Amount', 'Net Pay']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 20)
        row = 1
        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            total_earn = sum(float(l.total) for l in earnings)
            total_ded = abs(sum(float(l.total) for l in deductions))
            sheet.write(row, 0, payslip.employee_id.name, bold)
            sheet.write(row, 5, total_earn - total_ded, money)
            row += 1
            for line in earnings:
                sheet.write(row, 1, line.name)
                sheet.write(row, 2, float(line.total), money)
                row += 1
            for line in deductions:
                sheet.write(row, 3, line.name)
                sheet.write(row, 4, abs(float(line.total)), money)
                row += 1
            row += 1
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_detailed_breakdown.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])

    def _export_summary_breakdown_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Summary Breakdown')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        headers = ['Employee', 'Gross Salary', 'Total Earnings', 'Total Deductions', 'Net Pay']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
            sheet.set_column(col, col, 20)
        for row, payslip in enumerate(payslips, 1):
            earnings, deductions = self._split_lines(payslip)
            total_earn = sum(float(l.total) for l in earnings)
            total_ded = abs(sum(float(l.total) for l in deductions))
            basic = float((payslip.line_ids.filtered(lambda l: l.code == "BASIC").mapped('total') or [0])[0])
            sheet.write(row, 0, payslip.employee_id.name)
            sheet.write(row, 1, basic, money)
            sheet.write(row, 2, total_earn, money)
            sheet.write(row, 3, total_ded, money)
            sheet.write(row, 4, total_earn - total_ded, money)
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_summary_breakdown.xlsx"
        return request.make_response(output.read(), [("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", f'attachment; filename="{filename}"')])