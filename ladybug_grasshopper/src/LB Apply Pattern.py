# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Filter a data collection or list of data collections by a pattern of True/False
values. True values will be kept while False values will be filtered out.
-

    Args:
        _data: A Data Collection or list of aligned Data Collections to be filtered
            by a pattern.
        _pattern: A list of True/False values. Typically, list has a length matching
            the length of the Data Collection(s)'s values. However, it can also
            be a pattern to be repeated over the Data Collection(s)'s values.

    Returns:
        data: A list of Data Collections that have been filtered by the _pattern.
"""

ghenv.Component.Name = 'LB Apply Pattern'
ghenv.Component.NickName = 'Pattern'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    data = []
    for dat in _data:
        assert isinstance(dat, BaseCollection), '_data must be a data' \
            ' collection. Got {}.'.format(type(dat))
        data.append(dat.filter_by_pattern(_pattern))