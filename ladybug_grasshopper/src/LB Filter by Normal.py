# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Filter or select faces of geometry based on their orientation.

    Args:
        north_: A number between -360 and 360 for the counterclockwise difference between
            the North and the positive Y-axis in degrees. 90 is West and 270
            is East. This can also be Vector for the direction to North. (Default: 0)
        _geometry: Rhino Breps and/or Rhino Meshes which will be broken down into individual
            planar faces and filtered based on the direction they face.
        _orientation: Text for the direction that the geometry is facing. This can also be
            a number between 0 and 360 for the azimuth (clockwise horizontal
            degrees from North) that the geometry should face. Choose from
            the following:
            _
            * N = North
            * NE = Northeast
            * E = East
            * SE = Southeast
            * S = South
            * SW = Southwest
            * W = West
            * NW = Northwest
            * Up = Upwards
            * Down = Downwards
        _up_angle_: A number in degrees for the maximum declination angle from the positive
            Z Axis that is considerd up. This should be between 0 and 90 for
            the results to be practical. (Default: 30).
        _down_angle_: A number in degrees for the maximum angle difference from the newative
            Z Axis that is considerd down. This should be between 0 and 90 for
            the results to be practical. (Default: 30).
        _horiz_angle_: Angle in degrees for the horizontal deviation from _orientation
            that is still considered to face that orientation. This should be
            between 0 and 90 for the results to be practical. Note that this input
            has no effect when the input orientation is "Up" or "Down". (Default: 23).

    Returns:
        report: ...
        sel_geo: Selected faces of the input geometry that are facing the direction
            corresponding to the input criteria.
"""

ghenv.Component.Name = 'LB Filter by Normal'
ghenv.Component.NickName = 'FilterNormal'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import math

try:
    from ladybug_geometry.geometry2d import Vector2D
    from ladybug_geometry.geometry3d import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_face3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

ORIENT_MAP = {
    'N': 0,
    'NE': 45,
    'E': 90,
    'SE': 135,
    'S': 180,
    'SW': 225,
    'W': 270,
    'NW': 315,
    'NORTH': 0,
    'NORTHEAST': 45,
    'EAST': 90,
    'SOUTHEAST': 135,
    'SOUTH': 180,
    'SOUTHWEST': 225,
    'WEST': 270,
    'NORTHWEST': 315,
    'UP': 'UP',
    'DOWN': 'DOWN',
    'UPWARDS': 'UP',
    'DOWNWARDS': 'DOWN'
}


if all_required_inputs(ghenv.Component):
    # process all of the global inputs
    if north_ is not None:  # process the north_
        try:
            north_ = to_vector2d(north_).angle_clockwise(Vector2D(0, 1))
        except AttributeError:  # north angle instead of vector
            north_ = math.radians(float(north_))
    else:
        north_ = 0
    up_angle = math.radians(_up_angle_) if _up_angle_ is not None else math.radians(30)
    down_angle = math.radians(_down_angle_) if _down_angle_ is not None else math.radians(30)
    horiz_angle =  math.radians(_horiz_angle_) if _horiz_angle_ is not None else math.radians(23)
    up_vec, down_vec = Vector3D(0, 0, 1), Vector3D(0, 0, -1)

    # process the geometry and the orientation
    all_geo = [f for geo in _geometry for f in to_face3d(geo)]
    try:
        orient = ORIENT_MAP[_orientation.upper()]
    except KeyError:
        try:
            orient = float(_orientation)
        except Exception:
            msg = 'Orientation must be text (eg. N, E, S W) or a number for the\n' \
                'azimuth of the geometry. Got {}.'.format(_orientation)
            raise TypeError(msg)

    # filter the geometry by the orientation
    if orient == 'UP':
        sel_geo = [f for f in all_geo if f.normal.angle(up_vec) < up_angle]
    elif orient == 'DOWN':
        sel_geo = [f for f in all_geo if f.normal.angle(down_vec) < down_angle]
    else:
        sel_geo = []
        dir_vec = Vector2D(0, 1).rotate(north_).rotate(-math.radians(orient))
        full_down_ang = math.pi - down_angle
        for f in all_geo:
            if up_angle <= f.normal.angle(up_vec) <= full_down_ang:
                norm_2d = Vector2D(f.normal.x, f.normal.y)
                if -horiz_angle <= norm_2d.angle(dir_vec) <= horiz_angle:
                    sel_geo.append(f)

    # translate the Face3D back to Rhino geometry
    sel_geo = [from_face3d(f) for f in sel_geo]
