from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('hospital.appointment',string='Appointment',domain=[('state','=','draft')])
    reason = fields.Char(string='Reason')
    date_cancel = fields.Date(string='Cancellation Date', default=fields.Date.today)

    @api.model
    def default_get(self, fields_list):
        """Prefill wizard values from the active appointment."""

        res = super().default_get(fields_list)

        res["date_cancel"] = fields.Date.today()

        active_id = self.env.context.get("active_id")
        if active_id:
            res["appointment_id"] = active_id

        return res

    def action_cancel(self):
        """Cancel the appointment if it satisfies the cancellation policy."""

        self.ensure_one()

        cancel_days = int(
            self.env["ir.config_parameter"].sudo()
            .get_param("hospital_management.cancel_days", default=1))
        booking_date = self.appointment_id.booking_date
        allowed_cancel_date = booking_date - relativedelta(days=cancel_days)

        if fields.Date.today() > allowed_cancel_date:
            raise ValidationError(
                f"Appointments can only be cancelled at least {cancel_days} day(s) before the booking date."
            )

        self.appointment_id.write({
            "state": "cancel",
        })

        return {
            "type": "ir.actions.act_window_close",
        }
