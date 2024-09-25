from pathlib import Path
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_us.entities import *
from policyengine_us.parameters.gov.irs.uprating import (
    set_irs_uprating_parameter,
)
from policyengine_core.simulations import (
    Simulation as CoreSimulation,
    Microsimulation as CoreMicrosimulation,
    IndividualSim as CoreIndividualSim,
)
from policyengine_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)
from policyengine_us.tools.parameters import backdate_parameters
from policyengine_us.reforms import create_structural_reforms_from_parameters
from policyengine_core.parameters.operations.homogenize_parameters import (
    homogenize_parameter_structures,
)
from policyengine_core.parameters.operations.interpolate_parameters import (
    interpolate_parameters,
)
from policyengine_core.parameters.operations.propagate_parameter_metadata import (
    propagate_parameter_metadata,
)
from policyengine_core.parameters.operations.uprate_parameters import (
    uprate_parameters,
)
from .tools.default_uprating import add_default_uprating
from policyengine_us_data import DATASETS, CPS_2024
import ast
import glob
import os

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2024
year_start = str(CURRENT_YEAR) + "-01-01"


class CountryTaxBenefitSystem(TaxBenefitSystem):
    variables_dir = COUNTRY_DIR / "variables"
    auto_carry_over_input_variables = True
    basic_inputs = [
        "state_name",
        "employment_income",
        "age",
    ]
    modelled_policies = COUNTRY_DIR / "modelled_policies.yaml"

    def __init__(self, reform=None):
        super().__init__(entities, reform=reform)

        self.structural_reform_variables = {}

        self.load_parameters(COUNTRY_DIR / "parameters")
        if reform:
            self.apply_reform_set(reform)
        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = homogenize_parameter_structures(
            self.parameters, self.variables
        )
        self.parameters = propagate_parameter_metadata(self.parameters)
        self.parameters = interpolate_parameters(self.parameters)
        self.parameters = uprate_parameters(self.parameters)
        self.parameters = propagate_parameter_metadata(self.parameters)
        self.add_abolition_parameters()
        add_default_uprating(self)

        new_vars = self.parse_structural_reforms_from_dir(COUNTRY_DIR / "reforms")

        structural_reform = create_structural_reforms_from_parameters(
            self.parameters, year_start
        )
        if reform is None:
            reform = ()
        reform = (reform, structural_reform)

        self.parameters = backdate_parameters(
            self.parameters, first_instant="2015-01-01"
        )

        for parameter in self.parameters.get_descendants():
            parameter.modified = False

        if reform is not None:
            self.apply_reform_set(reform)

        self.add_variables(*create_50_state_variables())

    def parse_structural_reforms_from_dir(self, dir_path):
        py_files = glob.glob(os.path.join(dir_path, "*.py"))

        parsed_vars = []

        for py_file in py_files:
            new_vars = self.parse_variables_from_file(py_file)
            parsed_vars.extend(new_vars)
        subdirectories = glob.glob(os.path.join(dir_path, "*/"))

        for subdirectory in subdirectories:
            new_vars = self.parse_structural_reforms_from_dir(subdirectory)
            parsed_vars.extend(new_vars)
        
        return parsed_vars

    def parse_variables_from_file(self, file_path):

        # Read the content of the file
        with open(file_path, 'r') as file:
            source = file.read()

        # Parse the source code into an AST
        tree = ast.parse(source)

        variables = []

        # Helper function to extract attributes from a class definition
        def extract_attributes(class_def):
            attributes = {}
            for node in class_def.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if isinstance(node.value, ast.Str):
                                attributes[target.id] = node.value.s
                            elif isinstance(node.value, (ast.Num, ast.NameConstant)):
                                attributes[target.id] = node.value.value
                            elif isinstance(node.value, ast.Name):
                            # Try to get the object that the name refers to
                              try:
                                  obj = eval(node.value.id)
                                  # Check if the object has a __name__ attribute
                                  if hasattr(obj, '__name__'):
                                      attributes[target.id] = obj.__name__
                                  # If it doesn't have __name__, try to get its class name
                                  else:
                                      attributes[target.id] = obj.__class__.__name__
                              except NameError:
                                  # If the name isn't in the current namespace, use it as a string
                                  attributes[target.id] = node.value.id
            return attributes

        # Walk through the entire AST and find class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class inherits from Variable
                if any(base.id == 'Variable' for base in node.bases if isinstance(base, ast.Name)):
                    variable_info = {
                        'name': node.name,
                        **extract_attributes(node)
                    }
                    variables.append(variable_info)

        return variables

system = CountryTaxBenefitSystem()


class Simulation(CoreSimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, year_start
        )
        if reform is not None:
            self.apply_reform(reform)

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input(
                "self_employment_income_before_lsr", known_period, array
            )
            self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input(
                "weekly_hours_worked_before_lsr", known_period, array
            )
            weekly_hours.delete_arrays(known_period)

class Microsimulation(CoreMicrosimulation):
    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = CPS_2024
    default_dataset_year = CURRENT_YEAR
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR
    datasets = DATASETS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, year_start
        )
        if reform is not None:
            self.apply_reform(reform)

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in self_employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input(
                "self_employment_income_before_lsr", known_period, array
            )
            self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input(
                "weekly_hours_worked_before_lsr", known_period, array
            )
            weekly_hours.delete_arrays(known_period)

        self.input_variables = [
            variable
            for variable in self.input_variables
            if variable
            not in [
                "employment_income",
                "self_employment_income",
                "weekly_hours_worked",
            ]
        ] + [
            "employment_income_before_lsr",
            "self_employment_income_before_lsr",
            "weekly_hours_worked_before_lsr",
        ]


class IndividualSim(CoreIndividualSim):  # Deprecated
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = CPS_2024
    default_roles = dict(
        tax_unit="member",
        spm_unit="member",
        household="member",
        family="member",
    )
    required_entities = [
        "tax_unit",
        "spm_unit",
        "household",
        "family",
    ]
