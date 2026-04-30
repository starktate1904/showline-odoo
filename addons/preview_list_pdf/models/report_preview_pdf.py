from odoo import models


class ReportPreviewListPdf(models.AbstractModel):
    _name = "report.preview_list_pdf.report_preview_list_pdf"
    _description = "Preview List PDF Report Values"

    def _get_report_values(self, docids, data=None):
        payload = data or {}
        return {
            "doc_ids": docids or [],
            "doc_model": "ir.model",
            "docs": self.env["ir.model"].browse([]),
            "data": payload,
        }
