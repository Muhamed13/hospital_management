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

    'data/patient_sequence.xml',
    'data/appointment_sequence.xml',
    'data/patient_tag_data.xml',

    'views/base_menu.xml',
    'views/patient_view.xml',
    'views/female_patient_view.xml',
    'views/appointment_view.xml',
    'views/patient_tag_view.xml',
    'views/hospital_config_settings_view.xml',
    'views/hospital_operation_view.xml',

    'wizard/cancel_appointment_view.xml',

    'report/appointment_report.xml',

    ],

    'auto_install': False,
    'license': 'LGPL-3',
    'application': True,
}