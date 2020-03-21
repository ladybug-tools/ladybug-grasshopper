# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a DataCollection to the input _to_unit.
-

    Args:
        _data: A DataCollection for which you want to convert units.
        _to_unit: Text representing the unit that you would like to convert the
            DataCollection to.
    
    Returns:
        all_unit: A list of all possible units that the input _data can be converted to.
        data: The converted DataCollection
"""

ghenv.Component.Name = 'LB To Unit'
ghenv.Component.NickName = 'ToUnit'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_data, BaseCollection), \
        '_data must be a Data Collection. Got {}.'.format(type(_data))
    all_unit = _data.header.data_type.units
    if _to_unit:
        data = _data.to_unit(_to_unit)