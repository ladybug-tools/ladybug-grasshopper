# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Open a new viewport in Rhino that shows the parallel-projected view from the sun.
_
This is useful for understanding what parts of Rhino geometry are shaded at a
particular hour of the day.
-

    Args:
        _direction: A vector for the direction that the viewport camera faces.
        _position_: A point for the position of the vieport camera in 3D space.
            If no point is provided, the Rhino origin will be used (0, 0, 0).
        look_around_: Optional 2D point (aka. UV coordinates) to tilt the viewport
            camera off from from the input _direction. Values for UV
            coordinates must be between 0 and 1 and these correspond to a
            tilt of 90 degrees in either direction (with 0.5, 0.5 being
            centered on the _direction). Inputting a native Grasshopper
            Slider MD component will allow the most control of view offsetting.
        width_: An optional interger for the width (in pixels) of the Rhino
            viewport that will be generated.
        height_: An optional interger for the height (in pixels) of the Rhino
            viewport that will be generated.
        lens_len_: An optional number that sets the lens length of the viewport
            camera in mm. Typical values are around 20-50mm but wider angle
            views can be achieved by lowering this number to 10 or less.
            If unspecified, the lens length of the currently active Rhino
            viewport will be used.
        mode_: An optional text input for the display mode of the Rhino viewport
            that will be generated. For example: Wireframe, Shaded, Rendered, etc.
            If unspecified, the mode of the currenlty active Rhino viewport
            will be used

    Returns:
        report: The name of the viewport that was opened.
"""

ghenv.Component.Name = 'LB Set View'
ghenv.Component.NickName = 'SetView'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import math

try:
    from ladybug_geometry.geometry3d import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector3d, to_point2d
    from ladybug_rhino.fromgeometry import from_vector3d
    from ladybug_rhino.viewport import open_viewport, viewport_by_name, \
        set_view_direction, set_view_display_mode
    from ladybug_rhino.grasshopper import all_required_inputs, component_guid, \
        get_sticky_variable, set_sticky_variable
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the name of the view and the previous width/height
    view_name = 'SetView_{}'.format(component_guid(ghenv.Component))
    print(view_name)  # print so that the user has the name if needed
    vw = get_sticky_variable('set_view_width')
    vh = get_sticky_variable('set_view_height')

    # if there are look-around coordinates, rotate the direction
    if look_around_ is not None:
        uv_pt = to_point2d(look_around_)
        dir_vec = to_vector3d(_direction)
        v = (uv_pt.y - 0.5) * math.pi
        dir_vec = dir_vec.rotate(dir_vec.cross(Vector3D(0, 0, 1)), v)
        u = -(uv_pt.x - 0.5) * math.pi
        dir_vec = dir_vec.rotate_xy(u)
        _direction = from_vector3d(dir_vec)

    # get the viewport from which the direction will be set
    view_port = None
    if width_ == vw and height_ == vh:  # no need to generate new view; get existing one
        try:
            view_port = viewport_by_name(view_name)
        except ValueError:  # the viewport does not yet exist
            pass
    if view_port is None:
        view_port = open_viewport(view_name, width_, height_)
    set_sticky_variable('set_view_width', width_)
    set_sticky_variable('set_view_height', height_)

    # set the direction of the viewport camera
    set_view_direction(view_port, _direction, _position_, lens_len_)

    # set the display mode if requested
    if mode_:
        set_view_display_mode(view_port, mode_)
