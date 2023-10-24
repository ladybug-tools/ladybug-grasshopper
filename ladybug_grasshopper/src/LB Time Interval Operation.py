# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Perform time interval operations on an hourly data collection.
_
This includes operations like:
- Average
- Total
- Percentile
_
These actions can be performed over the following time intervals:
- Daily
- Monthly
- Monthly per Hour
-

    Args:
        _data: A Ladybug data collection object.
        _operation_: Text indicating the operation that should be performed on
            the input hourly data.
            _
            Such text must be one of the following:
                - average
                - total
                - [a number between 0 and 100]
            _
            In the case of the last option, the number will be interpreted as
            a percentile of the data over the time period. For example,
            inputting 75 will return the 75th percentile value of each
            day/month/hour, inputting 0 will give the minimum value of each 
            day/month/hour and inputting 100 will give the max value of each
            day/month/hour.
            _
            Default is 'average' if the input data type is not cumulative and
            'total' if the data type is cumulative.

    Returns:
        daily: Daily data collection derived from the input _data and _operation_.
        monthly: Monthly data collection derived from the input _data and _operation_.
        mon_per_hr: Monthly Per Hour data collection derived from the input
            _data and _operation_.
"""

ghenv.Component.Name = 'LB Time Interval Operation'
ghenv.Component.NickName = 'TimeOp'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.datacollection import HourlyDiscontinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_data, HourlyDiscontinuousCollection), \
        '_data must be an Hourly Data Collection.' \
        ' Got {}.'.format(type(_data))
    if _operation_ is None:
        _operation_ = 'total' if _data.header.data_type.cumulative else 'average'

    if _operation_.lower() == 'average':
        daily = _data.average_daily()
        monthly = _data.average_monthly()
        mon_per_hr = _data.average_monthly_per_hour()
    elif _operation_.lower() == 'total':
        daily = _data.total_daily()
        monthly = _data.total_monthly()
        mon_per_hr = _data.total_monthly_per_hour()
    else:
        try:
            percentile = float(_operation_)
        except ValueError as e:
            raise TypeError(" Input '{}' for _operation_ is not valid. \n"
                            "operation_ must be one of the following:\n"
                            " average\n total\n [a number between 0 and "
                            "100]".format(_operation_))
        else:
            daily = _data.percentile_daily(percentile)
            monthly = _data.percentile_monthly(percentile)
            mon_per_hr = _data.percentile_monthly_per_hour(percentile)