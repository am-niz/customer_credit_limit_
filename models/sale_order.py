from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            if order.amount_total > order.partner_id.credit_limit and not self.env.user.has_group('base.group_system'):
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Credit Limit Exceeded',
                    'res_model': 'sale.order.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_sale_order_id': order.id}
                }
        return super(SaleOrder, self).action_confirm()


