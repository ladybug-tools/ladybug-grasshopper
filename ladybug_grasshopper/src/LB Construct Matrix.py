# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Construct a Ladybug Matrix object from a Grasshopper Data Tree of values.
-

    Args:
        _values: A Grasshopper Data Tree of values to be merged into a matrix object.

    Returns:
        matrix: A Ladybug Matrix object encapsulating all of the input values.
"""

ghenv.Component.Name = "LB Construct Matrix"
ghenv.Component.NickName = '+Matrix'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output, \
        data_tree_to_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    python_mtx = [row[1] for row in data_tree_to_list(_values)]
    matrix = objectify_output('Matrix', python_mtx)