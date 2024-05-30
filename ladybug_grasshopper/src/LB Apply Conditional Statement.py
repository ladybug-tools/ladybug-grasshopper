# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a conditional statement to a data collection.
-

    Args:
        _data: A list of aligned Data Collections to be evaluated against
            the _statement.
        _statement: A conditional statement as a string (e.g. a > 25).
            _
            The variable of the first data collection should always be named 'a'
            (without quotations), the variable of the second list should be
            named 'b', and so on.
            _
            For example, if three data collections are connected to _data
            and the following statement is applied:
            '18 < a < 26 and b < 80 and c > 2'
            The resulting collections will only include values where the first
            data collection is between 18 and 26, the second collection is less
            than 80 and the third collection is greater than 2.

    Returns:
        data: A list of Data Collections that have been filtered by the _statement.
"""

ghenv.Component.Name = 'LB Apply Conditional Statement'
ghenv.Component.NickName = 'Statement'
ghenv.Component.Message = '1.8.2'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
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
    for dat in _data:
        assert isinstance(dat, BaseCollection), '_data must be a data' \
            ' collection. Got {}.'.format(type(dat))

    data = BaseCollection.filter_collections_by_statement(
        _data, _statement)