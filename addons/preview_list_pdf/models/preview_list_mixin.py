from odoo import models


class PreviewListMixin(models.AbstractModel):
    _name = "preview.list.mixin"
    _description = "Preview List PDF Mixin"

    def preview_list_pdf_license_valid(self):
        return self.env["preview.list.license.manager"]._is_license_valid()
