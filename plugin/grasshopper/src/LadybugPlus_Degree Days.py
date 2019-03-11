# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate humidity metrics from relative humidity, dry bulb temperature and
(if present) atmospheric pressure.
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

ghenv.Component.Name = "LadybugPlus_Degree Days"
ghenv.Component.NickName = 'HDD_CDD'
ghenv.Component.Message = 'VER 0.0.04\nMAR_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _dry_bulb:
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
    
    heat_deg_days = hourly_heat.total / 24.
    cool_deg_days = hourly_cool.total / 24.