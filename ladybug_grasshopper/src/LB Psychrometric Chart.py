# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Draw a psychrometric chart in the Rhino scene and plot a set of temperatures and
humidity values on it.
_
Connected data can be either outdoor temperature and humidty from imported EPW
weather data or indoor temperature and humidity ratios from an energy simulation.
-

    Args:
        _temperature: A hourly, daily, or sub-hourly data collection of temperature values
            or a single temperature value in Celcius to be used for the whole
            analysis. If this input data collection is in in Farenheit, the
            entire chart will be drawn using IP units. Operative temperature
            should be used if it is available. Otherwise, air temperature
            (aka. dry bulb temperature) is suitable.
        _rel_humidity: A hourly, daily, or sub-hourly data collection of relative humidity
            values in % or a single relative humidity value to be used for the
            whole analysis. Note that the input data collection here must align
            with the _temperature input.
        _pressure_: A data collection of atmospheric pressure in Pascals or a single
            number for the average air pressure across the data plotted on the
            chart. It is recommended that the barometric pressure from the
            "Import EPW" component be used here as the default is not sutiable
            for higher elevations. (Default: 101325 Pa; pressure at sea level).
        _base_pt_: A point to be used as the bottom-left-most point from which all
            geometry of the plot will be generated. (Default: (0, 0, 0)).
        _scale_: A number to set the dimensions of the chart. (Default: 1).
        _temp_range_: An optional domain (or number for the upper temperature), which
            will be used to set the lower and upper boundaries of temperature
            on the psychrometric chart. (Default: -20 to 55 when the chart is
            in SI; -5 to 115 when the chart is in IP).
        plot_wet_bulb_: Boolean to note whether the psychrometric chart should be ploted
            with lines of constant enthalpy (False) or lines of constant wet bulb
            temperature (True).  (Default: False).
        legend_par_: An optional LegendParameter object from the "LB Legend Parameters"
            component to change the display of the Pyschrometric Chart.
        data_: Optional data collections, which are aligned with the input _temperature
            and _rel_humidity, which will be output from the data of this
            component and can be used to color points with data. This data
            can also be used along with the statement_ below to select out
            data that meets certain conditions.
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
            .
            For this component, temperature will always be the second-to-last
            letter and relative humidity will be the last letter.
        period_: A Ladybug analysis period to be applied to the _temperature and
            _rel_humidity of the input data_.

    Returns:
        report: ...
        title: Text objects for the chart title and axes titles as well as a polyline for
            the outer border of the chart. Note that the polyline for the border
            excludes the saturation line.
        temp_lines: A list of line segments and text objects for the temperature labels
            on the chart.
        rh_lines: A list of curves and text objects for the relative humidity labels
            on the chart.
        hr_lines: A list of line segments and text objects for the humidty ratio labels
            on the chart.
        enth_wb_lines: A list of line segments and text objects for the enthalpy or
            wet bulb temperature labels on the chart.
        mesh: A colored mesh showing the number of input hours that happen in each part
            of the psychrometric chart.
        legend: A colored legend showing the number of hours that correspond to
            each color.
        points: Points representing each of the input temperature and humidity values.
            By default, this ouput is hidden and it should be connected it to a
            native Grasshopper preview component to view it.
        data: The input data_ with the input statements or the periods applied to it.
            These can be deconstructed with the "LB Deconstruct Data" component
            and the resulting values can be plugged into the "LB Create Legend"
            component to generate colors that can be used to color the points
            above using the native Grasshopper "Custom Preview" component.
        psych_chart: A Psychrometric Chart object, which can be connected to any
            of the "Comfort Polygon" components in order to plot polygons on
            the chart and perform thermal comfort analyses on the data.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the Psychrometric Chart in the Rhino scene. This can be
            connected to the "LB Preview Visualization Set" component to display
            this version of the Psychrometric Chart in Rhino.
