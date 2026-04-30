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

    def _validate_license(self, license_key=None):
        icp = self.env["ir.config_parameter"].sudo()
        key = (license_key or icp.get_param("customer_supplier_separation.license_key") or "").strip().upper()
        if not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            return False
        expected = hashlib.sha256(f"{self._get_app_prefix()}_{key}_{self._get_app_salt()}".encode()).hexdigest()[:16]
        return expected == (icp.get_param("customer_supplier_separation.license_hash") or self._get_seed_license_hash())

    def _is_license_valid(self):
        return self._validate_license()

    def _periodic_validate_license(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "customer_supplier_separation.license_valid", "True" if self._is_license_valid() else "False"
        )
        return True


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    css_license_key = fields.Char(string="Customer Supplier Separation License Key")
    css_license_valid = fields.Boolean(string="License Valid", readonly=True)
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

    @api.model
    def get_values(self):
        values = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        values.update(
            css_license_key=icp.get_param("customer_supplier_separation.license_key"),
            css_license_valid=self.env["cust.supp.license.manager"]._is_license_valid(),
        )
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        key = (self.css_license_key or "").strip().upper()
        if key and not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("customer_supplier_separation.license_key", key)
        icp.set_param(
            "customer_supplier_separation.license_valid",
            "True" if self.env["cust.supp.license.manager"]._validate_license(key) else "False",
        )

    def action_activate_customer_supplier_separation_license(self):
        self.ensure_one()
        key = (self.css_license_key or "").strip().upper()
        if key and not re.match(r"^[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}$", key):
            raise UserError(_("License key format must be XXXX-XXXX-XXXX-XXXX."))
        manager = self.env["cust.supp.license.manager"]
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("customer_supplier_separation.license_key", key)
        is_valid = manager._validate_license(key)
        icp.set_param("customer_supplier_separation.license_valid", "True" if is_valid else "False")
        icp.set_param("customer_supplier_separation.license_activated", "True" if is_valid else "False")
        if not is_valid:
            raise UserError(_("Invalid license key. Please verify the key and configured license hash."))
        self.css_license_valid = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Customer Supplier Separation license activated successfully."),
                "type": "success",
            },
        }
