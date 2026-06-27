from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('hospital.appointment',string='Appointment',domain=[('state','=','draft')])
    reason = fields.Char(string='Reason')
    date_cancel = fields.Date(string='Cancellation Date', default=fields.Date.today)

    # @api.model
    # def default_get(self, fields):
    #     res = super(CancelAppointmentWizard, self).default_get(fields)
    #     res['date_cancel'] = datetime.date.today()
    #     if self.env.context.get('active_id'):
    #         res['appointment_id'] = self.env.context.get('active_id')
    #     return res

    def action_cancel(self):
        if self.appointment_id.booking_date <= fields.Date.today():
            raise ValidationError(
                "You cannot cancel an appointment on or after its scheduled date."
            )

        self.appointment_id.write({
            'state': 'cancel',
        })

        return {'type': 'ir.actions.act_window_close'}
