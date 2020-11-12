# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate the number of hours of direct sunlight received by geometry using sun
vectors obtained from the "LB SunPath" component.
_
Such direct sun calculations can be used for shadow studies of outdoor enviroments
or can be used to estimate glare potential from direct sun on the indoors.
_
Note that this component uses the CAD environment's ray intersection methods,
which can be fast for geometries with low complexity but does not scale well
for complex geometries or many test points. For such complex studies,
honeybee-radiance should be used.
-

    Args:
        _vectors: Sun vectors from the "LB SunPath" component, which will be used
            to determine the number of hours of direct sunlight received by the
            test _geometry.
        _timestep_: A positive integer for the number of timesteps per hour at
            which the "LB SunPath" component generated sun vectors. This is used
            to correctly interpret the time duration represented by each of
            the input sun vectors. (Default: 1 for 1 vector per hour).
        _geometry: Rhino Breps and/or Rhino Meshes for which direct sun analysis
            will be conducted. If Breps are input, they will be subdivided using
            the _grid_size to yeild individual points at which analysis will
            occur. If a Mesh is input, direct sun analysis analysis will be
            performed for each face of this mesh instead of subdividing it.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry
            that can block sunlight to the test _geometry.
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
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        parallel_: Set to "True" to run the study using multiple CPUs. This can
            dramatically decrease calculation time but can interfere with
            other computational processes that might be running on your
            machine. (Default: False).
        _run: Set to "True" to run the component and perform direct sun analysis.

    Returns:
        report: ...
        points: The grid of points on the test _geometry that are be used to perform
            the direct sun analysis.
        results: A list of numbers that aligns with the points. Each number indicates
            the number of hours of direct sunlight received by each of the
            points.  Note that is is the number of hours out of the total
            number of connected _vectors.
        mesh: A colored mesh of the test _geometry representing the hours of direct
            sunlight received by this input _geometry
        legend: A legend showing the number of hours that correspond to the colors
            of the mesh.
        title: A text object for the study title.
        int_mtx: A Matrix object that can be connected to the "LB Deconstruct Matrix"
            component to obtain detailed vector-by-vector results of the study.
            Each sub-list of the matrix (aka. branch of the Data Tree) represents
            one of the points used for analysis. The length of each sub-list
            matches the number of _vectors used for the analysis. Each value
            in the sub-list is either a "1", indicating that the sun is visible
            for that vector, or a "0", indicating that the sun is not visible
            for that vector.
"""

ghenv.Component.Name = "LB Direct Sun Hours"
ghenv.Component.NickName = 'DirectSunHours'
ghenv.Component.Message = '1.1.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        show_output, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
        # set the default offset distance
        _offset_dist_ = _offset_dist_ if _offset_dist_ is not None \
            else 0.1 / conversion_to_meters()

        # create the gridded mesh from the geometry
        study_mesh = to_joined_gridded_mesh3d(_geometry, _grid_size)
        points = [from_point3d(pt.move(vec * _offset_dist_)) for pt, vec in
                  zip(study_mesh.face_centroids, study_mesh.face_normals)]
        hide_output(ghenv.Component, 1)

        # mesh the geometry and context
        shade_mesh = join_geometry_to_mesh(_geometry + context_)

        # get the study points and reverse the sun vectors (for backward ray-tracting)
        rev_vec = [from_vector3d(to_vector3d(vec).reverse()) for vec in _vectors]
        normals = [from_vector3d(vec) for vec in study_mesh.face_normals]

        # intersect the rays with the mesh
        int_matrix, angles = intersect_mesh_rays(
            shade_mesh, points, rev_vec, normals, parallel=parallel_)

        # compute the results
        int_mtx = objectify_output('Sun Intersection Matrix', int_matrix)
        if _timestep_ and _timestep_ != 1:  # divide by the timestep before output
            results = [sum(int_list) / _timestep_ for int_list in int_matrix]
        else:  # no division required
            results = [sum(int_list) for int_list in int_matrix]

        # create the mesh and legend outputs
        graphic = GraphicContainer(results, study_mesh.min, study_mesh.max, legend_par_)
        graphic.legend_parameters.title = 'hours'
        if legend_par_ is None or legend_par_.are_colors_default:
            graphic.legend_parameters.colors = Colorset.ecotect()
        title = text_objects('Direct Sun Hours', graphic.lower_title_location,
                             graphic.legend_parameters.text_height * 1.5,
                             graphic.legend_parameters.font)

        # create all of the visual outputs
        study_mesh.colors = graphic.value_colors
        mesh = from_mesh3d(study_mesh)
        legend = legend_objects(graphic.legend)
