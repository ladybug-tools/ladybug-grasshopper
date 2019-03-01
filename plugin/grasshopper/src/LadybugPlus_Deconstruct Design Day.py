# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct design day into parameters.

-

    Args:
        _design_day: A DesignDay object to deconstruct.
        
    Returns:
        name: The name of the DesignDay object.
        day_type: Text indicating the type of design day (ie. 'SummerDesignDay',
            'WinterDesignDay' or other EnergyPlus days).
        location: A Ladybug Location object describing the location of the design day.
        analysis_period: Analysis period for the design day
        dry_bulb_max: Maximum dry bulb temperature over the design day (in C).
        dry_bulb_range: Dry bulb range over the design day (in C).
        humidity_type: Type of humidity to use. (ie. Wetbulb, Dewpoint, HumidityRatio, Enthalpy)
        humidity_value: The value of the humidity condition above.
        barometric_p: Barometric pressure in Pa.
        wind_speed: Wind speed over the design day in m/s.
        wind_dir: Wind direction over the design day in degrees.
        sky_model: Type of solar model to use.  (ie. ASHRAEClearSky, ASHRAETau)
        sky_properties: A list of properties describing the sky above.
            For ASHRAEClearSky this is a single value for clearness.
            For ASHRAETau, this is the tau_beam and tau_diffuse.
"""

ghenv.Component.Name = "LadybugPlus_Deconstruct Design Day"
ghenv.Component.NickName = 'decnstrDesignDay'
ghenv.Component.Message = 'VER 0.0.04\nNOV_17_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "5"


if _design_day:
    name = _design_day.name
    day_type = _design_day.day_type
    location  = _design_day.location
    analysis_period = _design_day.analysis_period
    dry_bulb_max = _design_day.dry_bulb_condition.dry_bulb_max
    dry_bulb_range = _design_day.dry_bulb_condition.dry_bulb_range
    humidity_type = _design_day.humidity_condition.hum_type
    humidity_value = _design_day.humidity_condition.hum_value
    barometric_p = _design_day.humidity_condition.barometric_pressure
    wind_speed = _design_day.wind_condition.wind_speed
    wind_dir = _design_day.wind_condition.wind_direction
    sky_type = _design_day.sky_condition.solar_model
    if sky_type == 'ASHRAETau':
        sky_properties = [_design_day.sky_condition.tau_b, _design_day.sky_condition.tau_d]
    else:
        sky_properties = _design_day.sky_condition.clearness