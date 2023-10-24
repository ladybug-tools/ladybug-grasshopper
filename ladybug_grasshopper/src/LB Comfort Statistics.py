# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get statitics of thermal comfort from a Ladybug Comfort Object.
-

    Args:
        _comf_obj: A Ladybug ComfortCollection object from any of the comfort
            model components.
    
    Returns:
        pct_hot: The percent of time that conditions are hotter than acceptable limits.
        pct_neutral: The percent of time that conditions are within acceptable limits
            (aka. the percent of time comfortable).
        pct_cold: The percent of time that conditions are colder than acceptable limits.
"""

ghenv.Component.Name = 'LB Comfort Statistics'
ghenv.Component.NickName = 'ComfStat'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.collection.base import ComfortCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_comf_obj, ComfortCollection), '_comf_obj must be a ' \
        'Ladybug ComfortCollection object. Got {}.'.format(type(_comf_obj))

    pct_hot = _comf_obj.percent_hot
    pct_neutral = _comf_obj.percent_neutral
    pct_cold = _comf_obj.percent_cold