from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'ref'
    _order = "id desc"

    doctor_id = fields.Many2one('res.users', string='Doctor', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='restrict')
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string='Pharmacy Lines')
    gender = fields.Selection(related='patient_id.gender', store=True)
    appointment_time = fields.Datetime(string='Appointment Time', default=fields.Datetime.now)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today)
    ref = fields.Char(string='Reference', default='New', readonly=True, copy=False)
    patient_ref = fields.Char(string="Patient Reference", related="patient_id.ref", store=True, readonly=True)
    prescription = fields.Html(string='Prescription')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ], string='Priority')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], default='draft', tracking=True)
    hide_sales_price = fields.Boolean(string='Hide Sales Price')
    operation_id = fields.Many2one('hospital.operation', string='Operation')
    duration = fields.Float(string='Duration')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
                
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("Only appointments in Draft state can be deleted."))
        return super().unlink()

    def action_in_consultation(self):
        for rec in self:
            rec.state = 'in_consultation'

    # def action_done(self):
    #     for rec in self:
    #         rec.state = 'done'

    def action_done(self):
        for rec in self:
            if rec.state != "in_consultation":
                raise ValidationError("Only appointments that are in consultation can be marked as Done.")

            rec.state = "done"

    def action_cancel(self):
        action = self.env.ref(
            'hospital_management.action_cancel_appointment'
        ).read()[0]

        action['context'] = {
            'default_appointment_id': self.id
        }

        return action

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'



class AppointmentPharmacyLines(models.Model):

    _name = 'appointment.pharmacy.lines'
    _description = 'Appointment Pharmacy Lines'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    price_unit = fields.Float(related='product_id.list_price', string='Sales Price')
    qty = fields.Integer(string='Quantity', default=1)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', required=True, ondelete='cascade')