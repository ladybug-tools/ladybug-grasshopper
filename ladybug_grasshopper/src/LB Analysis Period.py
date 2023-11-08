# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Analysis Period to describe a slice of time during the year.

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
        period: Analysis period.
        hoys: List of dates in this analysis period.
        dates: List of hours of the year in this analysis period.
"""

ghenv.Component.Name = 'LB Analysis Period'
ghenv.Component.NickName = 'AnalysisPeriod'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    import ladybug.analysisperiod as ap
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import wrap_output, turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


anp = ap.AnalysisPeriod(
    _start_month_, _start_day_, _start_hour_,
    _end_month_, _end_day_, _end_hour_, _timestep_)

if anp:
    period = anp
    dates = wrap_output(anp.datetimes)
    hoys = anp.hoys