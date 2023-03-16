
from odoo import models, fields, api,_
class ResPartner(models.Model):
    _inherit = 'res.partner'
    def _invoice_total_weight(self):
        for rec in self:
            move_list = []
            all_invoice = self.env['account.move'].search([])
            print(all_invoice)
            for inv in all_invoice:
                print(inv)
                for line in inv.invoice_line_ids:
                    print(line.product_uom_id.category_id.name)
                    if line.product_uom_id.category_id.name == 'Weight':
                        move_list.append(inv.id)
            print(move_list)
            rec.total_invoiced_weight = len(move_list)

    total_invoiced_weight = fields.Monetary(compute='_invoice_total_weight', string="Total Invoiced",
                                     groups='account.group_account_invoice,account.group_account_readonly')

    def action_to_open_invoice_weight(self):
        move_list = []
        all_invoice = self.env['account.move'].search([])
        print(all_invoice)
        for inv in all_invoice:
            print(inv.move_type)
            print(inv)
            for line in inv.invoice_line_ids:
                print(line.product_uom_id.category_id.name)
                if line.product_uom_id.category_id.name == 'Weight':
                    move_list.append(inv.id)
        print(move_list)

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


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'



    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                                                                             quantity=quantity, currency=currency,
                                                                             product=product, partner=partner,
                                                                             is_refund=move_type in (
                                                                             'out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi currency, round before it's use for computing debit credit

        if self.product_uom_id.category_id.name == "Weight":
            res['price_subtotal'] = self.price_unit * self.move_id.metal_price * self.quantity
        else:
            res['price_subtotal'] = self.price_unit * self.quantity
        print(res)

        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        print(res)
        return res


    @api.onchange('product_id')
    def onchange_method(self):
        if self.product_uom_id.category_id.name=="Weight":
            print(self.price_unit*self.move_id.metal_price*self.quantity )
            self.price_subtotal = self.price_unit*self.move_id.metal_price*self.quantity
        else:
            self.price_subtotal = self.price_unit * self.quantity


    name = fields.Char()

class AccountMove(models.Model):
    _inherit = 'account.move'
    def get_metal_price(self):
        metal_pbj = self.env['metal.price']
        print(fields.Date.today())
        metal_pbj_date = metal_pbj.search([('date', '=',fields.Date.today() )])
        print(metal_pbj_date)
        if metal_pbj_date:
            return metal_pbj_date.price
        else:
            return 0.0
    metal_price = fields.Float(
        string='Metal Price',
        required=False,default=get_metal_price)
    @api.model
    def create(self, values):
        # Add code here
        res = super(AccountMove, self).create(values)
        metal_pbj = self.env['metal.price']

        metal_pbj_date = metal_pbj.search([('date', '=',fields.Date.today() )])
        if not metal_pbj_date and 'metal_price' in values:
            metal_pbj.create({
                "date": fields.Date.today(),
                "price": res.metal_price,
            })


        return res

class MetalPrice(models.Model):
    _name = 'metal.price'

    date = fields.Date(
        string='Date', 
        required=False)
    price = fields.Float(
        string='Price', 
        required=False)

class ModernMoveAttendance(models.TransientModel):
    _name = 'metal.price.wizard'

    date = fields.Date(
        string='Date',
        required=False,default=fields.Date.context_today)
    price = fields.Float(
        string='Price',
        required=False)
    def create_metal_price(self):
        metal_pbj = self.env['metal.price']
        metal_pbj_date = metal_pbj.search([('date','=',self.date)])
        if metal_pbj_date:
            metal_pbj_date.write({
                'price':self.price
            })
        else:
            metal_pbj.create({
                "date":self.date,
                "price":self.price,
            })


