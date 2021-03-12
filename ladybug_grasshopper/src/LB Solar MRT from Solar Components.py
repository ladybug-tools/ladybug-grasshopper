# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
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
        _longwave_mrt: A single number or an hourly data collection with the long-wave
            mean radiant temperature around the person in degrees C.
            This includes the temperature of the ground and any other
            surfaces between the person and their view to the sky.
            Typically, air temperature is used when such surface
            temperatures are unknown.
        _dir_horiz_rad: Hourly Data Collection with the direct horizontal solar
            irradiance in W/m2.
        _diff_horiz_rad: Hourly Data Collection with diffuse horizontal solar
            irradiance in W/m2.
        fract_body_exp_: A single number between 0 and 1 or a data collection
            representing the fraction of the body exposed to direct sunlight.
            Note that this does not include the body’s self-shading; only the
            shading from surroundings.
            Default is 1 for a person standing in an open area.
        _ground_ref_: A single number between 0 and 1 or a data collection
            that represents the reflectance of the floor. Default is for 0.25
            which is characteristic of outdoor grass or dry bare soil.
        _solar_body_par_: Optional solar body parameters from the "LB Solar Body Parameters"
            object to specify the properties of the human geometry assumed in the
            shortwave MRT calculation. The default assumes average skin/clothing
            absorptivity and a human subject always has their back to the sun
            at a 45-degree angle (SHARP = 135).
        _run: Set to True to run the component.

    Returns:
        report: Reports, errors, warnings, etc.
        erf: Data collection of effective radiant field (ERF) in W/m2.
        dmrt: Data collection of mean radiant temperature delta in C.
        mrt: Data collection of mean radiant temperature in C.
"""

ghenv.Component.Name = 'LB Solar MRT from Solar Components'
ghenv.Component.NickName = 'ComponentSolarMRT'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.collection.solarcal import HorizontalSolarCal
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run is True:
    solar_mrt_obj = HorizontalSolarCal(_location, _dir_horiz_rad,
                                       _diff_horiz_rad, _longwave_mrt,
                                       fract_body_exp_, _ground_ref_, _solar_body_par_)

    erf = solar_mrt_obj.effective_radiant_field
    dmrt = solar_mrt_obj.mrt_delta
    mrt = solar_mrt_obj.mean_radiant_temperature