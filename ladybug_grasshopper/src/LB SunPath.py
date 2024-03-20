# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Output a Sunpath (aka. sun plot) graphic into the Rhino scene.
-
The component also outputs sun vectors that can be used for solar access
analysis and shading design.
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        hoys_: A number or list of numbers between 0 and 8760 that represent the
            hour of the year at which to evaluate the sun position. The
            "LB Calculate HOY" component can output this number given a month,
            day and hour. The "LB Analysis Period" component can output a
            list of HOYs within a certain hour or date range.
        dl_saving_: An optional analysis period for daylight saving time.
            If None, no daylight saving time will be used. (Default: None)
        solar_time_: A boolean to indicate if the input hours should be treated
             as solar time instead of standard or daylight time. (Default: False)
        _center_pt_: A point for the center of the sun path. (Default: (0, 0, 0))
        _scale_: A number to set the scale of the sun path. The default is 1,
            which corresponds to a radius of 100 meters in the current Rhino
            model's unit system.
        projection_: Optional text for the name of a projection to use from the sky
            dome hemisphere to the 2D plane. If None, a 3D sun path will be drawn
            instead of a 2D one. (Default: None) Choose from the following:
                * Orthographic
                * Stereographic
        daily_: Boolean to note whether the sunpath should display only one daily
            arc for each unique day in the input hoys_ (True) or whether the
            output sun path geometry should be for the entire year, complete
            with analemmas for all sun-up hours and a daily arc for each
            month (False). (Default: False)
        data_: Optional HourlyContinuousCollection objects, which will be used
            to generate colors that align with each of the sun_pts. This data
            can also be used along with the statement_ below to select out
            sun positions that meet certain conditions.
        statement_: A conditional statement as a string (e.g. a > 25).
            .   
            The variable of the first data collection should always be named 'a'
            (without quotations), the variable of the second list should be
            named 'b', and so on.
            .
            For example, if three data collections are connected to _data
            and the following statement is applied:
            '18 < a < 26 and b < 80 and c > 2'
            The resulting collections will only include values where the first
            data collection is between 18 and 26, the second collection is less
            than 80 and the third collection is greater than 2.
        legend_par_: An optional LegendParameter object to change the display
            of the data on the sun path. This can also be a list of legend
            parameters to be applied to the different connected data_.

    Returns:
        report: Reports, errors, warnings, etc.
        vectors: Vector(s) indicating the direction of sunlight for each sun
            position on the sun path. Note that these vectors point downwards
            towards the ground.
        altitudes: Number(s) indicating the sun altitude(s) in degrees for
            each sun position on the sun path.
        azimuths: Number(s) indicating the sun azimuths in degrees for each
            sun position on the sun path.
        hoys: The hour of the year for each sun positions on the sun path.
        sun_pts: Point(s) representing the location of the sun on the sunpath.
        analemma: A set of curves that mark the hourly positions of the sun
            throughout the different months of the year.
        daily: A set of arcs that mark the path of the sun across the sky
            dome over the course of a day.
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in relation to the sun path.
        legend: Geometry representing the legend for the input data_. Will be None
            if no _data is connected.
        title: A text object for the title of the sunpath.
        color_pts: A list of points colored with the input data_, which will display
            in the Rhino scene in accordance with the legend. Note that
            the text representation of these objects bears the RGB color of each
            point. So casting this output to text and then to a color will
            yeild color objects that can be used for previewing other types
            of geometry with the input data_. Will be None if no _data is connected.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the Sunpath in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this version
            of the Sunpath in Rhino.
