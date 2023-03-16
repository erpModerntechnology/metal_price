from odoo import api, fields, models

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


