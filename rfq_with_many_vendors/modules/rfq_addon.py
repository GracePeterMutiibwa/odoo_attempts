from odoo import fields, models, api

from odoo.exceptions import ValidationError

class MultiVendorRFQ(models.Model):
    _inherit = 'purchase.order'

    vendor_ids = fields.Many2many('res.partner',
                                  string='Attached Vendors',
                                  domain=[('supplier_rank', '>', 0)],
                                  help='Vendors to inform'
                                  )
    
    bid_ids = fields.One2many(
        'purchase.bid',
        'attached_order',
        string='Bids'
    )


class BidItem(models.Model):
    _name = 'purchase.bid'

    _description = 'Makes it possible to attach bids to a given purchase order'

    attached_order = fields.Many2one('purchase.order', string='Purchase Order', required=True, help='Choose the attached purchase order')

    vendor_id = fields.Many2one(
        'res.partner', 
        string='Vendor',
        domain=[('supplier_rank', '>', 0)],
        help='What vendor is making the bid'
        )
    
    bid_state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending',
        string='Bid status',
        help='Current state of the bid'
        )
    
    bid_amount = fields.Float(string='Bid Amount', required=True, help='Amount proposed by the vendor')

    bid_description = fields.Text(string='Bid Description', help='Vendor pricing and conditions about the order')

    bid_date = fields.Datetime(
        string='Submitted Date',
        help='Date when the bid was submitted',
        default=lambda self: fields.Datetime.now() 
    )

    is_winner = fields.Boolean(
        string='Is the Winning bid',
        default=False
    )

    
    @api.constrains('vendor_id', 'attached_order')
    def _ensure_that_bids_are_unique(self):
        for eachRecord in self:
            # find if bids from the same vendor exist
            bids_from_same_vendor = self.search(
                [
                    ('vendor_id', '=', eachRecord.vendor_id.id),
                    ('attached_order', '=', eachRecord.attached_order.id),
                    ('id', '!=', eachRecord.id)
                ]
            )

            if bids_from_same_vendor:
                raise ValidationError("There exists a bid submitted already from this Vendor..")

    def choose_winning_bid(self):
        # debug
        # print('It worked:', self.id)

        # unset all bids as not winners
        self.attached_order.bid_ids.write({
            'is_winner': False
        })

        # mark this bid as winner
        self.is_winner = True

        # reflect changes for both fields
        self.attached_order.partner_id = self.vendor_id
        
        # drop ll the rest and the marked one
        self.attached_order.vendor_ids = [(6, 0, [self.vendor_id.id])]

        # mark it accepted
        self.bid_state = 'accepted'


