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
ghenv.Component.Message = 'VER 0.0.04\nMAR_05_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "3"


if _data_ip:
    assert hasattr(_data_ip, 'isDataCollection'), \
        'Expected DataCollection. Got {}.'.format(type(_data_ip))
    data_si = _data_ip.to_si()