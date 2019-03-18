# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate Mean Radiant Temperature (MRT) as a result of outdoor shortwave
solar shining directly onto people as well as longwave radiant exchange
with the sky.
-
This component uses the SolarCal model of ASHRAE-55 to estimate the effects
of shortwave solar and a simple sky exposure method to determine longwave
radiant exchange.
-

    Args:
        _location: A Ladybug Location object.
        _dir_norm_solar: Hourly Data Collection with the direct normal solar
            irradiance in W/m2.
        _diff_horiz_solar: Hourly Data Collection with diffuse horizontal solar
            irradiance in W/m2.
        _horiz_infrared: Hourly Data Collection with the horizontal infrared
            radiation intensity from the sky in W/m2.
        _surface_temp: A single number or an hourly data collection with the
            temperature of surfaces around the person in degrees C. This includes
            the ground and any other surfaces blocking the view to the sky.
            Typically, outdoor dry bulb temperature is used when such surface
            temperatures are unknown.
        fract_body_exp_: A single number between 0 and 1 or a data collection
            representing the fraction of the body exposed to direct sunlight.
            Note that this does not include the bodys self-shading; only the
            shading from surroundings.
            Default is 1 for a person standing in an open area.
        sky_exposure_: A single number between 0 and 1 or a data collection
            representing the fraction of the sky vault in occupants view.
            Default is 1 for a person standing in an open area.
        _ground_ref_: A single number between 0 and 1 or a data collection
            that represents the reflectance of the floor. Default is for 0.25
            which is characteristic of outdoor grass or dry bare soil.
        _solar_body_par_: Optional Solar Body Parameter object to account for
            properties of the human geometry.
        _run: Set to True to run the component and calculate PMV.
    Returns:
        report: Reports, errors, warnings, etc.
        short_erf: Data collection of shortwave effective radiant field (ERF) in W/m2.
        long_erf: Data collection of longwave effective radiant field (ERF) in W/m2.
        short_dmrt: Data collection of shortwave mean radiant temperature delta in C.
        long_dmrt: Data collection of longwave mean radiant temperature delta in C.
        mrt: Data collection of mean radiant temperature in C.  This accounts for
            both the shortwave solar shining directly onto people as well as
            longwave radiant exchange with the sky.
"""

ghenv.Component.Name = "LadybugPlus_Outdoor Solar MRT"
ghenv.Component.NickName = 'outdoorSolarMRT'
ghenv.Component.Message = 'VER 0.0.04\nMAR_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:
    from ladybug_comfort.collection.solarcal import OutdoorSolarCal
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _run is True and _location and _diff_horiz_solar and _dir_norm_solar and \
        _horiz_infrared and _surface_temp:
    
    solar_mrt_obj = OutdoorSolarCal(_location, _dir_norm_solar, _diff_horiz_solar,
                                    _horiz_infrared, _surface_temp, fract_body_exp_,
                                    sky_exposure_, _ground_ref_, _solar_body_par_)
    
    short_erf = solar_mrt_obj.shortwave_effective_radiant_field
    long_erf = solar_mrt_obj.longwave_effective_radiant_field
    short_dmrt = solar_mrt_obj.shortwave_mrt_delta
    long_dmrt = solar_mrt_obj.longwave_mrt_delta
    mrt = solar_mrt_obj.mean_radiant_temperature