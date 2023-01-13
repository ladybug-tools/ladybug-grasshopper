# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize the portion of the sky dome that is masked by context geometry or shading
strategies around a given point.
_
Separate meshs will be generated for the portions of the sky dome that are masked
vs visible. The percentage of the sky that is masked by the context geometry and
is visible will also be computed.
-

    Args:
        context_: Rhino Breps and/or Rhino Meshes representing context geometry that
            can block the sky to the center of the sky mask.
        orientation_: A number between 0 and 360 that sets the direction of a vertically-
            oriented surface for which the sky view will be visualized and
            computed. Alternatively, this input can be the words "north",
            "east", "south" or "west." An input here will result in the output
            of an orient_mask, which blocks the portion of the sky that is not
            visible from a vertical surface with this orientation. Furthermore,
            all of the view-related outputs will be computed for a surface with
            the specified orientation (overriding any plane input for the _center_).
        overhang_proj_: A number between 0 and 90 that sets the angle between the _center_
            and the edge of an imagined horizontal overhang projecting past
            the point. Note that this option is only available when there is
            an input for orientation_ above. An input here will result in the
            output of a strategy_mask, which blocks the portion of the sky
            taken up by an overhang with the input projection angle.
        left_fin_proj_: A number between 0 and 180 that sets the angle between the _center_
            and the edge of an imagined vertical fin projecting past the left
            side of the point. Note that this option is only available when
            there is an input for orientation_ above. An input here will result
            in the output of a strategy_mask, which blocks the portion of the
            sky taken up by a vertical fin with the input projection angle.
        right_fin_proj_: A number between 0 and 180 that sets the angle between the _center_
            and the edge of an imagined vertical fin projecting past the right
            side of the point. Note that this option is only available when
            there is an input for orientation_ above. An input here will result
            in the output of a strategy_mask, which blocks the portion of the
            sky taken up by a vertical fin with the input projection angle.
        _density_: An integer that is greater than or equal to 1, which to sets the
            number of times that the sky patches are split. Higher numbers
            input here will ensure a greater accuracy but will also take
            longer to run. A value of 3 should result in sky view factors
            with less than 1% error from the true value. (Default: 1).
        _center_: A point or plane for which the visible portion of the sky will
            be evaluated. If a point is input here, the view-related outputs
            will be indiferent to orientation and the sky_view outut will
            technically be Sky Exposure (or the fraction of the sky hemisphere
            that is visible from the point). If a plane is input here (or an
            orientation_ is connected), the view-related outputs will be
            sensitive to orientation and the sky_view output will be true
            Sky View (or the fraction of the sky visible from a surface in
            a plane). If no value is input here, the center will be a point
            (Sky Exposure) at the Rhino origin (0, 0, 0).
        _scale_: A number to set the scale of the sky mask. The default is 1,
            which corresponds to a radius of 100 meters in the current Rhino
            model's unit system.
        projection_: Optional text for the name of a projection to use from the sky
            dome hemisphere to the 2D plane. If None, a 3D dome will be drawn
            instead of a 2D one. Choose from the following:
                * Orthographic
                * Stereographic

    Returns:
        report: ...
        context_mask: A mesh for the portion of the sky dome masked by the context_
            geometry.
        orient_mask: A mesh for the portion of the sky dome that is not visible from
            a surface is facing a given orientation.
        strategy_mask: A mesh of the portion of the sky dome masked by the overhang,
            left fin, and right fin projections.
        sky_mask: A mesh of the portion of the sky dome visible by the _center_
            through the strategies and context_ geometry.
        context_view: The percentage of the sky dome masked by the context_ geometry.
        orient_view: The percentage of the sky dome that is not visible from a
            surface is facing a given orientation.
        strategy_view: The percentage of the sky dome viewed by the overhang, left
            fin, and right fin projections.
        sky_view: The percentage of the sky dome visible by the _center_ through
            the strategies and context_ geometry.
