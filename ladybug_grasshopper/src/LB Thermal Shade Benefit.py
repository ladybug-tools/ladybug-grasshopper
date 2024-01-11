# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize the desirability of shade in terms of proximity of conditions to
a favorable temerature range.
_
The calculation runs by generating solar vectors for a data collection of input
temperature values. Solar vectors for hours when the temperature is above the
upper temperature threshold contribute positively to shade desirability (shade_help)
while solar vectors for hours when the temperature is below the lower temperature
threshold contribute negatively (shade_harm).
_
The component outputs a colored mesh of the shade illustrating the net effect of
shading each part of the _shade_geo. A higher saturation of blue indicates that
shading the cell is desirable to avoid excessively hot temperatures. A higher
saturation of red indicates that shading the cell is harmful, blocking helpful
sun in cold conditions that could bring conditions closer to the desired
temperature range. Desaturated cells indicate that shading the cell will have
relatively little effect on keeping the _study_region in the desired thermal range.
_
The units for shade desirability are degree-days per unit area of shade, which are
essentially the amount of time in days that sun is blocked by a given cell
multiplied by the degrees above (or below) the temperature thresholds during
that time. So, if a given square meter of input _shade_geo has a shade desirability
of 10 degree-days per square meter, this means that a shade in this location
provides roughly 1 day of sun protection from conditions 10 degrees Celsius
warmer than the _up_threshold_ to the _study_region.
_
More information on the methods used by this component can be found in the
following publication:
Mackey, Christopher; Sadeghipour Roudsari, Mostapha; Samaras, Panagiotis.
“ComfortCover: A Novel Method for the Design of Outdoor Shades.” In Proceedings
of Symposium on Simulation for Architecture and Urban Design. Washington, DC,
United States, Apr 12-15 2015.
https://drive.google.com/file/d/0Bz2PwDvkjovJQVRTRHhMSXZWZjQ/view?usp=sharing
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        _temperature: An hourly data collection with the unshaded temperature experienced
            at the _study_region. This temperature will be used to evaluate shade
            benefit for this study region. This temperature data collection should
            typically be informed by an analysis with the "LB Outdoor Solar MRT"
            or the "LB Indoor Solar MRT" component, which will account for the
            increased temperature delta expereinced as a result of being in the
            sun. For evaluation of shade in terms of outdoor thermal comfort, the
            best practice is to use the Universal Thermal Climate Index (UTCI)
            temperature at the study region for this input. For evaluation of
            shade benefit in terms of indoor comfort,  the best practice is to
            use the Standard Effective Temperature (SET) derived from the
            "LB PMV Comfort" component for this input. In both cases, the MRT
            inputs to the thermal comfort models should use solar-adjusted MRT.
        _study_region: Rhino Breps and/or Rhino Meshes representing an area for which shading
            desirability is being evaluated. This is often the region where a human
            subject will sit (eg. a bench) or it could be the window of a building
            where an occupant might be standing or sitting.
        _shade_geo: Rhino Breps and/or Rhino Meshes representing shading to be evaluated
            in terms of its benefit. Note that, in the case that multiple
            shading geometries are connected, this component does not account
            for the interaction between the different shading surfaces and will
            just evaluate each part of the shade independently.
        context_: Rhino Breps and/or Rhino Meshes representing context geometry that can
            block sunlight to the _study_region, therefore discounting any benefit
            or harm that could come to the region.
        _grid_size: A positive number in Rhino model units for the size of grid cells at
            which the input _shade_geo will be subdivided for shade benefit
            analysis. The smaller the grid size, the higher the resolution of
            the analysis and the longer the calculation will take.  So it is
            recommended that one start with a large value here and decrease
            the value as needed. However, the grid size should usually be
            smaller than the dimensions of the smallest piece of the _shade_geo
            and context_ in order to yield meaningful results.
        _up_threshold_: A number representing the temperature in Celsius above which
            shade is considered desirable/helpful. The default is 26C, which
            corresponds to the upper limit of "No Thermal Stress" according
            to the UTCI thermal comfort model (above this, heat stress begins).
            A different value may be desirable for indoor thermal comfort studies.
        _low_threshold_: A number representing the temperature in Celsius below which shade
            is considered harmful and access to the sun is preferable. The default
            is 9C, which corresponds to the lower limit of "No Thermal Stress"
            according to the UTCI thermal comfort model (below this, cold stress
            begins). A different value may be desirable for indoor thermal
            comfort studies.
        _timestep_: An integer for the number of timesteps per hour at which
            sun vectors will be generated for the analysis. Higher values will
            result in the generation of more vectors, which will make the
            resulting shade mesh smoother and a better representation of shade
            benefit and harm. However, the calculation will take
            longer as there are more intersection operations to perform. The
            default is 1 timestep per hour, which is the coarsest resolution
            avalable and the fastest calculation.
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and perform shade benefit analysis.

    Returns:
        report: ...
        vectors: The sun vectors that were used to evaluate the shade (note that
            these will increase as the _timestep_ increases).
        points: Points across the study_region from which sun vectors are projected.
        mesh: A colored mesh of the _shade_geo showing where shading is helpful (in blue),
            harmful (in red), or does not make much of a difference (white or
            desaturated colors). Note that the colors can change depending upon
            the input legend_par_.
        legend: Legend showing the numeric values of degree-days per unit are of shade
            that correspond to the colors in the shade mesh.
        title: A text object for the study title.
        shade_help: The cumulative degree-days per square area unit helped by shading each
            cell of the shade. If a given square meter of _shade_geo has a helpfulness
            of 10 degree-days/m2, this means that a shade in this location provides
            1 day of sun protection from conditions 10 degrees warmer than the
            _up_threshold_ to the _study_region.
        shade_harm: The cumulative degree-days per square area unit harmed by shading each
            cell of the shade. If a given square meter of _shade_geo has a harmfulness
            of -10 degree-days, this means that a shade in this location blocks
            1 day of sun duirng conditions that are 10 degrees Celsius colder than
            the _low_threshold_ to the _study_region.
        shade_net: The sum of the helpfulness and harmfulness for each cell. This will be
            negative if shading the cell has a net harmful effect and positive
            if the shade has a net helpful effect.
