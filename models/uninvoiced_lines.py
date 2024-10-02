from odoo import fields, models


class SaleOrderWizard(models.TransientModel):
    _name = "uninvoiced.wizard.line"

    uninvoiced_wizard_id = fields.Many2one("sale.order.wizard", string="Warning")
    number = fields.Char(string="Order Number")
    order_date = fields.Date(string="Order Date")
    customer = fields.Char(string="Customer")
    salesperson = fields.Many2one("res.users")

