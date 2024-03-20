# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
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
        _vector: A sun vector from which the the Rhino view will be generated.
            Use the "LB SunPath" component to generate sun vectors.
        _center_pt_: The target point of the camera for the Rhino view that will be
            generated.  This point should be close to the Rhino geometry that
            you are interested in viewing from the sun. If no point is provided,
            the Rhino origin will be used (0, 0, 0).
        width_: An optional interger for the width (in pixels) of the Rhino
            viewport that will be generated.
        height_: An optional interger for the height (in pixels) of the Rhino
            viewport that will be generated.
        mode_: An optional text input for the display mode of the Rhino viewport
            that will be generated. For example: Wireframe, Shaded, Rendered, etc.

    Returns:
        report: The name of the viewport that was opened.
"""

ghenv.Component.Name = 'LB View From Sun'
ghenv.Component.NickName = 'ViewFromSun'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:
    from ladybug_rhino.viewport import viewport_by_name, open_viewport, \
        set_iso_view_direction, set_view_display_mode
    from ladybug_rhino.grasshopper import all_required_inputs, component_guid, \
        get_sticky_variable, set_sticky_variable
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the name of the view and the previous width/height
    view_name = 'ViewFromSun_{}'.format(component_guid(ghenv.Component))
    print(view_name)  # print so that the user has the name if needed
    vw = get_sticky_variable('sun_view_width')
    vh = get_sticky_variable('sun_view_height')

    # get the viewport from which the direction will be set
    view_port = None
    if width_ == vw and height_ == vh:  # no need to generate new view; get existing one
        try:
            view_port = viewport_by_name(view_name)
        except ValueError:  # the viewport does not yet exist
            pass
    if view_port is None:
        view_port = open_viewport(view_name, width_, height_)
    set_sticky_variable('sun_view_width', width_)
    set_sticky_variable('sun_view_height', height_)

    # set the direction of the viewport camera
    set_iso_view_direction(view_port, _vector, _center_pt_)

    # set the display mode if requested
    if mode_:
        set_view_display_mode(view_port, mode_)
