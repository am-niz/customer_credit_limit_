from odoo import fields, models

PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
]


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard.line"

    wizard_id = fields.Many2one("sale.order.wizard", string="Warning")
    name = fields.Char(string="Number")
    customer = fields.Char(string="Customer")
    invoice_date = fields.Date(string="Invoice Date")
    due_date = fields.Date(string="Due Date")
    total = fields.Float(string="Total")
    payment_state = fields.Selection(
        selection=PAYMENT_STATE_SELECTION,
        string="Payment Status",
    )


