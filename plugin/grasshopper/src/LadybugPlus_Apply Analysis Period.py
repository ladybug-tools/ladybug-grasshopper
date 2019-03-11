# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply an analysis period to a data collection.
-

    Args:
        _data: A Ladybug data collection object.
        _period: A Ladybug analysis period.
    Returns:
        data: The data collection with the analysis period applied to it.
"""

ghenv.Component.Name = "LadybugPlus_Apply Analysis Period"
ghenv.Component.NickName = 'applyPer'
ghenv.Component.Message = 'VER 0.0.04\nMAR_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


if _data and _period:
    assert hasattr(_data, 'isDataCollection'), '_data must be a data collection.' \
        ' Got {}.'.format(type(_data))
    assert hasattr(_period, 'isAnalysisPeriod'), '_period must be an analysis' \
        ' period. Got {}.'.format(type(_period))
    data = _data.filter_by_analysis_period(_period)