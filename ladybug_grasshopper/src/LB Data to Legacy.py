# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a Ladybug DataCollection into its Ladybug Legacy format.
-
Note that this component is intended to be temporary as people transition from
Ladybug Legacy to Ladybug[+].
-

    Args:
        _data: A Ladybug DataCollection object.
    
    Returns:
        data: A Ladybug Legacy list with meatadata and values.
"""

ghenv.Component.Name = "LB Data to Legacy"
ghenv.Component.NickName = 'ToLegacy'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection, MonthlyPerHourCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# base header list
head = ['key:location/dataType/units/frequency/startsAt/endsAt',
        'Unkown Location']


if all_required_inputs(ghenv.Component):
    # add the location, data type, and units
    meta_data = _data.header.metadata
    if 'city' in meta_data:
        head[1] = meta_data['city']
    if 'type' in meta_data:
        if 'Zone' in meta_data:
            head.append('{} for {}'.format(meta_data['type'], meta_data['Zone']))
        elif 'System' in meta_data:
            head.append('{} for {}'.format(meta_data['type'], meta_data['System']))
        else:
            head.append(meta_data['type'])
    else:
        head.append(str(_data.header.data_type))
    head.append(_data.header.unit)

    # add the time interval
    a_per = _data.header.analysis_period
    if isinstance(_data, HourlyContinuousCollection):
        if a_per.timestep == 1:
            head.append('Hourly')
        else:
            head.append('Timestep')
    elif isinstance(_data, MonthlyCollection):
        head.append('Monthly')
    elif isinstance(_data, DailyCollection):
        head.append('Daily')
    elif isinstance(_data, MonthlyPerHourCollection):
        head.append('Monthly-> averaged for each hour')
    else:
        raise TypeError(
            '_data must be a Data Collection. Got {}.'.format(type(_data)))

    # add the analysis period
    head.append((a_per.st_month, a_per.st_day, a_per.st_hour + 1))
    head.append((a_per.end_month, a_per.end_day, a_per.end_hour + 1))

    # return the data
    data = head + list(_data.values)
