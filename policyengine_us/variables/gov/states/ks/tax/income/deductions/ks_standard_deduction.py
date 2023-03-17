from policyengine_us.model_api import *


class ks_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/k-4021.pdf"
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/k-4022.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
    """
