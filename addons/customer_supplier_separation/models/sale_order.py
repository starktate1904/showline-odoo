from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(
        domain="[('is_customer', '=', True)]",
    )

    @api.model
    def _get_customer_supplier_domain(self, doc_type):
        icp = self.env["ir.config_parameter"].sudo()
        if doc_type == "sale" and icp.get_param("customer_supplier_separation.show_only_customers_in_sales", "True") == "True":
            return [("is_customer", "=", True)]
        if doc_type == "purchase" and icp.get_param("customer_supplier_separation.show_only_suppliers_in_purchases", "True") == "True":
            return [("is_supplier", "=", True)]
        return []
