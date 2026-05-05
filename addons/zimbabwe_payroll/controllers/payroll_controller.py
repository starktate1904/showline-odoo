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

            if "employer_cost" in payslip._fields:
                totals["employer_costs"] += payslip.employer_cost or 0.0
            else:
                employer_lines = payslip.line_ids.filtered(
                    lambda line: line.total > 0
                    and ("NSSA" in (line.code or "") and "EMP" in (line.code or ""))
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
