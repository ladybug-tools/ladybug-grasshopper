# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Evaluate the percent view to the outdoors or sky from input geometry through context.
_
Such view calculations can be used to estimate the quality of a view to the
outdoors from a given location on the indoors. They can also be used on
the outdoors to evaluate the openness of street canyons to the sky, which has
implications for the pedestrian expereince as well as the rate of radiant heat
loss from urban surfaces and the sky at night.
_
Note that this component uses the CAD environment's ray intersection methods,
which can be fast for geometries with low complexity but does not scale well
for complex geometries or many test points. For such complex studies,
honeybee-radiance should be used.
-

    Args:
        _view_type: Text or an integer representing the type of view analysis
            to conduct.  Choose from the following options.
                _
                0 - HorizontalRadial - The percentage of the 360 horizontal view
                    plane that is not blocked by the context geometry.
                _
                1 - Horizonta30DegreeOffset - The percentage of the 360 horizontal
                    view band bounded on top and bottom by a 30 degree offset from
                    the horizontal plane. 30 degress corresponds roughly to the
                    vertical limit of human peripheral vision.
                _
                2 - Spherical - The percentage of the sphere surrounding each of
                    the test points that is not blocked by context geometry. This
                    is equivalent to a solid angle and gives equal weight to all
                    portions of the sphere.
                _
                3 - SkyExposure - The percentage of the sky that is visible from
                    each of the the test points. This is distinct from SkyView,
                    which is the amount of sky seen by a surface. SkyExposure is
                    equivalent to a solid angle and gives equal weight to all
                    portions of the sky.
                _
                4 - SkyView - The percentage of the sky that is visible from the
                    _geometry surfaces. This is distinct from SkyExposure, which
                    treats each part of the sky with equal weight. SkyView weights
                    the portions of the sky according to thier projection into
                    the plane of the surface being evaluated. So SkyView for a
                    horizontal surface would give more importance to the sky
                    patches that are overhead vs. those near the horizon.
        _resolution_: A positive integer for the number of times that the original
            view vectors are subdivided. 1 indicates that 145 evenly-spaced
            vectors are used to describe a hemisphere, 2 indicates that
            577 vectors describe a hemisphere, and each successive value will
            roughly quadruple the number of view vectors used. Setting this to
            a high value will result in a more accurate analysis but will take
            longer to run. (Default: 1).
        _geometry: Rhino Breps and/or Rhino Meshes for which view analysis
            will be conducted. If Breps are input, they will be subdivided using
            the _grid_size to yeild individual points at which analysis will
            occur. If a Mesh is input, view analysis analysis will be
            performed for each face of this mesh instead of subdividing it.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry
            that can block view from the test _geometry.
        _grid_size: A positive number in Rhino model units for the size of grid
            cells at which the input _geometry will be subdivided for direct sun
            analysis. The smaller the grid size, the higher the resolution of
            the analysis and the longer the calculation will take.  So it is
            recommended that one start with a large value here and decrease
            the value as needed. However, the grid size should usually be
            smaller than the dimensions of the smallest piece of the _geometry
            and context_ in order to yield meaningful results.
        _offset_dist_: A number for the distance to move points from the surfaces
            of the input _geometry.  Typically, this should be a small positive
            number to ensure points are not blocked by the mesh. (Default: 10 cm
            in the equivalent Rhino Model units).
        _geo_block_: Set to "True" to count the input _geometry as opaque and
            set to "False" to discount the _geometry from the calculation and
            only look at context_ that blocks the view.  The default depends on
            the _view_type used.
            _
            It is "True" for:
            * SkyExposure
            * SkyView
            _
            It is "False" for:
            * HorizontalRadial
            * Horizonta30DegreeOffset
            * Spherical
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and perform view analysis of
            the input _geometry.

    Returns:
        report: ...
        points: The grid of points on the test _geometry that are be used to perform
            the view analysis.
        view_vecs: A list of vectors which are projected from each of the points
            to evaluate view.
        results: A list of numbers that aligns with the points. Each number indicates
            the percentage of the view_vecs that are not blocked by context geometry.
        mesh: A colored mesh of the test _geometry representing the percentage of
            the input _geometry's view that is not blocked by context.
        legend: A legend showing the number of hours that correspond to the colors
            of the mesh.
        title: A text object for the study title.
        int_mtx: A Matrix object that can be connected to the "LB Deconstruct Matrix"
            component to obtain detailed vector-by-vector results of the study.
            Each sub-list (aka. branch of the Data Tree) represents one of the
            points used for analysis. The length of each sub-list matches the
            number of view_vecs used for the analysis. Each value in the sub-list
            is either a "1", indicating that the vector is visible for that
            vector, or a "0", indicating that the vector is not visible for
            that vector.
