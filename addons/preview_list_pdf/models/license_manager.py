import hashlib
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PreviewListLicenseManager(models.AbstractModel):
    _name = "preview.list.license.manager"
    _description = "Preview List PDF License Manager"

    def _get_app_prefix(self):
        return "PREVIEW_LIST"

    def _get_app_salt(self):
        return "PREVIEW_LIST_PDF_SALT_2024"

    def _get_seed_license_hash(self):
        return "febd085fb95b9fa3"

    def _license_pattern_ok(self, license_key):
        return bool(re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", (license_key or "").strip().upper()))

    def _expected_hash(self, license_key):
        payload = f"{self._get_app_prefix()}_{license_key}_{self._get_app_salt()}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _validate_license(self, license_key=None):
        icp = self.env["ir.config_parameter"].sudo()
        key = (license_key or icp.get_param("preview_list_pdf.license_key") or "").strip().upper()
        if not self._license_pattern_ok(key):
            return False
        stored = icp.get_param("preview_list_pdf.license_hash") or self._get_seed_license_hash()
        return self._expected_hash(key) == stored

    def _is_license_valid(self):
        return self._validate_license()

    def _periodic_validate_license(self):
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("preview_list_pdf.license_valid", "True" if self._is_license_valid() else "False")
        return True


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    preview_list_pdf_license_key = fields.Char(string="Preview List PDF License Key")
    preview_list_pdf_license_valid = fields.Boolean(string="License Valid", readonly=True)

    @api.model
    def get_values(self):
        values = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        manager = self.env["preview.list.license.manager"]
        values.update(
            preview_list_pdf_license_key=icp.get_param("preview_list_pdf.license_key"),
            preview_list_pdf_license_valid=manager._is_license_valid(),
        )
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        key = (self.preview_list_pdf_license_key or "").strip().upper()
        icp = self.env["ir.config_parameter"].sudo()
        if key and not self.env["preview.list.license.manager"]._license_pattern_ok(key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        icp.set_param("preview_list_pdf.license_key", key)
        icp.set_param("preview_list_pdf.license_valid", "True" if self.env["preview.list.license.manager"]._validate_license(key) else "False")

    def action_activate_preview_list_pdf_license(self):
        self.ensure_one()
        key = (self.preview_list_pdf_license_key or "").strip().upper()
        manager = self.env["preview.list.license.manager"]
        if not manager._license_pattern_ok(key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("preview_list_pdf.license_key", key)
        is_valid = manager._validate_license(key)
        icp.set_param("preview_list_pdf.license_valid", "True" if is_valid else "False")
        icp.set_param("preview_list_pdf.license_activated", "True" if is_valid else "False")
        if not is_valid:
            raise UserError(_("Invalid license key. Please verify the key and configured license hash."))
        self.preview_list_pdf_license_valid = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Preview List PDF license activated successfully."),
                "type": "success",
            },
        }
