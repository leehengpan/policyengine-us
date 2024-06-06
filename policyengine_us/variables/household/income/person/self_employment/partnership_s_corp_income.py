from policyengine_us.model_api import *


class partnership_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "partnership/S-corp income"
    unit = USD
    definition_period = YEAR
    adds = [
        "partnership_income",
        "s_corp_income",
    ]
