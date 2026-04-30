from odoo import http, fields, _  
from odoo.http import request
from .common import HavanoApiControllerMixin

class HavanoStockController(HavanoApiControllerMixin, http.Controller):
    
    @http.route("/api/v1/stock/levels", auth="public", methods=["GET", "POST"], type="json", csrf=False)
    def get_stock_levels(self, limit=100, offset=0, **kwargs):
        """GET /api/v1/stock/levels - Get stock levels for all products."""
        return self._handle_route(lambda env: self._get_stock(env, limit, offset))
    
    def _get_stock(self, env, limit, offset):
        try:
            limit = min(int(limit), 500)
            offset = int(offset) if offset else 0
        except (ValueError, TypeError):
            limit, offset = 100, 0
        
        product_model = env["product.product"]
        type_field = "detailed_type" if "detailed_type" in product_model._fields else "type"
        products = product_model.search_read(
            domain=[(type_field, "=", "product")],
            fields=["id", "name", "default_code", "qty_available", 
                   "virtual_available", "incoming_qty", "outgoing_qty"],
            limit=limit,
            offset=offset,
            order="id desc",
        )
        
        return self._success({
            "items": products,
            "total": len(products),
        })
    
    @http.route("/api/v1/stock/low", auth="public", methods=["GET", "POST"], type="json", csrf=False)
    def get_low_stock(self, threshold=10, **kwargs):
        """GET /api/v1/stock/low?threshold=10 - Get products below threshold."""
        return self._handle_route(lambda env: self._get_low_stock(env, threshold))
    
    def _get_low_stock(self, env, threshold):
        try:
            threshold = float(threshold)
        except (ValueError, TypeError):
            threshold = 10
        
        product_model = env["product.product"]
        type_field = "detailed_type" if "detailed_type" in product_model._fields else "type"
        products = product_model.search_read(
            domain=[(type_field, "=", "product")],
            fields=["id", "name", "default_code", "qty_available", 
                   "virtual_available"],
            order="id desc",
            limit=500,
        )
        products = [p for p in products if float(p.get("qty_available", 0.0)) < threshold]
        products = sorted(products, key=lambda x: float(x.get("qty_available", 0.0)))[:100]
        
        return self._success({
            "items": products,
            "total": len(products),
            "threshold": threshold,
        })