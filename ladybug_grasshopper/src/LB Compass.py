# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a compass sign that indicates the direction of North in the Rhino scene.
-

    Args:
        _north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. Counterclockwise
            means "90 is West and 270 is East". This can also be Vector for the
            direction to North. (Default: 0)
        _center_: A point for the center position of the compass in the Rhino
            scene. (Default: (0, 0, 0) aka. the Rhino scene origin).
        _scale_: A number to set the scale of the compass. The default is 1,
            which corresponds to a radius of 10 meters in the current Rhino
            model's unit system.

    Returns:
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in the Rhino scene.
"""

ghenv.Component.Name = 'LB Compass'
ghenv.Component.NickName = 'Compass'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D, Point2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.compass import Compass
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_vector2d, to_point2d, to_point3d
    from ladybug_rhino.fromgeometry import from_arc2d, from_linesegment2d
    from ladybug_rhino.text import text_objects
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def translate_compass(compass, z=0, font='Arial'):
    """Translate a Ladybug Compass object into Grasshopper geometry.

    Args:
        compass: A Ladybug Compass object to be converted to Rhino geometry.
        z: A number for the Z-coordinate to be used in translation. (Default: 0)
        font: Optional text for the font to be used in creating the text.
            (Default: 'Arial')

    Returns:
        A list of Rhino geometries in the following order.
        -   all_boundary_circles -- Three Circle objects for the compass boundary.
        -   major_azimuth_ticks -- Line objects for the major azimuth labels.
        -   major_azimuth_text -- Bake-able text objects for the major azimuth labels.
     """
    # set default variables based on the compass properties
    maj_txt = compass.radius / 2.5
    xaxis = Vector3D(1, 0, 0).rotate_xy(math.radians(compass.north_angle))
    result = []  # list to hold all of the returned objects

    # create the boundary circles
    for circle in compass.all_boundary_circles:
        result.append(from_arc2d(circle, z))

    # generate the labels and tick marks for the azimuths
    for line in compass.major_azimuth_ticks:
        result.append(from_linesegment2d(line, z))
    for txt, pt in zip(compass.MAJOR_TEXT, compass.major_azimuth_points):
        result.append(text_objects(
            txt, Plane(o=Point3D(pt.x, pt.y, z), x=xaxis), maj_txt, font, 1, 3))
    return result


# set defaults for all of the
if _north_ is not None:  # process the _north_
    try:
        _north_ = math.degrees(to_vector2d(_north_).angle_clockwise(Vector2D(0, 1)))
    except AttributeError:  # north angle instead of vector
        _north_ = float(_north_)
else:
    _north_ = 0
if _center_ is not None:  # process the center point into a Point2D
    center_pt, z = to_point2d(_center_), to_point3d(_center_).z
else:
    center_pt, z = Point2D(), 0
_scale_ = 1 if _scale_ is None else _scale_ # process the scale into a radius
radius = (10 * _scale_) / conversion_to_meters()

# create the compass
compass = translate_compass(Compass(radius, center_pt, _north_, 1), z)
