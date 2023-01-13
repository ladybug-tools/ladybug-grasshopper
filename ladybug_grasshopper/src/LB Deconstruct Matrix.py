# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Ladybug Matrix object into a Grasshopper Data Tree of values.
-

    Args:
        _matrix: A Ladybug Matrix object such as the intersection matrices output
            from any of the ray-tracing components (eg. "LB Direct Sun Hours").

    Returns:
        values: The numerical values of the matrix as a Grasshopper Data Tree.
"""

ghenv.Component.Name = "LB Deconstruct Matrix"
ghenv.Component.NickName = 'XMatrix'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, de_objectify_output, \
        list_to_data_tree, merge_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    values = []
    for i, mtx in enumerate(_matrix):
        values.append(list_to_data_tree(de_objectify_output(mtx), root_count=i))
    values = merge_data_tree(values)
