# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate the incident radiation on geometry using a sky matrix from the "Cumulative
Sky Matrix" component.
_
Such studies of incident radiation can be used to apprxomiate the energy that can
be collected from photovoltaic or solar thermal systems. They are also useful
for evaluating the impact of a building's orientation on both energy use and the
size/cost of cooling systems. For studies of photovoltaic potential or building
energy use impact, a sky matrix from EPW radiation should be used. For studies
of cooling system size/cost, a sky matrix derived from the STAT file's clear sky
radiation should be used.
_
NOTE THAT NO REFLECTIONS OF SOLAR ENERGY ARE INCLUDED
IN THE ANALYSIS PERFORMED BY THIS COMPONENT.
_
Ground reflected irradiance is crudely acounted for by means of an emissive
"ground hemisphere," which is like the sky dome hemisphere and is derived from
the ground reflectance that is associated with the connected _sky_mtx. This
means that including geometry that represents the ground surface will effectively
block such crude ground reflection.
_
Also note that this component uses the CAD environment's ray intersection methods,
which can be fast for geometries with low complexity but does not scale well for
complex geometries or many test points. For such complex cases and situations
where relfection of solar energy are important, honeybee-radiance should be used.
-

    Args:
        _sky_mtx: A Sky Matrix from the "LB Cumulative Sky Matrix" component or the
            "LB Benefit Sky Matrix" component, which describes the radiation
            coming from the various patches of the sky. The "LB Sky Dome"
            component can be used to visualize any sky matrix to understand
            its relationship to the test geometry.
        _geometry: Rhino Breps and/or Rhino Meshes for which incident radiation analysis
            will be conducted. If Breps are input, they will be subdivided using
            the _grid_size to yeild individual points at which analysis will
            occur. If a Mesh is input, radiation analysis analysis will be
            performed for each face of this mesh instead of subdividing it.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry
            that can block solar radiation to the test _geometry.
        _grid_size: A positive number in Rhino model units for the size of grid
            cells at which the input _geometry will be subdivided for incident
            radiation analysis. The smaller the grid size, the higher the
            resolution of the analysis and the longer the calculation will take.
            So it is recommended that one start with a large value here and
            decrease the value as needed. However, the grid size should usually
            be smaller than the dimensions of the smallest piece of the _geometry
            and context_ in order to yield meaningful results.
        _offset_dist_: A number for the distance to move points from the surfaces
            of the input _geometry.  Typically, this should be a small positive
            number to ensure points are not blocked by the mesh. (Default: 10 cm
            in the equivalent Rhino Model units).
        irradiance_: Boolean to note whether the study should output units of cumulative
            Radiation (kWh/m2) [False] or units of average Irradiance (W/m2)
            [True].  (Default: False).
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and perform incident radiation
            analysis.

    Returns:
        report: ...
        points: The grid of points on the test _geometry that are be used to perform
            the incident radiation analysis.
        results: A list of numbers that aligns with the points. Each number indicates
            the cumulative incident radiation received by each of the points
            from the sky matrix in kWh/m2.
        total: A number for the total incident solar energy falling on all input geometry
            in kWh. Note that, unlike the radiation results above, which are
            normlaized by area, these values are not area-normalized and so
            the input geometry must be represented correctly in the Rhino
            model's unit system in order for this output to be meaningful.
        mesh: A colored mesh of the test _geometry representing the cumulative
            incident radiation received by the input _geometry.
        legend: A legend showing the kWh/m2 that correspond to the colors of the mesh.
        title: A text object for the study title.
        int_mtx: A Matrix object that can be connected to the "LB Deconstruct Matrix"
            component to obtain detailed patch-by-patch results of the study.
            Each sub-list of the matrix (aka. branch of the Data Tree) represents
            one of the points used for analysis. The length of each sub-list
            matches the number of sky patches in the input sky matrix (145 for
            the default Tregenza sky and 577 for the high_density Reinhart sky).
            Each value in the sub-list is a value between 0 and 1 indicating the
            relationship between the point and the patch of the sky. A value of
            "0", indicates that the patch is not visible for that point at all
            while a value of "1" indicates that the patch hits the surface that
            the point represents head on.
