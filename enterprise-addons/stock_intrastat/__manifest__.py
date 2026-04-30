# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Intrastat',
    'category': 'Supply Chain/Inventory',
    'description': """
A module that add the stock management in intrastat reports.
============================================================

This module gives the details of the goods traded between the countries of
European Union.""",
    'depends': ['stock_account', 'account_intrastat'],
    'data': [
        'views/stock_warehouse_view.xml',
    ],
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
