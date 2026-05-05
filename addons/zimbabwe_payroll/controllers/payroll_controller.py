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
            "PAYE",
            "AIDS_LEVY",
            "NSSA",
            "MED_AID",
            "FUNERAL",
            "LOAN",
            "ALLOW_DED",
            "NONALLOW_DED",
            "NEC",
            "ZIMDEF",
            "DED",
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

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/salary_summary", type="http", auth="user")
    def salary_summary_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        totals = {
            "basic_salary": 0.0,
            "gross_wage": 0.0,
            "net_pay": 0.0,
            "total_earnings": 0.0,
            "total_deductions": 0.0,
            "employer_costs": 0.0,
        }

        for payslip in payslips:
            earnings, deductions = self._split_lines(payslip)
            totals["total_earnings"] += sum(earnings.mapped("total"))
            totals["total_deductions"] += abs(sum(deductions.mapped("total")))

            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            if basic_line:
                totals["basic_salary"] += basic_line.total

            gross_wage = payslip.gross_wage if "gross_wage" in payslip._fields else 0.0
            net_wage = payslip.net_wage if "net_wage" in payslip._fields else 0.0
            totals["gross_wage"] += gross_wage or 0.0
            totals["net_pay"] += net_wage or 0.0

            if "employer_cost" in payslip._fields and payslip.employer_cost:
                totals["employer_costs"] += payslip.employer_cost
            else:
                employer_lines = payslip.line_ids.filtered(
                    lambda line: line.category_id.code == "COMP"
                )
                totals["employer_costs"] += sum(employer_lines.mapped("total"))

        report = request.env.ref("zimbabwe_payroll.action_report_salary_summary")
        data = {"data": {"summary": totals}}
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_salary_summary.pdf"
        return self._build_pdf_response(pdf_content, filename)

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/nssa_report", type="http", auth="user")
    def nssa_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        ceiling = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_ceiling', '700'))
        employer_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employer_pct', '4.5'))
        
        employee_rows = []
        for payslip in payslips:
            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            basic = basic_line.total if basic_line else (payslip.version_id.contract_wage if hasattr(payslip, 'version_id') and payslip.version_id else 0.0)
            
            pensionable = min(basic, ceiling) if ceiling > 0 else basic
            
            nssa_line = payslip.line_ids.filtered(lambda line: line.code == "NSSA")[:1]
            employee_nssa = abs(nssa_line.total) if nssa_line else 0.0
            
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
                "insurable_earnings": pensionable,
                "employee_nssa": employee_nssa,
                "employer_nssa": employer_nssa,
                "total_nssa": employee_nssa + employer_nssa,
            })
            
        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        
        totals = {
            "insurable_earnings": sum(r["insurable_earnings"] for r in employee_rows),
            "employee_nssa": sum(r["employee_nssa"] for r in employee_rows),
            "employer_nssa": sum(r["employer_nssa"] for r in employee_rows),
            "total_nssa": sum(r["total_nssa"] for r in employee_rows),
        }

        report = request.env.ref("zimbabwe_payroll.action_report_nssa")
        data = {
            "data": {
                "nssa": {
                    "employees": employee_rows,
                    "totals": totals,
                    "report_date": date.today().isoformat(),
                }
            }
        }
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_NSSA_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

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
                
            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            basic = basic_line.total if basic_line else (payslip.version_id.contract_wage if hasattr(payslip, 'version_id') and payslip.version_id else 0.0)
            
            gross_line = payslip.line_ids.filtered(lambda line: line.code in ("GROSS_TAXABLE", "GROSS", "TAXABLE_INC"))[:1]
            gross = gross_line.total if gross_line else 0.0
            
            paye_line = payslip.line_ids.filtered(lambda line: line.code == "PAYE")[:1]
            paye = abs(paye_line.total) if paye_line else 0.0
            
            aids_levy_line = payslip.line_ids.filtered(lambda line: line.code == "AIDS_LEVY")[:1]
            aids_levy = abs(aids_levy_line.total) if aids_levy_line else 0.0
            
            employee_rows.append({
                "employee_id": employee.identification_id or str(employee.id),
                "surname": surname,
                "first_names": first_names,
                "basic": basic,
                "gross": gross,
                "paye": paye,
                "aids_levy": aids_levy,
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
        data = {
            "data": {
                "zimra": {
                    "employees": employee_rows,
                    "totals": totals,
                    "report_date": date.today().isoformat(),
                }
            }
        }
        
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            report.report_name, [pay_run.id], data=data
        )
        filename = f"{pay_run.name or 'pay_run'}_ZIMRA_ITF_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    @http.route("/zimbabwe_payroll/export/<string:report_type>/<int:pay_run_id>", type="http", auth="user")
    def export_report(self, report_type, pay_run_id, format='pdf', **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()
            
        if report_type == 'nssa':
            if format == 'pdf':
                return self.nssa_report_pdf(pay_run_id)
            return self._export_nssa_excel(pay_run)
            
        elif report_type == 'zimra_itf':
            if format == 'pdf':
                return self.zimra_itf_report_pdf(pay_run_id)
            return self._export_zimra_itf_excel(pay_run)
            
        elif report_type == 'nec':
            if format == 'pdf':
                return self.nec_report_pdf(pay_run_id)
            return self._export_nec_excel(pay_run)
            
        elif report_type == 'zimdef':
            if format == 'pdf':
                return self.zimdef_report_pdf(pay_run_id)
            return self._export_zimdef_excel(pay_run)
            
        return request.not_found()

    def _export_nssa_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        ceiling = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_ceiling', '700'))
        employer_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.nssa_employer_pct', '4.5'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('NSSA Report')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        
        headers = ['Surname', 'First Name', 'Start Date', 'End Date', 'Insurable Earnings', 'Employee NSSA', 'Employer NSSA', 'Total NSSA']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)
            sheet.set_column(col, col, 15)
            
        row = 1
        for payslip in payslips:
            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            basic = basic_line.total if basic_line else (payslip.version_id.contract_wage if hasattr(payslip, 'version_id') and payslip.version_id else 0.0)
            pensionable = min(basic, ceiling) if ceiling > 0 else basic
            
            nssa_line = payslip.line_ids.filtered(lambda line: line.code == "NSSA")[:1]
            employee_nssa = abs(nssa_line.total) if nssa_line else 0.0
            employer_nssa = pensionable * employer_pct / 100.0
            
            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''
                
            sheet.write(row, 0, surname)
            sheet.write(row, 1, first_names)
            sheet.write(row, 2, str(payslip.date_from))
            sheet.write(row, 3, str(payslip.date_to))
            sheet.write(row, 4, pensionable, money)
            sheet.write(row, 5, employee_nssa, money)
            sheet.write(row, 6, employer_nssa, money)
            sheet.write(row, 7, employee_nssa + employer_nssa, money)
            row += 1
            
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_NSSA_Report.xlsx"
        headers_response = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ]
        return request.make_response(output.read(), headers=headers_response)

    def _export_zimra_itf_excel(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('ZIMRA ITF Report')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        
        headers = ['ID', 'Surname', 'First Name', 'Basic Pension', 'Gross Pay', 'PAYE', 'AIDS Levy', 'Total Tax Due']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)
            sheet.set_column(col, col, 15)
            
        row = 1
        for payslip in payslips:
            employee = payslip.employee_id
            parts = employee.name.rsplit(' ', 1)
            first_names = parts[0] if len(parts) > 1 else ''
            surname = parts[-1] if parts else ''
            if not first_names:
                first_names = surname
                surname = ''
                
            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            basic = basic_line.total if basic_line else (payslip.version_id.contract_wage if hasattr(payslip, 'version_id') and payslip.version_id else 0.0)
            
            gross_line = payslip.line_ids.filtered(lambda line: line.code in ("GROSS_TAXABLE", "GROSS", "TAXABLE_INC"))[:1]
            gross = gross_line.total if gross_line else 0.0
            
            paye_line = payslip.line_ids.filtered(lambda line: line.code == "PAYE")[:1]
            paye = abs(paye_line.total) if paye_line else 0.0
            
            aids_levy_line = payslip.line_ids.filtered(lambda line: line.code == "AIDS_LEVY")[:1]
            aids_levy = abs(aids_levy_line.total) if aids_levy_line else 0.0
            
            sheet.write(row, 0, employee.identification_id or str(employee.id))
            sheet.write(row, 1, surname)
            sheet.write(row, 2, first_names)
            sheet.write(row, 3, basic, money)
            sheet.write(row, 4, gross, money)
            sheet.write(row, 5, paye, money)
            sheet.write(row, 6, aids_levy, money)
            sheet.write(row, 7, paye + aids_levy, money)
            row += 1
            
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_ZIMRA_ITF_Report.xlsx"
        headers_response = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ]
        return request.make_response(output.read(), headers=headers_response)

    def _get_nec_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        
        employee_rows = []
        for payslip in payslips:
            basic_line = payslip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            overtime_line = payslip.line_ids.filtered(lambda line: line.code == "OVERTIME")[:1]
            cola_line = payslip.line_ids.filtered(lambda line: line.code == "COLA")[:1]
            backpay_line = payslip.line_ids.filtered(lambda line: line.code == "BACKPAY")[:1]
            
            basic = basic_line.total if basic_line else (payslip.version_id.contract_wage if hasattr(payslip, 'version_id') and payslip.version_id else 0.0)
            overtime = overtime_line.total if overtime_line else 0.0
            cola = cola_line.total if cola_line else 0.0
            backpay = backpay_line.total if backpay_line else 0.0
            
            earnings_base = basic + overtime + cola + backpay
            
            nec_line = payslip.line_ids.filtered(lambda line: line.code == "NEC")[:1]
            employee_nec = abs(nec_line.total) if nec_line else 0.0
            
            nec_er_line = payslip.line_ids.filtered(lambda line: line.code == "NEC_ER")[:1]
            employer_nec = abs(nec_er_line.total) if nec_er_line else 0.0
            
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
                "earnings_base": earnings_base,
                "employee_nec": employee_nec,
                "employer_nec": employer_nec,
                "total_nec": employee_nec + employer_nec,
            })
            
        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {
            "earnings_base": sum(r["earnings_base"] for r in employee_rows),
            "employee_nec": sum(r["employee_nec"] for r in employee_rows),
            "employer_nec": sum(r["employer_nec"] for r in employee_rows),
            "total_nec": sum(r["total_nec"] for r in employee_rows),
        }
        return employee_rows, totals

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/nec_report", type="http", auth="user")
    def nec_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        employee_rows, totals = self._get_nec_data(pay_run)
        
        report = request.env.ref("zimbabwe_payroll.action_report_nec")
        data = {
            "data": {
                "nec": {
                    "employees": employee_rows,
                    "totals": totals,
                    "report_date": date.today().isoformat(),
                }
            }
        }
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
        
        headers = ['Surname', 'First Name', 'Start Date', 'End Date', 'NEC Earnings Base', 'Employee Contribution', 'Employer Contribution', 'Total NEC']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)
            sheet.set_column(col, col, 15)
            
        row = 1
        for emp in employee_rows:
            sheet.write(row, 0, emp['surname'])
            sheet.write(row, 1, emp['first_names'])
            sheet.write(row, 2, str(emp['start_date']))
            sheet.write(row, 3, str(emp['end_date']))
            sheet.write(row, 4, emp['earnings_base'], money)
            sheet.write(row, 5, emp['employee_nec'], money)
            sheet.write(row, 6, emp['employer_nec'], money)
            sheet.write(row, 7, emp['total_nec'], money)
            row += 1
            
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_NEC_Report.xlsx"
        headers_response = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ]
        return request.make_response(output.read(), headers=headers_response)

    def _get_zimdef_data(self, pay_run):
        payslips = request.env["hr.payslip"].search([("payslip_run_id", "=", pay_run.id)])
        basic_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.zimdef_basic_pct', '1.0'))
        contrib_pct = float(request.env['ir.config_parameter'].sudo().get_param('zimbabwe_payroll.zimdef_contrib_pct', '1.0'))
        
        employee_rows = []
        for payslip in payslips:
            gross_line = payslip.line_ids.filtered(lambda line: line.code == "GROSS")[:1]
            if not gross_line:
                gross_line = payslip.line_ids.filtered(lambda line: line.code == "GROSS_TAXABLE")[:1]
            gross = gross_line.total if gross_line else 0.0
            
            nssa_line = payslip.line_ids.filtered(lambda line: line.code == "NSSA")[:1]
            nssa = abs(nssa_line.total) if nssa_line else 0.0
            
            nec_line = payslip.line_ids.filtered(lambda line: line.code == "NEC")[:1]
            nec = abs(nec_line.total) if nec_line else 0.0
            
            zimdef_on_gross = gross * basic_pct / 100.0
            contribs_base = nssa + nec
            zimdef_on_contribs = contribs_base * contrib_pct / 100.0
            
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
                "gross": gross,
                "zimdef_on_gross": zimdef_on_gross,
                "contribs_base": contribs_base,
                "zimdef_on_contribs": zimdef_on_contribs,
                "total_zimdef": zimdef_on_gross + zimdef_on_contribs,
            })
            
        employee_rows.sort(key=lambda x: (x['surname'] or '').lower())
        totals = {
            "gross": sum(r["gross"] for r in employee_rows),
            "zimdef_on_gross": sum(r["zimdef_on_gross"] for r in employee_rows),
            "contribs_base": sum(r["contribs_base"] for r in employee_rows),
            "zimdef_on_contribs": sum(r["zimdef_on_contribs"] for r in employee_rows),
            "total_zimdef": sum(r["total_zimdef"] for r in employee_rows),
        }
        return employee_rows, totals

    @http.route("/zimbabwe_payroll/payrun/<int:pay_run_id>/zimdef_report", type="http", auth="user")
    def zimdef_report_pdf(self, pay_run_id, **kwargs):
        pay_run = request.env["hr.payslip.run"].browse(pay_run_id).exists()
        if not pay_run:
            return request.not_found()

        employee_rows, totals = self._get_zimdef_data(pay_run)
        
        report = request.env.ref("zimbabwe_payroll.action_report_zimdef")
        data = {
            "data": {
                "zimdef": {
                    "employees": employee_rows,
                    "totals": totals,
                    "report_date": date.today().isoformat(),
                }
            }
        }
        pdf_content, _ = request.env["ir.actions.report"]._render_qweb_pdf(report.report_name, [pay_run.id], data=data)
        filename = f"{pay_run.name or 'pay_run'}_ZIMDEF_Report.pdf"
        return self._build_pdf_response(pdf_content, filename)

    def _export_zimdef_excel(self, pay_run):
        employee_rows, totals = self._get_zimdef_data(pay_run)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('ZIMDEF Report')
        bold = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00'})
        
        headers = ['Surname', 'First Name', 'Gross Wage', 'ZIMDEF on Gross', 'NSSA+NEC Base', 'ZIMDEF on Contribs', 'Total ZIMDEF']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)
            sheet.set_column(col, col, 15)
            
        row = 1
        for emp in employee_rows:
            sheet.write(row, 0, emp['surname'])
            sheet.write(row, 1, emp['first_names'])
            sheet.write(row, 2, emp['gross'], money)
            sheet.write(row, 3, emp['zimdef_on_gross'], money)
            sheet.write(row, 4, emp['contribs_base'], money)
            sheet.write(row, 5, emp['zimdef_on_contribs'], money)
            sheet.write(row, 6, emp['total_zimdef'], money)
            row += 1
            
        workbook.close()
        output.seek(0)
        filename = f"{pay_run.name or 'pay_run'}_ZIMDEF_Report.xlsx"
        headers_response = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ]
        return request.make_response(output.read(), headers=headers_response)
