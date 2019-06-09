# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a DataCollection to SI values.
-

    Args:
        _data_ip: A DataCollection in IP (or other) units.
    Returns:
        data_si: The DataCollection in SI units.
"""

ghenv.Component.Name = "LadybugPlus_To SI"
ghenv.Component.NickName = 'toSI'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from ladybug.datacollection import BaseCollection
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_data_ip, BaseCollection), \
        '_data_ip must be a Data Collection. Got {}.'.format(type(_data_ip))
    data_si = _data_ip.to_si()