"""

ghenv.Component.Name = 'LB Sky Mask'
ghenv.Component.NickName = 'SyMask'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.viewsphere import view_sphere
    from ladybug.compass import Compass
    from ladybug.color import Color
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d, to_plane
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def apply_mask_to_sky(sky_pattern, mask_pattern):
    """Apply a pattern of a mask to a pattern of visible sky."""
    for i, val in enumerate(mask_pattern):
        if val:
            sky_pattern[i] = False


def apply_mask_to_base_mask(base_pattern, mask_pattern, ignore_pattern):
    """Apply a pattern of a mask to a base pattern with the option to ignore elements."""
    for i, (val, ig_val) in enumerate(zip(mask_pattern, ignore_pattern)):
        if val and not ig_val:
            base_pattern[i] = True


def mask_mesh_from_pattern(base_mask, mask_pattern, color):
    """Get a Rhino mesh of a mask from a pattern aligned to the faces of a base mesh."""
    try:
        mask_mesh = base_mask.remove_faces_only(mask_pattern)
    except AssertionError:  # all mesh faces have been removed
        return None
    mask_mesh.colors = [color] * len(mask_mesh.faces)
    return from_mesh3d(mask_mesh)



# process the inputs and set defaults for global variables
_scale_ = 1 if _scale_ is None else _scale_
radius = (100 * _scale_) / conversion_to_meters()
if _center_ is not None:  # process the center point into a Point2D
    try:  # assume that it is a point
        center_pt3d, direction = to_point3d(_center_), None
    except AttributeError:
        plane, is_orient = to_plane(_center_), True
        center_pt3d, direction = plane.o, plane.n
else:
    center_pt3d, direction = Point3D(), None
az_count, alt_count = 72, 18
if _density_:
    az_count = az_count * _density_
    alt_count = alt_count * _density_
if orientation_ is not None:  # process the orientation to a number
    ori_dict = {'north': 0, 'east': 90, 'south': 180, 'west': 270}
    try:  # first check if it's text for the direction
        orientation_ = ori_dict[orientation_.lower()]
    except KeyError:  # it's a number for the orientation
        orientation_ = float(orientation_)
    direction = Vector3D(0, 1, 0).rotate_xy(-math.radians(orientation_))


# create the dome mesh of the sky and position/project it correctly
sky_mask, view_vecs = view_sphere.dome_radial_patches(az_count, alt_count)
sky_mask = sky_mask.scale(radius)
if center_pt3d != Point3D():
    m_vec = Vector3D(center_pt3d.x, center_pt3d.y, center_pt3d.z)
    sky_mask = sky_mask.move(m_vec)
if projection_ is not None:
    if projection_.title() == 'Orthographic':
        pts = (Compass.point3d_to_orthographic(pt) for pt in sky_mask.vertices)
    elif projection_.title() == 'Stereographic':
        pts = (Compass.point3d_to_stereographic(pt, radius, center_pt3d)
               for pt in sky_mask.vertices)
    else:
        raise ValueError(
            'Projection type "{}" is not recognized.'.format(projection_))
    pts3d = tuple(Point3D(pt.x, pt.y, center_pt3d.z) for pt in pts)
    sky_mask = Mesh3D(pts3d, sky_mask.faces)
sky_pattern = [True] * len(view_vecs)  # pattern to be adjusted by the various masks


# account for the orientation and any of the projection strategies
orient_pattern, strategy_pattern = None, None
if direction is not None:
    orient_pattern, dir_angles = view_sphere.orientation_pattern(direction, view_vecs)
    apply_mask_to_sky(sky_pattern, orient_pattern)
    if overhang_proj_ or left_fin_proj_ or right_fin_proj_:
        strategy_pattern = [False] * len(view_vecs)
        if overhang_proj_:
            over_pattern = view_sphere.overhang_pattern(direction, overhang_proj_, view_vecs)
            apply_mask_to_base_mask(strategy_pattern, over_pattern, orient_pattern)
            apply_mask_to_sky(sky_pattern, over_pattern)
        if left_fin_proj_ or right_fin_proj_:
            f_pattern = view_sphere.fin_pattern(direction, left_fin_proj_, right_fin_proj_, view_vecs)
            apply_mask_to_base_mask(strategy_pattern, f_pattern, orient_pattern)
            apply_mask_to_sky(sky_pattern, f_pattern)


# account for any input context
context_pattern = None
if len(context_) != 0:
    shade_mesh = join_geometry_to_mesh(context_)  # mesh the context
    points = [from_point3d(center_pt3d)]
    view_vecs = [from_vector3d(pt) for pt in view_vecs]
    int_matrix, angles = intersect_mesh_rays(shade_mesh, points, view_vecs)
    context_pattern = [val == 0 for val in int_matrix[0]]
    apply_mask_to_sky(sky_pattern, context_pattern)


# get the weights for each patch to be used in view factor calculation
weights = view_sphere.dome_radial_patch_weights(az_count, alt_count)
if direction is not None:
    weights = [wgt * abs(math.cos(ang)) * 2 for wgt, ang in zip(weights, dir_angles)]


# create meshes for the masks and compute any necessary view factors
gray, black = Color(230, 230, 230), Color(0, 0, 0)
context_view, orient_view, strategy_view = 0, 0, 0
if context_pattern is not None:
    context_mask = mask_mesh_from_pattern(sky_mask, context_pattern, black)
    context_view = sum(wgt for wgt, is_viz in zip(weights, context_pattern) if is_viz)
if orient_pattern is not None:
    orient_mask = mask_mesh_from_pattern(sky_mask, orient_pattern, black)
    orient_view = sum(wgt for wgt, is_viz in zip(weights, orient_pattern) if is_viz)
if strategy_pattern is not None:
    strategy_mask = mask_mesh_from_pattern(sky_mask, strategy_pattern, black)
    strategy_view = sum(wgt for wgt, is_viz in zip(weights, strategy_pattern) if is_viz)
sky_mask = mask_mesh_from_pattern(sky_mask, sky_pattern, gray)
sky_view = sum(wgt for wgt, is_viz in zip(weights, sky_pattern) if is_viz)
