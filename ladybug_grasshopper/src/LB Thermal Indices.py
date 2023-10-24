# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate thermal indices that have historically been used by meteorologists.
All of them are "feels like" temperatures that attempt to account for factors
beyond sir temperature. These include the following:
_
* Wet Bulb Globe Temperature (WBGT)
* Heat Index (HI)
* Wind Chill Temperature (WCT)
_
Most of these indices have fallen out of use in favor of Universal Thermal
Climate Index (UTCI). However, they are still used in some regions and are a
part of older codes and standards.
-

    Args:
        _air_temp: Data Collection or individual value for air temperature in C.
            This input is used by all three metrics.
        _mrt_: Data Collection or individual value for mean radiant temperature
            (MRT) in C. Default is the same as the air_temp. This input only
            affects the WBGT.
        _rel_humid: Data Collection or individual value for relative humidity in %.
            Note that percent values are between 0 and 100. This input affects
            WBGT as well as HI.
        _wind_vel: Data Collection or individual value for meteoroligical wind velocity
            at 10 m above ground level in m/s. This is used by both WBGT and WCT.
    
    Returns:
        wbgt: A data collection or value for Wet Bulb Globe Temperature (WBGT) [C].
            WBGT is a type of feels-like temperature that is widely used as a
            heat stress index (ISO 7243). It is incorporates the effect of
            temperature, humidity, wind speed, and mean radiant temperature
            (optionally including the effect of sun).
        heat_index: A data collection or value for Heat Index (HI) temperature [C].
            Heat index is derived from original work carried out by Robert G.
            Steadman, which defined heat index through large tables of empirical
            data. The formula here approximates the heat index to within +/- 0.7C
            and is the result of a multivariate fit. Heat index was adopted by
            the US's National Weather Service (NWS) in 1979.
        wind_chill: A data collection or value for Wind Cill Temperature (WCT) [C].
            Wind Chill Index is derived from original work carried out by
            Gregorczuk. It qualifies thermal sensations of a person in
            wintertime. It is especially useful at low and very low air
            temperature and at high wind speed.
"""

ghenv.Component.Name = 'LB Thermal Indices'
ghenv.Component.NickName = 'ThermalIndices'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.wbgt import wet_bulb_globe_temperature
    from ladybug_comfort.hi import heat_index as heat_index_temperature
    from ladybug_comfort.wc import windchill_temp
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.temperature import WetBulbGlobeTemperature, \
        HeatIndexTemperature, WindChillTemperature
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if _mrt_ is None:
        _mrt_ = _air_temp

    wbgt = HourlyContinuousCollection.compute_function_aligned(
        wet_bulb_globe_temperature, [_air_temp, _mrt_, _wind_vel, _rel_humid],
        WetBulbGlobeTemperature(), 'C')

    heat_index = HourlyContinuousCollection.compute_function_aligned(
        heat_index_temperature, [_air_temp, _rel_humid],
        HeatIndexTemperature(), 'C')

    wind_chill = HourlyContinuousCollection.compute_function_aligned(
        windchill_temp, [_air_temp, _wind_vel],
        WindChillTemperature(), 'C')