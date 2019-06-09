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
        _start_month_: Start month (1-12).
        _start_day_: Start day (1-31).
        _start_hour_: Start hour (0-23).
        _end_month_: End month (1-12).
        _end_day_: End day (1-31).
        _end_hour_: End hour (0-23).
        _timestep_: An integer number for the number of time steps per hours.
            Acceptable inputs include: 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60
    Returns:
        analysis_period: Analysis period.
        hoys: List of dates in this analysis period.
        dates: List of hours of the year in this analysis period.
"""

ghenv.Component.Name = "LadybugPlus_Analysis Period"
ghenv.Component.NickName = 'analysisPeriod'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.analysisperiod as ap
    from ladybug_rhino.grasshopper import wrap_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

anp = ap.AnalysisPeriod(
    _start_month_, _start_day_, _start_hour_,
    _end_month_, _end_day_, _end_hour_, _timestep_)

if anp:
    analysis_period = anp
    dates = wrap_output(anp.datetimes)
    hoys = anp.hoys