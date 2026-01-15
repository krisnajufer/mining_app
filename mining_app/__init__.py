__version__ = "0.0.1"

import erpnext.controllers.taxes_and_totals as taxes_and_totals
from mining_app.controllers.taxes_and_totals import calculate_taxes_and_totals

taxes_and_totals.calculate_taxes_and_totals = calculate_taxes_and_totals