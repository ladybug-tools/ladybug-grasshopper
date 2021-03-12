# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate date information from an hour of the year.
_
Date information includes the month of the year, day of the month and the
hour + minute of the day.
-

    Args:
        _hoy: A number between 0 and 8759 for an hour of the year.

    Returns:
        month: The month of the year on which the input hoy falls.
        day: The day of the month on which the input hoy falls.
        hour: The hour of the day on which the input hoy falls.
        minute: The minute of the hour on which the input hoy falls.
        date: The input information as a human-readable date time.
        
"""

ghenv.Component.Name = "LB HOY to DateTime"
ghenv.Component.NickName = 'DateTime'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.dt import DateTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    month = []
    day = []
    hour = []
    minute = []
    date = []

    for hoy in _hoy:
        datetime = DateTime.from_hoy(hoy)
        month.append(datetime.month)
        day.append(datetime.day)
        hour.append(datetime.hour)
        minute.append(datetime.minute)
        date.append(datetime)
