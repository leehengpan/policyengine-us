from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_if_active


def create_remove_head_of_household() -> Reform:
    class reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    return reform


def create_remove_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    if bypass or parameters is None:
        return create_remove_head_of_household()

    # Look ahead for the next five years
    p = parameters.gov.contrib.congress.romney.family_security_act
    reform_active = reform_is_active(p, period, 5, "remove_head_of_household")

    if reform_active:
        return create_remove_head_of_household()
    else:
        return None


remove_head_of_household = create_reform_if_active(
    None,
    None,
    "gov.contrib.congress.romney.family_security_act.remove_head_of_household",
    create_remove_head_of_household,
    bypass=True,
)
