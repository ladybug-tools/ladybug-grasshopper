# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate view factors from a point or plane to a set of geometries.
_
View factors are used in many thermal comfort calculations such as mean radiant
temperture (MRT) or discomfort from radiant assymetry. 
-

    Args:
        _study_point: A point or plane from which view vectors will be projected.
            Note that, if a point is connected, all view vectors will be
            weighted evenly (assuming no directional bias). However, if
            a plane is connected, vectors will be weighted based on their
            angle to the plane normal, producing view factors for a surface
            in the connected plane. The first is useful for MRT calculations
            while the latter is needed for radiant assymetry calculations.
            This input can also be a list of several points or planes.
        _view_geo: A list of breps, surfaces, or meshes to which you want to compute
            view factors. Note that by meshing and joining several goemtries
            together, the combined view factor to these geometries can
            be computed.
        context_: Optional context geometry as breps, surfaces, or meshes that can
            block the view to the _view_geo.
        _resolution_: A positive integer for the number of times that the original
            view vectors are subdivided. 1 indicates that 145 evenly-spaced
            vectors are used to describe a hemisphere, 2 indicates that
            577 vectors describe a hemisphere, and each successive value will
            roughly quadruple the number of view vectors used. Setting this to
            a high value will result in a more accurate analysis but will take
            longer to run. (Default: 1).
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to True to run the component and claculate view factors.

    Returns:
        report: ...
        view_vecs: A list of vectors which are projected from each of the points to evaluate view.
        patch_mesh: A mesh that represents the sphere of view patches around the _study_point
            at the input _resolution_. There is one face per patch and this can be
            used along with the int_mtx to create a colored visualization of patches
            corresponding to different geometries around the point. Specifically,
            the "LB Spaital Heatmap" component is recommended for such visualizations.
            Note that only one sphere is ever output from here and, in the event
            that several _study_points are connected, this sphere will be located
            at the first point. Therefore, to create visualizations for the other
            points, this mesh should be moved using the difference between the
            first study point and following study points.
        view_factors: A list of view factors that describe the fraction of sperical
            view taken up by the input surfaces.  These values range from 0 (no view)
            to 1 (full view).  If multiple _study_points have been connected,
            this output will be a data tree with one list for each point.
        int_mtx: A Matrix object that can be connected to the "LB Deconstruct Matrix"
            component to obtain detailed vector-by-vector results of the study.
            Each sub-list (aka. branch of the Data Tree) represents one of the
            points used for analysis. Each value in this sub-list corresponds
            to a vector used in the study and the value denotes the index of the
            geometry that each view vector hit. This can be used to identify
            which view pathces are intersected by each geometry. If no geometry
            is intersected by a given vector, the value will be -1.
"""

ghenv.Component.Name = 'LB View Factors'
ghenv.Component.NickName = 'ViewFactors'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.viewsphere import view_sphere
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_plane, to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_view_factor
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        show_output, objectify_output, list_to_data_tree, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set up the defaults
    _resolution_ = _resolution_ if _resolution_ is not None else 1
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()

    # process the input points and determine whether they are points or planes
    points, normals = [], []
    for geo in _study_point:
        try:
            test_plane = to_plane(geo)
            points.append(from_point3d(test_plane.o))
            normals.append(from_vector3d(test_plane.n))
        except AttributeError:  # it is a point
            points.append(geo)
            normals.append(None)
    if all(n is None for n in normals):
        normals = None  # none of the inputs were planes

    # generate the view vectors based on the resolution
    patch_mesh, lb_vecs = view_sphere.sphere_patches(_resolution_)
    patch_wghts = view_sphere.sphere_patch_weights(_resolution_)
    # correct for the fact that the last patch has several mesh faces
    patch_count = 144 * (_resolution_ ** 2) + 1
    extend_count = ((6 * _resolution_) - 1)
    up_dome, down_dome = list(lb_vecs[:patch_count]), list(lb_vecs[patch_count:])
    up_dome.extend([up_dome[-1]] * extend_count)
    down_dome.extend([down_dome[-1]] * extend_count)
    lb_vecs = up_dome + down_dome
    up_weights, down_weights = list(patch_wghts[:patch_count]), list(patch_wghts[patch_count:])
    up_weights.extend([up_weights[-1] / extend_count] * extend_count)
    down_weights.extend([down_weights[-1] / extend_count] * extend_count)
    patch_wghts = up_weights + down_weights

    # process the context if it is input
    context_mesh = join_geometry_to_mesh(context_) if len(context_) != 0 else None

    # perform the intersection to compute view factors
    view_vecs = [from_vector3d(pt) for pt in lb_vecs]
    view_factors, mesh_indices = intersect_view_factor(
        _view_geo, points, view_vecs, patch_wghts,
        context_mesh, normals, cpu_count=workers)

    # convert the outputs into the correct Grasshopper format
    view_factors = list_to_data_tree(view_factors)
    int_mtx = objectify_output('View Factor Intersection Matrix', mesh_indices)
    patch_mesh = from_mesh3d(patch_mesh.move(to_vector3d(points[0])))
    hide_output(ghenv.Component, 2)
