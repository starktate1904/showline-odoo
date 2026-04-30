# -*- coding: utf-8 -*-
# Part of Erp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Appointment Testing Module',
    'version': "1.0",
    'category': 'Hidden/Tests',
    'sequence': 9999,
    'summary': 'Appointment Testing Module',
    'website': 'https://dev.erpsys.top/app/appointments',
    'description': """
Take into account the working schedule (sick leaves, part time, ...) of employees when scheduling appointments
--------------------------------------------------------------------------------------------------------------
""",
    'depends': [
        'appointment_crm',
        'appointment_hr',
        'google_calendar',
        'microsoft_calendar',
        'website_appointment',
    ],
    'author': 'Erp S.A.',
    'license': 'OEEL-1',
}
