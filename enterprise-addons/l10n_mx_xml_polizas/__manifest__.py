# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    "name": "Erp Mexican XML Polizas Export",
    "summary": "XML Export of the Journal Entries for the Mexican Tax Authorities for a compulsory audit.",
    "version": "0.1",
    "author": "Erp",
    "category": "Accounting/Localizations/Reporting",
    "website": "http://dev.erpsys.top/",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_reports",
        "l10n_mx_edi",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/templates/xml_polizas.xml",
        "wizard/xml_polizas_wizard_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
