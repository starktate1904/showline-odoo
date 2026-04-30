from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer = fields.Boolean(string="Is Customer", default=True, tracking=True)
    is_supplier = fields.Boolean(string="Is Supplier", default=False, tracking=True)
    contact_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "Supplier"), ("both", "Both"), ("none", "None")],
        compute="_compute_contact_type",
        store=True,
        string="Contact Type",
    )

    @api.depends("is_customer", "is_supplier")
    def _compute_contact_type(self):
        for partner in self:
            if partner.is_customer and partner.is_supplier:
                partner.contact_type = "both"
            elif partner.is_customer:
                partner.contact_type = "customer"
            elif partner.is_supplier:
                partner.contact_type = "supplier"
            else:
                partner.contact_type = "none"

    @api.model_create_multi
    def create(self, vals_list):
        icp = self.env["ir.config_parameter"].sudo()
        auto_customer = icp.get_param("customer_supplier_separation.auto_mark_customer_from_sales", "True") == "True"
        auto_supplier = icp.get_param("customer_supplier_separation.auto_mark_supplier_from_purchase", "True") == "True"
        for vals in vals_list:
            vals.setdefault("is_customer", True)
            if auto_customer and self.env.context.get("from_sale_order"):
                vals["is_customer"] = True
            if auto_supplier and self.env.context.get("from_purchase_order"):
                vals["is_supplier"] = True
        return super().create(vals_list)

    @api.constrains("is_customer", "is_supplier")
    def _check_customer_or_supplier_required(self):
        for partner in self:
            if not partner.is_customer and not partner.is_supplier:
                raise ValidationError(
                    _("At least one option must be selected: Is Customer or Is Supplier.")
                )
