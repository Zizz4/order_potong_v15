from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_potong_ids = fields.One2many('sdl.order.potong', 'purchase_id', 'Order Potong')

