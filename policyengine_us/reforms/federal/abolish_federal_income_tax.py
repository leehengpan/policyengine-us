from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_if_active


def create_abolish_federal_income_tax() -> Reform:
    class household_tax_before_refundable_credits(Variable):
        value_type = float
        entity = Household
        label = "total tax before refundable credits"
        documentation = "Total tax liability before refundable credits."
        unit = USD
        definition_period = YEAR

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = (
                p.gov.household.household_tax_before_refundable_credits
            )
            added_components = [
                c
                for c in added_components
                if c != "income_tax_before_refundable_credits"
            ]
            return add(household, period, added_components)

    class household_refundable_tax_credits(Variable):
        value_type = float
        entity = Household
        label = "refundable tax credits"
        definition_period = YEAR
        unit = USD

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = p.gov.household.household_refundable_credits
            added_components = [
                c
                for c in added_components
                if c != "income_tax_refundable_credits"
            ]
            return add(household, period, added_components)

    class reform(Reform):
        def apply(self):
            self.update_variable(household_tax_before_refundable_credits)
            self.update_variable(household_refundable_tax_credits)

    return reform


abolish_federal_income_tax = create_reform_if_active(
    None,
    None,
    "gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax",
    create_abolish_federal_income_tax,
    bypass=True,
)
