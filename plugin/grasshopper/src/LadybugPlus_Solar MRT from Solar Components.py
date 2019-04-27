# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate Mean Radiant Temperature (MRT) as a result of shortwave solar using
horizontal solar components (direct horizontal and diffuse horizontal solar).
-
This component uses the SolarCal model of ASHRAE-55 to estimate the effects
of shortwave solar and a simple sky exposure method to determine longwave
radiant exchange.
-

    Args:
        _location: A Ladybug Location object.
        _dir_horiz_solar: Hourly Data Collection with the direct horizontal solar
            irradiance in W/m2.
        _diff_horiz_solar: Hourly Data Collection with diffuse horizontal solar
            irradiance in W/m2.
        _longwave_mrt: A single number or an hourly data collection with the
            long wave mean radiant temperature around the person in degrees C.
            This includes the temperature of the ground and any other surfaces
            between the person and their view to the sky.
            Typically, dry bulb temperature is used when such surface
            temperatures are unknown.
        fract_body_exp_: A single number between 0 and 1 or a data collection
            representing the fraction of the body exposed to direct sunlight.
            Note that this does not include the bodys self-shading; only the
            shading from surroundings.
            Default is 1 for a person standing in an open area.
        _ground_ref_: A single number between 0 and 1 or a data collection
            that represents the reflectance of the floor. Default is for 0.25
            which is characteristic of outdoor grass or dry bare soil.
        _solar_body_par_: Optional Solar Body Parameter object to account for
            properties of the human geometry.
        _run: Set to True to run the component.
    Returns:
        report: Reports, errors, warnings, etc.
        erf: Data collection of effective radiant field (ERF) in W/m2.
        dmrt: Data collection of mean radiant temperature delta in C.
        mrt: Data collection of mean radiant temperature in C.
"""

ghenv.Component.Name = "LadybugPlus_Solar MRT from Solar Components"
ghenv.Component.NickName = 'componentSolarMRT'
ghenv.Component.Message = 'VER 0.0.04\nAPR_27_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:
    from ladybug_comfort.collection.solarcal import HorizontalSolarCal
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _run is True and _location and _diff_horiz_solar and _dir_horiz_solar \
        and _longwave_mrt:
    
    solar_mrt_obj = HorizontalSolarCal(_location, _dir_horiz_solar,
                                       _diff_horiz_solar, _longwave_mrt,
                                       fract_body_exp_, _ground_ref_, _solar_body_par_)
    
    erf = solar_mrt_obj.effective_radiant_field
    dmrt = solar_mrt_obj.mrt_delta
    mrt = solar_mrt_obj.mean_radiant_temperature