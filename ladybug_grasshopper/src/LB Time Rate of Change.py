# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a DataCollection of time-aggregated values to time rate of change units.
_
For example, if the collection has an Energy data type in kWh, this method will
return a collection with an Power data type in W.
-

    Args:
        _data: A houry, sub-hourly or daily data collection that can converted to
            a time rate of change metric. (eg. a data collection of Energy
            values in kWh).

    Returns:
        data_rate: The data collection converted to time rate of changevalues.
            (eg. a data collection of Energy values in kWh).
"""

ghenv.Component.Name = 'LB Time Rate of Change'
ghenv.Component.NickName = 'Rate'
ghenv.Component.Message = '1.7.0'
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
    data_rate = _data.to_time_rate_of_change()
