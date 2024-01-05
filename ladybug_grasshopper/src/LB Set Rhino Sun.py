# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the sun in the Rhino scene to correspond to a given location and date/time.
_
This can be help coordinate Rhino visualizations with Ladybug analyses.
-

    Args:
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        hoys_: A number between 0 and 8760 that represents the hour of the year at
            which to set the sun position. This can also be a list of numbers
            in which case several Rhino suns will be rendered in the scene.
            The "LB Calculate HOY" component can output this number given a
            month, day and hour. The "LB Analysis Period" component can
            output a list of HOYs within a certain hour or date range.
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _run: Set to True to run the component set the Rhino Sun.

    Returns:
        report: Reports, errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Set Rhino Sun'
ghenv.Component.NickName = 'RhinoSun'
ghenv.Component.Message = '1.7.2'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.light import set_sun, disable_sun, set_suns
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    disable_sun()
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    if len(_hoy) == 1:
        set_sun(_location, _hoy[0], north_)
    else:
        set_suns(_location, _hoy, north_)
else:
    disable_sun()
