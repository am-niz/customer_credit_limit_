from odoo import models, fields, api


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Credit Limit Exceed Approval Request'

    name = fields.Char(string='Request Name', required=True)
    request_owner_id = fields.Many2one('res.users', string='Requestor', required=True)
    approver_ids = fields.One2many('approval.request.approver', 'request_id', string='Approvers')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Customer')
    credit_limit = fields.Float(string='Credit Limit')
    exceed_amount = fields.Float(string='Exceed Amount')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending', tracking=True)

    def action_approve(self):
        self.ensure_one()
        if self.env.user.has_group('base.group_system'):
            self.write({'state': 'approved'})
            self._send_approval_notification()
            if self.sale_order_id:
                self.sale_order_id.action_confirm()

    def action_reject(self):
        self.ensure_one()
        if self.env.user.has_group('base.group_system'):
            self.write({'state': 'rejected'})
            self._send_rejection_notification()

    def _send_approval_notification(self):
        template = self.env.ref('customer_credit_limit.credit_limit_approval_notification_template')
        if template:
            template.send_mail(self.id, email_layout_xmlid='mail.mail_notification_light', force_send=True)
        self.sale_order_id.message_post(body="Credit limit exceed request has been approved.")

    def _send_rejection_notification(self):
        template = self.env.ref('customer_credit_limit.credit_limit_rejection_notification_template')
        if template:
            template.send_mail(self.id, email_layout_xmlid='mail.mail_notification_light', force_send=True)
        self.sale_order_id.message_post(body="Credit limit exceed request has been rejected.")


class ApprovalRequestApprover(models.Model):
    _name = 'approval.request.approver'
    _description = 'Approval Request Approver'

    request_id = fields.Many2one('approval.request', string='Approval Request')
    user_id = fields.Many2one('res.users', string='Approver')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')