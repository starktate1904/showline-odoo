import hashlib
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class NoDuplicateLicenseManager(models.AbstractModel):
    _name = "no.duplicate.license.manager"
    _description = "Disallow Duplicate Contacts License Manager"

    def _get_app_prefix(self):
        return "NO_DUPLICATE"

    def _get_app_salt(self):
        return "NO_DUPLICATE_CONTACTS_SALT_2024"

    def _get_seed_license_hash(self):
        return "455ab86e06b01054"

    def _validate_license(self, license_key=None):
        icp = self.env["ir.config_parameter"].sudo()
        key = (license_key or icp.get_param("disallow_duplicate_contacts.license_key") or "").strip().upper()
        if not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            return False
        expected = hashlib.sha256(f"{self._get_app_prefix()}_{key}_{self._get_app_salt()}".encode()).hexdigest()[:16]
        return expected == (icp.get_param("disallow_duplicate_contacts.license_hash") or self._get_seed_license_hash())

    def _is_license_valid(self):
        return self._validate_license()

    def _periodic_validate_license(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "disallow_duplicate_contacts.license_valid", "True" if self._is_license_valid() else "False"
        )
        return True


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ddc_license_key = fields.Char(string="Duplicate Guard License Key")
    ddc_license_valid = fields.Boolean(string="License Valid", readonly=True)
    ddc_check_email_name = fields.Boolean(
        string="Detect duplicate by Name + Email",
        config_parameter="disallow_duplicate_contacts.check_email_name",
        default=True,
    )
    ddc_check_email_only = fields.Boolean(
        string="Detect duplicate by Email only",
        config_parameter="disallow_duplicate_contacts.check_email_only",
        default=True,
    )
    ddc_check_phone_name = fields.Boolean(
        string="Detect duplicate by Name + Phone",
        config_parameter="disallow_duplicate_contacts.check_phone_name",
        default=True,
    )
    ddc_check_phone_only = fields.Boolean(
        string="Detect duplicate by Phone only",
        config_parameter="disallow_duplicate_contacts.check_phone_only",
        default=True,
    )
    ddc_check_name_address = fields.Boolean(
        string="Detect duplicate by Name + Street + City",
        config_parameter="disallow_duplicate_contacts.check_name_address",
        default=True,
    )
    ddc_check_name_exact = fields.Boolean(
        string="Detect duplicate by exact Name only",
        config_parameter="disallow_duplicate_contacts.check_name_exact",
        default=True,
    )

    @api.model
    def get_values(self):
        values = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        values.update(
            ddc_license_key=icp.get_param("disallow_duplicate_contacts.license_key"),
            ddc_license_valid=self.env["no.duplicate.license.manager"]._is_license_valid(),
        )
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        key = (self.ddc_license_key or "").strip().upper()
        if key and not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("disallow_duplicate_contacts.license_key", key)
        icp.set_param(
            "disallow_duplicate_contacts.license_valid",
            "True" if self.env["no.duplicate.license.manager"]._validate_license(key) else "False",
        )

    def action_activate_disallow_duplicate_contacts_license(self):
        self.ensure_one()
        key = (self.ddc_license_key or "").strip().upper()
        if not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        manager = self.env["no.duplicate.license.manager"]
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("disallow_duplicate_contacts.license_key", key)
        is_valid = manager._validate_license(key)
        icp.set_param("disallow_duplicate_contacts.license_valid", "True" if is_valid else "False")
        icp.set_param("disallow_duplicate_contacts.license_activated", "True" if is_valid else "False")
        if not is_valid:
            raise UserError(_("Invalid license key. Please verify the key and configured license hash."))
        self.ddc_license_valid = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Disallow Duplicate Contacts license activated successfully."),
                "type": "success",
            },
        }
