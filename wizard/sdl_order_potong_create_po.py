from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SDLOrderPotongCreatePO(models.TransientModel):
    _name = 'sdl.order.potong.create.po'
    _description = 'Wizard Create PO dari Order Potong'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    order_line_ids = fields.One2many('sdl.order.potong.create.po.line', 'order_id', 'Order Line')

    def default_get(self, fields):
        res = super(SDLOrderPotongCreatePO, self).default_get(fields)
        order_potong_id = self._context.get('active_id')

        if order_potong_id:
            order_potong = self.env['sdl.order.potong'].browse(order_potong_id)
            lines = []
            for line in order_potong.hasil_potong_ids:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'qty': line.qty,
                }))
            res.update({
                'order_line_ids': lines,
            })
        return res

    def action_create_po(self):
        if not self.order_line_ids:
            raise UserError("You must add at least one order line to create a Purchase Order.")

        po_vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': []
        }
        for line in self.order_line_ids:
            po_line_vals = {
                'product_id': line.product_id.id,
                'product_qty': line.qty,
                'price_unit': line.unit_price,
                'name': line.product_id.name,
                'date_planned': fields.Datetime.now(),
                'product_uom': line.product_id.uom_po_id.id,
                'taxes_id': [(6, 0, line.taxes_id.ids)]
            }
            po_vals['order_line'].append((0, 0, po_line_vals))
        po = self.env['purchase.order'].create(po_vals)

        order_potong_id = self._context.get('active_id')
        if order_potong_id:
            order_potong = self.env['sdl.order.potong'].browse(order_potong_id)
            order_potong.purchase_id = po.id
            order_potong.state = 'done'
            order_potong._create_picking()

        return {
            'type': 'ir.actions.act_window_close',
        }


class SDLOrderPotongCreatePOLine(models.TransientModel):
    _name = 'sdl.order.potong.create.po.line'
    _description = 'Wizard Create PO Line dari Order Potong'

    order_id = fields.Many2one('sdl.order.potong.create.po', 'Order Potong')
    product_id = fields.Many2one('product.product', string='Product')
    currency_id = fields.Many2one('res.currency', 'Currency', related='order_id.currency_id')
    qty = fields.Float('Qty')
    unit_price = fields.Monetary('Unit Price')
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    total_price = fields.Monetary('Total Price')

    @api.onchange('qty', 'unit_price', 'taxes_id')
    def _onchange_total_price(self):
        """Calculate total price including taxes."""
        for rec in self:
            # Calculate base amount (without taxes)
            base_amount = rec.qty * rec.unit_price

            if rec.taxes_id:
                # Compute taxes using Odoo's built-in method
                taxes = rec.taxes_id.compute_all(base_amount, currency=rec.currency_id, quantity=1.0,
                                                 product=rec.product_id, partner=rec.order_id.partner_id)

                # Get the total amount including taxes
                rec.total_price = taxes['total_included']
            else:
                # If no taxes are applied, use the base amount
                rec.total_price = base_amount