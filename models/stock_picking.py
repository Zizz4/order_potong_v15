from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    order_potong_ids = fields.One2many('sdl.order.potong', 'picking_id', 'Order Potong')
