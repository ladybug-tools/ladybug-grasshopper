# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get a Data Collection that is aggregated by an area value.
_
Note that this component will raise a ValueError if the data type in the header
of the data collection is not normalizable to yeild a useful type.
-

    Args:
        _data: A Data Collection to be aggregated by the input _area.
        _area: A number representing area by which all of the data is aggregated.
        _unit_: Text for the units that the area value is in. Acceptable inputs include
            'm2', 'ft2' and any other unit that is supported. (Default: m2).

    Returns:
        data: A Ladybug data collection object aggregated by the input area
"""

ghenv.Component.Name = 'LB Area Aggregate'
ghenv.Component.NickName = 'AreaAgg'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    unit = _unit_ if _unit_ is not None else 'm2'
    data = _data.aggregate_by_area(_area, unit)
