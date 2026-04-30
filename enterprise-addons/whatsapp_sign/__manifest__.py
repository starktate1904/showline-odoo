# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'WhatsApp-Sign',
    'category': 'WhatsApp',
    'summary': 'This module enables users to send signature requests via WhatsApp in Erp Sign',
    'description': """This module allows users to send signature requests via WhatsApp using Erp Sign""",
    'depends': ['sign', 'whatsapp'],
    'data': [
        'data/sign_request_whatsapp_templates.xml',
        'data/config_parameter_whatsapp_template.xml',
        'wizard/sign_send_request_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
    'auto_install': True
}
