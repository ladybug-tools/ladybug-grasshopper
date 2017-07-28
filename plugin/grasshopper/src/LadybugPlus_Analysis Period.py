# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Analysis Period.

-

    Args:
        _startMonth_: Start month (1-12).
        _startDay_: Start day (1-31).
        _startHour_: Start hour (0-23).
        _endMonth_: End month (1-12).
        _endDay_: End day (1-31).
        _endHour_: End hour (0-23).
        _timestep_: An integer number from 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60
    Returns:
        analysisPeriod: Analysis period.
        hoys: List of dates in this analysis period.
        dates: List of hours of the year in this analysis period.
"""

ghenv.Component.Name = "LadybugPlus_Analysis Period"
ghenv.Component.NickName = 'analysisPeriod'
ghenv.Component.Message = 'VER 0.0.01\nJUL_28_2017'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    import ladybug.analysisperiod as ap
    import ladybug.output as output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

anp = ap.AnalysisPeriod(
    _startMonth_, _startDay_, _startHour_,
    _endMonth_, _endDay_, _endHour_, _timestep_)

if anp:
    analysisPeriod = anp
    dates = output.wrap(anp.datetimes)
    hoys = output.wrap(anp.hoys)