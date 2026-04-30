{
    "name": "Customer Supplier Separation",
    "version": "19.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Separate customer and supplier contacts with filtered domains",
    "author": "Custom",
    "website": "https://example.com",
    "license": "OPL-1",
    "depends": ["base", "contacts", "sale_management", "purchase", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/license_data.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/settings_views.xml",
        "views/license_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "customer_supplier_separation/static/src/js/partner_type.js",
        ],
    },
    "installable": True,
    "application": False,
}
