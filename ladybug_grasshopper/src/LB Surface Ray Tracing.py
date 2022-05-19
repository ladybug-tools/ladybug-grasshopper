# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get a ray tracing visualization of direct sunlight rays reflected off of _source_geo
and subsequently bouncing through a set of context_ geometries.
_
Examples where this visualization could be useful include understading the
reflection of light by a light shelf or testing to see whether a parabolic
glass or metal building geometry might focus sunlight to dangerous levels at
certain times of the year.
_
Note that this component assumes that all sun light is reflected specularly
(like a mirror) and, for more detailed raytracing analysis with diffuse
scattering, the Honeybee Radiance components should be used.
-

    Args:
        _vector: A sun vector (typically from the "LB SunPath" component), which will
            be used to evaluate the light boucing off of the _source_geo and
            through the context_.
        _source_geo: A brep or mesh representing a surface off of which sun rays first
            bounce. Lists of breps or meshes are also acceptable. These surfaces
            will be used to generate the initial sun rays in a grid-like pattern.
        context_: Breps or meshes for conext geometry, which will reflect the sun rays
            after they bounce off of the _source_geo.
        _grid_size: A positive number in Rhino model units for the average distance between
            sun ray points to generate along the _source_geo.
        _bounce_count_: An positive integer for the number of ray bounces to trace
            the sun rays forward. (Default: 1).
        _first_length_: A positive number in Rhino model units for the length of the
            sun ray before the first bounce. If unspecified, this will be
            the diagonal of the bounding box surrounding all input geometries.
        _last_length_: A positive number in Rhino model units representing the length
            of the sun ray after the last bounce. If unspecified, this will be
            the diagonal of the bounding box surrounding all input geometries.

    Returns:
        rays: A list of polylines representing the sun rays traced forward onto
            the _source_geo and then through the context_.
        int_pts: A data tree of intersection points one one branch for each of the
            rays above.
"""

ghenv.Component.Name = 'LB Surface Ray Tracing'
ghenv.Component.NickName = 'SrfRayTrace'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug_geometry.geometry3d.ray import Ray3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_point3d, \
        to_vector3d
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d, from_ray3d, \
        from_polyline3d
    from ladybug_rhino.intersect import join_geometry_to_brep, bounding_box_extents, \
        trace_ray, normal_at_point
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        hide_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the _bounce_count_
    _bounce_count_ = 0 if _bounce_count_ is None else _bounce_count_ - 1
    assert _bounce_count_ >= 0, 'The input _bounce_count_ must be greater '  \
        'than zero. Got {}.'.format(_bounce_count_ + 1)
    # process the input sun vector
    lb_vec = to_vector3d(_vector).normalize()
    neg_lb_vec = -lb_vec
    vec = from_vector3d(lb_vec)

    # convert all of the _source_geo and contex into a single Brep for ray tracing
    rtrace_brep = join_geometry_to_brep(_source_geo + context_)

    # autocompute the first and last bounce length if it's unspecified
    if _first_length_ is None or _last_length_ is None:
        max_pt, min_pt = (to_point3d(p) for p in bounding_box_extents(rtrace_brep))
        diag_dist = max_pt.distance_to_point(min_pt)
        _first_length_ = diag_dist if _first_length_ is None else _first_length_
        _last_length_ = diag_dist if _last_length_ is None else _last_length_

    # create the gridded mesh from the _source_geo and set up the starting rays
    study_mesh = to_joined_gridded_mesh3d(_source_geo, _grid_size)
    move_vec = neg_lb_vec * _first_length_
    source_points = [pt + move_vec for pt in study_mesh.face_centroids]
    lb_rays = [Ray3D(pt, lb_vec) for pt in source_points]
    start_rays = [from_ray3d(ray) for ray in lb_rays]

    # trace each ray through the geometry
    cutoff_ang = math.pi / 2
    rtrace_geo = [rtrace_brep]
    rays, int_pts = [], []
    for ray, pt, norm in zip(start_rays, source_points, study_mesh.face_normals):
        if norm.angle(neg_lb_vec) < cutoff_ang:
            pl_pts = trace_ray(ray, rtrace_geo, _bounce_count_ + 1)
            # if the intersection was successful, create a polyline represeting the ray
            if pl_pts:
                # gather all of the intersection points
                all_pts = [pt]
                for i_pt in pl_pts:
                    all_pts.append(to_point3d(i_pt))
                # compute the last point
                if len(pl_pts) < _bounce_count_ + 2:
                    int_norm = normal_at_point(rtrace_brep, pl_pts[-1])
                    int_norm = to_vector3d(int_norm)
                    last_vec = all_pts[-2] - all_pts[-1]
                    last_vec = last_vec.normalize()
                    final_vec = last_vec.reflect(int_norm).reverse()
                    final_pt = all_pts[-1] + (final_vec * _last_length_)
                    all_pts.append(final_pt)
                # create a Polyline3D from the points
                lb_ray_line = Polyline3D(all_pts)
                rays.append(from_polyline3d(lb_ray_line))
                int_pts.append([from_point3d(p) for p in all_pts])

    # convert the intersection points to a data tree
    int_pts = list_to_data_tree(int_pts)
    hide_output(ghenv.Component, 1)
