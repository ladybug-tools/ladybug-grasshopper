# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get the hours, days, or months of the year associated with the values of a data collection.
-

    Args:
        _data: An hourly, daily, or monthly collection from which hours, days, or
            months of the year will be retrieved.

    Returns:
        hoys: Numbers for the, hours, days or months of the year in the data collection.
"""

ghenv.Component.Name = 'LB Data DateTimes'
ghenv.Component.NickName = 'DataDT'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.dt import DateTime
    from ladybug.datacollection import HourlyDiscontinuousCollection, DailyCollection, \
        MonthlyCollection, MonthlyPerHourCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if isinstance(_data, HourlyDiscontinuousCollection):
        hoys = [dt.hoy for dt in _data.datetimes]
    elif isinstance(_data, (MonthlyCollection, DailyCollection)):
        hoys = _data.datetimes
    elif isinstance(_data, MonthlyPerHourCollection):
        hoys = [DateTime(dt[0], 1, dt[1], dt[2]).hoy for dt in _data.datetimes]
    else:
        raise ValueError('Expected data collection. Got {}.'.format(type(data)))
