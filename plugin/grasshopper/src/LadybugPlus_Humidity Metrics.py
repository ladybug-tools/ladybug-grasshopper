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

ghenv.Component.Name = "LadybugPlus_Humidity Metrics"
ghenv.Component.NickName = 'humidity'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from ladybug.psychrometrics import humid_ratio_from_db_rh, enthalpy_from_db_hr, \
        wet_bulb_from_db_rh, dew_point_from_db_rh
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import HumidityRatio
    from ladybug.datatype.specificenergy import Enthalpy
    from ladybug.datatype.temperature import WetBulbTemperature, DewPointTemperature
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

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