# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import PoolMeta


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    def _get_account_stock_move_lines(self, type_):
        lines = super()._get_account_stock_move_lines(type_)
        if type_.startswith('in'):
            location = self.from_location
        else:
            location = self.to_location
        account = self.product.account_category.compute_location_account(
            location)
        if not account:
            return lines
        for line in lines:
            line.account = account
        return lines
