# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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

ghenv.Component.Name = "LadybugPlus_Unit Converter"
ghenv.Component.NickName = 'Units'
ghenv.Component.Message = 'VER 0.0.04\nMAR_05_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import ladybug.datatype

all_u = [': '.join([key, ', '.join(val)]) for key, val in ladybug.datatype.UNITS.items()]

if _values != [] and _values[0] and _from_u and _to_u:
    base_type = None
    for key in ladybug.datatype.UNITS:
        if _from_u in ladybug.datatype.UNITS[key]:
            base_type = ladybug.datatype.TYPESDICT[key]()
    assert base_type, 'Input _from_u "{}" is not recgonized as a valid unit.\n' \
        'Check all_u for acceptable units'.format(_from_u)
    
    values = base_type.to_unit(_values, _to_u, _from_u)