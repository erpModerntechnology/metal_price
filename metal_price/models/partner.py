from odoo import models, fields, api,_

class ResPartner(models.Model):
    _inherit = 'res.partner'
    def _invoice_total_weight(self):
        for rec in self:
            move_list = []
            all_invoice = self.env['account.move'].search([])

            for inv in all_invoice:

                for line in inv.invoice_line_ids:

                    if line.product_uom_id.category_id.name == 'Weight':
                        move_list.append(inv.id)

            rec.total_invoiced_weight = len(move_list)

    total_invoiced_weight = fields.Monetary(compute='_invoice_total_weight', string="Total Invoiced",
                                     groups='account.group_account_invoice,account.group_account_readonly')

    def action_to_open_invoice_weight(self):
        move_list = []
        all_invoice = self.env['account.move'].search([])
        for inv in all_invoice:

            for line in inv.invoice_line_ids:
                if line.product_uom_id.category_id.name == 'Weight':
                    move_list.append(inv.id)

        domain = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('partner_id', 'child_of', self.id),
            ('id', 'in', move_list),
        ]

        return {
            'name': _('invoices With weight'),
            'domain': domain,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

