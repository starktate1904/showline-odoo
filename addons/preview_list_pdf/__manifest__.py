{
    "name": "Preview List PDF",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "Generate PDF previews from any list view with dynamic column detection",
    "description": """
Preview List PDF
================

A professional, production-ready module by **Showline Solutions** that adds a 
**"Preview PDF"** button to every list view in Odoo, allowing users to instantly 
generate beautifully formatted PDF documents from any model.

Key Features
------------

* **Dynamic Column Detection** — The PDF automatically captures exactly the columns 
  visible in your current list view, respecting any column configuration, sorting, 
  and filtering you've applied.
* **Smart Pagination** — Respects the current page and record limit from your list 
  view, showing the same records you see on screen.
* **Auto-Orientation** — Automatically switches between portrait and landscape mode 
  based on the number of columns (5+ columns triggers landscape).
* **Image-Free Output** — Automatically filters out avatar, image, and icon fields 
  for clean, professional PDF output.
* **Beautiful Styling** — Clean, modern table design with branded header colors, 
  alternating rows, and professional typography.
* **License Protected** — One-time license key activation per database. Includes 
  automatic periodic validation to ensure continuous operation.
* **Fast & Efficient** — Optimized data fetching and rendering for large datasets.
* **Custom PDF Viewer** — Opens in a dedicated window with Print and Download 
  buttons for easy document handling.
* **Loading Animation** — Professional Lottie-powered loading overlay with progress 
  tracking while the PDF is being generated.

How It Works
------------

1. Navigate to any list view in Odoo (Sales Orders, Contacts, Products, etc.).
2. Configure your columns, filters, and pagination as desired.
3. Click the **"Preview PDF"** button in the control panel.
4. A loading overlay appears with a professional animation and progress bar.
5. The PDF opens in a new window showing exactly the data from your current view.

License Activation
------------------

This module requires a one-time license key to activate. To activate:

1. Go to **Settings → General Settings → Preview List PDF**.
2. Enter your license key in the format `XXXX-XXXX-XXXX-XXXX`.
3. Click **"Activate License"**.
4. Once activated, the license is validated periodically to ensure continued access.

**Note:** The module includes a built-in license manager with automatic validation 
via scheduled actions (every 12 hours).

Technical Notes
---------------

* Compatible with Odoo 17, 18, and 19.
* Works on both Community and Enterprise editions.
* Supports all models and custom fields.
* Handles relational fields (many2one, one2many, many2many) gracefully.
* Binary and image fields are automatically excluded from PDF output.

About Showline Solutions
------------------------

This module was developed by **Showline Solutions**, delivering professional 
Odoo customizations and business solutions.

    """,
    "author": "Showline Solutions",
    "website": "https://showline.co.zw",
    "license": "OPL-1",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/license_data.xml",
        "views/client_action.xml",
        "views/preview_templates.xml",
        "views/license_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "preview_list_pdf/static/src/js/preview_button.js",
            "preview_list_pdf/static/src/js/preview_page.js",
            "preview_list_pdf/static/src/xml/preview_page.xml",
            "preview_list_pdf/static/src/scss/preview_style.scss",
        ],
    },
    "images": [
        "static/description/icon.svg",
    ],
    "installable": True,
    "application": False,
}