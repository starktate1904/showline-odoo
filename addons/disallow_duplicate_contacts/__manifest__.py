{
    "name": "Disallow Duplicate Contacts",
    "version": "19.0.1.0.0",
    "category": "Contacts",
    "summary": "Prevent duplicate customer/vendor creation with configurable rules",
    "author": "Custom",
    "website": "https://example.com",
    "license": "OPL-1",
    "depends": ["base", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/license_data.xml",
        "views/license_views.xml",
    ],
    "installable": True,
    "application": False,
}
