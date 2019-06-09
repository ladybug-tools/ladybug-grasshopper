# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct a Ladybug DataCollection into a header and values.
-

    Args:
        _data: A Ladybug DataCollection object.
    Returns:
        header: The header of the DataCollection (containing metadata).
        values: The numerical values of the DataCollection.
"""

ghenv.Component.Name = "LadybugPlus_Deconstruct Data"
ghenv.Component.NickName = 'XData'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug.datacollection import BaseCollection
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_data, BaseCollection), \
        '_data must be a Data Collection. Got {}.'.format(type(_data))
    header = _data.header
    values = _data.values