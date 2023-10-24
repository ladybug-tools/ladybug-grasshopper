# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate humidity metrics from relative humidity, dry bulb temperature and
(if present) atmospheric pressure.
-

    Args:
        _dry_bulb: A value or data collection representing  dry bulb temperature [C]
        _rel_humid: A value or data collection representing relative humidity [%]
        _pressure_: A value or data collection representing atmospheric pressure [Pa]
            Default is to use air pressure at sea level (101,325 Pa).
    
    Returns:
        humid_ratio: A data collection or value for humidity ratio
            (aka. absolute humidity). Units are fractional (kg water / kg air).
        enthalpy: A data collection or value for enthalpy (kJ / Kg).
        wet_bulb: A data collection or value for wet bulb temperature (C).
        dew_point: A data collection or value for dew point temperature (C).
"""

ghenv.Component.Name = "LB Humidity Metrics"
ghenv.Component.NickName = 'HumidityR'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.psychrometrics import humid_ratio_from_db_rh, enthalpy_from_db_hr, \
        wet_bulb_from_db_rh, dew_point_from_db_rh
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import HumidityRatio
    from ladybug.datatype.specificenergy import Enthalpy
    from ladybug.datatype.temperature import WetBulbTemperature, DewPointTemperature
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if _pressure_ is None:
        _pressure_ = 101325

    humid_ratio = HourlyContinuousCollection.compute_function_aligned(
        humid_ratio_from_db_rh, [_dry_bulb, _rel_humid, _pressure_],
        HumidityRatio(), 'fraction')
    
    enthalpy = HourlyContinuousCollection.compute_function_aligned(
        enthalpy_from_db_hr, [_dry_bulb, humid_ratio], Enthalpy(), 'kJ/kg')

    wet_bulb = HourlyContinuousCollection.compute_function_aligned(
        wet_bulb_from_db_rh, [_dry_bulb, _rel_humid, _pressure_],
        WetBulbTemperature(), 'C')

    dew_point = HourlyContinuousCollection.compute_function_aligned(
        dew_point_from_db_rh, [_dry_bulb, _rel_humid],
        DewPointTemperature(), 'C')