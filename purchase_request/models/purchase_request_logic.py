from odoo import api, fields,models, _

from odoo.exceptions import ValidationError

class PurchaseRequest(models.Model):
    _name = 'purchase.request'

    _description = 'Purchase request made by company employees'

    # data fields
    request_name = fields.Char(string='Request Reference', required=True, copy=False, default=lambda self: _('New'))
    
    request_submitter = fields.Many2one('res.users', string="Submitted By?", default=lambda self: self.env.user, readonly=True)
    
    from_what_department = fields.Many2one('hr.department', string='Department')
    
    when_request_was_made = fields.Datetime(string='Submitted On?', default=fields.Datetime.now, readonly=True)
    
    for_what_products = fields.One2many('purchase.request.product', 'attached_request', string='Requested Products')
    
    # upon creation its considered 'draft'
    request_state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved')
    ], default='pending', string='Status of Request')

    proposed_vendors = fields.Many2many('res.partner', string='Vendors', domain=[('supplier_rank', '>', 0)])


    @api.constrains('for_what_products')
    def _check_for_what_products(self):
        for record in self:
            if not record.for_what_products:
                raise ValidationError(_('You must add at least one product to your request..'))

    @api.constrains('proposed_vendors')
    def _check_for_selected_vendors(self):
        for record in self:
            if not record.proposed_vendors:
                raise ValidationError(_('You must add at least one vendor to your request..'))
        


    def action_reject_request(self):
        self.ensure_one()

        # delete the request
        self.unlink()
        
        return

    def action_approve_request(self):
        for record in self:
            record.ensure_one()
            
            purchase_order_vals = {
                'partner_id': record.proposed_vendors[0].id,
                'vendor_ids': [(6, 0, record.proposed_vendors.ids)],
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_quantity,
                    'price_unit': line.product_id.standard_price,
                }) for line in record.for_what_products]
            }
            
            self.env['purchase.order'].create(purchase_order_vals)

            # delete the request then
            self.unlink()

        return
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('request_name', _('New')) == _('New'):
                # generate a sequence number for each request
                vals['request_name'] = self.env['ir.sequence'].next_by_code('purchase.request') or _('New')
        
        return super(PurchaseRequest, self).create(vals_list)


class PurchaseRequestProduct(models.Model):
    _name = 'purchase.request.product'

    _description = 'Handles the individual list of products for a given request'

    # fields
    attached_request = fields.Many2one('purchase.request', string='Attached to what request')

    # basic info about the product
    product_id = fields.Many2one('product.product', string='Product')

    product_quantity = fields.Float(string='Quantity')