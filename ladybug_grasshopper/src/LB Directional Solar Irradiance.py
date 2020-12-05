# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Compute the hourly solar irradiance falling on an unobstructed surface that faces
any direction.
_
The calculation method of this component is faster than running "LB Incident
Radiation" studies on an hour-by-hour basis and it is slighty more acurate as
it accounts for ground reflection. However, this comes at the cost of not being
able to account for any obstructions that block the sun.
-

    Args:
        _location: A Ladybug Location object, used to determine the altitude and
            azimuth of the sun at each hour.
        _dir_norm_rad: Hourly Data Collection with the direct normal solar
            irradiance in W/m2.
        _diff_horiz_rad: Hourly Data Collection with diffuse horizontal solar
            irradiance in W/m2.
        _srf_azimuth_: A number between 0 and 360 that represents the azimuth at which
            irradiance is being evaluated in degrees.  0 = North, 90 = East,
            180 = South, and 270 = West.  (Default: 180).
        _srf_altitude_: A number between -90 and 90 that represents the altitude at which
            irradiance is being evaluated in degrees. A value of 0 means the
            surface is facing the horizon and a value of 90 means a surface is
            facing straight up. (Default: 0).
        _ground_ref_: A number between 0 and 1 that represents the reflectance of the
            ground. (Default: 0.2). Some common ground reflectances are:
                *   urban: 0.18
                *   grass: 0.20
                *   fresh grass: 0.26
                *   soil: 0.17
                *   sand: 0.40
                *   snow: 0.65
                *   fresh_snow: 0.75
                *   asphalt: 0.12
                *   concrete: 0.30
                *   sea: 0.06
        anisotrophic_: A boolean value that sets whether an anisotropic sky is used
            (as opposed to an isotropic sky). An isotrophic sky assumes an
            even distribution of diffuse irradiance across the sky while an
            anisotropic sky places more diffuse irradiance near the solar
            disc. (Default: False).

    Returns:
        report: ...
        total_rad: A data collection of total solar irradiance in the direction of
            the _srf_azimuth_ and _srf_altitude_.
        direct_rad: A data collection of direct solar irradiance in the direction of
            the _srf_azimuth_ and _srf_altitude_.
        diff_rad: A data collection of diffuse sky solar irradiance in the direction
            of the _srf_azimuth_ and _srf_altitude_.
        reflect_rad: A data collection of ground reflected solar irradiance in the direction
            of the _srf_azimuth_ and _srf_altitude_.
"""

ghenv.Component.Name = 'LB Directional Solar Irradiance'
ghenv.Component.NickName = 'DirSolar'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    az = _srf_azimuth_ if _srf_azimuth_ is not None else 180
    alt = _srf_altitude_ if _srf_altitude_ is not None else 0
    gref = _ground_ref_ if _ground_ref_ is not None else 0.2
    isot = not anisotrophic_

    # create the Wea and output irradaince
    wea = Wea(_location, _dir_norm_rad, _diff_horiz_rad)
    total_rad, direct_rad, diff_rad, reflect_rad = \
        wea.directional_irradiance(alt, az, gref, isot)
