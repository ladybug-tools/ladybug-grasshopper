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
ghenv.Component.Message = 'VER 0.0.04\nDEC_21_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

from ladybug.datatypenew import DataTypes

all_u = DataTypes.all_possible_units()

if _values != [] and _values[0] and _from_u and _to_u:
    data_type = DataTypes.type_by_unit(_from_u)
    values = data_type.to_unit(_values, _to_u, _from_u)