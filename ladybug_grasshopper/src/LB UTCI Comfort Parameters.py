# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a set of parameters that define the acceptable conditions of the
Universal Thermal Climate Index (UTCI) comfort model.
-
These parameters can be plugged into any of the components that compute UTCI comfort.
-

    Args:
        _cold_thresh_: Temperature in Celsius below which the UTCI represents
            cold stress. (Default: 9C).
        heat_thresh: Temperature in Celsius above which the UTCI represents
            heat stress. (Default: 26C).

    Returns:
        utci_par: A UTCI comfort parameter object that can be plugged into
            any of the components that compute UTCI thermal comfort.
"""

ghenv.Component.Name = 'LB UTCI Comfort Parameters'
ghenv.Component.NickName = 'UTCIPar'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.parameter.utci import UTCIParameter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


moderate_cold, moderate_heat = None, None
if _cold_thresh_ and _cold_thresh_ < 0:
    moderate_cold = _cold_thresh_
if _heat_thresh_ and _heat_thresh_ > 28:
    moderate_heat = _heat_thresh_

utci_par = UTCIParameter(
    cold_thresh=_cold_thresh_,
    heat_thresh=_heat_thresh_,
    moderate_cold_thresh=moderate_cold,
    moderate_heat_thresh=moderate_heat
)
