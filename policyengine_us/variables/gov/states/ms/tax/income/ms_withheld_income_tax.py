from policyengine_us.model_api import *


class ms_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Mississippi withheld income tax"
    defined_for = StateCode.MS
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = add(
            person, period, ["irs_employment_income", "self_employment_income"]
        )
        p = parameters(period).gov.states.ms.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rate.calc(reduced_employment_income)
