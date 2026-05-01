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

    def _license_pattern_ok(self, license_key):
        return bool(re.match(
            r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$",
            (license_key or "").strip().upper()
        ))

    def _expected_hash(self, license_key):
        payload = f"{self._get_app_prefix()}_{license_key}_{self._get_app_salt()}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _validate_license(self, license_key=None):
        icp = self.env["ir.config_parameter"].sudo()
        key = (license_key or icp.get_param("disallow_duplicate_contacts.license_key") or "").strip().upper()
        if not self._license_pattern_ok(key):
            return False
        stored = icp.get_param("disallow_duplicate_contacts.license_hash") or self._get_seed_license_hash()
        return self._expected_hash(key) == stored

    def _is_license_valid(self):
        return self._validate_license()

    def is_license_valid(self):
        """Public RPC-safe wrapper for web client checks."""
        return self._is_license_valid()

    def _periodic_validate_license(self):
        icp = self.env["ir.config_parameter"].sudo()
        is_valid = self._is_license_valid()
        icp.set_param("disallow_duplicate_contacts.license_valid", "True" if is_valid else "False")
        if is_valid:
            icp.set_param("disallow_duplicate_contacts.license_activated", "True")
        return True


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ddc_license_key = fields.Char(string="Duplicate Guard License Key")
    ddc_license_valid = fields.Boolean(string="License Valid", readonly=True)

    # Computed status field
    ddc_license_status = fields.Char(
        string="License Status",
        compute="_compute_ddc_license_status",
        readonly=True,
    )

    # Detection Rules
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

    @api.depends('ddc_license_valid', 'ddc_license_key')
    def _compute_ddc_license_status(self):
        for record in self:
            if record.ddc_license_valid:
                record.ddc_license_status = "Activated & Verified"
            elif record.ddc_license_key:
                record.ddc_license_status = "Invalid License Key"
            else:
                record.ddc_license_status = "Not Licensed"

    @api.model
    def get_values(self):
        values = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        manager = self.env["no.duplicate.license.manager"]
        values.update(
            ddc_license_key=icp.get_param("disallow_duplicate_contacts.license_key"),
            ddc_license_valid=manager._is_license_valid(),
        )
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        key = (self.ddc_license_key or "").strip().upper()
        icp = self.env["ir.config_parameter"].sudo()
        if key and not self.env["no.duplicate.license.manager"]._license_pattern_ok(key):
            raise UserError(_(
                "Invalid license key format.\n\n"
                "Expected format: XXXX-XXXX-XXXX-XXXX\n"
                "Example: A1B2-C3D4-E5F6-G7H8"
            ))
        icp.set_param("disallow_duplicate_contacts.license_key", key)
        is_valid = self.env["no.duplicate.license.manager"]._validate_license(key)
        icp.set_param(
            "disallow_duplicate_contacts.license_valid",
            "True" if is_valid else "False",
        )

    def action_activate_disallow_duplicate_contacts_license(self):
        self.ensure_one()
        key = (self.ddc_license_key or "").strip().upper()
        manager = self.env["no.duplicate.license.manager"]

        if not key:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("License Required"),
                    "message": _("Please enter a license key before activating."),
                    "type": "warning",
                    "sticky": True,
                },
            }

        if not manager._license_pattern_ok(key):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invalid Format"),
                    "message": _(
                        "The license key format is invalid.\n\n"
                        "Expected format: XXXX-XXXX-XXXX-XXXX\n"
                        "Example: A1B2-C3D4-E5F6-G7H8"
                    ),
                    "type": "danger",
                    "sticky": True,
                },
            }

        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("disallow_duplicate_contacts.license_key", key)
        is_valid = manager._validate_license(key)

        icp.set_param(
            "disallow_duplicate_contacts.license_valid",
            "True" if is_valid else "False",
        )

        if is_valid:
            icp.set_param("disallow_duplicate_contacts.license_activated", "True")
            self.ddc_license_valid = True

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("✅ License Activated"),
                    "message": _(
                        "Disallow Duplicate Contacts is now active!\n\n"
                        "Duplicate detection is enabled. Configure your "
                        "detection rules below to match your requirements."
                    ),
                    "type": "success",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        else:
            icp.set_param("disallow_duplicate_contacts.license_activated", "False")
            self.ddc_license_valid = False

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("❌ Invalid License Key"),
                    "message": _(
                        "The license key could not be verified.\n\n"
                        "Please double-check the key and try again. "
                        "Contact Showline Solutions if the problem persists."
                    ),
                    "type": "danger",
                    "sticky": True,
                },
            }