from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from urllib.parse import quote

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'ref'
    _order = "id desc"

    ref = fields.Char(string='Reference', default='New', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], default='draft', tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ], string='Priority')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='restrict')
    doctor_id = fields.Many2one('res.users', string='Doctor', required=True, tracking=True)
    operation_id = fields.Many2one('hospital.operation', string='Operation')
    appointment_time = fields.Datetime(string='Appointment Time', default=fields.Datetime.now)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today)
    duration = fields.Float(string='Duration')
    prescription = fields.Html(string='Prescription')
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines',
                                        'appointment_id', string='Pharmacy Lines')
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', currency_field='currency_id')
    gender = fields.Selection(related='patient_id.gender', store=True)
    patient_ref = fields.Char(string="Patient Reference", related="patient_id.ref", store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    hide_sales_price = fields.Boolean(string='Hide Sales Price')

    # ===== Compute Method =====
    @api.depends('pharmacy_line_ids.price_subtotal')
    def _compute_amount_total(self):
        """Compute total amount from pharmacy lines."""

        for rec in self:
            rec.amount_total = sum(rec.pharmacy_line_ids.mapped('price_subtotal'))

    # ===== CRUD Methods =====
    @api.model_create_multi
    def create(self, vals_list):
        """Generate appointment reference before record creation."""

        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
                
        return super().create(vals_list)

    def unlink(self):
        """Allow deleting appointments only when they are in draft state."""

        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("Only appointments in Draft state can be deleted."))
        return super().unlink()

    # ===== Workflow Actions =====
    def action_in_consultation(self):
        for rec in self:
            rec.state = 'in_consultation'

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

    # ===== External Action =====
    def action_share_whatsapp(self):
        self.ensure_one()

        if not self.patient_id.phone:
            raise UserError(_("Missing phone number in patient record."))

        message = (
            f"Hello {self.patient_id.name}, "
            f"your appointment reference is {self.ref}. "
            f"Thank you."
        )
        whatsapp_url = (
            f"https://api.whatsapp.com/send?"
            f"phone={self.patient_id.phone}&text={quote(message)}"
        )
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_url,
        }



class AppointmentPharmacyLines(models.Model):

    _name = 'appointment.pharmacy.lines'
    _description = 'Appointment Pharmacy Lines'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    price_unit = fields.Float(related='product_id.list_price', string='Sales Price', digits='Product Price')
    qty = fields.Integer(string='Quantity', default=1)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment',
                                     required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal',
                                     currency_field='currency_id')

    # ===== Compute Method =====
    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        """Compute pharmacy line subtotal."""

        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty