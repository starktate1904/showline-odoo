from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from urllib.parse import unquote_plus
import json


class PreviewListPdfController(http.Controller):
    @http.route("/preview/pdf/<string:model_name>", type="http", auth="user", methods=["GET"], csrf=False)
    def preview_pdf(self, model_name, domain="[]", fields="[]", labels="[]", limit=80, offset=0, total=0, **kwargs):
        if not request.env["preview.list.license.manager"].sudo()._is_license_valid():
            return request.not_found()
        raw_domain = unquote_plus(domain or "[]") if isinstance(domain, str) else "[]"
        raw_fields = unquote_plus(fields or "[]") if isinstance(fields, str) else "[]"
        raw_labels = unquote_plus(labels or "[]") if isinstance(labels, str) else "[]"
        try:
            parsed_domain = safe_eval(raw_domain) if raw_domain else []
        except Exception:
            parsed_domain = []
        try:
            parsed_fields = json.loads(raw_fields) if raw_fields else []
        except Exception:
            parsed_fields = []
        try:
            parsed_labels = json.loads(raw_labels) if raw_labels else []
        except Exception:
            parsed_labels = []

        try:
            limit = min(int(limit), 500)
            offset = int(offset)
        except (TypeError, ValueError):
            limit = 80
            offset = 0

        model = request.env[model_name].sudo()
        valid_fields = [field for field in parsed_fields if field in model._fields]
        if not valid_fields:
            valid_fields = ["display_name"]
            parsed_labels = ["Name"]
        headers = parsed_labels[: len(valid_fields)] if parsed_labels else valid_fields
        rows_data = model.search_read(parsed_domain, fields=valid_fields, limit=limit, offset=offset)
        rows = []
        for row in rows_data:
            values = []
            for field in valid_fields:
                value = row.get(field)
                if isinstance(value, (list, tuple)) and len(value) >= 2:
                    values.append(str(value[1])[:100])
                elif isinstance(value, bool):
                    values.append("Yes" if value else "No")
                elif value is None:
                    values.append("")
                else:
                    values.append(str(value)[:100])
            rows.append(values)

        total_count = model.search_count(parsed_domain)
        total_pages = (total_count // limit) + (1 if total_count % limit else 0) if limit else 1
        page_number = (offset // limit) + 1 if limit else 1

        max_cols = 8
        table_chunks = []
        for start in range(0, len(headers), max_cols):
            end = start + max_cols
            chunk_rows = [row[start:end] for row in rows]
            table_chunks.append({
                "headers": headers[start:end],
                "rows": chunk_rows,
            })

        report_data = {
            "model_name": model._description or model_name,
            "company_name": request.env.company.name,
            "headers": headers,
            "rows": rows,
            "table_chunks": table_chunks,
            "column_count": len(headers),
            "page_number": page_number,
            "total_pages": total_pages,
            "showing_from": offset + 1 if total_count > 0 else 0,
            "showing_to": min(offset + limit, total_count),
            "total_records": total_count,
            "is_landscape": len(headers) > 5,
        }
        pdf, _ = request.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "preview_list_pdf.action_report_preview_list_pdf", data=report_data
        )
        response_headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", str(len(pdf))),
        ]
        if kwargs.get("download"):
            response_headers.append(("Content-Disposition", f'attachment; filename="{model_name}_preview.pdf"'))
        else:
            response_headers.append(("Content-Disposition", "inline"))
        return request.make_response(pdf, headers=response_headers)
