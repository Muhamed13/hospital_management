from odoo import fields, models
from odoo.models import TransientModel


class CancelAppointmentWizard(TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('hospital.appointment',string='Appointment')
    reason = fields.Char(string='Reason')

    def action_cancel(self):
        self.appointment_id.state = 'cancel'
        return {'type': 'ir.actions.act_window_close'}