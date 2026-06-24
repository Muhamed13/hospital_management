from odoo import api, fields, models
from datetime import date

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    ref = fields.Char(string='Reference')
    date_of_birth = fields.Datetime(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], tracking=True, default='male')
    active = fields.Boolean(string='Active', default=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    image = fields.Image(string='Image')
    tag_ids = fields.Many2many('patient.tag', string='Tags')

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0