"""

ghenv.Component.Name = "LB View Percent"
ghenv.Component.NickName = 'ViewPercent'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import math
try:  # python 2
    from itertools import izip as zip
except ImportError:  # python 3
    pass

try:
    from ladybug.viewsphere import view_sphere
    from ladybug.color import Colorset
    from ladybug.graphic import GraphicContainer
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        show_output, objectify_output, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# dictionary to record all available view types
VIEW_TYPES = {
    'HorizontalRadial': 'Horizontal Radial',
    'Horizonta30DegreeOffset': 'Horizontal 30-Degree Offset',
    'Spherical': 'Spherical',
    'SkyExposure': 'Sky Exposure',
    'SkyView': 'Sky View',
    '0': 'Horizontal Radial',
    '1': 'Horizontal 30-Degree Offset',
    '2': 'Spherical',
    '3': 'Sky Exposure',
    '4': 'Sky View'
}


if all_required_inputs(ghenv.Component) and _run:
    # process the view_type_ and set the default values
    vt_str = VIEW_TYPES[_view_type]
    _resolution_ = _resolution_ if _resolution_ is not None else 1
    _offset_dist_ = _offset_dist_ if _offset_dist_ is not None \
        else 0.1 / conversion_to_meters()
    if _geo_block_ is None:
        _geo_block_ = True if vt_str in ('Sky Exposure', 'Sky View') else False
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()

    # create the gridded mesh from the geometry
    study_mesh = to_joined_gridded_mesh3d(_geometry, _grid_size)
    points = [from_point3d(pt.move(vec * _offset_dist_)) for pt, vec in
              zip(study_mesh.face_centroids, study_mesh.face_normals)]
    hide_output(ghenv.Component, 1)

    # get the view vectors based on the view type
    patch_wghts = None
    if vt_str == 'Horizontal Radial':
        lb_vecs = view_sphere.horizontal_radial_vectors(30 * _resolution_)
    elif vt_str == 'Horizontal 30-Degree Offset':
        patch_mesh, lb_vecs = view_sphere.horizontal_radial_patches(30, _resolution_)
        patch_wghts = view_sphere.horizontal_radial_patch_weights(30, _resolution_)
    elif vt_str == 'Spherical':
        patch_mesh, lb_vecs = view_sphere.sphere_patches(_resolution_)
        patch_wghts = view_sphere.sphere_patch_weights(_resolution_)
    else:
        patch_mesh, lb_vecs = view_sphere.dome_patches(_resolution_)
        patch_wghts = view_sphere.dome_patch_weights(_resolution_)
    view_vecs = [from_vector3d(pt) for pt in lb_vecs]

    # mesh the geometry and context
    shade_mesh = join_geometry_to_mesh(_geometry + context_) if _geo_block_ \
        else join_geometry_to_mesh(context_)

    # intersect the rays with the mesh
    if vt_str == 'Sky View':  # account for the normals of the surface
        normals = [from_vector3d(vec) for vec in study_mesh.face_normals]
        int_matrix, angles = intersect_mesh_rays(
            shade_mesh, points, view_vecs, normals, cpu_count=workers)
    else:
        int_matrix, angles = intersect_mesh_rays(
            shade_mesh, points, view_vecs, cpu_count=workers)

    # compute the results
    int_mtx = objectify_output('View Intersection Matrix', int_matrix)
    vec_count = len(view_vecs)
    results = []
    if vt_str == 'Sky View':  # weight intersections by angle before output
        for int_vals, angles in zip(int_matrix, angles):
            w_res = (ival * 2 * math.cos(ang) for ival, ang in zip(int_vals, angles))
            weight_result = sum(r * w for r, w in zip(w_res, patch_wghts))
            results.append(weight_result * 100 / vec_count)
    else:
        if patch_wghts:
            for int_list in int_matrix:
                weight_result = sum(r * w for r, w in zip(int_list, patch_wghts))
                results.append(weight_result * 100 / vec_count)
        else:
            results = [sum(int_list) * 100 / vec_count for int_list in int_matrix]

    # create the mesh and legend outputs
    graphic = GraphicContainer(results, study_mesh.min, study_mesh.max, legend_par_)
    graphic.legend_parameters.title = '%'
    if legend_par_ is None or legend_par_.are_colors_default:
        graphic.legend_parameters.colors = Colorset.view_study()
    title_txt = vt_str if vt_str in ('Sky Exposure', 'Sky View') else \
        '{} View'.format(vt_str)
    title = text_objects(
        title_txt, graphic.lower_title_location,
        graphic.legend_parameters.text_height * 1.5,
        graphic.legend_parameters.font)

    # create all of the visual outputs
    study_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(study_mesh)
    legend = legend_objects(graphic.legend)
