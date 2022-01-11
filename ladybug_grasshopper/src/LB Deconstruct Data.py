# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Ladybug DataCollection into a header and values.
-

    Args:
        _data: A Ladybug DataCollection object.
    Returns:
        header: The header of the DataCollection (containing metadata).
        values: The numerical values of the DataCollection.
"""

ghenv.Component.Name = "LB Deconstruct Data"
ghenv.Component.NickName = 'XData'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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
    header = _data.header
    values = _data.values