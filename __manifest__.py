{
    'name': 'Hospital Management',
    'author': 'Muhamed Helmy',
    'version': '17.0.1.0',
    'category': 'Hospital',
    'summary': 'Hospital Management System',
    'description': """
        Hospital Management System
    """,

    'depends': ['base',
                'mail',
                'product'],

    'data': [
        'security/ir.model.access.csv',

        'views/base_menu.xml',
        'views/patient_view.xml',
        'views/female_patient_view.xml',
        'views/appointment_view.xml',
    ],

    'demo': [],

    'auto_install': False,
    'license': 'LGPL-3',
    'application': True,
}