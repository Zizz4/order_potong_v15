from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SDLPurchaseAmbilPotong(models.TransientModel):
    _name = 'sdl.purchase.ambil.potong'
    _description = 'Wizard Create Hasil Potong di PO'

    name = fields.Char('Name')
    potong_line_ids = fields.One2many('sdl.purchase.ambil.potong.line', 'potong_id', 'Potong Line')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', readonly=True)

    def action_confirm(self):
        """Method to confirm and save hasil potong from wizard to purchase.hasil.potong
        and update the quantity_potong in purchase.order.line
        """
        for line in self.potong_line_ids:
            # 1. Create record in purchase.hasil.potong
            self.env['purchase.hasil.potong'].create({
                'purchase_id': self.purchase_order_id.id,
                'product_id': line.product_id.id,
                'qty': line.qty,
                'po_line_id': line.po_line_id.id,
                'qty_asal': line.qty_asal,
            })

            # 2. Update the quantity_potong in the related purchase.order.line
            line.po_line_id.quantity_potong += line.qty_asal

        return {
            'type': 'ir.actions.act_window_close',
        }


class SDLPurchaseAmbilPotongLine(models.TransientModel):
    _name = 'sdl.purchase.ambil.potong.line'
    _description = 'Wizard Line Create Hasil Potong di PO'

    potong_id = fields.Many2one('sdl.purchase.ambil.potong', 'Ambil Potong')
    product_id = fields.Many2one('product.product')
    qty = fields.Integer('Quantity')
    po_line_id = fields.Many2one('purchase.order.line', 'Product Source', domain="[('order_id', '=', parent.purchase_order_id)]")
    qty_asal = fields.Integer('Qty Asal')

