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

    @api.onchange("is_supplier")
    def _onchange_is_supplier(self):
        """
        Sync is_supplier with Odoo's native supplier_rank.
        A supplier IS a vendor in Odoo. Setting is_supplier = True
        automatically makes the contact appear in the Vendor list.
        """
        if self.is_supplier:
            # supplier_rank > 0 makes the contact appear as a vendor
            if self.supplier_rank <= 0:
                self.supplier_rank = 1
        else:
            # Only reset if it was set by this module (rank == 1)
            if self.supplier_rank == 1:
                self.supplier_rank = 0

    @api.model_create_multi
    def create(self, vals_list):
        icp = self.env["ir.config_parameter"].sudo()
        auto_customer = icp.get_param(
            "customer_supplier_separation.auto_mark_customer_from_sales", "True"
        ) == "True"
        auto_supplier = icp.get_param(
            "customer_supplier_separation.auto_mark_supplier_from_purchase", "True"
        ) == "True"
        
        for vals in vals_list:
            # Default to customer
            if "is_customer" not in vals and "is_supplier" not in vals:
                vals.setdefault("is_customer", True)
            
            # Auto-mark from context
            if auto_customer and self.env.context.get("from_sale_order"):
                vals["is_customer"] = True
            if auto_supplier and self.env.context.get("from_purchase_order"):
                vals["is_supplier"] = True
                # Sync with vendor list
                vals["supplier_rank"] = 1
            
        return super().create(vals_list)

    def write(self, vals):
        # Sync supplier_rank when is_supplier changes
        if "is_supplier" in vals:
            if vals["is_supplier"]:
                vals["supplier_rank"] = max(1, self.supplier_rank)
            else:
                if self.supplier_rank == 1:
                    vals["supplier_rank"] = 0
        return super().write(vals)

    @api.constrains("is_customer", "is_supplier")
    def _check_customer_or_supplier_required(self):
        for partner in self:
            if not partner.is_customer and not partner.is_supplier:
                raise ValidationError(
                    _("At least one option must be selected: Is Customer or Is Supplier.")
                )