# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Perform time interval operations on an hourly data collection.
.
This includes operations like:
- Average
- Total
- Percentile
.
These actions can be performed over the following time intervals:
- Daily
- Monthly
- Monthly per Hour
-

    Args:
        _data: A Ladybug data collection object.
        _operation_: Text indicating the operation that should be performed on
            the input hourly data.
            .
            Such text must be one of the following:
                - average
                - total
                - [a number between 0 and 100]
            .
            In the case of the last option, the number will be interpreted as
            a percentile of the data over the time period. For example,
            inputting 75 will return the 75th percentile value of each
            day/month/hour, inputting 0 will give the minimum value of each 
            day/month/hour and inputting 100 will give the max value of each
            day/month/hour.
            .
            Default is set to 'average'.
    Returns:
        daily: Daily data collection derived from the input _data and _operation_.
        monthly: Monthly data collection derived from the input _data and _operation_.
        mon_per_hr: Monthly Per Hour data collection derived from the input
            _data and _operation_.
"""

ghenv.Component.Name = "LadybugPlus_Time Interval Operation"
ghenv.Component.NickName = 'timeOp'
ghenv.Component.Message = 'VER 0.0.04\nMAR_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


if _data:
    assert hasattr(_data, 'isHourly'), '_data must be an hourly data collection.' \
        ' Got {}.'.format(type(_data))
    
    if _operation_ is None or _operation_.lower() == 'average':
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