# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta


class Category(metaclass=PoolMeta):
    __name__ = 'product.category'

    location_accounts = fields.One2Many(
        'product.category-stock.location-account.account', 'category',
        'Location Account')

    def compute_location_account(self, location):
        for la in self.location_accounts:
            if la.location == location:
                return la.account


class CategoryLocationAccount(ModelSQL, ModelView):
    "Category - Location - Account"
    __name__ = 'product.category-stock.location-account.account'

    category = fields.Many2One('product.category', 'Category', required=True,
        ondelete='CASCADE')
    location = fields.Many2One('stock.location', 'Location', required=True,
        ondelete='CASCADE',
        domain=[
            ('type', 'in', [
                'production', 'lost_found', 'supplier',
                'customer', 'drop', 'view'
                ])
        ])
    account = fields.Many2One('account.account', 'Account', required=True,
        ondelete='CASCADE',
        domain=[
            ('type', '!=', None),
            ('closed', '!=', True)
            ])
