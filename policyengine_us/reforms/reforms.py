from .congress.delauro import create_american_family_act_with_baby_bonus_reform
from .dc_kccatc import create_dc_kccatc_reform
from .winship import create_eitc_winship_reform
from .dc_tax_threshold_joint_ratio import (
    create_dc_tax_threshold_joint_ratio_reform,
)
from .congress.romney.family_security_act import (
    create_remove_head_of_household_reform,
)
from .cbo.payroll import (
    create_increase_taxable_earnings_for_social_security_reform,
)
from .congress.wyden_smith import create_ctc_expansion_reform

from .congress.tlaib.end_child_poverty_act import create_ecpa_adult_dependent_credit_reform
from .congress.tlaib.end_child_poverty_act import create_ecpa_filer_credit_reform

from .williamson import create_universal_child_allowance_reform

from policyengine_core.reforms import Reform
import warnings


def create_structural_reforms_from_parameters(parameters, period):
    afa_reform = create_american_family_act_with_baby_bonus_reform(
        parameters, period
    )
    winship_reform = create_eitc_winship_reform(parameters, period)
    dc_kccatc_reform = create_dc_kccatc_reform(parameters, period)
    dc_tax_threshold_joint_ratio_reform = (
        create_dc_tax_threshold_joint_ratio_reform(parameters, period)
    )
    remove_head_of_household = create_remove_head_of_household_reform(
        parameters, period
    )
    increase_taxable_earnings_for_social_security_reform = (
        create_increase_taxable_earnings_for_social_security_reform(
            parameters, period
        )
    )
    ctc_expansion = create_ctc_expansion_reform(parameters, period)

    ecpa_adult_dependent_credit = create_ecpa_adult_dependent_credit_reform(parameters, period)

    ecpa_filer_credit = create_ecpa_filer_credit_reform(parameters, period)

    universal_child_allowance = create_universal_child_allowance_reform(parameters, period)

    reforms = [
        afa_reform,
        winship_reform,
        dc_kccatc_reform,
        dc_tax_threshold_joint_ratio_reform,
        remove_head_of_household,
        increase_taxable_earnings_for_social_security_reform,
        ctc_expansion,
        ecpa_adult_dependent_credit,
        ecpa_filer_credit,
        universal_child_allowance,
    ]

    reforms = tuple(filter(lambda x: x is not None, reforms))

    class combined_reform(Reform):
        def apply(self):
            for reform in reforms:
                reform.apply(self)

    return combined_reform
