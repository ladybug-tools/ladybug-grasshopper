# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Compute a True North angle and vector from Magnetic North at a given location.
_
This component uses then World Magnetic Model (WMM) developed and maintained by NOAA.
https://www.ncei.noaa.gov/products/world-magnetic-model
-

    Args:
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component. This is used
            to determine the difference between magnetic and true North.
        _mag_north: A number between -360 and 360 for the counterclockwise difference
            between Magnetic North and the positive Y-axis in degrees. Counterclockwise
            means "90 is West and 270 is East". This can also be Vector for the
            magnetic North direction.
        _year_: A number for the year in which the Magnetic North was evaluated. Decimal
            values are accepted. This is needed as the location of Magnetic
            North has been moving at a rate of roughly 50 km/year for the
            past couple of decades. (Default: 2025).
        cof_file_: An optional path to a .COF file containing the coefficients that form the
            inputs for the World Magnetic Model (WMM). A new set of coefficients
            is published roughly every 5 years as the magnetic poles continue to
            move. If unspecified, coefficients will be taken from the most
            recent model. COF files with the most recent coefficients and
            historical values are available at:
            https://www.ncei.noaa.gov/products/world-magnetic-model/wmm-coefficients

    Returns:
        mag_declination: The magnetic declination in degrees. Magnetic declination is the
        difference between magnetic North and true North at a given location on
        the globe (expressed in terms of degrees).
        true_north: A number between -360 and 360 for the True North angle in degrees.
        true_north_vec: A vector for the True North direction. This can be plugged into
            any of the north_ inputs of the other LAdybug Tools components.
"""

ghenv.Component.Name = 'LB Magnetic to True North'
ghenv.Component.NickName = 'TrueNorth'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.north import WorldMagneticModel
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.fromgeometry import from_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the _magn_north and the year
    try:
        _mag_north = math.degrees(to_vector2d(_mag_north).angle_clockwise(Vector2D(0, 1)))
    except AttributeError:  # north angle instead of vector
        _mag_north = float(_mag_north)
    _year_ = _year_ if _year_ is not None else 2025

    # initialize the WorldMagneticModel and convert the north angle
    wmm_obj = WorldMagneticModel(cof_file_)
    true_north = wmm_obj.magnetic_to_true_north(_location, _mag_north, _year_)
    mag_declination = true_north - _mag_north

    # convert the true north angle to a vector
    st_north = Vector2D(0, 1).rotate(math.radians(_mag_north))
    true_north_vec = st_north.rotate(math.radians(true_north))
    true_north_vec = from_vector2d(true_north_vec)
