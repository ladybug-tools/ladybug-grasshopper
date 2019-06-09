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
        _dir_norm_rad: Hourly Data Collection with the direct normal solar
            irradiance in W/m2.
        _diff_horiz_rad: Hourly Data Collection with diffuse horizontal solar
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
        sky_exposure_: A single number between 0 and 1 or a data collection
            representing the fraction of the sky vault in occupants view.
            Default is 1 for a person standing in an open area.
        _ground_ref_: A single number between 0 and 1 or a data collection
            that represents the reflectance of the floor. Default is for 0.25
            which is characteristic of concrete.
        _window_trans_: A Data Collection or number between 0 and 1 that
                represents the broadband solar transmittance of the window through which
                the sun is coming. Such values tend to be slightly less than the
                SHGC. Values might be as low as 0.2 and could be as high as 0.85
                for a single pane of glass. Default is 0.4 assuming a double pane
                window with a relatively mild low-e coating.
        _solar_body_par_: Optional Solar Body Parameter object to account for
            properties of the human geometry.
        _run: Set to True to run the component.
    Returns:
        report: Reports, errors, warnings, etc.
        erf: Data collection of effective radiant field (ERF) in W/m2.
        dmrt: Data collection of mean radiant temperature delta in C.
        mrt: Data collection of mean radiant temperature in C.
"""

ghenv.Component.Name = "LadybugPlus_Indoor Solar MRT"
ghenv.Component.NickName = 'indoorSolarMRT'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:
    from ladybug_comfort.collection.solarcal import IndoorSolarCal
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component) and _run is True:
    solar_mrt_obj = IndoorSolarCal(_location, _dir_norm_rad,
                                   _diff_horiz_rad, _longwave_mrt,
                                   fract_body_exp_, sky_exposure_,
                                   _ground_ref_, _window_trans_, _solar_body_par_)
    
    erf = solar_mrt_obj.effective_radiant_field
    dmrt = solar_mrt_obj.mrt_delta
    mrt = solar_mrt_obj.mean_radiant_temperature