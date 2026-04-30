# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale Enterprise",
    'category': 'Sales',
    'summary': "Advanced Features for Sale Management",
    'description': "Contains advanced features for sale management.",
    'depends': ['sale', 'web_map'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
