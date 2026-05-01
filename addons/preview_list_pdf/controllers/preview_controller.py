import logging
import time
from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from urllib.parse import unquote_plus
import json

_logger = logging.getLogger(__name__)


class PreviewListPdfController(http.Controller):
    @http.route("/preview/pdf/<string:model_name>", type="http", auth="user", methods=["GET"], csrf=False)
    def preview_pdf(self, model_name, domain="[]", fields="[]", labels="[]", limit=80, offset=0, total=0, **kwargs):
        start_time = time.time()
        
        if not request.env["preview.list.license.manager"].sudo()._is_license_valid():
            return request.not_found()
        
        try:
            parsed_domain = safe_eval(unquote_plus(domain)) if domain and domain != "[]" else []
        except:
            parsed_domain = []
            
        try:
            parsed_fields = json.loads(unquote_plus(fields)) if fields and fields != "[]" else []
        except:
            parsed_fields = []
            
        try:
            parsed_labels = json.loads(unquote_plus(labels)) if labels and labels != "[]" else []
        except:
            parsed_labels = []
            
        try:
            limit = min(int(limit or 80), 200)
            offset = int(offset or 0)
        except:
            limit = 80
            offset = 0

        model = request.env[model_name].sudo()
        
        # Build field-label pairs, filtering out binary/image fields TOGETHER
        valid_fields = []
        valid_labels = []
        
        for i, f in enumerate(parsed_fields):
            if f in model._fields:
                field_obj = model._fields[f]
                # Skip binary and image fields
                if field_obj.type in ('binary', 'image'):
                    continue
                valid_fields.append(f)
                # Get matching label
                if i < len(parsed_labels):
                    valid_labels.append(parsed_labels[i])
                else:
                    valid_labels.append(f.replace('_', ' ').title())
        
        if not valid_fields:
            valid_fields = ["display_name"]
            valid_labels = ["Name"]
        
        # valid_fields and valid_labels are now perfectly aligned
        headers = valid_labels
        fields_to_fetch = valid_fields
        
        rows_data = model.search_read(parsed_domain, fields=fields_to_fetch, limit=limit, offset=offset)
        total_count = model.search_count(parsed_domain)
        
        rows = []
        for row in rows_data:
            values = []
            for field in fields_to_fetch:
                value = row.get(field)
                field_obj = model._fields.get(field)
                
                if field_obj and field_obj.type == 'many2one':
                    if isinstance(value, (list, tuple)) and len(value) >= 2:
                        values.append(str(value[1])[:80])
                    elif value:
                        values.append(str(value)[:80])
                    else:
                        values.append("")
                elif field_obj and field_obj.type in ('one2many', 'many2many'):
                    if isinstance(value, (list, tuple)):
                        if len(value) > 0 and isinstance(value[0], (list, tuple)) and len(value[0]) >= 2:
                            values.append(str(value[0][1])[:80])
                        else:
                            values.append(f"({len(value)})")
                    else:
                        values.append("")
                elif isinstance(value, bool):
                    values.append("Yes" if value else "No")
                elif value is None or value is False:
                    values.append("")
                elif isinstance(value, (int, float)):
                    if field_obj and field_obj.type == 'monetary':
                        values.append(f"{value:,.2f}")
                    else:
                        values.append(f"{value:,}")
                else:
                    clean = str(value).replace('\n', ' ').replace('\r', '')[:80]
                    values.append(clean)
            rows.append(values)

        total_pages = max(1, (total_count + limit - 1) // limit) if limit > 0 else 1
        page_number = (offset // limit) + 1 if limit > 0 else 1
        
        column_count = len(headers)
        is_landscape = column_count >= 5
        
        # Single table in landscape, chunked in portrait
        if is_landscape:
            table_chunks = [{"headers": headers, "rows": rows}]
        else:
            max_cols = 4
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
            "column_count": column_count,
            "page_number": page_number,
            "total_pages": total_pages,
            "showing_from": offset + 1 if total_count > 0 else 0,
            "showing_to": min(offset + limit, total_count),
            "total_records": total_count,
            "is_landscape": is_landscape,
        }
        
        # Set paper format
        paperformat_xmlid = "preview_list_pdf.paperformat_landscape" if is_landscape else "preview_list_pdf.paperformat_portrait"
        try:
            report_action = request.env.ref("preview_list_pdf.action_report_preview_list_pdf").sudo()
            paperformat = request.env.ref(paperformat_xmlid).sudo()
            report_action.write({"paperformat_id": paperformat.id})
        except Exception as e:
            _logger.warning(f"Could not set paper format: {e}")
        
        pdf, _ = request.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "preview_list_pdf.action_report_preview_list_pdf", 
            data=report_data
        )
        
        _logger.info(f"PDF generated in {time.time() - start_time:.2f}s - {len(rows)} rows, {column_count} cols, landscape: {is_landscape}")
        
        response_headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", str(len(pdf))),
            ("Cache-Control", "private, max-age=30"),
        ]
        
        if kwargs.get("download"):
            response_headers.append(
                ("Content-Disposition", f'attachment; filename="{model_name}_preview.pdf"')
            )
        else:
            response_headers.append(("Content-Disposition", "inline"))
            
        return request.make_response(pdf, headers=response_headers)