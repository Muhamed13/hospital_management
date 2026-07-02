from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    ref = fields.Char(string='Reference', default='New', readonly=True, copy=False)
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', search='_search_age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], tracking=True, default='male')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Image(string='Image')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    tag_ids = fields.Many2many('patient.tag', string='Tags')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    marital_status = fields.Selection([
        ('married', 'Married'),
        ('single', 'Single'),
    ], string='Material Status', default='single', tracking=True)
    partner_name = fields.Char(string='Partner Name')
    emergency_contact_name = fields.Char(string='Emergency Name')
    emergency_contact_phone = fields.Char(string='Emergency Phone')


    # ===== Compute Methods =====
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)

    @api.depends("date_of_birth")
    def _compute_age(self):
        """Compute patient age from date of birth."""

        today = date.today()

        for rec in self:
            if rec.date_of_birth:
                age = today.year - rec.date_of_birth.year

                if (today.month, today.day) < (
                        rec.date_of_birth.month,
                        rec.date_of_birth.day
                ):
                    age -= 1

                rec.age = age
            else:
                rec.age = 0

    # ===== Search Method =====
    def _search_age(self, operator, value):
        if operator != "=":
            raise NotImplementedError("This search currently supports only '=' operator.")

        today = date.today()

        date_to = today - relativedelta(years=value)
        date_from = date_to - relativedelta(years=1) + relativedelta(days=1)

        return [
            ("date_of_birth", ">=", date_from),
            ("date_of_birth", "<=", date_to),
        ]

    # ===== Constraint Methods =====
    @api.constrains('marital_status', 'partner_name')
    def _check_partner_name(self):
        for rec in self:
            if rec.marital_status == 'married' and not rec.partner_name:
                raise ValidationError(_("Partner Name is required for married patients."))

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_("Date of Birth cannot be in the future."))

    # ===== CRUD Method =====
    @api.model_create_multi
    def create(self, vals_list):
        """Generate patient sequence before record creation."""

        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')

        return super().create(vals_list)

    # ===== OnDelete Method =====
    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_("You cannot delete a patient who has existing appointments."))

    # ===== Action Method=====
    def action_view_appointments(self):
        """Open appointments related to the current patient."""

        return {
            "type": "ir.actions.act_window",
            "name": _("Appointments"),
            "res_model": "hospital.appointment",
            "view_mode": "tree,form,calendar,activity",
            "domain": [("patient_id", "=", self.id)],
            "context": {
                "default_patient_id": self.id,
            },
            "target": "current",
        }