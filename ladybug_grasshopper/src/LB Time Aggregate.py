# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a DataCollection of point-in-time values to its time-aggregated equivalent.
_
For example, if the collection has a Power data type in W, this method will
return a collection with an Energy data type in kWh.
-

    Args:
        _data: A houry, sub-hourly or daily data collection that can be aggregated
            over time to yield data of a different metric. (eg. a data collection
            of Power values in W).

    Returns:
        data_aggr: The data collection aggregated over time. (eg. a data collection
            of Energy values in kWh).
"""

ghenv.Component.Name = 'LB Time Aggregate'
ghenv.Component.NickName = 'Aggr'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import HourlyDiscontinuousCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    accept = (HourlyDiscontinuousCollection, DailyCollection)
    assert isinstance(_data, accept), '_data must be a an hourly ot daily data ' \
        'collection. Got {}.'.format(type(_data))
    if _data.header.data_type.time_aggregated_type is not None:
        data_aggr = _data.to_time_aggregated()
    else:
        data_aggr = _data