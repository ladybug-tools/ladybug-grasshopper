# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Orient a series of geometries to the active viewport camera.
-

    Args:
        _geo: A series of geometries to be oriented to the camera of the active
            Rhino viewport.
        _position_: A point to be used as the origin around which the the geometry
            will be oriented. If None, the lower left corner of the bounding box
            around the geometry will be used.
        refresh_: Connect a Grasshopper "button" component to refresh the orientation
            upon hitting the button. You can also connect a Grasshopper "Timer"
            component to update the view in real time as you navigate through
            the Rhino scene.
    
    Returns:
        geo: The input geometry that has been oriented to the camera of the active
            Rhino viewport.
"""

ghenv.Component.Name = 'LB Orient to Camera'
ghenv.Component.NickName = 'OrientCam'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import Rhino.Geometry as rg
import Rhino.Display as rd

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.text import TextGoo
    from ladybug_rhino.viewport import camera_oriented_plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def bounding_box_origin(geometry):
    """Get the origin of a bounding box around a list of geometry.

    Args:
        geometry: A list of geometry for which the bounding box origin will
            be computed.
    """
    b_box = geometry[0].GetBoundingBox(False)
    for geo in geometry[1:]:
        if isinstance(geo, rd.Text3d):
            b_box = rg.BoundingBox.Union(b_box, geo.BoundingBox)
        else:
            b_box = rg.BoundingBox.Union(b_box, geo.GetBoundingBox(False))
    return b_box.Corner(True, True, True)


if all_required_inputs(ghenv.Component):
    # set the default position if it is None
    origin = bounding_box_origin(_geo)
    pt = origin if _position_ is None else _position_

    # get a plane oriented to the camera
    oriented_plane = camera_oriented_plane(pt)

    # orient the input geometry to the plane facing the camera
    base_plane = rg.Plane(origin, rg.Vector3d(0, 0, 1))
    xform = rg.Transform.PlaneToPlane(base_plane, oriented_plane)
    geo = []
    for rh_geo in _geo:
        if isinstance(rh_geo, rd.Text3d):
            geo.append(TextGoo(rh_geo).Transform(xform))
        else:
            new_geo = rh_geo.Duplicate()
            new_geo.Transform(xform)
            geo.append(new_geo)
