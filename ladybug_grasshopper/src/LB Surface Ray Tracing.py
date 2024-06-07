# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
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
            after they bounce off of the _source_geo. They can also block the
            sun rays to the _source_geo if context_block_ is set to True.
        receiver_: Optional breps or meshes for receiver geometry for which sun ray
            intersection is being studied. If specified, only sun rays that
            reflect off of the _source_geo and have their last bounce intersect
            this receiver within the _last_length_ distance will appear in
            the result. This can help filter results to only an area of
            intersect where the impact of reflected sun rays is a concern.
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
        context_block_: Set to "True" to count the input _context as something that fully
            blocks rays as opposed to having the rays simply bounce off of it.
            This can be particularly useful in cases with lots of rays where
            you are only concered about the rays that can actually hit the
            _source_geo. (Default: False).
        _run: Set to "True" to run the component and perform the ray tracing study.

    Returns:
        report: Reports, errors, warnings, etc.
        rays: A list of polylines representing the sun rays traced forward onto
            the _source_geo and then through the context_.
        int_pts: A data tree of intersection points one one branch for each of the
            rays above.
"""

ghenv.Component.Name = 'LB Surface Ray Tracing'
ghenv.Component.NickName = 'SrfRayTrace'
ghenv.Component.Message = '1.8.1'
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
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_point3d, \
        to_vector3d
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d, from_ray3d, \
        from_polyline3d
    from ladybug_rhino.intersect import join_geometry_to_brep, join_geometry_to_mesh, \
        intersect_mesh_rays, bounding_box_extents, trace_ray, normal_at_point, \
        intersect_mesh_rays_distance
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        hide_output, show_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
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
    source_normals = study_mesh.face_normals
    lb_rays = [Ray3D(pt, lb_vec) for pt in source_points]
    start_rays = [from_ray3d(ray) for ray in lb_rays]

    # if context_block_ is set to True, filter the source_points
    if context_block_:
        shade_mesh = join_geometry_to_mesh(context_)
        rev_vec = [from_vector3d(to_vector3d(_vector).reverse())]
        normals = [from_vector3d(vec) for vec in study_mesh.face_normals]
        points = [from_point3d(pt) for pt in study_mesh.face_centroids]
        int_matrix, angles = intersect_mesh_rays(
            shade_mesh, points, rev_vec, normals, cpu_count=1)
        new_start_rays, new_source_points, new_source_normals = [], [], []
        for ray, pt, norm, inter in zip(start_rays, source_points, source_normals, int_matrix):
            if inter[0] == 1:
                new_start_rays.append(ray)
                new_source_points.append(pt)
                new_source_normals.append(norm)
        start_rays, source_points, source_normals = \
            new_start_rays, new_source_points, new_source_normals

    # trace each ray through the geometry
    cutoff_ang = math.pi / 2
    rtrace_geo = [rtrace_brep]
    rays, int_pts = [], []
    for ray, pt, norm in zip(start_rays, source_points, source_normals):
        if norm.angle(neg_lb_vec) < cutoff_ang:
            pl_pts = trace_ray(ray, rtrace_geo, _bounce_count_ + 2)
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

    # if a receiver is specified, filter the output rays for intersection
    if len(receiver_) != 0:
        rec_mesh = join_geometry_to_mesh(receiver_)
        new_rays, new_int_pts = [], []
        for pl_pts, sun_ray in zip(int_pts, rays):
            start_point = pl_pts[-2]
            end_vec3d = to_point3d(pl_pts[-1]) - to_point3d(pl_pts[-2])
            end_vec = from_vector3d(end_vec3d.normalize())
            dist_list = intersect_mesh_rays_distance(rec_mesh, start_point, [end_vec])
            if 0 < dist_list[0] <= end_vec3d.magnitude + tolerance:
                new_rays.append(sun_ray)
                new_int_pts.append(pl_pts)
        rays, int_pts = new_rays, new_int_pts

    # convert the intersection points to a data tree
    int_pts = list_to_data_tree(int_pts)
    hide_output(ghenv.Component, 2)
