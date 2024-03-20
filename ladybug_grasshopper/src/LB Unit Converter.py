# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a value or list of values from one unit to another.
-

    Args:
        _values: Values to be converted from one unit type to another.
        _from_u: Text indicating the units of the input _values (eg. 'C')
        _to_u: Text indicating the units of the output values (eg. 'K')

    Returns:
        all_u: A text string indicating all possible units
            that can be plugged into _from_u and _to_u.
        values: The converted numerical values.
"""

ghenv.Component.Name = 'LB Unit Converter'
ghenv.Component.NickName = 'Units'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    import ladybug.datatype
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


all_u = [': '.join([key, ', '.join(val)]) for key, val in ladybug.datatype.UNITS.items()]

if all_required_inputs(ghenv.Component):
    base_type = None
    for key in ladybug.datatype.UNITS:
        if _from_u in ladybug.datatype.UNITS[key]:
            base_type = ladybug.datatype.TYPESDICT[key]()
            break
    else:
        msg = 'Input _from_u "{}" is not recgonized as a valid unit.\n Check all_u ' \
        '(with nothing connected to the component) to see the acceptable units.'.format(_from_u)
        raise ValueError(msg)

    values = base_type.to_unit(_values, _to_u, _from_u)