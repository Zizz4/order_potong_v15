from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SDLOrderPotong(models.Model):
    _name = 'sdl.order.potong'
    _description = 'Order Potong'

    name = fields.Char('Order Potong', readonly=True, default=lambda self: _('New'))
    order_potong_date = fields.Date('Tgl. Order Potong')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('done', 'Done'),
    ], string='State', default='draft')
    order_potong_line = fields.One2many('sdl.order.potong.line', 'order_potong_id', string="Order Line")
    hasil_potong_ids = fields.One2many('sdl.hasil.potong', 'order_potong_id', string="Hasil Potong")
    source_location_id = fields.Many2one('stock.location', 'Source Location')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    picking_id = fields.Many2one('stock.picking', string='Delivery Order')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sdl.order.potong.seq') or _('New')
        res = super(SDLOrderPotong, self).create(vals)
        return res

    def action_confirm_order_potong(self):
        if not self.order_potong_line:
            raise UserError("No order lines to confirm.")

        for line in self.order_potong_line:
            quant = self.env['stock.quant'].search([
                ('location_id', '=', self.source_location_id.id),
                ('product_id', '=', line.product_id.id)
            ], limit=1)
            if not quant:
                raise UserError(
                    f"Product {line.product_id.name} is not available in the location {self.source_location_id.name}.")
            if quant.quantity < line.qty:
                raise UserError(
                    f"Not enough quantity for product {line.product_id.name} in location {self.source_location_id.name}. Available: {quant.quantity}, Required: {line.qty}.")
        self.state = 'progress'

    def action_view_po(self):
        return {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_id.id,
            'target': 'current'
        }

    def action_view_do(self):
        return {
            'name': 'Stock Picking',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
            'target': 'current'
        }

    def _create_picking(self):
        picking_type_order_potong = self.env.ref('sdl_order_potong.stock_picking_type_order_potong')
        picking_vals = {
            'picking_type_id': picking_type_order_potong.id,
            'location_id': self.source_location_id.id,  # Source location
            'location_dest_id': picking_type_order_potong.default_location_dest_id.id,  # Destination location
            'origin': self.name,  # Reference the Order Potong
            'move_lines': []
        }
        for line in self.order_potong_line:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.source_location_id.id,  # Source location
                'location_dest_id': picking_type_order_potong.default_location_dest_id.id,  # Destination location
            }
            picking_vals['move_lines'].append((0, 0, move_vals))
        picking = self.env['stock.picking'].create(picking_vals)

        # Confirm the picking (this will confirm the stock move)
        picking.action_confirm()

        # Check availability (reserve stock for this move)
        picking.action_assign()

        # Forcefully set the stock moves as done (validate the picking)
        for move in picking.move_lines:
            move.quantity_done = move.product_uom_qty  # Ensure that the done quantity is set
        picking.button_validate()

        self.picking_id = picking


class SDLOrderPotongLine(models.Model):
    _name = 'sdl.order.potong.line'
    _description = 'Order Potong Line'
    _rec_name = 'product_id'

    name = fields.Char('Order Potong Line')
    order_potong_id = fields.Many2one('sdl.order.potong', 'Order Potong')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Qty')
    keterangan = fields.Char('Keterangan')


class SDLHasilPotong(models.Model):
    _name = 'sdl.hasil.potong'
    _description = 'hasil order potong'
    _rec_name = 'product_id'

    name = fields.Char('Hasil Potong')
    order_potong_id = fields.Many2one('sdl.order.potong', 'Order Potong')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Qty')
    keterangan = fields.Char('Keterangan')
