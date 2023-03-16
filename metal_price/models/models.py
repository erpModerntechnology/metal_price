
from odoo import api, fields, models ,_

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
    def onchange_product_id(self):
        if self.product_uom_id.category_id.name=="Weight":

            self.price_subtotal = self.price_unit*self.move_id.metal_price*self.quantity
        else:
            self.price_subtotal = self.price_unit * self.quantity


class AccountMove(models.Model):
    _inherit = 'account.move'


    def get_metal_price(self):
        metal_pbj = self.env['metal.price']
        metal_pbj_date = metal_pbj.search([('date', '=',fields.Date.today() )])
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

