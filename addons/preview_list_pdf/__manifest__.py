{
    "name": "Preview List PDF",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "Inline PDF preview for every list view with license validation",
    "description": """
Preview List PDF
================

Adds a "Preview PDF" button to list views and renders the active list as an inline PDF.
Includes app-specific license activation and periodic validation.
    """,
    "author": "Custom",
    "website": "https://example.com",
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
    "installable": True,
    "application": False,
}
