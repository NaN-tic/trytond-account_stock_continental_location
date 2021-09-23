# This file is part account_stock_continental_location module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import stock
from . import product


def register():
    Pool.register(
        stock.Move,
        product.Category,
        product.CategoryLocationAccount,
        module='account_stock_continental_location', type_='model')
    Pool.register(
        module='account_stock_continental_location', type_='wizard')
    Pool.register(
        module='account_stock_continental_location', type_='report')
