# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate hour of the year from month, day, hour, minute.
-

    Args:
        _month_: Integer for month (1-12).
        _day_: Integer for day (1-31).
        _hour_: Integer for hour (0-23).
        _minute_: Integer for minute (0-59).

    Returns:
        hoy: Hour of the year.
        doy: Day of the year.
        date: Human readable date time.
"""

ghenv.Component.Name = 'LB Calculate HOY'
ghenv.Component.NickName = 'HOY'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.dt import DateTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

month = _month_ or 9
day = _day_ or 21
hour = _hour_ if _hour_ is not None else 12
minute = _minute_ or 0

datetime = DateTime(month, day, hour, minute)
hoy = datetime.hoy
doy = datetime.doy
date = datetime
