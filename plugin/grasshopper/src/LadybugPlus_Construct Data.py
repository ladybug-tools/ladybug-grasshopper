# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a Ladybug data collection from header and values.
-

    Args:
        _header:A Ladybug header object describing the data of the data collection.
        _values: A list of numerical values for the data collection.
    Returns:
        data: A Ladybug data collection object.
"""

ghenv.Component.Name = "LadybugPlus_Construct Data"
ghenv.Component.NickName = 'constrData'
ghenv.Component.Message = 'VER 0.0.04\nJAN_24_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if _header and _values != [] and _values[0] is not None:
    data = HourlyContinuousCollection(_header, _values)