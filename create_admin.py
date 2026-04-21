from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
user = env['res.users'].create({
    'name': 'Administrator',
    'login': 'Odooadmin@showline.com',
    'password': 'OdooAdmin@2026!',
    'email': 'Odooadmin@showline.com',
})
env.cr.commit()
print("Admin user created successfully!")
