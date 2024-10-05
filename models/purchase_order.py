from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_potong_ids = fields.One2many('sdl.order.potong', 'purchase_id', 'Order Potong')

    hasil_potong_ids = fields.One2many('purchase.hasil.potong', 'purchase_id', 'Hasil Potong')

    order_type = fields.Selection([
        ('order_barang', 'Order Barang'),
        ('order_potong', 'Order Potong')
    ], default='order_barang', string="Order Type")

    @api.onchange('order_type')
    def _onchange_order_type(self):
        for rec in self:
            if rec.order_type == 'order_potong':
                picking_type = self.env.ref('sdl_order_potong.stock_picking_type_vendor_to_vendor')
                rec.picking_type_id = picking_type.id

    def action_open_ambil_potong_wizard(self):
        return {
            'name': _('Ambil Potong'),
            'type': 'ir.actions.act_window',
            'res_model': 'sdl.purchase.ambil.potong',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_order_id': self.id,
            },
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    quantity_potong = fields.Integer(string='Qty Potong')


class PurchaseHasilPotong(models.Model):
    _name = 'purchase.hasil.potong'
    _rec_name = 'product_id'

    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Integer('Quantity')
    po_line_id = fields.Many2one('purchase.order.line', 'Product Purchase')
    qty_asal = fields.Integer('Qty Asal')