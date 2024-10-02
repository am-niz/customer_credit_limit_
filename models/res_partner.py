from odoo import fields, models


class PartnerCategory(models.Model):
    _inherit = "res.partner"

    credit_limit = fields.Float(stirng="Credit Limit")

