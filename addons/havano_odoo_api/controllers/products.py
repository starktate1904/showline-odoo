# from odoo import http, fields, _  
# from odoo.http import request
# from odoo.exceptions import MissingError, ValidationError
# from .common import HavanoApiControllerMixin

# import logging
# _logger = logging.getLogger(__name__)

# class HavanoProductsController(HavanoApiControllerMixin, http.Controller):
    
#     def _serialize_product(self, product):
#         """Convert product.template to API response dict."""
#         has_detailed_type = "detailed_type" in product._fields
#         return {
#             "id": product.id,
#             "name": product.name or "",
#             "default_code": product.default_code or "",
#             "barcode": product.barcode or "",
#             "list_price": product.list_price,
#             "standard_price": product.standard_price,
#             "active": product.active,
#             "product_type": product.detailed_type if has_detailed_type else product.type,
#             "category": product.categ_id.name or "",
#             "category_id": product.categ_id.id,
#             "uom": product.uom_id.name or "",
#             "uom_id": product.uom_id.id,
#             "qty_available": product.qty_available,
#             "description": product.description or "",
#             "description_sale": product.description_sale or "",
#         }
    
#     # =========================================================================
#     # ENDPOINTS
#     # =========================================================================
    
#     @http.route("/api/v1/products", auth="public", methods=["GET"], type="json", csrf=False)
#     def list_products(self, limit=100, offset=0, order="id desc", **kwargs):
#         """GET /api/v1/products - List products with pagination."""
#         return self._handle_route(lambda env: self._list_products(env, limit, offset, order))
    
#     def _list_products(self, env, limit, offset, order):
#         try:
#             limit = min(int(limit), 500)
#             offset = int(offset) if offset else 0
#         except (ValueError, TypeError):
#             limit, offset = 100, 0
        
#         product_model = env["product.template"]
#         has_detailed_type = "detailed_type" in product_model._fields
#         type_field = "detailed_type" if has_detailed_type else "type"

#         domain = [("active", "=", True)]
        
#         products = product_model.search_read(
#             domain=domain,
#             fields=["id", "name", "default_code", "barcode", "list_price",
#                    "standard_price", "active", type_field, "categ_id",
#                    "uom_id", "qty_available", "description", "description_sale"],
#             limit=limit,
#             offset=offset,
#             order=order,
#         )
#         for item in products:
#             item["product_type"] = item.get(type_field)
        
#         total = product_model.search_count(domain)
        
#         return self._success({
#             "items": products,
#             "total": total,
#             "limit": limit,
#             "offset": offset,
#         })
    
#     @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["GET"], type="json", csrf=False)
#     def get_product(self, product_id, **kwargs):
#         """GET /api/v1/products/:id - Get single product."""
#         return self._handle_route(lambda env: self._get_product(env, product_id))
    
#     def _get_product(self, env, product_id):
#         product = env["product.template"].browse(product_id)
#         if not product.exists():
#             raise MissingError(_("Product #%s not found.") % product_id)
        
#         return self._success(self._serialize_product(product))
    
#     @http.route("/api/v1/products", auth="public", methods=["POST"], type="json", csrf=False)
#     def create_product(self, **kwargs):
#         """POST /api/v1/products - Create or update product by SKU."""
#         return self._handle_route(lambda env: self._upsert_product(env))
    
#     def _upsert_product(self, env):
#         data = self._parse_json_data()
#         sku = data.get("default_code") or data.get("sku")
        
#         if not sku:
#             raise ValidationError(_("Product SKU (default_code) is required."))
        
#         if not data.get("name"):
#             data["name"] = sku
        
#         # Check existing by SKU
#         product = env["product.template"].search([
#             ("default_code", "=", str(sku).strip())
#         ], limit=1)
        
#         if product:
#             product.write(data)
#             msg = _("Product updated.")
#             status = 200
#         else:
#             product = env["product.template"].create(data)
#             msg = _("Product created.")
#             status = 201
        
#         _logger.info("Product %s: id=%s, sku=%s", "updated" if status == 200 else "created", 
#                     product.id, sku)
        
#         return self._success(self._serialize_product(product), message=msg, status=status)
    
#     @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["PUT", "POST"], type="json", csrf=False)
#     def update_product(self, product_id, **kwargs):
#         """PUT /api/v1/products/:id - Update product."""
#         return self._handle_route(lambda env: self._update_product(env, product_id))
    
#     def _update_product(self, env, product_id):
#         data = self._parse_json_data()
#         product = env["product.template"].browse(product_id)
        
#         if not product.exists():
#             raise MissingError(_("Product #%s not found.") % product_id)
        
#         if not data:
#             raise ValidationError(_("No data provided for update."))
        
#         product.write(data)
#         return self._success(self._serialize_product(product), message=_("Product updated."))