"""

ghenv.Component.Name = 'LB SunPath'
ghenv.Component.NickName = 'Sunpath'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D, Point2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.sunpath import Sunpath
    from ladybug.compass import Compass
    from ladybug.graphic import GraphicContainer
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.dt import Date
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.colorize import ColoredPoint
    from ladybug_rhino.fromgeometry import from_polyline3d, from_polyline2d, \
        from_arc3d, from_vector3d, from_point3d, from_point2d
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.togeometry import to_vector2d, to_point2d, to_point3d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        hide_output, show_output, schedule_solution, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import math


def draw_analemma_and_arcs(sp, datetimes, radius, center_pt3d):
    """Draw analemma and day arc Rhino geometry.

    Args:
        sp: Sunpath object for which geometry will be drawn.
        datetimes: A list of datetimes, which will be used to get days
            if daily_ is True.
        radius: Number for the radius of the sun path.
        center_pt3d: Point3D for the center of the sun path.

    Returns:
        analemma: List of Rhino curves for the analemmas
        daily: List of Rhino curves for the daily arcs.
    """
    sp.daylight_saving_period = None  # set here so analemmas aren't messed up

    center_pt, z = Point2D(center_pt3d.x, center_pt3d.y), center_pt3d.z
    if not daily_:
        if projection_ is None:
            analemma = [from_polyline3d(pline) for pline in sp.hourly_analemma_polyline3d(
                center_pt3d, radius, True, solar_time_)]
            daily = [from_arc3d(arc) for arc in sp.monthly_day_arc3d(center_pt3d, radius)]
        else:
            analemma = [from_polyline2d(pline, z) for pline in sp.hourly_analemma_polyline2d(
                projection_, center_pt, radius, True, solar_time_)]
            daily = [from_polyline2d(arc, z) for arc in sp.monthly_day_polyline2d(
                projection_, center_pt3d, radius)]
    else:
        analemma = []  # No Analemmas for a daily sun path
        doys = set(dt.doy for dt in datetimes)
        dates = [Date.from_doy(doy) for doy in doys]
        if projection_ is None:
            daily = [from_arc3d(sp.day_arc3d(dat.month, dat.day, center_pt3d, radius))
                     for dat in dates]
        else:
            daily = []
            for dat in dates:
                pline = sp.day_polyline2d(dat.month, dat.day, projection_, center_pt, radius)
                daily.append(from_polyline2d(pline, z))
    return analemma, daily


def draw_sun_positions(suns, radius, center_pt3d):
    """Draw Rhino points from a list of sun objects.

    Args:
        suns: A list of suns to be output as points
        radius: Number for the radius of the sun path.
        center_pt3d: Point3D for the center of the sun path.

    Returns:
        A list of Rhino points for sun positions
    """
        # get points for sun positions
    if projection_ is None:
        return [from_point3d(sun.position_3d(center_pt3d, radius)) for sun in suns]
    else:
        return [from_point2d(sun.position_2d(projection_, center_pt3d, radius), z)
                for sun in suns]


def title_text(data_col):
    """Get a text string for the title of the sunpath."""
    title_array = ['{} ({})'.format(data_col.header.data_type,
                                    data_col.header.unit)]
    for key, val in data_col.header.metadata.items():
        title_array.append('{}: {}'.format(key, val))
    return '\n'.join(title_array)


if all_required_inputs(ghenv.Component):
    # process all of the global inputs for the sunpath
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    if _center_pt_ is not None:  # process the center point into a Point2D
        center_pt, center_pt3d = to_point2d(_center_pt_), to_point3d(_center_pt_)
        z = center_pt3d.z
    else:
        center_pt, center_pt3d = Point2D(), Point3D()
        z = 0
    _scale_ = 1 if _scale_ is None else _scale_ # process the scale into a radius
    radius = (100 * _scale_) / conversion_to_meters()
    solar_time_ = False if solar_time_ is None else solar_time_  # process solar time
    daily_ = False if daily_ is None else daily_  # process the daily input
    projection_ = projection_.title() if projection_ is not None else None

    # create a intersection of the input hoys_ and the data hoys
    if len(data_) > 0 and data_[0] is not None and len(hoys_) > 0:
        all_aligned = all(data_[0].is_collection_aligned(d) for d in data_[1:])
        assert all_aligned, 'All collections input to data_ must be aligned for ' \
            'each Sunpath.\nGrafting the data_ and suplying multiple grafted ' \
            '_center_pt_ can be used to view each data on its own path.'
        if statement_ is not None:
            data_ = HourlyContinuousCollection.filter_collections_by_statement(
                data_, statement_)
        data_hoys = set(dt.hoy for dt in data_[0].datetimes)
        hoys_ = list(data_hoys.intersection(set(hoys_)))

    # initialize sunpath based on location
    sp = Sunpath.from_location(_location, north_, dl_saving_)

    # process all of the input hoys into altitudes, azimuths and vectors
    altitudes, azimuths, datetimes, moys, hoys, vectors, suns = [], [], [], [], [], [], []
    for hoy in hoys_:
        sun = sp.calculate_sun_from_hoy(hoy, solar_time_)
        if sun.is_during_day:
            altitudes.append(sun.altitude)
            azimuths.append(sun.azimuth)
            datetimes.append(sun.datetime)
            moys.append(sun.datetime.moy)
            hoys.append(sun.datetime.hoy)
            vectors.append(from_vector3d(sun.sun_vector))
            suns.append(sun)

    if len(data_) > 0 and data_[0] is not None and len(hoys_) > 0:  # build a sunpath for each data collection
        title, all_sun_pts, all_analemma, all_daily, all_compass, all_col_pts, all_legends = \
            [], [], [], [], [], [], []
        for i, data in enumerate(data_):
            try:  # sense when several legend parameters are connected
                lpar = legend_par_[i]
            except IndexError:
                lpar = None if len(legend_par_) == 0 else legend_par_[-1]

            # move the center point so sun paths are not on top of one another
            fac = i* radius * 3
            center_pt_i = Point2D(center_pt.x + fac, center_pt.y)
            center_pt3d_i = Point3D(center_pt3d.x + fac, center_pt3d.y, center_pt3d.z)

            # create the ladybug compass object
            lb_compass = Compass(radius, center_pt_i, north_)

            # create a graphic container to generate colors and legends
            n_data = data.filter_by_moys(moys)  # filter data collection by sun-up hours
            graphic = GraphicContainer(
                n_data.values, lb_compass.min_point3d(z), lb_compass.max_point3d(z),
                lpar, n_data.header.data_type, n_data.header.unit)
            all_legends.append(legend_objects(graphic.legend))
            title.append(text_objects(
                title_text(n_data), graphic.lower_title_location,
                graphic.legend_parameters.text_height, graphic.legend_parameters.font))

            # create points, analemmas, daily arcs, and compass geometry
            sun_pts_init = draw_sun_positions(suns, radius, center_pt3d_i)
            analemma_i, daily_i = draw_analemma_and_arcs(sp, datetimes, radius, center_pt3d_i)
            compass_i = compass_objects(lb_compass, z, None, projection_,
                                        graphic.legend_parameters.font)
            all_analemma.append(analemma_i)
            all_daily.append(daily_i)
            all_compass.append(compass_i)

            # produce a visualization of colored points
            cols = [color_to_color(col) for col in graphic.value_colors]
            col_pts = []
            for pt, col in zip(sun_pts_init, cols):
                col_pt = ColoredPoint(pt)
                col_pt.color = col
                col_pts.append(col_pt)
            all_sun_pts.append(sun_pts_init)
            all_col_pts.append(col_pts)

        # convert all nested lists to data trees
        sun_pts = list_to_data_tree(all_sun_pts)
        analemma = list_to_data_tree(all_analemma)
        daily = list_to_data_tree(all_daily)
        compass = list_to_data_tree(all_compass)
        legend = list_to_data_tree(all_legends)

        # do some acrobatics to get the colored points to display
        # CWM: I don't know why we have to re-schedule the solution but this is the
        # only way I found to get the colored points to appear (redraw did not work).
        color_pts = list_to_data_tree(all_col_pts)
        hide_output(ghenv.Component, 5)
        schedule_solution(ghenv.Component, 2)
    else:  # no data connected; just output one sunpath
        sun_pts = draw_sun_positions(suns, radius, center_pt3d)
        analemma, daily = draw_analemma_and_arcs(sp, datetimes, radius, center_pt3d)
        font = legend_par_[0].font if len(legend_par_) != 0 and \
            legend_par_[0] is not None else 'Arial'
        compass = compass_objects(Compass(radius, center_pt, north_), z, None, projection_, font)
        if _location.city:
            title = text_objects(
                'city: {}'.format(_location.city),
                Plane(o=center_pt3d.move(Vector3D(-radius * 1.25, -radius * 1.25))),
                radius / 15, font)
        show_output(ghenv.Component, 5)

    # create the output VisualizationSet arguments
    l_par = None
    if len(legend_par_) != 0:
        l_par = legend_par_[0] if len(legend_par_) == 1 else legend_par_
    vis_set = [sp, hoys_, data_, l_par, radius, center_pt3d, solar_time_, daily_, projection_]
    vis_set = objectify_output('VisualizationSet Aruments [Sunpath]', vis_set)
