{
    "name": "Customer Supplier Separation",
    "version": "19.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Separate customer and supplier/vendor contacts with filtered domains",
    "description": """
Customer Supplier Separation
============================

A professional, production-ready module by **Showline Solutions** that separates 
customer and supplier (vendor) contacts with dedicated flags, computed contact types, 
and filtered domains in Sales and Purchase orders.

Key Features
------------

* **Customer & Supplier Flags** — Dedicated `is_customer` and `is_supplier` boolean 
  fields on contacts with automatic computation.
* **Computed Contact Type** — Automatically determines if a contact is a Customer, 
  Supplier, Both, or None based on their flags.
* **Filtered Domains** — Sales orders only show customers; Purchase orders only 
  show suppliers (configurable).
* **Auto-Categorization** — Contacts created from Sales are auto-marked as customers; 
  from Purchases as suppliers.
* **Vendor List Integration** — Suppliers automatically appear in the Vendor list 
  (res.partner `supplier` rank is synchronized).
* **Search Filters** — Quick filters for "Only Customers", "Only Suppliers", and "Both".
* **License Protected** — One-time license key activation with 12-hour auto-validation.
* **Professional UI** — Purple/amber color scheme with clear status indicators.

How It Works
------------

1. Activate your license key in **Settings → General Settings**.
2. Configure behavior options (auto-mark, filtered domains).
3. When creating contacts from Sales orders, they're auto-marked as customers.
4. When creating contacts from Purchase orders, they're auto-marked as suppliers.
5. Sales partner dropdown only shows customers; Purchase only shows suppliers.

License Activation
------------------

1. Go to **Settings → General Settings → Customer Supplier Separation License**.
2. Enter your license key: XXXX-XXXX-XXXX-XXXX.
3. Click "Validate & Activate License".
4. Green badge confirms activation.

About Showline Solutions
------------------------

Developed by **Showline Solutions** — Professional Odoo customizations.
    """,
    "author": "Showline Solutions",
    "website": "https://showline.co.zw",
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
    "images": [
        "static/description/icon.svg",
        "static/description/icon.png",
    ],
    "installable": True,
    "application": False,
}