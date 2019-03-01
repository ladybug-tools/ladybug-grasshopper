# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a DataCollection to IP values.
-

    Args:
        _data_si: A DataCollection in SI units.
    Returns:
        data_ip: The DataCollection in IP units.
"""

ghenv.Component.Name = "LadybugPlus_To IP"
ghenv.Component.NickName = 'toIP'
ghenv.Component.Message = 'VER 0.0.04\nDEC_21_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "3"


if _data_si:
    assert hasattr(_data_si, 'isDataCollection'), \
        'Expected DataCollection. Got {}.'.format(type(_data_si))
    data_ip = _data_si.to_ip()