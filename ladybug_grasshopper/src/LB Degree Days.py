# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate heating and cooling degree-days from outdoor dry bulb temperature.
-

    Args:
        _dry_bulb: A data collection representing outdoor dry bulb temperature [C]
        _heat_base_: A number for the base temperature below which a given hour
            is considered to be in heating mode. Default is 18 Celcius, which is
            a common balance point for buildings.
        _cool_base_: A number for the base temperature above which a given hour
            is considered to be in cooling mode. Default is 23 Celcius, which is
            a common balance point for buildings.

    Returns:
        hourly_heat: A data collection of heating degree-days.
            Plug this into the 'Time Interval Operation' component to get
            the number of degree-days at different time intervals.
        hourly_cool: A data collection of cooling degree-days.
            Plug this into the 'Time Interval Operation' component to get
            the number of degree-days at different time intervals.
        heat_deg_days: A value indicating the total number of heating degree-days
            over the entire input _dry_bulb collection.
        cool_deg_days: A value indicating the total number of cooling degree-days
            over the entire input _dry_bulb collection.
"""

ghenv.Component.Name = 'LB Degree Days'
ghenv.Component.NickName = 'HDD_CDD'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if _heat_base_ is None:
        _heat_base_ = 18
    if _cool_base_ is None:
        _cool_base_ = 23

    hourly_heat = HourlyContinuousCollection.compute_function_aligned(
        heating_degree_time, [_dry_bulb, _heat_base_],
        HeatingDegreeTime(), 'degC-hours')
    hourly_heat.convert_to_unit('degC-days')

    hourly_cool = HourlyContinuousCollection.compute_function_aligned(
        cooling_degree_time, [_dry_bulb, _cool_base_],
        CoolingDegreeTime(), 'degC-hours')
    hourly_cool.convert_to_unit('degC-days')

    heat_deg_days = hourly_heat.total
    cool_deg_days = hourly_cool.total