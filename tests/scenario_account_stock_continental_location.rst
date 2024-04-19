==================================
Account Stock Continental Scenario
==================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> from trytond.modules.account_stock_continental.tests.tools import \
    ...     add_stock_accounts
    >>> today = datetime.date.today()

Install account_stock_continental, sale and purchase::

    >>> config = activate_modules([
    ...         'account_stock_continental',
    ...         'sale',
    ...         'purchase',
    ...         'sale_supply_drop_shipment',
    ...         'account_stock_continental_location'
    ...         ])

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.account_stock_method = 'continental'
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = add_stock_accounts(get_accounts(company), company)
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> stock = accounts['stock']
    >>> stock_in = accounts['stock_expense']
    >>> stock_out, = stock_in.duplicate()
    >>> stock_production, = stock_in.duplicate()
    >>> stock_lost_found, = stock_in.duplicate()

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create product category::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.account_stock = stock
    >>> account_category.account_stock_in = stock_in
    >>> account_category.account_stock_out = stock_out
    >>> account_category.save()

    >>> Location = Model.get('stock.location')
    >>> elimination_location = Location()
    >>> elimination_location.name = "Elimination"
    >>> elimination_location.type = 'lost_found'
    >>> elimination_location.save()

    >>> LocationAccount = Model.get('product.category-stock.location-account.account')
    >>> location_account = LocationAccount()
    >>> location_account.location = elimination_location
    >>> location_account.account = stock_production
    >>> location_account.category = account_category
    >>> location_account.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.cost_price_method = 'fixed'
    >>> template.lead_time = datetime.timedelta(0)
    >>> template.account_category = account_category
    >>> product, = template.products
    >>> product.cost_price = Decimal('5')
    >>> template.save()
    >>> product, = template.products
    >>> template_average, = template.duplicate({
    ...         'cost_price_method': 'average',
    ...         })
    >>> product_average, = template_average.products

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Purchase 5 products::

    >>> Purchase = Model.get('purchase.purchase')
    >>> purchase = Purchase()
    >>> purchase.party = supplier
    >>> purchase.payment_term = payment_term
    >>> purchase.invoice_method = 'shipment'
    >>> purchase_line = purchase.lines.new()
    >>> purchase_line.product = product
    >>> purchase_line.quantity = 5.0
    >>> purchase_line.unit_price = Decimal(4)
    >>> purchase.click('quote')
    >>> purchase.click('confirm')
    >>> purchase.click('process')
    >>> purchase.state
    'processing'

Receive 5 products::

    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> Move = Model.get('stock.move')
    >>> shipment = ShipmentIn(supplier=supplier)
    >>> move, = [m for m in purchase.moves if m.product == product]
    >>> move = Move(move.id)
    >>> shipment.incoming_moves.append(move)
    >>> move.quantity = 5.0
    >>> shipment.click('receive')
    >>> shipment.click('do')
    >>> shipment.state
    'done'
    >>> stock_in.reload()
    >>> stock_in.debit
    Decimal('0.00')
    >>> stock_in.credit
    Decimal('25.00')
    >>> stock.reload()
    >>> stock.debit
    Decimal('25.00')
    >>> stock.credit
    Decimal('0.00')

Create stock moves::

    >>> StockMove = Model.get('stock.move')
    >>> move = StockMove()
    >>> from_location = Location.find([('type', '=', 'storage')])[0]
    >>> move.from_location = from_location
    >>> move.to_location = elimination_location
    >>> move.quantity = 2
    >>> move.product = product
    >>> move.save()

Check account moves::

    >>> stock_lost_found.debit - stock_lost_found.credit
    Decimal('0.00')
    >>> stock_production.debit - stock_production.credit
    Decimal('0.00')
    >>> move.click('do')
    >>> stock_production.reload()
    >>> stock_lost_found.reload()
    >>> stock_lost_found.debit - stock_lost_found.credit
    Decimal('0.00')
    >>> stock_production.debit -stock_production.credit
    Decimal('10.00')