#     @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["DELETE"], type="json", csrf=False)
#     def delete_product(self, product_id, **kwargs):
#         """DELETE /api/v1/products/:id - Archive product (soft delete)."""
#         return self._handle_route(lambda env: self._delete_product(env, product_id))

#     def _delete_product(self, env, product_id):
#         product = env["product.template"].browse(product_id)
#         if not product.exists():
#             raise MissingError(_("Product #%s not found.") % product_id)

#         if not product.active:
#             return self._success(
#                 {"id": product.id, "active": False},
#                 message=_("Product already archived.")
#             )

#         product.write({"active": False})
#         _logger.info("Product archived: id=%s, name=%s", product.id, product.name)
#         return self._success(
#             {"id": product.id, "active": False},
#             message=_("Product archived.")
#         )
    
#     @http.route("/api/v1/products/search", auth="public", methods=["POST"], type="json", csrf=False)
#     def search_products(self, **kwargs):
#         """POST /api/v1/products/search - Search products with domain filters."""
#         return self._handle_route(lambda env: self._search_products(env))
    
#     def _search_products(self, env):
#         data = self._parse_json_data()
#         query = data.get("query", "")
#         limit = min(data.get("limit", 50), 200)
        
#         domain = [("active", "=", True)]
        
#         if query:
#             domain += [
#                 "|", "|", "|",
#                 ("name", "ilike", query),
#                 ("default_code", "ilike", query),
#                 ("barcode", "ilike", query),
#                 ("description", "ilike", query),
#             ]
        
#         # Additional filters from request
#         if data.get("category_id"):
#             domain.append(("categ_id", "=", int(data["category_id"])))
        
#         if data.get("min_price"):
#             domain.append(("list_price", ">=", float(data["min_price"])))
        
#         if data.get("max_price"):
#             domain.append(("list_price", "<=", float(data["max_price"])))
        
#         products = env["product.template"].search_read(
#             domain=domain,
#             fields=["id", "name", "default_code", "barcode", "list_price", 
#                    "qty_available", "categ_id"],
#             limit=limit,
#         )
        
#         return self._success({
#             "items": products,
#             "total": len(products),
#         })

from odoo import http, fields, _  
from odoo.http import request
from odoo.exceptions import MissingError, ValidationError
from .common import HavanoApiControllerMixin

import logging
_logger = logging.getLogger(__name__)

