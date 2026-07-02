from odoo import fields, models, api

class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _description = "Hospital Operation"
    _order = "sequence,id"

    name = fields.Char(string='Name', required=True)
    doctor_id = fields.Many2one("res.users", string="Doctor", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    _sql_constraints = [("operation_name_unique", "unique(name)", "Operation name must be unique.")]

    # ===== CRUD Methods =====
    @api.model
    def name_create(self, name):
        """Create a new operation from a Many2one field."""

        operation = self.create({
            "name": name,
        })
        return operation.name_get()[0]