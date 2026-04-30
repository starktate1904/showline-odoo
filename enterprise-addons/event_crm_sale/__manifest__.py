# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Event CRM Sale',
    'version': '1.0',
    'category': 'Marketing/Events',
    'website': 'https://dev.erpsys.top/app/events',
    'description': "Add information of sale order linked to the registration for the creation of the lead.",
    'depends': ['event_crm', 'event_sale'],
    'data': [
        'views/event_lead_rule_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'LGPL-3',
}
