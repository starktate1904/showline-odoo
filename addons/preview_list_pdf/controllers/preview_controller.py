from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from urllib.parse import unquote_plus


class PreviewListPdfController(http.Controller):
    @http.route("/preview/pdf/<string:model_name>", type="http", auth="user", methods=["GET"], csrf=False)
    def preview_pdf(self, model_name, domain="[]", **kwargs):
        if not request.env["preview.list.license.manager"].sudo()._is_license_valid():
            return request.not_found()
        raw_domain = unquote_plus(domain or "[]") if isinstance(domain, str) else "[]"
        try:
            parsed_domain = safe_eval(raw_domain) if raw_domain else []
        except Exception:
            parsed_domain = []
        docs = request.env[model_name].sudo().search(parsed_domain, limit=5000)
        values = {
            "docs": docs,
            "model_name": model_name,
            "company": request.env.company,
        }
        pdf, _ = request.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "preview_list_pdf.action_report_preview_list_pdf", data=values
        )
        headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", str(len(pdf))),
            ("Content-Disposition", 'inline; filename="%s_preview.pdf"' % model_name.replace(".", "_")),
        ]
        return request.make_response(pdf, headers=headers)
