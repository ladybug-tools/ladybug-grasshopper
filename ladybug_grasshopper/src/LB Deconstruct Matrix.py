# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, de_objectify_output, \
        list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    values = list_to_data_tree(de_objectify_output(_matrix))