"""

ghenv.Component.Name = 'LB Psychrometric Chart'
ghenv.Component.NickName = 'PsychrometricChart'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.datacollection import BaseCollection
    from ladybug.psychchart import PsychrometricChart
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point2d, to_point3d
    from ladybug_rhino.fromgeometry import from_mesh2d, from_polyline2d, \
        from_linesegment2d, from_point2d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        hide_output, show_output, longest_list, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def leg_par_by_index(i):
    """Get legend parameters associated with a given index of the chart."""
    try:
        return legend_par_[i]
    except IndexError:
        return None


def small_labels(psy_chart, labels, points, x_align, y_align, factor=1.0):
    """Translate a list of psych chart text labels into the Rhino scene."""
    return [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, z)),
                         psy_chart.legend_parameters.text_height * factor,
                         psy_chart.legend_parameters.font, x_align, y_align)
            for txt, pt in zip(labels, points)]


def plane_from_point(point_2d, align_vec=Vector3D(1, 0, 0)):
    """Get a Plane from a Point2D.

    Args:
        point_2d: A Point2D to serve as the origin of the plane.
        align_vec: A Vector3D to serve as the X-Axis of the plane.
    """
    return Plane(o=Point3D(point_2d.x, point_2d.y, z), x=align_vec)


def draw_psych_chart(psy_chart):
    """Draw a given psychrometric chart object into Rhino geometry.

    This will NOT translate any colored meshes or data points.
    """
    # output all of the lines/polylines for the various axes
    title_i = [from_polyline2d(psy_chart.chart_border, z)]
    temp_lines_i = [from_linesegment2d(tl, z) for tl in psy_chart.temperature_lines]
    rh_lines_i = [from_polyline2d(rhl, z) for rhl in psy_chart.rh_lines]
    hr_lines_i = [from_linesegment2d(hrl, z) for hrl in psy_chart.hr_lines]

    # add the text to the various lines
    title_i.append(text_objects(
        psy_chart.x_axis_text, plane_from_point(psy_chart.x_axis_location),
        psy_chart.legend_parameters.text_height * 1.5,
        psy_chart.legend_parameters.font, 0, 0))
    title_i.append(text_objects(
        psy_chart.y_axis_text, plane_from_point(psy_chart.y_axis_location, Vector3D(0, 1)),
        psy_chart.legend_parameters.text_height * 1.5,
        psy_chart.legend_parameters.font, 2, 0))
    temp_lines_i = temp_lines_i + small_labels(
        psy_chart, psy_chart.temperature_labels, psy_chart.temperature_label_points, 1, 0)
    rh_lines_i = rh_lines_i + small_labels(
        psy_chart, psy_chart.rh_labels[:-1], psy_chart.rh_label_points[:-1], 2, 3, 0.8)
    hr_lines_i = hr_lines_i + small_labels(
        psy_chart, psy_chart.hr_labels, psy_chart.hr_label_points, 0, 3)

    # add enthalpy or wet bulb lines
    if plot_wet_bulb_:
        enth_wb_lines_i = [from_linesegment2d(el, z) for el in psy_chart.wb_lines]
        enth_wb_lines_i = enth_wb_lines_i + small_labels(
            psy_chart, psy_chart.wb_labels, psy_chart.wb_label_points, 2, 3)
    else:
        enth_wb_lines_i = [from_linesegment2d(el, z) for el in psy_chart.enthalpy_lines]
        enth_wb_lines_i = enth_wb_lines_i + small_labels(
            psy_chart, psy_chart.enthalpy_labels, psy_chart.enthalpy_label_points, 2, 3)

    # add all of the objects to the bse list
    title.append(title_i)
    temp_lines.append(temp_lines_i)
    rh_lines.append(rh_lines_i)
    hr_lines.append(hr_lines_i)
    enth_wb_lines.append(enth_wb_lines_i)


if all_required_inputs(ghenv.Component):
    # process the base point
    bp = to_point2d(_base_pt_) if _base_pt_ is not None else Point2D()
    z = to_point3d(_base_pt_).z if _base_pt_ is not None else 0

    # create lists to be filled with objects
    title = []
    temp_lines = []
    rh_lines = []
    hr_lines = []
    enth_wb_lines = []
    mesh = []
    legend = []
    points = []
    data_colls = []
    psych_chart = []
    vis_set = []

    # loop through the input temperatures and humidity and plot psych charts
    for j, (temperature, rel_humid) in enumerate(zip(_temperature, _rel_humidity)):
        # process the pressure input
        pressure = 101325
        if len(_pressure_) != 0:
            pr = longest_list(_pressure_, j)
            try:
                pressure = float(pr)
            except Exception:  # assume that it's a data collection
                assert pr.header.unit == 'Pa', '_pressure_ input must be in Pa.'
                pressure = pr.average

        # sense if the input temperature is in Farenheit
        use_ip = False
        if isinstance(temperature, BaseCollection):
            if temperature.header.unit != 'C':  # convert to C and set chart to use_ip
                temperature = temperature.to_si()
                use_ip = True

        # set default values for the chart dimensions
        _scale_ = 1.0 if _scale_ is None else _scale_
        x_dim = _scale_ * 2 / conversion_to_meters()
        y_dim = (_scale_ * 2 * 1500) / conversion_to_meters()
        y_dim = y_dim * (9 / 5) if use_ip else y_dim
        t_min, t_max = (-5, 115) if use_ip else (-20, 50)
        if _temp_range_ is not None:
            t_min, t_max = _temp_range_
        y_move_dist = -y_dim * 0.04 * j
        base_pt = bp.move(Vector2D(0, y_move_dist))

        # apply any analysis periods and conditional statements to the input collections
        original_temperature = temperature
        all_data = data_ + [temperature, rel_humid]
        if period_ is not None:
            all_data = [coll.filter_by_analysis_period(period_) for coll in all_data]
        if statement_ is not None:
            all_data = BaseCollection.filter_collections_by_statement(all_data, statement_)

        # create the psychrometric chart object and draw it in the Rhino scene
        psy_chart = PsychrometricChart(
            all_data[-2], all_data[-1], pressure, leg_par_by_index(0), base_pt, x_dim, y_dim,
            t_min, t_max, use_ip=use_ip)
        psy_chart.z = z
        psy_chart.original_temperature = original_temperature
        draw_psych_chart(psy_chart)
        if isinstance(all_data[-2], BaseCollection):
            meta_i = all_data[-2].header.metadata.items()
            title_items = ['Time [hr]'] + ['{}: {}'.format(k, v) for k, v in meta_i]
        else:
            title_items = ['Psychrometric Chart']
        ttl_tp = psy_chart.container.upper_title_location
        if z != 0:
            ttl_tp = Plane(n=ttl_tp.n, o=Point3D(ttl_tp.o.x, ttl_tp.o.y, z), x=ttl_tp.x)
        title[j + j * len(data_)].append(text_objects(
            '\n'.join(title_items), ttl_tp,
            psy_chart.legend_parameters.text_height * 1.5,
            psy_chart.legend_parameters.font, 0, 0))
        psych_chart.append(psy_chart)
        vs_args = [psy_chart]

        # plot the data on the chart
        lb_points = psy_chart.data_points
        points.append([from_point2d(pt) for pt in lb_points])
        if len(lb_points) != 1:  # hide the points and just display the mesh
            hide_output(ghenv.Component, 8)
            mesh.append(from_mesh2d(psy_chart.colored_mesh, z))
            leg = psy_chart.legend
            if z != 0 and leg.legend_parameters.is_base_plane_default:
                nl_par = leg.legend_parameters.duplicate()
                m_vec = Vector3D(0, 0, z)
                nl_par.base_plane = nl_par.base_plane.move(m_vec)
                leg._legend_par = nl_par
            legend.append(legend_objects(leg))
        else:  # show the single point on the chart
            show_output(ghenv.Component, 8)

        # process any of the connected data into a legend and colors
        if len(data_) != 0:
            data_colls.append(all_data[:-2])
            move_dist = x_dim * (psy_chart.max_temperature - psy_chart.min_temperature + 20)
            vs_leg_par = []
            for i, d in enumerate(all_data[:-2]):
                # create a new psychrometric chart offset from the original
                new_pt = Point2D(base_pt.x + move_dist * (i + 1), base_pt.y)
                psy_chart = PsychrometricChart(
                    all_data[-2], all_data[-1], pressure, leg_par_by_index(0),
                    new_pt, x_dim, y_dim, t_min, t_max, use_ip=use_ip)
                psy_chart.z = z
                psy_chart.original_temperature = original_temperature
                draw_psych_chart(psy_chart)
                psych_chart.append(psy_chart)
                lb_mesh, container = psy_chart.data_mesh(d, leg_par_by_index(i + 1))
                mesh.append(from_mesh2d(lb_mesh, z))
                leg = container.legend
                vs_leg_par.append(leg.legend_parameters)
                if z != 0 and leg.legend_parameters.is_base_plane_default:
                    nl_par = leg.legend_parameters.duplicate()
                    m_vec = Vector3D(0, 0, z)
                    nl_par.base_plane = nl_par.base_plane.move(m_vec)
                    leg._legend_par = nl_par
                legend.append(legend_objects(leg))
                move_vec = Vector2D(base_pt.x + move_dist * (i + 1), 0)
                points.append([from_point2d(pt.move(move_vec)) for pt in lb_points])

                # add a title for the new chart
                title_items = ['{} [{}]'.format(d.header.data_type, d.header.unit)] + \
                    ['{}: {}'.format(key, val) for key, val in d.header.metadata.items()]
                ttl_tp = psy_chart.container.upper_title_location
                if z != 0:
                    ttl_tp = Plane(n=ttl_tp.n, o=Point3D(ttl_tp.o.x, ttl_tp.o.y, z), x=ttl_tp.x)
                title[j + j * len(data_) + (i + 1)].append(text_objects(
                    '\n'.join(title_items), ttl_tp,
                    psy_chart.legend_parameters.text_height * 1.5,
                    psy_chart.legend_parameters.font, 0, 0))
            vs_args.extend([all_data[:-2], vs_leg_par, z, bool(plot_wet_bulb_)])
        else:
            vs_args.extend([None, None, z, bool(plot_wet_bulb_)])
        vis_set.append(vs_args)

    # upack all of the python matrices into data trees
    title = list_to_data_tree(title)
    temp_lines = list_to_data_tree(temp_lines)
    rh_lines = list_to_data_tree(rh_lines)
    hr_lines = list_to_data_tree(hr_lines)
    enth_wb_lines = list_to_data_tree(enth_wb_lines)
    legend = list_to_data_tree(legend)
    points = list_to_data_tree(points)
    data = list_to_data_tree(data_colls)

    # output arguments for the visualization set
    vis_set = objectify_output('VisualizationSet Aruments [PsychrometricChart]', vis_set)
