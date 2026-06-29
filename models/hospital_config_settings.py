from odoo import fields, models

class HospitalSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cancel_days = fields.Integer(
        string="Cancellation Days",
        config_parameter="hospital_management.cancel_days",
    )