class HavanoProductsController(HavanoApiControllerMixin, http.Controller):
    
    def _serialize_product(self, product):
        """Convert product.template to API response dict with ALL fields."""
        has_detailed_type = "detailed_type" in product._fields
        
        # Taxes
        taxes = product.taxes_id
        supplier_taxes = product.supplier_taxes_id
        
        # Variants
        variants = []
        for variant in product.product_variant_ids:
            variants.append({
                "id": variant.id,
                "default_code": variant.default_code or "",
                "barcode": variant.barcode or "",
                "lst_price": variant.lst_price,
                "standard_price": variant.standard_price,
                "active": variant.active,
                "weight": variant.weight,
                "volume": variant.volume,
                "attributes": [{
                    "attribute_name": ptav.attribute_id.name,
                    "value_name": ptav.name,
                    "price_extra": ptav.price_extra,
                } for ptav in variant.product_template_attribute_value_ids],
            })
        
        # Suppliers/Vendors
        suppliers = []
        for seller in product.seller_ids:
            suppliers.append({
                "id": seller.id,
                "partner_id": seller.partner_id.id,
                "partner_name": seller.partner_id.name,
                "product_code": seller.product_code or "",
                "product_name": seller.product_name or "",
                "price": seller.price,
                "discount": seller.discount,
                "min_qty": seller.min_qty,
                "delay": seller.delay,
                "currency_id": seller.currency_id.id,
                "currency_name": seller.currency_id.name,
                "date_start": str(seller.date_start) if seller.date_start else None,
                "date_end": str(seller.date_end) if seller.date_end else None,
            })
        
        # Pricelist Rules
        pricelist_rules = []
        for rule in product.pricelist_rule_ids:
            pricelist_rules.append({
                "id": rule.id,
                "pricelist_id": rule.pricelist_id.id,
                "pricelist_name": rule.pricelist_id.name,
                "applied_on": rule.applied_on,
                "compute_price": rule.compute_price,
                "fixed_price": rule.fixed_price,
                "percent_price": rule.percent_price,
                "price_discount": rule.price_discount,
                "price_surcharge": rule.price_surcharge,
                "price_round": rule.price_round,
                "price_markup": rule.price_markup,
                "price_min_margin": rule.price_min_margin,
                "price_max_margin": rule.price_max_margin,
                "min_quantity": rule.min_quantity,
                "date_start": str(rule.date_start) if rule.date_start else None,
                "date_end": str(rule.date_end) if rule.date_end else None,
            })
        
        # Packagings/UoMs
        packagings = []
        for uom in product.uom_ids:
            packagings.append({
                "id": uom.id,
                "name": uom.name,
                "barcode": uom.barcode if hasattr(uom, 'barcode') else "",
            })
        
        return {
            # === BASIC INFO ===
            "id": product.id,
            "name": product.name or "",
            "display_name": product.display_name,
            "sequence": product.sequence,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            
            # === PRICING ===
            "list_price": product.list_price,
            "standard_price": product.standard_price,
            "currency_id": product.currency_id.id,
            "currency_name": product.currency_id.name,
            "cost_currency_id": product.cost_currency_id.id,
            "cost_currency_name": product.cost_currency_id.name,
            
            # === STATUS ===
            "active": product.active,
            "sale_ok": product.sale_ok,
            "purchase_ok": product.purchase_ok,
            
            # === PRODUCT TYPE ===
            "product_type": product.detailed_type if has_detailed_type else product.type,
            "service_tracking": product.service_tracking,
            
            # === CATEGORY ===
            "category": product.categ_id.name or "",
            "category_id": product.categ_id.id,
            "category_complete_name": product.categ_id.complete_name or "",
            
            # === UNIT OF MEASURE ===
            "uom": product.uom_id.name or "",
            "uom_id": product.uom_id.id,
            "uom_name": product.uom_name or "",
            "packagings": packagings,
            
            # === STOCK ===
            "qty_available": product.qty_available,
            "virtual_available": product.virtual_available if hasattr(product, 'virtual_available') else 0,
            "incoming_qty": product.incoming_qty if hasattr(product, 'incoming_qty') else 0,
            "outgoing_qty": product.outgoing_qty if hasattr(product, 'outgoing_qty') else 0,
            
            # === DESCRIPTIONS ===
            "description": product.description or "",
            "description_sale": product.description_sale or "",
            "description_purchase": product.description_purchase or "",
            
            # === PHYSICAL ===
            "weight": product.weight,
            "volume": product.volume,
            "weight_uom_name": product.weight_uom_name or "",
            "volume_uom_name": product.volume_uom_name or "",
            
            # === TAGS ===
            "tags": [{
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "visible_to_customers": tag.visible_to_customers,
            } for tag in product.product_tag_ids],
            
            # === TAXES ===
            "taxes": [{
                "id": tax.id,
                "name": tax.name,
                "amount": tax.amount,
                "type_tax_use": tax.type_tax_use,
            } for tax in taxes],
            "supplier_taxes": [{
                "id": tax.id,
                "name": tax.name,
                "amount": tax.amount,
            } for tax in supplier_taxes],
            
            # === ATTRIBUTES & VARIANTS ===
            "has_configurable_attributes": product.has_configurable_attributes,
            "is_dynamically_created": product.is_dynamically_created,
            "variant_count": product.product_variant_count,
            "variant_id": product.product_variant_id.id if product.product_variant_id else False,
            "variants": variants,
            
            # Attribute Lines
            "attribute_lines": [{
                "id": line.id,
                "attribute_id": line.attribute_id.id,
                "attribute_name": line.attribute_id.name,
                "display_type": line.attribute_id.display_type,
                "create_variant": line.attribute_id.create_variant,
                "sequence": line.sequence,
                "values": [{
                    "id": val.id,
                    "name": val.name,
                    "price_extra": val.price_extra,
                    "html_color": val.html_color or "",
                    "is_custom": val.is_custom,
                    "image": val.image.decode() if val.image else None,
                } for val in line.product_template_value_ids],
            } for line in product.attribute_line_ids],
            
            # === SUPPLIERS ===
            "suppliers": suppliers,
            
            # === PRICELIST RULES ===
            "pricelist_rules": pricelist_rules,
            
            # === COMPANY ===
            "company_id": product.company_id.id,
            "company_name": product.company_id.name,
            
            # === PROPERTIES ===
            "properties": product.product_properties or {},
            
            # === FAVORITE ===
            "is_favorite": product.is_favorite,
            
            # === DOCUMENTS ===
            "document_count": product.product_document_count,
            
            # === IMAGE ===
            "has_image": bool(product.image_1920),
            "image_128": product.image_128.decode() if product.image_128 else None,
            
            # === COMBO ===
            "combo_ids": [combo.id for combo in product.combo_ids] if product.combo_ids else [],
            
            # === TOOLTIP ===
            "tooltip": product.product_tooltip or "",
        }
    
    # =========================================================================
    # ENDPOINTS
    # =========================================================================
    
    @http.route("/api/v1/products", auth="public", methods=["GET"], type="json", csrf=False)
    def list_products(self, limit=100, offset=0, order="id desc", **kwargs):
        """GET /api/v1/products - List products with pagination."""
        return self._handle_route(lambda env: self._list_products(env, limit, offset, order))
    
    def _list_products(self, env, limit, offset, order):
        try:
            limit = min(int(limit), 500)
            offset = int(offset) if offset else 0
        except (ValueError, TypeError):
            limit, offset = 100, 0
        
        product_model = env["product.template"]
        has_detailed_type = "detailed_type" in product_model._fields
        type_field = "detailed_type" if has_detailed_type else "type"

        domain = [("active", "=", True)]
        
        products = product_model.search(domain, limit=limit, offset=offset, order=order)
        
        items = [self._serialize_product(p) for p in products]
        total = product_model.search_count(domain)
        
        return self._success({
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        })
    
    @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["GET"], type="json", csrf=False)
    def get_product(self, product_id, **kwargs):
        """GET /api/v1/products/:id - Get single product."""
        return self._handle_route(lambda env: self._get_product(env, product_id))
    
    def _get_product(self, env, product_id):
        product = env["product.template"].browse(product_id)
        if not product.exists():
            raise MissingError(_("Product #%s not found.") % product_id)
        
        return self._success(self._serialize_product(product))
    
    @http.route("/api/v1/products", auth="public", methods=["POST"], type="json", csrf=False)
    def create_product(self, **kwargs):
        """POST /api/v1/products - Create or update product by SKU."""
        return self._handle_route(lambda env: self._upsert_product(env))
    
    def _upsert_product(self, env):
        data = self._parse_json_data()
        sku = data.get("default_code") or data.get("sku")
        
        if not sku:
            raise ValidationError(_("Product SKU (default_code) is required."))
        
        if not data.get("name"):
            data["name"] = sku
        
        # Check existing by SKU
        product = env["product.template"].search([
            ("default_code", "=", str(sku).strip())
        ], limit=1)
        
        if product:
            product.write(data)
            msg = _("Product updated.")
            status = 200
        else:
            product = env["product.template"].create(data)
            msg = _("Product created.")
            status = 201
        
        _logger.info("Product %s: id=%s, sku=%s", "updated" if status == 200 else "created", 
                    product.id, sku)
        
        return self._success(self._serialize_product(product), message=msg, status=status)
    
    @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["PUT", "POST"], type="json", csrf=False)
    def update_product(self, product_id, **kwargs):
        """PUT /api/v1/products/:id - Update product."""
        return self._handle_route(lambda env: self._update_product(env, product_id))
    
    def _update_product(self, env, product_id):
        data = self._parse_json_data()
        product = env["product.template"].browse(product_id)
        
        if not product.exists():
            raise MissingError(_("Product #%s not found.") % product_id)
        
        if not data:
            raise ValidationError(_("No data provided for update."))
        
        product.write(data)
        return self._success(self._serialize_product(product), message=_("Product updated."))

    @http.route("/api/v1/products/<int:product_id>", auth="public", methods=["DELETE"], type="json", csrf=False)
    def delete_product(self, product_id, **kwargs):
        """DELETE /api/v1/products/:id - Archive product (soft delete)."""
        return self._handle_route(lambda env: self._delete_product(env, product_id))

    def _delete_product(self, env, product_id):
        product = env["product.template"].browse(product_id)
        if not product.exists():
            raise MissingError(_("Product #%s not found.") % product_id)

        if not product.active:
            return self._success(
                {"id": product.id, "active": False},
                message=_("Product already archived.")
            )

        product.write({"active": False})
        _logger.info("Product archived: id=%s, name=%s", product.id, product.name)
        return self._success(
            {"id": product.id, "active": False},
            message=_("Product archived.")
        )
    
    @http.route("/api/v1/products/search", auth="public", methods=["POST"], type="json", csrf=False)
    def search_products(self, **kwargs):
        """POST /api/v1/products/search - Search products with domain filters."""
        return self._handle_route(lambda env: self._search_products(env))
    
    def _search_products(self, env):
        data = self._parse_json_data()
        query = data.get("query", "")
        limit = min(data.get("limit", 50), 200)
        
        domain = [("active", "=", True)]
        
        if query:
            domain += [
                "|", "|", "|",
                ("name", "ilike", query),
                ("default_code", "ilike", query),
                ("barcode", "ilike", query),
                ("description", "ilike", query),
            ]
        
        if data.get("category_id"):
            domain.append(("categ_id", "=", int(data["category_id"])))
        
        if data.get("min_price"):
            domain.append(("list_price", ">=", float(data["min_price"])))
        
        if data.get("max_price"):
            domain.append(("list_price", "<=", float(data["max_price"])))
        
        products = env["product.template"].search(domain, limit=limit)
        
        return self._success({
            "items": [self._serialize_product(p) for p in products],
            "total": len(products),
        })