"""

ghenv.Component.Name = 'LB Thermal Shade Benefit'
ghenv.Component.NickName = 'ThermalShadeBenefit'
ghenv.Component.Message = '1.7.4'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import math

try:
    from ladybug.sunpath import Sunpath
    from ladybug.datacollection import HourlyDiscontinuousCollection
    from ladybug.color import Colorset
    from ladybug.graphic import GraphicContainer
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import units_abbreviation
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.intersect import join_geometry_to_mesh, generate_intersection_rays, \
        intersect_rays_with_mesh_faces
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output, \
        recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set the defaults and process all of the inputs
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    assert isinstance(_temperature, HourlyDiscontinuousCollection), \
        'Connected _temperature is not a Hourly Data Collection. Got {}'.format(
            type(_temperature))
    assert _temperature.header.unit == 'C', \
        'Connected _temperature must be in Celsius. Got {}.'.format(
            _temperature.header.unit)
    if _timestep_ and _timestep_ != _temperature.header.analysis_period.timestep:
        if _timestep_ < _temperature.header.analysis_period.timestep:
            data = _temperature.cull_to_timestep(_timestep_)
        else:
            data = _temperature.interpolate_to_timestep(_timestep_)
    else:
        data = _temperature
    t_step_per_day = data.header.analysis_period.timestep * 24
    up_thresh = 26 if _up_threshold_ is None else _up_threshold_
    low_thresh = 9 if _low_threshold_ is None else _low_threshold_
    assert up_thresh > low_thresh, 'Input _up_threshold_ [{}] must be greater ' \
        'than input _low_threshold_ [{}].'.format(up_thresh, low_thresh)

    # initialize sunpath based on location and get all of the vectors
    sp = Sunpath.from_location(_location, north_)
    lb_vecs, relevant_temps = [], []
    for dt, temp in zip(data.datetimes, data.values):
        if temp > up_thresh or temp < low_thresh:
            sun = sp.calculate_sun_from_date_time(dt)
            if sun.is_during_day:
                lb_vecs.append(sun.sun_vector_reversed)
                relevant_temps.append(temp)
    vectors = [from_vector3d(lb_vec) for lb_vec in lb_vecs]

    # create the gridded mesh from the geometry
    analysis_mesh = to_joined_gridded_mesh3d(_shade_geo, _grid_size)
    mesh = from_mesh3d(analysis_mesh)
    study_mesh = to_joined_gridded_mesh3d(_study_region, _grid_size / 2)
    points = [from_point3d(pt) for pt in study_mesh.face_centroids]
    hide_output(ghenv.Component, 2)

    # create a series of rays that represent the sun projected through the shade
    int_rays = generate_intersection_rays(points, vectors)

    # if there is context, remove any rays that are blocked by the context
    shade_mesh = join_geometry_to_mesh(context_) \
        if len(context_) != 0 and context_[0] is not None else None

    # intersect the sun rays with the shade mesh
    face_int = intersect_rays_with_mesh_faces(
        mesh, int_rays, shade_mesh, cpu_count=workers)

    # loop through the face intersection result and evaluate the benefit
    pt_div = 1 / float(len(points))
    shade_help, shade_harm, shade_net = [], [], []
    for face_res, face_area in zip(face_int, analysis_mesh.face_areas):
        f_help, f_harm = 0, 0
        for t_ind in face_res:
            t_val = relevant_temps[t_ind]
            if t_val > up_thresh:
                f_help += t_val - up_thresh
            elif t_val < low_thresh:
                f_harm += t_val - low_thresh
        # Normalize by the area of the cell so there's is a consistent metric
        # between cells of different areas.
        # Also, divide the value by t_step_per_day such that the final unit is in
        # degree-days/model unit instead of degree-timesteps/model unit.
        shd_help = ((f_help / face_area) / t_step_per_day) * pt_div
        shd_harm = ((f_harm / face_area) / t_step_per_day) * pt_div
        shade_help.append(shd_help)
        shade_harm.append(shd_harm)
        shade_net.append(shd_help + shd_harm)

    # create the mesh and legend outputs
    graphic = GraphicContainer(shade_net, analysis_mesh.min, analysis_mesh.max, legend_par_)
    graphic.legend_parameters.title = 'degC-days/{}2'.format(units_abbreviation())
    if legend_par_ is None or legend_par_.are_colors_default:
        graphic.legend_parameters.colors = reversed(Colorset.shade_benefit_harm())
    if legend_par_ is None or legend_par_.min is None or legend_par_.max is None:
        bnd_val = max(max(shade_net), abs(min(shade_net)))
        if legend_par_ is None or legend_par_.min is None:
            graphic.legend_parameters.min = -bnd_val
        if legend_par_ is None or legend_par_.max is None:
            graphic.legend_parameters.max = bnd_val
    title = text_objects('Thermal Shade Benefit', graphic.lower_title_location,
                         graphic.legend_parameters.text_height * 1.5,
                         graphic.legend_parameters.font)

    # create all of the visual outputs
    analysis_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(analysis_mesh)
    legend = legend_objects(graphic.legend)
