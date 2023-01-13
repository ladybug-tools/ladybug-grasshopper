# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Import climate data from a standard .epw file.

-

    Args:
        _epw_file: An .epw file path on your system as a string.
        
    Returns:
        location: A Ladybug Location object describing the location data in the
            weather file.
        dry_bulb_temperature: The houlry dry bulb temperature, in C.
            Note that this is a full numeric field (i.e. 23.6) and not an integer
            representation with tenths. Valid values range from 70 C to
            70 C. Missing value for this field is 99.9.
        dew_point_temperature: The hourly dew point temperature, in C.
            Note that this is a full numeric field (i.e. 23.6) and not an integer
            representation with tenths. Valid values range from 70 C to
            70 C. Missing value for this field is 99.9.
        relative_humidity: The hourly Relative Humidity in percent.
            Valid values range from 0% to 110%. Missing value for this field is 999.
        wind_speed: The hourly wind speed in m/sec.
            Values can range from 0 to 40. Missing value is 999.
        wind_direction: The hourly wind direction in degrees.
            The convention is North=0.0, East=90.0, South=180.0, West=270.0.
            If wind is calm for the given hour, the direction equals zero.
            Values can range from 0 to 360. Missing value is 999.
        direct_normal_rad: The hourly Direct Normal Radiation in Wh/m2.
            Direc Normal Radiation is the amount of solar radiation in Wh/m2
            received directly from the solar disk on a surface perpendicular
            to the sun's rays. Missing values are (9999).
        diffuse_horizontal_rad: The hourly Diffuse Horizontal Radiation in Wh/m2.
            Diffuse Horizontal Radiation is the amount of solar radiation in
            Wh/m2 received from the sky (excluding the solar disk) on a
            horizontal surface. Missing values are (9999).
        global_horizontal_rad: The hourly Global Horizontal Radiation in Wh/m2.
            Global Horizontal Radiation is the total amount of direct and
            diffuse solar radiation in Wh/m2 received on a horizontal surface.
            It is not currently used inbEnergyPlus calculations. It should
            have a minimum value of 0; missing value for this field is 9999.
        horizontal_infrared_rad: The Horizontal Infrared Radiation Intensity in Wh/m2.
            If it is missing, EnergyPlus calculates it from the Opaque Sky Cover
            field. It should have a minimum value of 0; missing value is 9999.
        direct_normal_ill: The hourly Direct Normal Illuminance in lux.
            Direct Normal Illuminance is the average amount of illuminance in
            lux received directly from the solar disk on a surface
            perpendicular to the sun's rays. It is not currently used in
            EnergyPlus calculations. It should have a minimum value of 0;
            missing value is 999999.
        diffuse_horizontal_ill: The hourly Diffuse Horizontal Illuminance in lux.
            Diffuse Horizontal Illuminance is the average amount of illuminance
            in lux received from the sky (excluding the solar disk) on a
            horizontal surface. It is not currently used in EnergyPlus
            calculations. It should have a minimum value of 0; missing
            value is 999999.
        global_horizontal_ill: The hourly Global Horizontal Illuminance in lux.
            Global Horizontal Illuminance is the average total amount of
            direct and diffuse illuminance in lux received on a horizontal
            surface. It is not currently used in EnergyPlus calculations.
            It should have a minimum value of 0; missing value is 999999.
        total_sky_cover: The fraction for Total Sky Cover  in tenths of coverage.
            (eg. 1 is 1/10 covered. 10 is total coverage). Total Sky Cover is
            the amount of the sky dome covered by clouds or obscuring phenomena.
            Minium value is 0; maximum value is 10; missing value is 99.
        barometric_pressure: The hourly weather station pressure in Pa.
            Valid values range from 31,000 to 120,000. Missing value is 999999.
        model_year: The year from which the hourly data has been extracted.
            EPW files are synthesized from real recorded data from different
            years in a given climate. This is done to ensure that, for each
            month, the selected data is statistically representative of the
            average monthly conditions over the 18+ years of recording the data.
            Different EPW files will be synthesized from different years
            depeding on whether they are TMY (Typical Meteorological Year),
            TMY2, TMY3, AMY (Actual Meteorological Year) or other.
        ground_temperature: Monthly ground temperature data if it exists within
            the EPW file. Typically, each data collection in this list
            represents monthly temperatures at three different depths.
            - 0.5 meters
            - 2.0 meters
            - 4.0 meters
"""

ghenv.Component.Name = 'LB Import EPW'
ghenv.Component.NickName = 'ImportEPW'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    import ladybug.epw as epw
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    epw_data = epw.EPW(_epw_file)
    location = epw_data.location
    dry_bulb_temperature = epw_data.dry_bulb_temperature
    dew_point_temperature = epw_data.dew_point_temperature
    relative_humidity = epw_data.relative_humidity
    wind_speed = epw_data.wind_speed
    wind_direction = epw_data.wind_direction
    direct_normal_rad = epw_data.direct_normal_radiation
    diffuse_horizontal_rad = epw_data.diffuse_horizontal_radiation
    global_horizontal_rad = epw_data.global_horizontal_radiation
    horizontal_infrared_rad = epw_data.horizontal_infrared_radiation_intensity
    direct_normal_ill = epw_data.direct_normal_illuminance
    diffuse_horizontal_ill = epw_data.diffuse_horizontal_illuminance
    global_horizontal_ill = epw_data.global_horizontal_illuminance
    total_sky_cover = epw_data.total_sky_cover
    barometric_pressure = epw_data.atmospheric_station_pressure
    model_year = epw_data.years
    g_temp = epw_data.monthly_ground_temperature
    ground_temperature = [g_temp[key] for key in sorted(g_temp.keys())]
