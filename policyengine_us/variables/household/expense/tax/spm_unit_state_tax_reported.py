from policyengine_us.model_api import *


class spm_unit_state_tax_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "State income tax (reported)"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
    adds = ["state_income_tax_reported"]
