# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a DataCollection to the input _to_unit.
-

    Args:
        _data: A DataCollection for which you want to convert units.
        _to_unit: Text representing the unit that you would like to convert the
            DataCollection to.
    Returns:
        all_unit: A list of all possible units that the input _data can be converted to.
        data: The converted DataCollection
"""

ghenv.Component.Name = "LadybugPlus_To Unit"
ghenv.Component.NickName = 'toUnit'
ghenv.Component.Message = 'VER 0.0.04\nDEC_21_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "3"


if _data:
    assert hasattr(_data, 'isDataCollection'), \
        'Expected DataCollection. Got {}.'.format(type(_data_si))
    all_unit = _data.header.data_type.units
    if _to_unit:
        data = _data.to_unit(_to_unit)