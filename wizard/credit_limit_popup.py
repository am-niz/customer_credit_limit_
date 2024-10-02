from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Custom Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order",
                                    default=lambda self: self.env.context.get('default_sale_order_id'))
    sale_order_ids = fields.One2many('uninvoiced.wizard.line', "uninvoiced_wizard_id", string="Uninvoiced Orders")
    account_move_line_ids = fields.One2many("sale.order.wizard.line", "wizard_id", string="Pending Invoices")
    partner_id = fields.Many2one('res.partner', string="Customer")
    credit_limit = fields.Float(string="Credit Limit", related="partner_id.credit_limit")
    unpaid_amt = fields.Float(string="Unpaid Amount", default=0.0)
    order_amt = fields.Float(string="Order Amount")
    exceed_amt = fields.Float(string="Exceeded Amount", compute="_compute_exceed_amt")
    has_pending_invoices = fields.Boolean(string="Has Pending Invoices", compute="_compute_has_pending_invoices")
    has_uninvoiced_orders = fields.Boolean(string="Has Uninvoiced Orders", compute="_compute_has_uninvoiced_orders")

    @api.depends('account_move_line_ids')
    def _compute_has_pending_invoices(self):
        for wizard in self:
            wizard.has_pending_invoices = bool(wizard.account_move_line_ids)

    @api.depends('sale_order_ids')
    def _compute_has_uninvoiced_orders(self):
        for wizard in self:
            wizard.has_uninvoiced_orders = bool(wizard.sale_order_ids)

    @api.model
    def default_get(self, fields):  # default_get is for prepopulating
        res = super(SaleOrderWizard, self).default_get(fields)
        sale_order_id = self.env.context.get('default_sale_order_id')
        if sale_order_id:
            sale_order = self.env['sale.order'].browse(sale_order_id)
            unpaid_invoices = self.env['account.move'].search([
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
                ('partner_id', '=', sale_order.partner_id.id)
            ])
            uninvoiced_orders = self.env["sale.order"].search([
                ('partner_id', '=', sale_order.partner_id.id),
                ('invoice_status', 'in', ['no', 'to invoice']),
                ('id', '!=', sale_order_id)  # Exclude current order
            ])

            res.update({
                "partner_id": sale_order.partner_id.id,
                "order_amt": sale_order.amount_total,
            })

            if unpaid_invoices:
                invoice_lines = []
                for invoice in unpaid_invoices:
                    # Odoo syntax for creating one2many or many2many records
                    invoice_lines.append((0, 0, {
                        "name": invoice.name,
                        "customer": invoice.invoice_partner_display_name,
                        "invoice_date": invoice.invoice_date,
                        "due_date": invoice.invoice_date_due,
                        "total": invoice.amount_total_signed,
                        "payment_state": invoice.payment_state,
                    }))
                res.update({
                    "account_move_line_ids": invoice_lines,
                    "unpaid_amt": sum(invoice.amount_total_signed for invoice in unpaid_invoices),
                })
            elif uninvoiced_orders:
                order_lines = []
                for order in uninvoiced_orders:
                    order_lines.append((0, 0, {
                        "number": order.name,
                        "order_date": order.create_date,
                        "customer": order.partner_id.name,
                        "salesperson": order.user_id.name,
                    }))
                res.update({
                    "sale_order_ids": order_lines,
                    "unpaid_amt": sum(order.amount_total for order in uninvoiced_orders),
                })

        return res

    @api.depends('unpaid_amt', 'order_amt', 'credit_limit')
    def _compute_exceed_amt(self):
        for wizard in self:
            wizard.exceed_amt = max(0, wizard.unpaid_amt + wizard.order_amt - wizard.credit_limit)

    def action_exceed_limit(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            raise UserError("Only salespeople can request to exceed credit limits.")

        # Find the admin user
        admin_user = self.env['res.users'].search([('login', '=', 'admin')], limit=1)
        if not admin_user:
            raise UserError("Admin user not found.")

        # Create an approval request
        approval_request = self.env['approval.request'].create({
            'name': f"Credit Limit Exceed Request for {self.partner_id.name}",
            'request_owner_id': self.env.user.id,
            'approver_ids': [(0, 0, {'user_id': admin_user.id})],
            'sale_order_id': self.sale_order_id.id,
            'partner_id': self.partner_id.id,
            'credit_limit': self.credit_limit,
            'exceed_amount': self.exceed_amt,
        })

        # Send email to the admin
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++==")
        print(f"Sending approval email for: Partner: {self.partner_id.name}, Credit Limit: {self.credit_limit}, Exceed Amount: {self.exceed_amt}")
        template = self.env.ref('customer_credit_limit.credit_limit_exceed_request_email_template')
        if template:
            template.send_mail(approval_request.id, email_layout_xmlid='mail.mail_notification_light', force_send=True)

        # Create a link to the approval request

        # if Odoo is running at https://mycompany.odoo.com, this code would return that URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_url = f"{base_url}/web#id={approval_request.id}&view_type=form&model=approval.request"

        # Post a message with the link
        self.sale_order_id.message_post(body=f"""
            Credit limit exceed request sent to admin for approval.
        # """)
        #
        # # Create a new message with the template
        # mail_message = self.env['mail.message'].create({
        #     'subject': template.subject,
        #     'body': template.body_html,
        #     'email_from': template.email_from,
        #     'author_id': self.env.user.partner_id.id,
        #     'model': 'sale.order',
        #     'res_id': self.sale_order_id.id,
        #     'message_type': 'email',
        #     'subtype_id': self.env.ref('mail.mt_comment').id,
        # })

        return {
            'type': 'ir.actions.act_window_close'
        }