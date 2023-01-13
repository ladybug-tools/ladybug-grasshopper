# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a DataCollection to the input _to_unit.
-

    Args:
        _data: A DataCollection to be converted to different units.
        to_unit_: Text representing the unit to convert the DataCollection to (eg. m2).
            Connect the _data and see the all_unit output for a list of all
            currently-supported units for a given collection. The default won't
            perform any unit conversion on the output data.

    Returns:
        all_unit: A list of all possible units that the input _data can be converted to.
        data: The converted DataCollection.
"""

ghenv.Component.Name = 'LB To Unit'
ghenv.Component.NickName = 'ToUnit'
ghenv.Component.Message = '1.6.0'
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
    data = _data.to_unit(to_unit_) if to_unit_ else _data