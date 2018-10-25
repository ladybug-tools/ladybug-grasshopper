# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import hourly climate data from a Ladybug DesignDay object.

-

    Args:
        _design_day: A DesignDay object to import.
        
    Returns:
        location: A Ladybug Location object describing the location of the design day.
        dry_bulb_temperature: The houlry dry bulb temperature over the design day, in C.
        dew_point_temperature: The hourly dew point temperature over the design day, in C.
        relative_humidity: The hourly Relative Humidity over the design day in percent.
        wind_speed: The hourly wind speed over the design day in m/sec.
        wind_direction: The hourly wind direction over the design day in degrees.
            The convention is that North=0.0, East=90.0, South=180.0, West=270.0.
        direct_normal_rad: The hourly Direct Normal Radiation over the design day in Wh/m2.
        diffuse_horizontal_rad: The hourly Diffuse Horizontal Radiation over the design day in Wh/m2.
        global_horizontal_rad: The hourly Global Horizontal Radiation over the design day in Wh/m2.
        horizontal_infrared_rad: The Horizontal Infrared Radiation Intensity over the design day in Wh/m2.
        total_sky_cover: The fraction for total sky cover over the design day in tenths of coverage.
        barometric_pressure: The hourly weather station pressure over the design day in Pa.
"""

ghenv.Component.Name = "LadybugPlus_Import Design Day"
ghenv.Component.NickName = 'importDesignDay'
ghenv.Component.Message = 'VER 0.0.04\nOCT_14_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

if _design_day:
    dry_bulb_temperature = _design_day.hourly_dry_bulb
    dew_point_temperature = _design_day.hourly_dew_point
    relative_humidity = _design_day.hourly_relative_humidity
    wind_speed = _design_day.hourly_wind_speed
    wind_direction = _design_day.hourly_wind_direction
    direct_normal_rad, diffuse_horizontal_rad, global_horizontal_rad = \
        _design_day.hourly_solar_radiation
    horizontal_infrared_rad = _design_day.hourly_horizontal_infrared
    total_sky_cover = _design_day.hourly_sky_cover
    barometric_pressure = _design_day.hourly_barometric_pressure
