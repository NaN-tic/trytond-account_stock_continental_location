# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval


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
        ondelete='CASCADE',
        context={
            'company': Eval('company'),
            },
        depends=['company'])
    location = fields.Many2One('stock.location', 'Location', required=True,
        ondelete='CASCADE',
        domain=[
            ('type', 'not in', ['view', 'warehouse'])
        ])
    account = fields.Many2One('account.account', 'Account', required=True,
        ondelete='CASCADE',
        domain=[
            ('type', '!=', None),
            ('closed', '=', False),
            ('type.stock', '=', True)
            ])
    company = fields.Function(fields.Many2One('company.company', 'Company'),
        'get_company', searcher='search_company')

    def get_company(self, name=None):
        if self.account:
            return self.account.company

    @classmethod
    def search_company(cls, name, clause):
        return [('account.%s' % name,) + tuple(clause[1:])]

