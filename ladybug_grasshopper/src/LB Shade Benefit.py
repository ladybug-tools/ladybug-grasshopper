# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize the desirability of shade in terms of the time period of blocked
sun vectors for each part of a shade geometry.
_
The calculation assumes that all input _vectors represent sun to be blocked, which
is often the case when evaluating shade in terms of its benefit for glare reduction
and occupant visual comfort. It can also be the case when sun vectors have been
filtered to account for times of peak cooling demand or for the heat stress of
human subjects.
_
The component outputs a colored mesh of the shade illustrating the helpfulness of
shading each part of the _shade_geo. A higher saturation of blue indicates that
shading the cell blocks more hours of sun and is therefore more desirable.
_
The units for shade desirability are hrs/square Rhino unit, which note the amount
of time that sun is blocked by a given cell. So, if a given square meter of input
_shade_geo has a shade desirability of 10 hrs/m2, this means that a shade in
this location blocks an average of 10 hours to each of the _study_points.
-

    Args:
        _vectors: Sun vectors from the "LB SunPath" component, which will be used
            to determine the number of hours of sun blocked by the _shade_geo.
            When evaluating shade benefit in terms of glare reduction, these
            vectors are typically for any sun-up hour of the year since looking
            into the sun at practically any hour is likely to induce glare.
            When using this component to approximate reductions to cooling
            demand or human heat stress, it's more appropriate to filter
            sun vectors using a conditional statement or use other types of
            shade benefit analysis like the "LB Thermal Shade Benefit"
            component or the "HB Energy Shade Benefit" component.
        _study_points: Points representing an location in space for which shading
            desirability is being evaluated. For a study of shade desirability for
            reducing glare, this is often the location of the human subject's
            view. For a study of shade desirability over a surface like a desk
            or a window, the "LB Generate Point Grid" component can be used to
            create a set of points over the surface to input here.
        study_directs_: Optional Vectors that align with the _study_points and represent
            the direction in which shade desirability is being evaluated. For a
            study of shade desirability for reducing glare, this is the direction
            in which human subject is looking. For a study of shade desirability
            over a surface like a desk or a window, the vectors output of the
            "LB Generate Point Grid" component should be input here. If not
            supplied, sun vectors coming from any direction will be used to
            evualuate shade desirability.
        _shade_geo: Rhino Breps and/or Rhino Meshes representing shading to be evaluated
            in terms of its benefit. Note that, in the case that multiple
            shading geometries are connected, this component does not account
            for the interaction between the different shading surfaces and will
            just evaluate each part of the shade independently.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry that can
            block sunlight to the _study_points, therefore discounting any benefit
            or harm that could come to the region.
        _grid_size: A positive number in Rhino model units for the size of grid cells at
            which the input _shade_geo will be subdivided for shade benefit
            analysis. The smaller the grid size, the higher the resolution of
            the analysis and the longer the calculation will take.  So it is
            recommended that one start with a large value here and decrease
            the value as needed. However, the grid size should usually be
            smaller than the dimensions of the smallest piece of the _shade_geo
            and context_ in order to yield meaningful results.
        _timestep_: A positive integer for the number of timesteps per hour at which
            the "LB SunPath" component generated sun vectors. This is used
            to correctly interpret the time duration represented by each of
            the input sun vectors. (Default: 1 for 1 vector per hour).
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and perform shade benefit analysis.

    Returns:
        report: ...
        mesh: A colored mesh of the _shade_geo showing where shading is helpful (in blue),
            and where it does not make much of a difference (white or desaturated
            colors). Note that the colors can change depending upon the input legend_par_.
        legend: Legend showing the numeric values of hrs / square unit that correspond to
            the colors in the shade mesh.
        title: A text object for the study title.
        shade_help: The cumulative hrs / square unit helped by shading the given cell. If a given
            square meter of _shade_geo has a shade helpfulness of 10 hrs/m2,
            this means that a shade in this location blocks an average of 10 hours
            to each of the _study_points.
"""

ghenv.Component.Name = 'LB Shade Benefit'
ghenv.Component.NickName = 'ShadeBenefit'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '4'


try:
    from ladybug.color import Colorset
    from ladybug.graphic import GraphicContainer
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import units_abbreviation
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.intersect import join_geometry_to_mesh, generate_intersection_rays, \
        intersect_rays_with_mesh_faces
    from ladybug_rhino.grasshopper import all_required_inputs, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set the defaults and process all of the inputs
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()
    _timestep_ = 1 if _timestep_ is None else _timestep_
    study_directs_ = None if len(study_directs_) == 0 else study_directs_

    # create the gridded mesh from the geometry
    analysis_mesh = to_joined_gridded_mesh3d(_shade_geo, _grid_size)
    mesh = from_mesh3d(analysis_mesh)

    # create a series of rays that represent the sun projected through the shade
    rev_vec = [from_vector3d(to_vector3d(vec).reverse()) for vec in _vectors]
    int_rays = generate_intersection_rays(_study_points, rev_vec)

    # if there is context, remove any rays that are blocked by the context
    shade_mesh = join_geometry_to_mesh(context_) \
        if len(context_) != 0 and context_[0] is not None else None

    # intersect the sun rays with the shade mesh
    face_int = intersect_rays_with_mesh_faces(
        mesh, int_rays, shade_mesh, study_directs_, cpu_count=workers)

    # loop through the face intersection result and evaluate the benefit
    pt_count = len(_study_points)
    shade_help = []
    for face_res, face_area in zip(face_int, analysis_mesh.face_areas):
        # Normalize by the area of the cell so there's is a consistent metric
        # between cells of different areas.
        # Also, divide the number of study points so people get a sense of
        # the average hours of blocked sun.
        shd_help = ((len(face_res) / face_area) / _timestep_) / pt_count
        shade_help.append(shd_help)

    # create the mesh and legend outputs
    graphic = GraphicContainer(shade_help, analysis_mesh.min, analysis_mesh.max, legend_par_)
    graphic.legend_parameters.title = 'hrs/{}2'.format(units_abbreviation())
    if legend_par_ is None or legend_par_.are_colors_default:
        graphic.legend_parameters.colors = Colorset.shade_benefit()
    if legend_par_ is None or legend_par_.min is None:
        graphic.legend_parameters.min = 0
    title = text_objects('Shade Benefit', graphic.lower_title_location,
                         graphic.legend_parameters.text_height * 1.5,
                         graphic.legend_parameters.font)

    # create all of the visual outputs
    analysis_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(analysis_mesh)
    legend = legend_objects(graphic.legend)
