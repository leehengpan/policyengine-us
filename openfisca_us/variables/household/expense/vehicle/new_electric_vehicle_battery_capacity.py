from openfisca_us.model_api import *


class new_electric_vehicle_battery_capacity(Variable):
    value_type = float
    entity = TaxUnit
    label = "Battery capacity of a purchased new electric vehicle"
    unit = "kWh"
    definition_period = YEAR
