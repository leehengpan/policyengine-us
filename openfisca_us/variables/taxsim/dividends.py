from openfisca_us.model_api import *


class dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "Dividends"
    unit = "currency-USD"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["dividend_income"])