"""

ghenv.Component.Name = "LB Incident Radiation"
ghenv.Component.NickName = 'IncidentRadiation'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import math
try:  # python 2
    from itertools import izip as zip
except ImportError:  # python 3
    pass

try:
    from ladybug.viewsphere import view_sphere
    from ladybug.graphic import GraphicContainer
    from ladybug.legend import LegendParameters
    from ladybug.color import Colorset
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        show_output, objectify_output, de_objectify_output, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set the default offset distance and _cpu_count
    _offset_dist_ = _offset_dist_ if _offset_dist_ is not None \
        else 0.1 / conversion_to_meters()
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()

    # create the gridded mesh from the geometry
    study_mesh = to_joined_gridded_mesh3d(_geometry, _grid_size)
    points = [from_point3d(pt.move(vec * _offset_dist_)) for pt, vec in
              zip(study_mesh.face_centroids, study_mesh.face_normals)]
    hide_output(ghenv.Component, 1)

    # mesh the geometry and context
    shade_mesh = join_geometry_to_mesh(_geometry + context_)

    # deconstruct the matrix and get the sky dome vectors
    mtx = de_objectify_output(_sky_mtx)
    total_sky_rad = [dir_rad + dif_rad for dir_rad, dif_rad in zip(mtx[1], mtx[2])]
    ground_rad = [(sum(total_sky_rad) / len(total_sky_rad)) * mtx[0][1]] * len(total_sky_rad)
    all_rad = total_sky_rad + ground_rad 
    lb_vecs = view_sphere.tregenza_dome_vectors if len(total_sky_rad) == 145 \
        else view_sphere.reinhart_dome_vectors
    if mtx[0][0] != 0:  # there is a north input for sky; rotate vectors
        north_angle = math.radians(mtx[0][0])
        lb_vecs = tuple(vec.rotate_xy(north_angle) for vec in lb_vecs)
    lb_grnd_vecs = tuple(vec.reverse() for vec in lb_vecs)
    all_vecs = [from_vector3d(vec) for vec in lb_vecs + lb_grnd_vecs]

    # intersect the rays with the mesh
    normals = [from_vector3d(vec) for vec in study_mesh.face_normals]
    int_matrix_init, angles = intersect_mesh_rays(
        shade_mesh, points, all_vecs, normals, cpu_count=workers)

    # compute the results
    results = []
    int_matrix = []
    for int_vals, angs in zip(int_matrix_init, angles):
        pt_rel = [ival * math.cos(ang) for ival, ang in zip(int_vals, angs)]
        int_matrix.append(pt_rel)
        rad_result = sum(r * w for r, w in zip(pt_rel, all_rad))
        results.append(rad_result)

    # convert to irradiance if requested
    study_name = 'Incident Radiation'
    if irradiance_:
        study_name = 'Incident Irradiance'
        factor = 1000 / _sky_mtx.wea_duration if hasattr(_sky_mtx, 'wea_duration') \
            else 1000 / (((mtx[0][3] - mtx[0][2]).total_seconds() / 3600) + 1)
        results = [r * factor for r in results]

    # output the intersection matrix and compute total radiation
    int_mtx = objectify_output('Geometry/Sky Intersection Matrix', int_matrix)
    unit_conv = conversion_to_meters() ** 2
    total = 0
    for rad, area in zip(results, study_mesh.face_areas):
        total += rad * area * unit_conv

    # create the mesh and legend outputs
    l_par = legend_par_ if legend_par_ is not None else LegendParameters()
    if hasattr(_sky_mtx, 'benefit_matrix') and _sky_mtx.benefit_matrix is not None:
        study_name = '{} Benefit/Harm'.format(study_name)
        if l_par.are_colors_default:
            l_par.colors = reversed(Colorset.benefit_harm())
        if l_par.min is None:
            l_par.min = min((min(results), -max(results)))
        if l_par.max is None:
            l_par.max = max((-min(results), max(results)))
    graphic = GraphicContainer(results, study_mesh.min, study_mesh.max, l_par)
    graphic.legend_parameters.title = 'kWh/m2' if not irradiance_ else 'W/m2'
    title = text_objects(
        study_name, graphic.lower_title_location,
        graphic.legend_parameters.text_height * 1.5,
        graphic.legend_parameters.font)

    # create all of the visual outputs
    study_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(study_mesh)
    legend = legend_objects(graphic.legend)
