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
Predicted Mean Vote (PMV) thermal comfort model.
-
These parameters can be plugged into any of the components that compute
PMV thermal comfort.
-

    Args:
        _ppd_thresh_:  A number between 5 and 100 that represents the upper
                threshold of PPD that is considered acceptable.
                Default is 10, which charcterizes most buildings in the
                ASHRAE-55 and EN-15251 standards.
        _hr_upper_: A number between 0 and 1 indicating the upper limit of
            humidity ratio that is considered acceptable.
            Default is 1 for essentially no limit.
        _hr_lower_: A number between 0 and 1 indicating the lower limit of
            humidity ratio considered acceptable.
            Default is 0 for essentially no limit.
        _still_air_thresh_: The air speed threshold in m/s at which the standard
            effective temperature (SET) model will be used to correct for the
            cooling effect of elevated air speeds.
            Default is 0.1 m/s, which is the limit according to ASHRAE-55.
    
    Returns:
        pmv_par: A PMV comfort parameter object that can be plugged into
            any of the components that compute PMV thermal comfort.
"""

ghenv.Component.Name = 'LB PMV Comfort Parameters'
ghenv.Component.NickName = 'PMVPar'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_comfort.parameter.pmv import PMVParameter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


pmv_par = PMVParameter(_ppd_thresh_, _hr_upper_, _hr_lower_, _still_air_thresh_)
