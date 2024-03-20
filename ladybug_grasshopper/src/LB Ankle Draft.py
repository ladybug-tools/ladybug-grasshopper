# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate the percentage of people dissatisfied from cold drafts at ankle-level.
_
The original tests used to create the model involved blowing cold air on
subject's ankles at a height of 10 cm off of the ground.
The formula was officially incorporated in the ASHRAE 55 standard in 2020
with a recommendation that PPD from ankle draft not exceed 20%.
_
For more information on the methods used to create this model see the following:
Liu, S., S. Schiavon, A. Kabanshi, W. Nazaroff. 2016. "Predicted
percentage of dissatisfied with ankle draft." Accepted Author Manuscript.
Indoor Environmental Quality. http://escholarship.org/uc/item/9076254n
-

    Args:
        _full_body_pmv: The full-body predicted mean vote (PMV) of the subject.
            Ankle draft depends on full-body PMV because subjects are more likely
            to feel uncomfortably cold at their extremities when their whole body
            is already feeling colder than neutral. The "LB PMV Comfort"
            component can be used to obatin this input here.
        _draft_velocity: The velocity of the draft in m/s at ankle level
            (10cm above the floor).

    Returns:
        ppd: The percentage of people dissatisfied (PPD) from cold drafts at ankle level.
"""

ghenv.Component.Name = 'LB Ankle Draft'
ghenv.Component.NickName = 'AnkleDraft'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.local import ankle_draft_ppd
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import PercentagePeopleDissatisfied
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    ppd = HourlyContinuousCollection.compute_function_aligned(
        ankle_draft_ppd, [_full_body_pmv, _draft_velocity],
        PercentagePeopleDissatisfied(), '%')
