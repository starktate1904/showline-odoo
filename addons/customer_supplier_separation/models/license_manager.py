import hashlib
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustSuppLicenseManager(models.AbstractModel):
    _name = "cust.supp.license.manager"
    _description = "Customer Supplier Separation License Manager"

    def _get_app_prefix(self):
        return "CUST_SUPP"

    def _get_app_salt(self):
        return "CUST_SUPP_SEP_SALT_2024"

    def _get_seed_license_hash(self):
        return "291d229f7d902d2f"

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
        key = (license_key or icp.get_param("customer_supplier_separation.license_key") or "").strip().upper()
        if not self._license_pattern_ok(key):
            return False
        stored = icp.get_param("customer_supplier_separation.license_hash") or self._get_seed_license_hash()
        return self._expected_hash(key) == stored

    def _is_license_valid(self):
        return self._validate_license()

    def is_license_valid(self):
        """Public RPC-safe wrapper for web client checks."""
        return self._is_license_valid()

    def _periodic_validate_license(self):
        icp = self.env["ir.config_parameter"].sudo()
        is_valid = self._is_license_valid()
        icp.set_param("customer_supplier_separation.license_valid", "True" if is_valid else "False")
        if is_valid:
            icp.set_param("customer_supplier_separation.license_activated", "True")
        return True


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    css_license_key = fields.Char(string="Customer Supplier Separation License Key")
    css_license_valid = fields.Boolean(string="License Valid", readonly=True)
    
    # Computed status
    css_license_status = fields.Char(
        string="License Status",
        compute="_compute_css_license_status",
        readonly=True,
    )
    
    # Behavior Settings
    show_only_customers_in_sales = fields.Boolean(
        string="Show Only Customers in Sales",
        default=True,
        config_parameter="customer_supplier_separation.show_only_customers_in_sales",
    )
    show_only_suppliers_in_purchases = fields.Boolean(
        string="Show Only Suppliers in Purchases",
        default=True,
        config_parameter="customer_supplier_separation.show_only_suppliers_in_purchases",
    )
    auto_mark_customer_from_sales = fields.Boolean(
        string="Auto-mark as Customer from Sales",
        default=True,
        config_parameter="customer_supplier_separation.auto_mark_customer_from_sales",
    )
    auto_mark_supplier_from_purchase = fields.Boolean(
        string="Auto-mark as Supplier from Purchases",
        default=True,
        config_parameter="customer_supplier_separation.auto_mark_supplier_from_purchase",
    )

    @api.depends('css_license_valid', 'css_license_key')
    def _compute_css_license_status(self):
        for record in self:
            if record.css_license_valid:
                record.css_license_status = "Activated & Verified"
            elif record.css_license_key:
                record.css_license_status = "Invalid License Key"
            else:
                record.css_license_status = "Not Licensed"

    @api.model
    def get_values(self):
        values = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        manager = self.env["cust.supp.license.manager"]
        values.update(
            css_license_key=icp.get_param("customer_supplier_separation.license_key"),
            css_license_valid=manager._is_license_valid(),
        )
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        key = (self.css_license_key or "").strip().upper()
        icp = self.env["ir.config_parameter"].sudo()
        if key and not self.env["cust.supp.license.manager"]._license_pattern_ok(key):
            raise UserError(_(
                "Invalid license key format.\n\n"
                "Expected format: XXXX-XXXX-XXXX-XXXX\n"
                "Example: A1B2-C3D4-E5F6-G7H8"
            ))
        icp.set_param("customer_supplier_separation.license_key", key)
        is_valid = self.env["cust.supp.license.manager"]._validate_license(key)
        icp.set_param(
            "customer_supplier_separation.license_valid",
            "True" if is_valid else "False",
        )

    def action_activate_customer_supplier_separation_license(self):
        self.ensure_one()
        key = (self.css_license_key or "").strip().upper()
        manager = self.env["cust.supp.license.manager"]

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
                        "Expected format: XXXX-XXXX-XXXX-XXXX"
                    ),
                    "type": "danger",
                    "sticky": True,
                },
            }

        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("customer_supplier_separation.license_key", key)
        is_valid = manager._validate_license(key)

        icp.set_param(
            "customer_supplier_separation.license_valid",
            "True" if is_valid else "False",
        )

        if is_valid:
            icp.set_param("customer_supplier_separation.license_activated", "True")
            self.css_license_valid = True

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("✅ License Activated"),
                    "message": _(
                        "Customer Supplier Separation is now active!\n\n"
                        "Customer/Supplier filtering is enabled. Configure "
                        "your behavior settings below."
                    ),
                    "type": "success",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        else:
            icp.set_param("customer_supplier_separation.license_activated", "False")
            self.css_license_valid = False

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("❌ Invalid License Key"),
                    "message": _(
                        "The license key could not be verified.\n\n"
                        "Please double-check the key and try again."
                    ),
                    "type": "danger",
                    "sticky": True,
                },
            }