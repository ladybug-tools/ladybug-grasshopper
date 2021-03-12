# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a Ladybug DataType to be used in the header of a ladybug DataCollection.
-

    Args:
        _name: A name for the data type as a string.
        _unit: A unit for the data type as a string.
        categories_: An optional list of text for categories to be associated with
            the data type. These categories will show up in the legend whenever
            data with this data type is visualized. The input should be
            text strings with a category number (integer) and name separated
            by a colon. For example:
            _
            .    -1: Cold
            .     0: Neutral
            .     1: Hot
    
    Returns:
        type: A Ladybug DataType object that can be assigned to the header
            of a Ladybug DataCollection.
"""

ghenv.Component.Name = "LB Construct Data Type"
ghenv.Component.NickName = 'ConstrType'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.datatype.generic import GenericType
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the categories_ if they are supplied
    unit_descr = None
    if categories_ != []:
        unit_descr = {}
        for prop in categories_:
            key, value = prop.split(':')
            unit_descr[int(key)] = value.strip()

    type = GenericType(_name, _unit, unit_descr=unit_descr)