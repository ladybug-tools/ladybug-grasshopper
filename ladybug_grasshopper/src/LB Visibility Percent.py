# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Evaluate the percent visibility from geometry to a specific set of points.
_
Such visibility calculations can be used to understand the portions of a building
facade that can see a skyline or landmark when used on the outdoors. When used
on the indoors, they can evaluate the spectator view of a stage, screen, or other
point of interest.
-

    Args:
        _view_points: A list of points that characterize an area of interest to which
            visibility is being evaluated. If the area of interest is more like
            a surface than an individual point, the "LB Generate Point Grid"
            component can be used to obtain a list of points that are evenly
            distributed over the surface.
        pt_weights_: An optional list of numbers that align with the _view_points
            and represent weights of importance for each point.  Weighted
            values should be between 0 and 1 and should be closer to 1 if a
            certain point is more important. The default value for all points
            is 0, which means they all have an equal importance.
        _geometry: Rhino Breps and/or Rhino Meshes for which visibility analysis
            will be conducted. If Breps are input, they will be subdivided using
            the _grid_size to yeild individual points at which analysis will
            occur. If a Mesh is input, visibility analysis analysis will be
            performed for each face of this mesh instead of subdividing it.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry
            that can block visibility from the test _geometry.
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
        max_dist_: An optional number to set the maximum distance beyond which the
            end_points are no longer considered visible by the start_points.
            If None, points with an unobstructed view to one another will be
            considered visible no matter how far they are from one another.
        _geo_block_: Set to "True" to count the input _geometry as opaque and
            set to "False" to discount the _geometry from the calculation and
            only look at context_ that blocks the visibility. (Default: True)
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        parallel_: Set to "True" to run the study using multiple CPUs. This can
            dramatically decrease calculation time but can interfere with
            other computational processes that might be running on your
            machine. (Default: False).
        _run: Set to "True" to run the component and perform visibility analysis of
            the input _geometry.

    Returns:
        report: ...
        points: The grid of points on the test _geometry that are be used to perform
            the visibility analysis.
        results: A list of numbers that aligns with the points. Each number indicates
            the percentage of the _view_points that are not blocked by context geometry.
        mesh: A colored mesh of the test _geometry representing the percentage of
            the input _geometry's visibility that is not blocked by context.
        legend: A legend showing the number of hours that correspond to the colors
            of the mesh.
        title: A text object for the study title.
        int_mtx: A Matrix object that can be connected to the "LB Deconstruct Matrix"
            component to obtain detailed point-by-point results of the study.
            Each sub-list (aka. branch of the Data Tree) represents one of the
            geometry points used for analysis. The length of each sub-list matches
            the number of _view_points used for the analysis. Each value in the
            sub-list is either a "1", indicating that the vector is visible
            for that vector, or a "0", indicating that the vector is not visible
            for that vector.
"""

ghenv.Component.Name = "LB Visibility Percent"
ghenv.Component.NickName = 'VisibilityPercent'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
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
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_lines
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        show_output, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
        # set the default values
        _offset_dist_ = _offset_dist_ if _offset_dist_ is not None \
            else 0.1 / conversion_to_meters()
        if pt_weights_:
            assert len(pt_weights_) == len(_view_points), \
                'The number of pt_weights_({}) must match the number of _view_points ' \
                '({}).'.format(len(pt_weights_), len(_view_points))

        # create the gridded mesh from the geometry
        study_mesh = to_joined_gridded_mesh3d(_geometry, _grid_size)
        points = [from_point3d(pt.move(vec * _offset_dist_)) for pt, vec in
                  zip(study_mesh.face_centroids, study_mesh.face_normals)]
        hide_output(ghenv.Component, 1)

        # mesh the geometry and context
        shade_mesh = join_geometry_to_mesh(_geometry + context_) if _geo_block_ \
            or _geo_block_ is None else join_geometry_to_mesh(context_)

        # intersect the lines with the mesh
        int_matrix = intersect_mesh_lines(
            shade_mesh, points, _view_points, max_dist_, parallel=parallel_)

        # compute the results
        int_mtx = objectify_output('Visibility Intersection Matrix', int_matrix)
        vec_count = len(_view_points)
        if pt_weights_:  # weight intersections by the input point weights
            tot_wght = sum(pt_weights_) / vec_count
            adj_weights = [wght / tot_wght for wght in pt_weights_]
            results = []
            for int_vals in int_matrix:
                w_res = [ival * wght for ival, wght in zip(int_vals, adj_weights)]
                results.append(sum(w_res) * 100 / vec_count)
        else:  # no need to wieght results
            results = [sum(int_list) * 100 / vec_count for int_list in int_matrix]

        # create the mesh and legend outputs
        graphic = GraphicContainer(results, study_mesh.min, study_mesh.max, legend_par_)
        graphic.legend_parameters.title = '%'
        if legend_par_ is None or legend_par_.are_colors_default:
            graphic.legend_parameters.colors = Colorset.view_study()
        title = text_objects(
            'Visibility Percent', graphic.lower_title_location,
            graphic.legend_parameters.text_height * 1.5,
            graphic.legend_parameters.font)

        # create all of the visual outputs
        study_mesh.colors = graphic.value_colors
        mesh = from_mesh3d(study_mesh)
        legend = legend_objects(graphic.legend)
