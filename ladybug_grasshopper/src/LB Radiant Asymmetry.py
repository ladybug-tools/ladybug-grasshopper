# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate the percentage of people dissatisfied from radiant asymmetry.
_
The comfort functions used here come from Figure 5.2.4.1 of ASHRAE 55 2010.
Note that, if the resulting input results in a PPD beyond what is included
in this Figure, the maximum PPD will simply be returned.
-

    Args:
        _radiant_diff: A number for the the radiant temperature difference between
            two sides of the same plane where an occupant is located [C].
            This can also be a data collection representing the radiant
            temperature difference over time [C].
        _asymmetry_type: Text or an integer that representing the type of radiant
            asymmetry being evaluated. Occupants are more sensitive to warm
            ceilings and cool walls than cool ceilings and warm walls.
            Choose from the following options.
            _
            * 0 = WarmCeiling
            * 1 = CoolWall
            * 2 = CoolCeiling
            * 3 = WarmWall

    Returns:
        ppd: The percentage of people dissatisfied (PPD) for the input radiant asymmetry.
"""

ghenv.Component.Name = 'LB Radiant Asymmetry'
ghenv.Component.NickName = 'RadAsymm'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.local import radiant_asymmetry_ppd
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import PercentagePeopleDissatisfied
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

ASYMMETRY_TYPES = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    'WarmCeiling': 0,
    'CoolWall': 1,
    'CoolCeiling': 2,
    'WarmWall': 3
}



if all_required_inputs(ghenv.Component):
    ppd = HourlyContinuousCollection.compute_function_aligned(
        radiant_asymmetry_ppd, [_radiant_diff, ASYMMETRY_TYPES[_asymmetry_type]],
        PercentagePeopleDissatisfied(), '%')
